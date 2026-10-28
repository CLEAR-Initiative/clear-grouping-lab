#!/usr/bin/env python3
"""Replay one day's signals through a candidate clustering algorithm and write
a layer: layers/<country>/<date>.<algo>[-<tag>].json

    python3 replay.py --country sudan --date 2026-10-20 --algo jev-v1
    python3 replay.py --country sudan --date 2026-10-20 --algo jev-v1 --window-hours 168 --tag 7d
    python3 replay.py --country sudan --date 2026-10-20 --algo naive-state   # no model calls

Algorithms
  jev-v1       Per signal, in publishedAt order: collect open events (built so
               far in this replay) in the same state within the window, falling
               back to the whole country when the signal only resolves to the
               country. One Jev Decisions call asks three questions over
               {signal, events}: `same_event` (Choice over the candidates plus
               "none"), `matches_any` (Noul: does it report on any listed event)
               and `relevant` (Noul: is it an actual current occurrence, the
               same gate production uses). Decision rule, all thresholds in
               params: relevance < relevance_threshold → dropped; no candidates
               → new; join the top candidate when matches_any ≥ any_threshold,
               its probability ≥ abs_threshold and it beats the runner-up by
               ≥ margin; otherwise new event, with the candidates recorded as
               links ("new-linked") so an analyst could merge later.
  naive-state  No model. Key = (state, glideCode) within the window. A cheap
               control that shows what an admin-1 fallback key would do (the
               page's idea 7, the one we said we would not ship).
  v2-replay    No model. Today's production rule (V2) replayed on the day:
               key = (district, type family = level_2 of the glide code), join
               the open event with the newest signal, and a signal with no
               district always starts its own event. A control: it differs
               from clear-as-run only in starting the day with no open events.
  v2-gazetteer v2-replay, plus idea 6's interim location fix: a signal that
               only resolves to a state or the country is promoted to a
               district when a place it names (translate.py's place list)
               matches exactly one district, or a named point inside one, in
               its state. `--type-level 1` keys on the top-level family
               (conflict) instead, idea 6's other half.
  embed-v1     No LLM. Same candidate pool as jev-v1; each candidate scores the
               highest cosine similarity between the signal's Voyage embedding
               (Voyage directly with VOYAGE_API_KEY, else through OpenRouter)
               and any of the candidate's signals. Join the best when it is
               ≥ --sim-threshold and beats the runner-up by ≥ --sim-margin.
               Tests whether Jev does more than text similarity would.

`--scope country` (jev-v1 and embed-v1) widens the candidate pool from the
signal's state to the whole country: same-state events first, then events
from other states newest first, up to --max-candidates. It tests whether a
mislocated signal misses its event because the right one is never offered.

The control algorithms (naive-state, v2-*, embed-v1) reuse CLEAR's own
relevance verdict, so their dropped signals are exactly CLEAR's.

Every candidate list and every probability is written to the layer under
`decisions[signalId]` so the viewer can show exactly what Jev saw. Jev
responses are cached under layers/.cache by request hash, so reruns with the
same prompts cost nothing; change the prompt version to invalidate.

Candidate summaries are built by rule, not by a model (decision Q3 in README):
  "<location> · <first title> · <n> signals <HH:MM>–<HH:MM> · latest: <title>"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timedelta

from lab_common import (
    DATA,
    LAB,
    LAYERS,
    Hierarchy,
    layer_path,
    load_day,
    load_env,
    now_iso,
    parse_iso,
    register_layer,
    require_env,
    write_json,
)

PROMPT_VERSION = "jev-v1.1"  # v1.1: admin names instead of landmark points in summaries

SAME_EVENT_INSTRUCTIONS = (
    "`signal` is one new report (an X post, alert or database row) from a crisis "
    "monitoring feed. `events` lists recent events already known for the same area, "
    "each with a short summary built from the reports it already contains. Which "
    "listed event is `signal` reporting on? Pick the event that describes the SAME "
    "real-world occurrence (same thing happening, same place, same time). A later "
    "update, a different wording, a different source or a different detail about the "
    "same occurrence still counts as the same event. Pick `none` when the report is "
    "about a different occurrence, a roundup of many occurrences, or no specific occurrence."
)
MATCHES_ANY_INSTRUCTIONS = (
    "Does `signal` report on the same real-world occurrence as at least one of the "
    "events listed in `events`?"
)
MATCHES_ANY_CRITERIA = {
    "true": "The report is about an occurrence that one of the listed events already describes.",
    "false": "The report is about a different occurrence, or is a roundup, analysis or general statement.",
}
# Copied from clear-pipeline/providers/jev.py so the lab's relevance gate matches production.
RELEVANT_INSTRUCTIONS = (
    "Does `text` report an ACTUAL, CURRENT humanitarian, disaster, or security "
    "incident — a real event that has happened or is happening?"
)
RELEVANT_CRITERIA = {
    "true": "A concrete incident/event is described (e.g. a flood, clash, outbreak, strike).",
    "false": "Routine news, analysis or opinion, a retrospective/anniversary, a "
    "forecast or warning with no event yet, or an unrelated topic.",
}
NONE_CRITERION = "A different occurrence from every event listed, or no specific occurrence."


# ── Jev transport (shape copied from clear-pipeline/providers/jev.py) ─────────

def jev_provider() -> tuple[str, str, str]:
    """(key, url, model). TypeSafe's own API when TYPESAFE_API_KEY is set,
    else OpenRouter's Decisions endpoint with OPENROUTER_API_KEY (what
    clear-pipeline uses). JEV_URL / JEV_MODEL override either."""
    if os.environ.get("TYPESAFE_API_KEY"):
        return (
            os.environ["TYPESAFE_API_KEY"],
            os.environ.get("JEV_URL", "https://api.typesafe.ai/v1/systemone"),
            os.environ.get("JEV_MODEL", "jev-latest"),
        )
    return (
        require_env("OPENROUTER_API_KEY"),
        os.environ.get("JEV_URL", "https://openrouter.ai/api/alpha/decisions"),
        os.environ.get("JEV_MODEL", "typesafe/jev-1.13"),
    )


def jev_call(body: dict, *, cache_dir, retries: int = 3, timeout: float = 60.0) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    cached = cache_dir / f"{digest}.json"
    if cached.exists():
        return json.loads(cached.read_text())

    key, url, _ = jev_provider()
    req_body = json.dumps(body, ensure_ascii=False).encode()
    last = "no attempts"
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            url,
            data=req_body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode())
            answers = payload.get("answers")
            if not isinstance(answers, dict):
                raise RuntimeError("Jev response missing `answers`")
            cached.write_text(json.dumps(payload, ensure_ascii=False))
            return payload
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            if exc.code < 500 and exc.code not in (408, 409, 425, 429):
                sys.exit(f"Jev HTTP {exc.code} (not retryable): {detail}")
            last = f"HTTP {exc.code}: {detail}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = f"{type(exc).__name__}: {exc}"
        if attempt < retries:
            time.sleep(0.5 * 2 ** (attempt - 1))
    sys.exit(f"Jev request failed after {retries} attempts: {last}")


# ── Replay state ─────────────────────────────────────────────────────────────

def hhmm(iso: str | None) -> str:
    dt = parse_iso(iso)
    return dt.strftime("%d %b %H:%M") if dt else "?"


class ReplayEvent:
    def __init__(self, eid: str, signal: dict, location_name: str | None):
        self.id = eid
        self.signals = [signal]
        self.location_id = signal.get("admin2Id") or signal.get("admin1Id") or (signal.get("location") or {}).get("id")
        self.location_name = location_name
        self.admin1_id = signal.get("admin1Id")
        self.first_at = signal["publishedAt"]
        self.last_at = signal["publishedAt"]

    def add(self, signal: dict) -> None:
        self.signals.append(signal)
        self.last_at = max(self.last_at, signal["publishedAt"])
        if not self.admin1_id and signal.get("admin1Id"):
            self.admin1_id = signal["admin1Id"]

    def summary(self) -> str:
        first = (self.signals[0].get("title") or self.signals[0].get("text") or "")[:120]
        parts = [self.location_name or "unknown place", first]
        if len(self.signals) == 1:
            parts.append(f"1 report at {hhmm(self.first_at)}")
        else:
            latest = (self.signals[-1].get("title") or "")[:120]
            parts.append(f"{len(self.signals)} reports {hhmm(self.first_at)}–{hhmm(self.last_at)}")
            parts.append(f"latest: {latest}")
        return " · ".join(p for p in parts if p)

    def to_json(self, hierarchy: Hierarchy) -> dict:
        sev = [s.get("severity") for s in self.signals if s.get("severity") is not None]
        return {
            "id": self.id,
            "title": (self.signals[0].get("title") or "")[:100],
            "signalIds": [s["id"] for s in self.signals],
            "locationId": self.location_id,
            "locationName": self.location_name,
            "severity": max(sev) if sev else None,
            "types": sorted({s.get("glideCode") for s in self.signals if s.get("glideCode")}),
            "firstAt": self.first_at,
            "lastAt": self.last_at,
        }


def place_name(signal: dict, hierarchy: Hierarchy) -> str | None:
    """District, else state, else whatever the signal resolved to. Landmark
    points (level 4) are named like "Point 10.78, 34.19", which tells Jev
    nothing, so prefer the admin names above them."""
    loc = signal.get("location") or {}
    if loc.get("level") is not None and loc["level"] <= 2:
        return loc.get("name")
    return hierarchy.name(signal.get("admin2Id")) or hierarchy.name(signal.get("admin1Id")) or loc.get("name")


def candidates_for(signal: dict, events: list[ReplayEvent], window: timedelta, cap: int, scope: str = "state") -> list[ReplayEvent]:
    """Open events within the window, newest first. scope="state": same state,
    or either side only resolves to the country. scope="country": that pool
    first, then other states' events, so widening never pushes out a
    same-state candidate that jev-v1 would have offered."""
    at = parse_iso(signal["publishedAt"])
    state = signal.get("admin1Id")
    pool, elsewhere = [], []
    for ev in events:
        if parse_iso(ev.last_at) < at - window:
            continue
        if state and ev.admin1_id and ev.admin1_id != state:
            elsewhere.append(ev)
        else:
            pool.append(ev)
    pool.sort(key=lambda e: e.last_at, reverse=True)
    if scope == "country":
        elsewhere.sort(key=lambda e: e.last_at, reverse=True)
        pool += elsewhere
    return pool[:cap]


SCOPE_DESCRIPTIONS = {
    "state": "same admin-1, country-level events everywhere",
    "country": "same admin-1 first, then every other state's open events, newest first",
}


def run_jev(day: dict, params: dict, hierarchy: Hierarchy) -> tuple[list[ReplayEvent], dict]:
    window = timedelta(hours=params["windowHours"])
    cache_dir = LAYERS / ".cache"
    events: list[ReplayEvent] = []
    decisions: dict[str, dict] = {}
    counter = 0
    total = len(day["signals"])

    for i, signal in enumerate(day["signals"], 1):
        if signal.get("retracted"):
            decisions[signal["id"]] = {"outcome": "retracted"}
            continue
        loc_name = place_name(signal, hierarchy)
        cands = candidates_for(signal, events, window, params["maxCandidates"], params["candidateScope"])
        keys = {f"e{n}": ev for n, ev in enumerate(cands, 1)}
        text = " ".join(filter(None, [signal.get("title"), signal.get("text")])) or "unknown"

        body = {
            "model": params["model"],
            "state": {
                "text": text,
                "signal": {
                    "text": text,
                    "publishedAt": signal["publishedAt"],
                    "location": loc_name,
                    "source": signal.get("source"),
                },
                "events": [{"id": k, "summary": ev.summary()} for k, ev in keys.items()],
            },
            "questions": {
                "relevant": {"type": "noul", "instructions": RELEVANT_INSTRUCTIONS, "criteria": RELEVANT_CRITERIA},
            },
        }
        if keys:
            body["questions"]["same_event"] = {
                "type": "choice",
                "instructions": SAME_EVENT_INSTRUCTIONS,
                "criteria": {**{k: ev.summary() for k, ev in keys.items()}, "none": NONE_CRITERION},
            }
            body["questions"]["matches_any"] = {
                "type": "noul",
                "instructions": MATCHES_ANY_INSTRUCTIONS,
                "criteria": MATCHES_ANY_CRITERIA,
            }
        # Cache is keyed by request body inside a per-prompt-version folder, so
        # editing the instructions above (and bumping PROMPT_VERSION) refetches.
        payload = jev_call(body, cache_dir=cache_dir / PROMPT_VERSION)
        answers = payload["answers"]

        relevance = float(answers.get("relevant", {}).get("noul") or 0.0)
        record: dict = {
            "relevance": round(relevance, 3),
            "candidates": [],
            "noneP": None,
            "matchesAny": None,
            "usage": payload.get("usage"),
        }
        if keys:
            probs = answers.get("same_event", {}).get("probabilities") or {}
            record["candidates"] = [
                {"eventId": ev.id, "summary": ev.summary(), "p": round(float(probs.get(k, 0.0)), 3)}
                for k, ev in keys.items()
            ]
            record["noneP"] = round(float(probs.get("none", 0.0)), 3)
            record["matchesAny"] = round(float(answers.get("matches_any", {}).get("noul") or 0.0), 3)
            record["choiceConfidence"] = answers.get("same_event", {}).get("confidence")

        if relevance < params["relevanceThreshold"]:
            record["outcome"] = "dropped"
        elif not keys:
            counter += 1
            ev = ReplayEvent(f"L{counter}", signal, loc_name)
            events.append(ev)
            record.update(outcome="no-candidates", eventId=ev.id)
        else:
            ranked = sorted(record["candidates"], key=lambda c: c["p"], reverse=True)
            top, runner = ranked[0], (ranked[1]["p"] if len(ranked) > 1 else 0.0)
            joins = (
                record["matchesAny"] >= params["anyThreshold"]
                and top["p"] >= params["absThreshold"]
                and top["p"] - runner >= params["margin"]
            )
            if joins:
                target = next(ev for ev in cands if ev.id == top["eventId"])
                target.add(signal)
                record.update(outcome="joined", eventId=target.id)
            else:
                counter += 1
                ev = ReplayEvent(f"L{counter}", signal, loc_name)
                events.append(ev)
                linked = [c["eventId"] for c in ranked[:3] if c["p"] >= params["linkThreshold"]]
                record.update(outcome="new-linked" if linked else "new", eventId=ev.id, linked=linked)
        decisions[signal["id"]] = record
        if i % 20 == 0 or i == total:
            print(f"  {i}/{total} signals, {len(events)} events so far")
    return events, decisions


def run_naive_state(day: dict, params: dict, hierarchy: Hierarchy) -> tuple[list[ReplayEvent], dict]:
    window = timedelta(hours=params["windowHours"])
    events: list[ReplayEvent] = []
    decisions: dict[str, dict] = {}
    counter = 0
    for signal in day["signals"]:
        if signal.get("retracted"):
            decisions[signal["id"]] = {"outcome": "retracted"}
            continue
        if not signal.get("eventIds"):
            # Reuse CLEAR's own relevance verdict: a signal CLEAR dropped stays dropped.
            decisions[signal["id"]] = {"outcome": "dropped"}
            continue
        at = parse_iso(signal["publishedAt"])
        state, code = signal.get("admin1Id"), signal.get("glideCode")
        match = None
        if state and code:
            for ev in reversed(events):
                if ev.admin1_id == state and code in {s.get("glideCode") for s in ev.signals} and parse_iso(ev.last_at) >= at - window:
                    match = ev
                    break
        if match:
            match.add(signal)
            decisions[signal["id"]] = {"outcome": "joined", "eventId": match.id}
        else:
            counter += 1
            ev = ReplayEvent(f"L{counter}", signal, place_name(signal, hierarchy))
            events.append(ev)
            decisions[signal["id"]] = {"outcome": "new", "eventId": ev.id}
    return events, decisions


# ── V2 replay and the gazetteer fix (idea 6) ─────────────────────────────────

def glide_taxonomy() -> dict[str, dict]:
    """Glide code → {l1, l2}, vendored from clear-pipeline's event_categories.json."""
    return json.loads((LAB / "glide_taxonomy.json").read_text())["codes"]


