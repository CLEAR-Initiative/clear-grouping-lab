#!/usr/bin/env python3
"""Translate a day's signals into English and list the places each one names,
for the viewer: data/<country>/<date>.translations.json

    python3 translate.py --country sudan --date 2026-10-20
    python3 translate.py --country sudan --date 2026-10-20 --limit 10   # smoke test

fetch_day.py runs this automatically after a fetch (skip with --no-translate);
run it by hand to retry failures or to translate a day fetched before that.

One model call per signal through OpenRouter (OPENROUTER_API_KEY, the key the
lab already uses for Jev). TRANSLATE_MODEL overrides the default model.
Responses are cached under data/.cache/<PROMPT_VERSION>/ by request hash, so
re-runs and new days only pay for signals not seen before.

This is not a judgment about grouping: the model only translates and lists
place names, one signal at a time, without seeing any other signal. The viewer
shows the original text under every translation so judges can check it.

Output shape:
  model, promptVersion, createdAt
  signals: {signalId: {lang, title, text, places: [str]}}
    lang    ISO 639-1 code of the original ("ar", "en", …)
    title   English title, or null when the original is already English
    text    English text, or null when the original is already English
    places  place names as they appear in the English (or original English) text
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

PROMPT_VERSION = "translate-v1"
DEFAULT_MODEL = "anthropic/claude-haiku-4.5"
URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM = """You help analysts read crisis-monitoring reports from Sudan (X posts, alerts, database rows).

You get one report as JSON with "title" and "text". Reply with JSON only, no prose and no code fence:
{"lang": "<ISO 639-1 code of the report's main language>",
 "title": "<English translation of title, or null>",
 "text": "<English translation of text, or null>",
 "places": ["<place name>", ...]}

Rules:
- If the report is already in English, set "title" and "text" to null.
- Otherwise translate faithfully and completely. Do not summarise, explain, correct or add anything. Keep hashtags, URLs, numbers and line breaks.
- Write place names in their usual English spelling (for example الكرمك → Al Kurmuk, الفاشر → El Fasher).
- "places": every named geographic place the report mentions (villages, towns, districts, states, countries, named sites such as airports, bridges, markets, hospitals, power stations), each written exactly as it appears in the English text (your translation, or the original if it was English). No people, armed groups or organisations. Empty list if none."""


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


def translate_day(country: str, date: str, *, limit: int | None = None, workers: int = 8) -> None:
    """Translate one fetched day and merge the result into its translations file."""
    load_env()
    key = require_env("OPENROUTER_API_KEY")
    model = os.environ.get("TRANSLATE_MODEL", DEFAULT_MODEL)
    day = load_day(country, date)
    signals = day["signals"][:limit] if limit else day["signals"]
    cache_dir = DATA / ".cache" / PROMPT_VERSION
    cache_dir.mkdir(parents=True, exist_ok=True)

    def one(s: dict) -> tuple[str, dict | None, str | None]:
        report = {"title": s.get("title") or "", "text": s.get("text") or ""}
        body = {
            "model": model,
            "temperature": 0,
            "max_tokens": 4000,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps(report, ensure_ascii=False)},
            ],
        }
        try:
            a = call(body, cache_dir=cache_dir, key=key)
        except RuntimeError as exc:
            return s["id"], None, str(exc)
        places = [p.strip() for p in a.get("places") or [] if isinstance(p, str) and p.strip()]
        lang = (a.get("lang") or "").lower()[:2] or None
        english = lang == "en"
        return s["id"], {
            "lang": lang,
            "title": None if english else (a.get("title") or None),
            "text": None if english else (a.get("text") or None),
            "places": list(dict.fromkeys(places)),
        }, None

    print(f"translating {len(signals)} signals with {model} …")
    out: dict[str, dict] = {}
    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for n, (sid, entry, err) in enumerate(pool.map(one, signals), 1):
            if entry is None:
                failed.append(f"{sid}: {err}")
            else:
                out[sid] = entry
            if n % 25 == 0 or n == len(signals):
                print(f"  {n}/{len(signals)}")

    path = DATA / country / f"{date}.translations.json"
    # Merge into an earlier run with the same model and prompt, so a --limit smoke test or a
    # partly failed run never throws away translations the viewer and packs already use.
    if path.exists():
        prev = json.loads(path.read_text())
        if prev.get("model") == model and prev.get("promptVersion") == PROMPT_VERSION:
            out = {**prev.get("signals", {}), **out}
    write_json(path, {"model": model, "promptVersion": PROMPT_VERSION, "createdAt": now_iso(), "signals": out})
    langs: dict[str, int] = {}
    for e in out.values():
        langs[e["lang"] or "?"] = langs.get(e["lang"] or "?", 0) + 1
    print(f"wrote {path}")
    print(f"  languages: {langs}; signals with places: {sum(1 for e in out.values() if e['places'])}")
    if failed:
        print(f"  {len(failed)} failed (re-run to retry; cached ones are free):")
        for line in failed[:10]:
            print(f"    {line[:200]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--limit", type=int, help="only the first N signals (smoke test)")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    translate_day(args.country, args.date, limit=args.limit, workers=args.workers)


if __name__ == "__main__":
    main()
