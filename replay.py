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
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta

from lab_common import (
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

PROMPT_VERSION = "jev-v1.0"

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

def jev_call(body: dict, *, cache_dir, retries: int = 3, timeout: float = 60.0) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    cached = cache_dir / f"{digest}.json"
    if cached.exists():
        return json.loads(cached.read_text())

    key = require_env("OPENROUTER_API_KEY")
    url = os.environ.get("JEV_URL", "https://openrouter.ai/api/alpha/decisions")
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


def candidates_for(signal: dict, events: list[ReplayEvent], window: timedelta, cap: int) -> list[ReplayEvent]:
    at = parse_iso(signal["publishedAt"])
    state = signal.get("admin1Id")
    pool = []
    for ev in events:
        if parse_iso(ev.last_at) < at - window:
            continue
        # Same state, or either side only resolves to the country.
        if state and ev.admin1_id and ev.admin1_id != state:
            continue
        pool.append(ev)
    pool.sort(key=lambda e: e.last_at, reverse=True)
    return pool[:cap]


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
        loc_name = (signal.get("location") or {}).get("name")
        cands = candidates_for(signal, events, window, params["maxCandidates"])
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
            ev = ReplayEvent(f"L{counter}", signal, (signal.get("location") or {}).get("name"))
            events.append(ev)
            decisions[signal["id"]] = {"outcome": "new", "eventId": ev.id}
    return events, decisions


ALGOS = {"jev-v1": run_jev, "naive-state": run_naive_state}


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
    parser.add_argument("--limit", type=int, help="only replay the first N signals (smoke test)")
    args = parser.parse_args()

    load_env()
    day = load_day(args.country, args.date)
    if args.limit:
        day["signals"] = day["signals"][: args.limit]
    hierarchy = Hierarchy(day["locations"])
    params = {
        "windowHours": args.window_hours,
        "maxCandidates": args.max_candidates,
        "absThreshold": args.abs_threshold,
        "margin": args.margin,
        "anyThreshold": args.any_threshold,
        "linkThreshold": args.link_threshold,
        "relevanceThreshold": args.relevance_threshold,
        "model": os.environ.get("JEV_MODEL", "typesafe/jev-1.13"),
        "promptVersion": PROMPT_VERSION,
        "candidateScope": "same admin-1, country-level events everywhere",
        "summary": "rule-built (first title, place, count, span, latest title)",
    }
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