def place_key(name: str) -> str:
    """Consonant skeleton, the viewer's placeKey: transliterations of Arabic
    names vary mostly in vowels and articles (Al-Kurmuk / Kurmuk → krmk)."""
    s = unicodedata.normalize("NFD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"\(unresolved\)", " ", s)
    s = re.sub(r"\s+-\s+[a-z]{2}$", "", s)  # district disambiguators: "Habila - SK"
    s = re.sub(r"\b(state|city|town|locality|district|area|village|region)\b", " ", s)
    s = re.sub(r"^\s*(al|el|ad|ar|as|ash|at|an|az|ed|en|es|er)[\s\-'’]+", "", s)
    s = re.sub(r"[^a-z]", "", s).replace("q", "k")
    s = re.sub(r"[aeiouy]", "", s)
    return re.sub(r"(.)\1+", r"\1", s)


class Gazetteer:
    """Place-name skeleton → district ids, built from the day file's location
    tree: districts by name, plus named points (level 4) under their district.
    Bare coordinates ("Point 10.78, 34.19"), Dataminr headlines stored as
    point names, and points the geocoder marked "(unresolved)" (their parent
    is a guess) are skipped. Country, state and region names (Darfur,
    Kordofan: a state name without its compass word) never name a district."""

    COMPASS = re.compile(r"^(north|south|east|west|central|northern|southern|eastern|western)\s+", re.I)

    def __init__(self, hierarchy: Hierarchy):
        self.hierarchy = hierarchy
        self.area_keys: set[str] = set()
        for n in hierarchy.locations.values():
            if n["level"] <= 1:
                self.area_keys |= {place_key(n["name"]), place_key(self.COMPASS.sub("", n["name"]))}
        self.index: dict[str, set[str]] = {}
        for lid, node in hierarchy.locations.items():
            name = node.get("name") or ""
            if node["level"] == 2:
                district = lid
            elif (
                node["level"] == 4
                and not name.startswith("Point ")
                and "(unresolved)" not in name
                and ":" not in name
                and len(name.split()) <= 4
            ):
                district = hierarchy.ancestor_at_level(lid, 2)
            else:
                continue
            key = place_key(name)
            if district and len(key) >= 2 and key not in self.area_keys:
                self.index.setdefault(key, set()).add(district)

    def district_for(self, places: list[str], state_id: str | None) -> str | None:
        """First named place, in mention order, that resolves to exactly one
        district inside the signal's state. A signal with no state needs a
        longer skeleton, since nothing else narrows a two-consonant match."""
        for place in places:
            key = place_key(place)
            hits = self.index.get(key, set())
            if state_id:
                hits = {d for d in hits if self.hierarchy.ancestor_at_level(d, 1) == state_id}
            elif len(key) < 3:
                continue
            if len(hits) == 1:
                return next(iter(hits))
        return None


def run_v2(day: dict, params: dict, hierarchy: Hierarchy) -> tuple[list[ReplayEvent], dict]:
    window = timedelta(hours=params["windowHours"])
    level = "l1" if params["typeLevel"] == 1 else "l2"
    taxonomy = glide_taxonomy()
    gazetteer = places = None
    if params["gazetteer"]:
        tr_path = DATA / day["country"] / f"{day['date']}.translations.json"
        if not tr_path.exists():
            sys.exit(f"v2-gazetteer needs {tr_path} for each signal's place names; run translate.py first")
        places = {sid: t.get("places") or [] for sid, t in json.loads(tr_path.read_text())["signals"].items()}
        gazetteer = Gazetteer(hierarchy)
    events: list[ReplayEvent] = []
    keys: dict[str, tuple[str, str]] = {}  # event id → (district, family) of its first signal
    decisions: dict[str, dict] = {}
    counter = 0
    for signal in day["signals"]:
        if signal.get("retracted"):
            decisions[signal["id"]] = {"outcome": "retracted"}
            continue
        if not signal.get("eventIds"):
            decisions[signal["id"]] = {"outcome": "dropped"}
            continue
        at = parse_iso(signal["publishedAt"])
        district, promoted = signal.get("admin2Id"), None
        if not district and gazetteer:
            district = promoted = gazetteer.district_for(places.get(signal["id"], []), signal.get("admin1Id"))
        family = (taxonomy.get(signal.get("glideCode") or "") or {}).get(level)
        record: dict = {"key": [hierarchy.name(district), family]}
        if promoted:
            record["promotedTo"] = hierarchy.name(promoted)
        match = None
        if district and family:
            # Production joins the matching open event with the newest signal.
            live = [ev for ev in events if keys.get(ev.id) == (district, family) and parse_iso(ev.last_at) >= at - window]
            match = max(live, key=lambda e: e.last_at, default=None)
        if match:
            match.add(signal)
            record.update(outcome="joined", eventId=match.id)
        else:
            counter += 1
            ev = ReplayEvent(f"L{counter}", signal, place_name(signal, hierarchy) if not promoted else hierarchy.name(promoted))
            if promoted:
                ev.location_id = promoted
            events.append(ev)
            if district and family:
                keys[ev.id] = (district, family)
            record.update(outcome="new" if district else "no-district", eventId=ev.id)
        decisions[signal["id"]] = record
    return events, decisions


# ── Embedding baseline ───────────────────────────────────────────────────────

VOYAGE_BATCH = 128  # Voyage's per-call input limit


def embed_provider() -> tuple[str, str, str]:
    """(key, url, model). Voyage's own API with clear-pipeline's model when
    VOYAGE_API_KEY is set, else Voyage through OpenRouter with the key Jev
    already uses (OpenRouter no longer lists voyage-3-large, so voyage-4-large).
    EMBED_MODEL overrides either."""
    if os.environ.get("VOYAGE_API_KEY"):
        return (
            os.environ["VOYAGE_API_KEY"],
            "https://api.voyageai.com/v1/embeddings",
            os.environ.get("EMBED_MODEL", "voyage-3-large"),
        )
    return (
        require_env("OPENROUTER_API_KEY"),
        "https://openrouter.ai/api/v1/embeddings",
        os.environ.get("EMBED_MODEL", "voyageai/voyage-4-large"),
    )


def embed_texts(texts: list[str], *, dims: int, cache_dir) -> list[list[float]]:
    """Embed texts, cached per (model, dims, text) so reruns are free."""
    key, url, model = embed_provider()
    cache_dir.mkdir(parents=True, exist_ok=True)
    digests = [hashlib.sha256(f"{model}|{dims}|{t}".encode()).hexdigest() for t in texts]
    missing = [i for i, d in enumerate(digests) if not (cache_dir / f"{d}.json").exists()]
    dim_field = "output_dimension" if "voyageai.com" in url else "dimensions"
    for start in range(0, len(missing), VOYAGE_BATCH):
        chunk = missing[start : start + VOYAGE_BATCH]
        body = json.dumps({
            "input": [texts[i] for i in chunk],
            "model": model,
            "input_type": "document",
            dim_field: dims,
        }).encode()
        last = "no attempts"
        for attempt in range(1, 5):
            req = urllib.request.Request(
                url, data=body, method="POST",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    rows = json.loads(resp.read().decode())["data"]
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode(errors="replace")[:300]
                if exc.code < 500 and exc.code != 429:
                    sys.exit(f"embedding HTTP {exc.code} (not retryable): {detail}")
                last = f"HTTP {exc.code}: {detail}"
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last = f"{type(exc).__name__}: {exc}"
            # Voyage's free tier allows 3 requests a minute, so back off generously.
            time.sleep(20 * attempt)
        else:
            sys.exit(f"embedding request failed after 4 attempts: {last}")
        for row in rows:
            i = chunk[row["index"]]
            (cache_dir / f"{digests[i]}.json").write_text(json.dumps(row["embedding"]))
    return [json.loads((cache_dir / f"{d}.json").read_text()) for d in digests]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) or 1.0)


