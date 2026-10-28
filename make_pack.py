#!/usr/bin/env python3
"""Build a judging pack: one self-contained HTML file with a day's data and
layers built in, for judges who should not need Python, a server or API keys.

    python3 make_pack.py --country sudan --date 2026-10-20 --send-to "James (james@…)"
    python3 make_pack.py --country sudan --date 2026-10-20 --layers clear-as-run,jev-v1

Writes `packs/<country>-<date>.html` (gitignored). The judge double-clicks it,
judges, presses "Download judgments" and sends the file back; it goes into
`judgments/<country>/` like any other. The pack holds real signal text, so
share it only with the people judging.
"""

from __future__ import annotations

import argparse
import json
import sys

from lab_common import DATA, LAB, LAYERS

PACKS = LAB / "packs"
MARKER = "<script>\n"  # the viewer's one inline script; the pack goes just before it


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--layers", help="comma-separated layer names (default: every layer for the day)")
    parser.add_argument("--send-to", default="", help="who judges send their file to, shown on the page")
    args = parser.parse_args()

    spec = f"{args.country}/{args.date}"
    day_path = DATA / args.country / f"{args.date}.json"
    if not day_path.exists():
        sys.exit(f"no day file at {day_path.relative_to(LAB)} — run fetch_day.py first")
    index_path = LAYERS / "index.json"
    known = json.loads(index_path.read_text()).get(spec, []) if index_path.exists() else []
    names = args.layers.split(",") if args.layers else known
    if not names:
        sys.exit(f"no layers for {spec} — run replay.py first; a pack without layers shows judges nothing")
    missing = [n for n in names if n not in known]
    if missing:
        sys.exit(f"unknown layer(s) for {spec}: {', '.join(missing)} (have: {', '.join(known) or 'none'})")

    files = {
        "layers/index.json": {spec: names},
        f"data/{spec}.json": json.loads(day_path.read_text()),
    }
    for name in names:
        files[f"layers/{spec}.{name}.json"] = json.loads((LAYERS / args.country / f"{args.date}.{name}.json").read_text())

    # Every `<` becomes \u003c (it only occurs inside JSON strings), so signal text such as
    # "</script>" or "<!--<script" can't end or derail the inline script.
    blob = json.dumps({"sendTo": args.send_to, "files": files}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    viewer = (LAB / "viewer.html").read_text()
    if viewer.count(MARKER) != 1:
        sys.exit("viewer.html no longer has exactly one inline <script>; update MARKER in make_pack.py")
    html = viewer.replace(MARKER, f"<script>window.LAB_PACK = {blob};</script>\n{MARKER}")

    PACKS.mkdir(exist_ok=True)
    out = PACKS / f"{args.country}-{args.date}.html"
    out.write_text(html)
    print(f"wrote {out.relative_to(LAB)} ({out.stat().st_size / 1e6:.1f} MB, layers: {', '.join(names)})")


if __name__ == "__main__":
    main()
