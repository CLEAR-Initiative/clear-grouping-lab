---
name: fetch-day
description: Pull one country-day of signals and events from the dev CLEAR API into the lab's gitignored data/ folder and build the clear-as-run layer. Use when James says "fetch <date>", "pull the day", or wants a new day to judge.
---

Fetch a day for the grouping lab. Arguments: `<country> <date>` (defaults: sudan, and ask for the date if missing).

1. Run, from the lab root:
   ```bash
   python3 fetch_day.py --country <country> --date <date>
   ```
   The script refuses any host other than `dev-api.clearinitiative.io`. If it refuses, tell James `.env` points at the wrong API and stop; never pass `--allow-host` on your own.
2. Never read, echo or grep `.env`. Filter command output for anything that looks like a key before showing it.
3. Report the printed counts: signals by source, signals in no event, events touched. Compare with the seed audit for that date in `seed/sudan-event-audit-2026-10-20-to-27.md` ("By day" section) and say whether the X count looks short; signals that never got a location are invisible to the fetch.
4. Outputs land in `data/<country>/<date>.json` and `layers/<country>/<date>.clear-as-run.json`, both gitignored. Nothing is committed.
5. Suggest the next command: `python3 replay.py --country <country> --date <date> --algo jev-v1 --limit 20` as a cheap first Jev run.