def run_embed(day: dict, params: dict, hierarchy: Hierarchy) -> tuple[list[ReplayEvent], dict]:
    window = timedelta(hours=params["windowHours"])
    live = [s for s in day["signals"] if not s.get("retracted") and s.get("eventIds")]
    texts = [" ".join(filter(None, [s.get("title"), s.get("text")])) or "unknown" for s in live]
    vectors = embed_texts(texts, dims=params["dims"], cache_dir=LAYERS / ".cache" / "embed")
    vec = {s["id"]: v for s, v in zip(live, vectors)}
    events: list[ReplayEvent] = []
    decisions: dict[str, dict] = {}
    counter = 0
    for signal in day["signals"]:
        if signal.get("retracted"):
            decisions[signal["id"]] = {"outcome": "retracted"}
            continue
        if not signal.get("eventIds"):
            decisions[signal["id"]] = {"outcome": "dropped"}
            continue
        loc_name = place_name(signal, hierarchy)
        cands = candidates_for(signal, events, window, params["maxCandidates"], params["candidateScope"])
        # Single link: an event is as close as its closest signal.
        scored = [
            {"eventId": ev.id, "summary": ev.summary(), "p": round(max(cosine(vec[signal["id"]], vec[s["id"]]) for s in ev.signals), 3)}
            for ev in cands
        ]
        record: dict = {"candidates": scored, "similarity": "max cosine to the event's signals (shown as p)"}
        ranked = sorted(scored, key=lambda c: c["p"], reverse=True)
        top = ranked[0] if ranked else None
        runner = ranked[1]["p"] if len(ranked) > 1 else 0.0
        if top and top["p"] >= params["simThreshold"] and top["p"] - runner >= params["simMargin"]:
            target = next(ev for ev in cands if ev.id == top["eventId"])
            target.add(signal)
            record.update(outcome="joined", eventId=target.id)
        else:
            counter += 1
            ev = ReplayEvent(f"L{counter}", signal, loc_name)
            events.append(ev)
            linked = [c["eventId"] for c in ranked[:3] if c["p"] >= params["simLinkThreshold"]]
            outcome = "no-candidates" if not cands else ("new-linked" if linked else "new")
            record.update(outcome=outcome, eventId=ev.id, linked=linked)
        decisions[signal["id"]] = record
    return events, decisions


