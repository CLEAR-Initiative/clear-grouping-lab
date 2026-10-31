#!/usr/bin/env python3
"""Location precision from fetched day files: the share of signals at district
(admin-2) or finer, per source and per day. This is the "Location precision"
metric in Notion (Data Strategy Execution → Metrics). Since 31 Oct 2026 clear-api
serves the production number (admin-only `locationPrecisionMetrics`, ADR-0012, on
/metrics); this script is the frozen per-day cross-check from day files.

    python3 precision.py --country sudan --from 2026-10-20 --to 2026-10-31
    python3 precision.py --country sudan --from 2026-10-20 --to 2026-10-31 --json out.json

Reads data/<country>/<date>.json written by fetch_day.py (fetch the days first).
Buckets, from each signal's stored location:
  country  level 0            state  level 1
  district level 2            point  a level-4 point inside a district (admin2Id set)
"district or finer" = district + point. Retracted signals are skipped. Signals
that never got a location are invisible to fetch_day.py and so to this script.
"""
from __future__ import annotations

import argparse
import collections
import json
from datetime import date, timedelta

import lab_common as lc

parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
parser.add_argument("--country", required=True)
parser.add_argument("--from", dest="date_from", required=True)
parser.add_argument("--to", dest="date_to", required=True)
parser.add_argument("--json", help="also write the counts to this file")
args = parser.parse_args()

start, end = date.fromisoformat(args.date_from), date.fromisoformat(args.date_to)
days = [(start + timedelta(n)).isoformat() for n in range((end - start).days + 1)]


def bucket(signal: dict) -> str:
    loc = signal.get("location") or {}
    level = loc.get("level")
    if level is None:
        return "none"
    if signal.get("admin2Id"):
        return "district" if level == 2 else "point"
    return {0: "country", 1: "state"}.get(level, f"level{level}-no-district")


by_source: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
by_day: dict[str, dict[str, collections.Counter]] = collections.defaultdict(
    lambda: collections.defaultdict(collections.Counter)
)
missing = []
for day in days:
    try:
        d = lc.load_day(args.country, day)
    except FileNotFoundError:
        missing.append(day)
        continue
    for s in d["signals"]:
        if s.get("retracted"):
            continue
        b = bucket(s)
        for counter in (by_source[s["source"]], by_day[day][s["source"]]):
            counter[b] += 1
            counter["total"] += 1

if missing:
    print(f"not fetched (run fetch_day.py): {', '.join(missing)}")


def fine(c: collections.Counter) -> int:
    return c["district"] + c["point"]


print(f"\n{args.country}, {days[0]} to {days[-1]}: share of signals at district or finer\n")
print(f"{'source':14}{'signals':>8}{'country':>9}{'state':>7}{'district':>9}{'point':>7}{'district+':>11}")
total_all = fine_all = 0
for source, c in sorted(by_source.items(), key=lambda kv: -kv[1]["total"]):
    total_all += c["total"]
    fine_all += fine(c)
    print(f"{source:14}{c['total']:>8}{c['country']:>9}{c['state']:>7}{c['district']:>9}"
          f"{c['point']:>7}{100 * fine(c) / c['total']:>10.0f}%")
if total_all:
    print(f"{'all sources':14}{total_all:>8}{'':>32}{100 * fine_all / total_all:>10.0f}%")

print("\nper day (district or finer / signals):")
sources = [s for s, _ in sorted(by_source.items(), key=lambda kv: -kv[1]["total"])][:3]
for day in days:
    cells = []
    for source in sources:
        c = by_day[day].get(source)
        cells.append(f"{source} {100 * fine(c) / c['total']:.0f}% ({fine(c)}/{c['total']})" if c and c["total"] else f"{source} -")
    print(f"  {day}  " + "   ".join(cells))

if args.json:
    out = {
        "country": args.country, "from": days[0], "to": days[-1],
        "bySource": {s: dict(c) for s, c in by_source.items()},
        "byDay": {d: {s: dict(c) for s, c in v.items()} for d, v in by_day.items()},
    }
    with open(args.json, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json}")
