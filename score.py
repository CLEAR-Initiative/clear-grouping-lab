#!/usr/bin/env python3
"""Score a layer against the day's judgments.

    python3 score.py --country sudan --date 2026-10-20 --layer jev-v1
    python3 score.py --country sudan --date 2026-10-20 --layer jev-v1 --judgments james
    python3 score.py --country sudan --date 2026-10-20 --all        # every registered layer, one table

Without judgments the shape metrics still print (events, merge ratio, singleton
share, projected alerts). With judgments:

  pair precision  of the signal pairs the layer puts in one event, and that a
                  judgment covers, the share the judge also put together
  pair recall     of the pairs the judge put together, the share the layer also
                  put together
  set hits        judged "same" sets that the layer keeps inside one event
  conflicts       judged pairs where a "same" set and an "apart" pair disagree

Judgments are signal-level, so one judgments file scores every layer for the
day. Files the viewer saved for a date range (<from>..<to>.<judge>.json) count
for every day they cover, restricted to that day's signals. Baseline to beat (week of 20–27 Oct, Sudan): merge ratio 1.2, ~41 alerts a day.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys

from lab_common import JUDGMENTS, LAYERS, layer_path, load_day


class UnionFind:
    def __init__(self):
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


JUDGMENT_FILE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:\.\.(\d{4}-\d{2}-\d{2}))?\.([^.]+)\.json$")


def load_judgments(country: str, date: str, name: str | None, day_ids: set[str]) -> dict | None:
    """Every judgments file covering `date`: single-day files (<date>.<judge>.json) and the
    viewer's date-range files (<from>..<to>.<judge>.json). A range file also judges other
    days' signals, so only this day's signals are kept; a pair across days can't be scored
    against a one-day layer."""
    folder = JUDGMENTS / country
    if not folder.exists():
        return None
    files = []
    for f in sorted(folder.glob("*.json")):
        m = JUDGMENT_FILE.match(f.name)
        if m and m.group(1) <= date <= (m.group(2) or m.group(1)) and (name is None or m.group(3) == name):
            files.append(f)
    if not files:
        return None
    merged = {"same": [], "apart": [], "campaigns": [], "files": []}
    for f in files:
        j = json.loads(f.read_text())
        merged["same"] += [g for g in ([i for i in grp if i in day_ids] for grp in j.get("same", [])) if len(g) > 1]
        merged["apart"] += [p for p in j.get("apart", []) if all(i in day_ids for i in p)]
        for c in j.get("campaigns", []):
            ids = [i for i in c.get("signalIds", []) if i in day_ids]
            if ids:
                merged["campaigns"].append({**c, "signalIds": ids})
        merged["files"].append(f.name)
    return merged


def shape_metrics(layer: dict, day: dict) -> dict:
    events = layer["events"]
    sizes = [len(e["signalIds"]) for e in events]
    assigned = sum(sizes)
    sev_by_signal = {s["id"]: s.get("severity") for s in day["signals"]}
    alerts = 0
    for e in events:
        sev = e.get("severity")
        if sev is None:
            sevs = [sev_by_signal.get(sid) for sid in e["signalIds"]]
            sevs = [s for s in sevs if s is not None]
            sev = max(sevs) if sevs else None
        if sev is not None and sev >= 4:
            alerts += 1
    outcomes: dict[str, int] = {}
    for d in layer.get("decisions", {}).values():
        outcomes[d.get("outcome", "?")] = outcomes.get(d.get("outcome", "?"), 0) + 1
    return {
        "signals_in_day": len(day["signals"]),
        "signals_assigned": assigned,
        "events": len(events),
        "merge_ratio": round(assigned / len(events), 2) if events else 0.0,
        "singleton_share": round(sum(1 for s in sizes if s == 1) / len(events), 2) if events else 0.0,
        "largest_event": max(sizes) if sizes else 0,
        "projected_alerts_sev4": alerts,
        "outcomes": outcomes,
    }


def judgment_metrics(layer: dict, judgments: dict) -> dict:
    event_of: dict[str, str] = {}
    for e in layer["events"]:
        for sid in e["signalIds"]:
            event_of[sid] = e["id"]

    uf = UnionFind()
    for group in judgments["same"]:
        for a, b in zip(group, group[1:]):
            uf.union(a, b)
    judged_same: set[frozenset] = set()
    for group in judgments["same"]:
        for a, b in itertools.combinations(group, 2):
            judged_same.add(frozenset((a, b)))
    # Transitive closure: pairs inside one judged component also count as same.
    members: dict[str, list[str]] = {}
    for sid in list(uf.parent):
        members.setdefault(uf.find(sid), []).append(sid)
    for comp in members.values():
        for a, b in itertools.combinations(comp, 2):
            judged_same.add(frozenset((a, b)))

    judged_apart = {frozenset(p) for p in judgments["apart"] if len(p) == 2}
    conflicts = judged_same & judged_apart
    judged_apart -= conflicts

    def layer_same(pair: frozenset) -> bool:
        a, b = tuple(pair)
        return a in event_of and b in event_of and event_of[a] == event_of[b]

    tp = sum(1 for p in judged_same if layer_same(p))
    fn = len(judged_same) - tp
    fp = sum(1 for p in judged_apart if layer_same(p))
    tn = len(judged_apart) - fp
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None

    set_hits, set_splits = 0, []
    for comp in members.values():
        if len(comp) < 2:
            continue
        ids = {event_of.get(s, "∅") for s in comp}
        if len(ids) == 1 and "∅" not in ids:
            set_hits += 1
        else:
            set_splits.append((len(comp), len(ids)))

    return {
        "judged_same_pairs": len(judged_same),
        "judged_apart_pairs": len(judged_apart),
        "conflicting_pairs": len(conflicts),
        "pair_precision": round(precision, 3) if precision is not None else None,
        "pair_recall": round(recall, 3) if recall is not None else None,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "judged_sets": sum(1 for c in members.values() if len(c) > 1),
        "set_hits": set_hits,
        "set_splits": set_splits,
        "campaigns_judged": len(judgments["campaigns"]),
        "judgment_files": judgments["files"],
    }


def score_one(country: str, date: str, algo: str, day: dict, judgments: dict | None) -> dict:
    path = layer_path(country, date, algo)
    if not path.exists():
        sys.exit(f"no layer at {path}")
    layer = json.loads(path.read_text())
    result = {"layer": algo, **shape_metrics(layer, day)}
    if judgments:
        result.update(judgment_metrics(layer, judgments))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--layer", help="layer name, e.g. clear-as-run or jev-v1-7d")
    parser.add_argument("--all", action="store_true", help="score every registered layer for the day")
    parser.add_argument("--judgments", help="judgments name to use (default: merge every file for the day)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.layer and not args.all:
        parser.error("give --layer or --all")

    day = load_day(args.country, args.date)
    judgments = load_judgments(args.country, args.date, args.judgments, {s["id"] for s in day["signals"]})
    if args.all:
        index_path = LAYERS / "index.json"
        index = json.loads(index_path.read_text()) if index_path.exists() else {}
        names = index.get(f"{args.country}/{args.date}", [])
    else:
        names = [args.layer]
    results = [score_one(args.country, args.date, n, day, judgments) for n in names]

    if args.json:
        print(json.dumps(results, indent=1))
        return
    if not judgments:
        print("(no judgments for this day yet — shape metrics only)\n")
    cols = ["layer", "events", "merge_ratio", "singleton_share", "projected_alerts_sev4",
            "pair_precision", "pair_recall", "set_hits", "judged_sets"]
    print(" | ".join(cols))
    for r in results:
        print(" | ".join(str(r.get(c, "")) for c in cols))
    for r in results:
        if r.get("set_splits"):
            print(f"\n{r['layer']}: judged sets split as (members → layer events): {r['set_splits']}")
        if r.get("conflicting_pairs"):
            print(f"{r['layer']}: {r['conflicting_pairs']} judged pairs are both same and apart — fix the judgments")
        print(f"{r['layer']}: outcomes {r['outcomes']}")


if __name__ == "__main__":
    main()