ALGOS = {
    "jev-v1": run_jev,
    "naive-state": run_naive_state,
    "v2-replay": run_v2,
    "v2-gazetteer": run_v2,
    "embed-v1": run_embed,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--algo", required=True, choices=sorted(ALGOS))
    parser.add_argument("--tag", help="suffix for the layer name, e.g. 7d → jev-v1-7d")
    parser.add_argument("--window-hours", type=int, default=72)
    parser.add_argument("--max-candidates", type=int, default=40)
    parser.add_argument("--abs-threshold", type=float, default=0.5)
    parser.add_argument("--margin", type=float, default=0.15)
    parser.add_argument("--any-threshold", type=float, default=0.5)
    parser.add_argument("--link-threshold", type=float, default=0.2)
    parser.add_argument("--relevance-threshold", type=float, default=0.3, help="production default from signals/config.py")
    parser.add_argument("--scope", choices=sorted(SCOPE_DESCRIPTIONS), default="state", help="candidate pool (jev-v1, embed-v1)")
    parser.add_argument("--type-level", type=int, choices=(1, 2), default=2, help="v2-*: key on type_level_2 (production) or type_level_1")
    parser.add_argument("--sim-threshold", type=float, default=0.78, help="embed-v1: join when the best cosine is at least this (0.78 ≈ the 99th percentile of random same-day pairs on Sudan 20 Oct)")
    parser.add_argument("--sim-margin", type=float, default=0.0, help="embed-v1: and beats the runner-up by this much")
    parser.add_argument("--sim-link-threshold", type=float, default=0.68, help="embed-v1: record near misses at or above this")
    parser.add_argument("--embed-dims", type=int, default=1024, help="embed-v1: clear-pipeline's default")
    parser.add_argument("--limit", type=int, help="only replay the first N signals (smoke test)")
    args = parser.parse_args()

    load_env()
    day = load_day(args.country, args.date)
    if args.limit:
        day["signals"] = day["signals"][: args.limit]
    hierarchy = Hierarchy(day["locations"])
    params: dict = {"windowHours": args.window_hours}
    if args.algo == "jev-v1":
        _, url, model = jev_provider()
        params.update({
            "maxCandidates": args.max_candidates,
            "absThreshold": args.abs_threshold,
            "margin": args.margin,
            "anyThreshold": args.any_threshold,
            "linkThreshold": args.link_threshold,
            "relevanceThreshold": args.relevance_threshold,
            "model": model,
            "jevHost": url.split("//")[-1].split("/")[0],
            "promptVersion": PROMPT_VERSION,
            "candidateScope": args.scope,
            "candidateScopeNote": SCOPE_DESCRIPTIONS[args.scope],
            "summary": "rule-built (first title, place, count, span, latest title)",
        })
    elif args.algo.startswith("v2-"):
        params.update({
            "typeLevel": args.type_level,
            "gazetteer": args.algo == "v2-gazetteer",
            "rule": "production V2: (district, type family) key, newest matching open event, no district → new event",
            "relevance": "CLEAR's own verdict",
        })
    elif args.algo == "embed-v1":
        params.update({
            "maxCandidates": args.max_candidates,
            "candidateScope": args.scope,
            "candidateScopeNote": SCOPE_DESCRIPTIONS[args.scope],
            "simThreshold": args.sim_threshold,
            "simMargin": args.sim_margin,
            "simLinkThreshold": args.sim_link_threshold,
            "model": embed_provider()[2],
            "embedHost": embed_provider()[1].split("//")[-1].split("/")[0],
            "dims": args.embed_dims,
            "relevance": "CLEAR's own verdict",
        })
    else:
        params["relevance"] = "CLEAR's own verdict"
    name = f"{args.algo}-{args.tag}" if args.tag else args.algo
    print(f"replaying {len(day['signals'])} signals with {name} …")
    events, decisions = ALGOS[args.algo](day, params, hierarchy)

    layer = {
        "algo": name,
        "params": params,
        "country": args.country,
        "date": args.date,
        "createdAt": now_iso(),
        "events": [ev.to_json(hierarchy) for ev in events],
        "decisions": decisions,
    }
    out = layer_path(args.country, args.date, name)
    write_json(out, layer)
    register_layer(args.country, args.date, name)
    assigned = sum(len(ev.signals) for ev in events)
    outcomes: dict[str, int] = {}
    for d in decisions.values():
        outcomes[d["outcome"]] = outcomes.get(d["outcome"], 0) + 1
    print(f"wrote {out}")
    print(f"  events={len(events)} signals_assigned={assigned} merge_ratio={assigned / len(events) if events else 0:.2f}")
    print(f"  outcomes: {outcomes}")


if __name__ == "__main__":
    main()
