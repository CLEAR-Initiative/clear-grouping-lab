#!/usr/bin/env python3
"""Pull the grouping-relevant characteristics out of each of a day's signals,
for the grouping algorithms to compare on fields instead of prose:
data/<country>/<date>.characteristics.json

    python3 characterize.py --country sudan --date 2026-10-20
    python3 characterize.py --country sudan --date 2026-10-20 --limit 10   # smoke test

One model call per signal through OpenRouter (OPENROUTER_API_KEY, the key the
lab already uses for Jev and translate). CHARACTERIZE_MODEL overrides the model.
Responses are cached under data/.cache/<PROMPT_VERSION>/ by request hash, so
re-runs and new days only pay for signals not seen before.

Each signal is characterised ALONE, without seeing any other signal — this is
extraction, not a grouping judgment. `replay.py` loads the result and feeds each
signal's characteristics into the grouper's state so same-event decisions can
compare what/where/when/who/scale, not only the raw text.

Output shape:
  model, promptVersion, createdAt
  signals: {signalId: {type, places, actors, occurredAt, scale}}
    type       short label of what happened ("air/drone strike", "flood", …);
               "none" for a roundup / analysis / no specific occurrence
    places     specific places named for THIS occurrence, most specific first
    actors     named parties/forces involved and the target, if stated
    occurredAt ISO-8601 date or date-time the occurrence happened, or null
               (the OCCURRENCE time, never the report/publication time)
    scale      short casualties / affected phrase ("12 killed"), or null
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
from concurrent.futures import ThreadPoolExecutor

from lab_common import DATA, load_day, load_env, now_iso, require_env, write_json

PROMPT_VERSION = "characteristics-v1"
DEFAULT_MODEL = "anthropic/claude-haiku-4.5"
URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM = """You help analysts group crisis-monitoring reports from Sudan (X posts, alerts, database rows) into real-world events.

You get one report as JSON with "title" and "text". Pull out the characteristics of the SINGLE real-world occurrence it reports. Reply with JSON only, no prose and no code fence:
{"type": "<short label of what happened>",
 "places": ["<place>", ...],
 "actors": ["<party or force, and the target if named>", ...],
 "occurredAt": "<ISO-8601 date or date-time of the occurrence, or null>",
 "scale": "<short casualties/affected phrase, or null>"}

Rules:
- Describe the one occurrence the report is about. If it is a roundup of several occurrences, analysis/opinion, a forecast, or no specific occurrence, set "type" to "none" and leave places/actors empty and occurredAt/scale null.
- "type": ONE short label for the kind of occurrence (for example: air/drone strike, shelling/artillery, armed clash, attack on civilians, abduction, looting, siege, flood, drought, epidemic, displacement). Use "other" for a real but unlisted kind.
- "places": every geographic place named for THIS occurrence, most specific first (town/camp/landmark, then district, then state). No people, armed groups or organisations. Empty if none.
- "actors": named parties, armed groups or forces involved, and the target if the text names one. No places, reporters, or NGOs cited as the source. Empty if none.
- "occurredAt": the time the occurrence happened if the text states or clearly implies it; otherwise null. NEVER use the report's own publication/detection time.
- "scale": only when the text gives a number (killed, injured, displaced, affected); otherwise null.
- Extract only what the text supports. Do not infer, correct or add anything."""


def call(body: dict, *, cache_dir, key: str, retries: int = 4, timeout: float = 90.0) -> dict:
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    cached = cache_dir / f"{digest}.json"
    if cached.exists():
        return json.loads(cached.read_text())
    last = "no attempts"
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            URL,
            data=json.dumps(body, ensure_ascii=False).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode())
            content = payload["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.strip("`").split("\n", 1)[1].rsplit("```", 1)[0]
            answer = json.loads(content[content.index("{") : content.rindex("}") + 1])
            cached.write_text(json.dumps(answer, ensure_ascii=False))
            return answer
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            if exc.code < 500 and exc.code not in (408, 409, 425, 429):
                sys.exit(f"OpenRouter HTTP {exc.code} (not retryable): {detail}")
            last = f"HTTP {exc.code}: {detail}"
        except (urllib.error.URLError, TimeoutError, OSError, KeyError, ValueError) as exc:
            last = f"{type(exc).__name__}: {exc}"
        if attempt < retries:
            time.sleep(0.5 * 2 ** (attempt - 1))
    raise RuntimeError(last)


def _clean_list(value) -> list[str]:
    return list(dict.fromkeys(v.strip() for v in value or [] if isinstance(v, str) and v.strip()))


def _clean(answer: dict) -> dict:
    kind = (answer.get("type") or "").strip() or "none"
    occurred = answer.get("occurredAt")
    scale = answer.get("scale")
    return {
        "type": kind,
        "places": _clean_list(answer.get("places")),
        "actors": _clean_list(answer.get("actors")),
        "occurredAt": occurred.strip() if isinstance(occurred, str) and occurred.strip() else None,
        "scale": scale.strip() if isinstance(scale, str) and scale.strip() else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--limit", type=int, help="only the first N signals (smoke test)")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    load_env()
    key = require_env("OPENROUTER_API_KEY")
    model = os.environ.get("CHARACTERIZE_MODEL", DEFAULT_MODEL)
    day = load_day(args.country, args.date)
    signals = day["signals"][: args.limit] if args.limit else day["signals"]
    cache_dir = DATA / ".cache" / PROMPT_VERSION
    cache_dir.mkdir(parents=True, exist_ok=True)

    def one(s: dict) -> tuple[str, dict | None, str | None]:
        report = {"title": s.get("title") or "", "text": s.get("text") or ""}
        body = {
            "model": model,
            "temperature": 0,
            "max_tokens": 1000,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps(report, ensure_ascii=False)},
            ],
        }
        try:
            a = call(body, cache_dir=cache_dir, key=key)
        except RuntimeError as exc:
            return s["id"], None, str(exc)
        return s["id"], _clean(a), None

    print(f"characterising {len(signals)} signals with {model} …")
    out: dict[str, dict] = {}
    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for n, (sid, entry, err) in enumerate(pool.map(one, signals), 1):
            if entry is None:
                failed.append(f"{sid}: {err}")
            else:
                out[sid] = entry
            if n % 25 == 0 or n == len(signals):
                print(f"  {n}/{len(signals)}")

    path = DATA / args.country / f"{args.date}.characteristics.json"
    # Merge into an earlier run with the same model and prompt, so a --limit smoke
    # test or a partly failed run never throws away characteristics replay already uses.
    if path.exists():
        prev = json.loads(path.read_text())
        if prev.get("model") == model and prev.get("promptVersion") == PROMPT_VERSION:
            out = {**prev.get("signals", {}), **out}
    write_json(path, {"model": model, "promptVersion": PROMPT_VERSION, "createdAt": now_iso(), "signals": out})
    types: dict[str, int] = {}
    for e in out.values():
        types[e["type"]] = types.get(e["type"], 0) + 1
    print(f"wrote {path}")
    print(f"  types: {dict(sorted(types.items(), key=lambda kv: -kv[1]))}")
    if failed:
        print(f"  {len(failed)} failed (re-run to retry; cached ones are free):")
        for line in failed[:10]:
            print(f"    {line[:200]}")


if __name__ == "__main__":
    main()
