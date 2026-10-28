#!/usr/bin/env python3
"""Fetch the shapes the viewer's per-card maps need into data/<country>/geo.json.

    python3 fetch_geo.py --country sudan            # states + districts, points for every fetched day
    python3 fetch_geo.py --country sudan --refresh  # refetch the state/district outlines too

Read-only. Outlines (country, states, districts) change rarely, so they are
fetched once and kept; points (the level-4 places signals resolve to) are
added for every day file under data/<country>/ on each run. fetch_day.py runs
this at the end, so a normal day fetch needs nothing extra.

geo.json shape:
  fetchedAt
  areas:  {locationId: {l: level, c: [lon, lat] centre, bb: [w, s, e, n], r: [[[lon, lat], …], …] outer rings}}
  points: {locationId: [lon, lat]}

Outlines are simplified to about 1 km (Douglas–Peucker), which is plenty for
a map a few hundred pixels wide and keeps a judging pack small.
"""

from __future__ import annotations

import argparse
import json
import math

from lab_common import COUNTRY_IDS, DATA, graphql, now_iso, write_json

BATCH = 40
TOLERANCE = {0: 0.02, 1: 0.01, 2: 0.005}  # degrees; ~2 km, 1 km, 0.5 km


def geo_path(country: str):
    return DATA / country / "geo.json"


def fetch_geometries(ids: list[str]) -> dict[str, dict]:
    """GeoJSON geometry per location id, BATCH ids per query via aliases."""
    out: dict[str, dict] = {}
    for start in range(0, len(ids), BATCH):
        chunk = ids[start : start + BATCH]
        query = "query LabGeo {" + "".join(
            f' l{n}: location(id: "{lid}") {{ id geometry }}' for n, lid in enumerate(chunk)
        ) + " }"
        for row in graphql(query).values():
            if row and row.get("geometry"):
                out[row["id"]] = row["geometry"]
    return out


def _perp(p, a, b) -> float:
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return math.hypot(x - x1, y - y1)
    return abs(dy * x - dx * y + x2 * y1 - y2 * x1) / math.hypot(dx, dy)


def simplify(ring: list, tol: float) -> list:
    """Douglas–Peucker, iterative so long rings don't hit the recursion limit."""
    if len(ring) < 5:
        return ring
    keep = [False] * len(ring)
    keep[0] = keep[-1] = True
    stack = [(0, len(ring) - 1)]
    while stack:
        i, j = stack.pop()
        best, idx = 0.0, -1
        for k in range(i + 1, j):
            d = _perp(ring[k], ring[i], ring[j])
            if d > best:
                best, idx = d, k
        if best > tol:
            keep[idx] = True
            stack += [(i, idx), (idx, j)]
    return [p for p, k in zip(ring, keep) if k]


def ring_area_centroid(ring: list) -> tuple[float, float, float]:
    """Signed shoelace area and centroid of one ring."""
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        cross = x1 * y2 - x2 * y1
        a += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if a == 0:
        xs, ys = [p[0] for p in ring], [p[1] for p in ring]
        return 0.0, sum(xs) / len(xs), sum(ys) / len(ys)
    return a / 2, cx / (3 * a), cy / (3 * a)


def area_entry(geometry: dict, level: int) -> dict | None:
    if geometry["type"] == "Polygon":
        polys = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        polys = geometry["coordinates"]
    else:
        return None
    tol = TOLERANCE.get(level, 0.005)
    rings, best = [], (0.0, None)
    for poly in polys:
        outer = [[round(x, 3), round(y, 3)] for x, y in poly[0]]
        a, cx, cy = ring_area_centroid(outer)
        if abs(a) > best[0]:
            best = (abs(a), [round(cx, 3), round(cy, 3)])
        small = simplify(outer, tol)
        if len(small) >= 4:
            rings.append(small)
    if not rings:
        return None
    xs = [p[0] for r in rings for p in r]
    ys = [p[1] for r in rings for p in r]
    return {"l": level, "c": best[1], "bb": [min(xs), min(ys), max(xs), max(ys)], "r": rings}


def update_geo(country: str, *, refresh: bool = False) -> None:
    path = geo_path(country)
    geo = json.loads(path.read_text()) if path.exists() and not refresh else {"areas": {}, "points": {}}

    days = sorted((DATA / country).glob("????-??-??.json"))
    if not days:
        print(f"geo: no day files under data/{country}/ yet; nothing to map")
        return
    # The admin tree is the same in every day file; the newest one is enough.
    locations = json.loads(days[-1].read_text())["locations"]

    admin_ids = [lid for lid, loc in locations.items() if loc["level"] <= 2 and lid not in geo["areas"]]
    if admin_ids:
        print(f"geo: fetching {len(admin_ids)} country/state/district outlines …")
        for lid, geometry in fetch_geometries(admin_ids).items():
            entry = area_entry(geometry, locations[lid]["level"])
            if entry:
                geo["areas"][lid] = entry

    wanted: set[str] = set()
    for day_file in days:
        for s in json.loads(day_file.read_text())["signals"]:
            loc = s.get("location") or {}
            if loc.get("level", 0) > 2 and loc.get("id") not in geo["points"]:
                wanted.add(loc["id"])
    if wanted:
        print(f"geo: fetching {len(wanted)} signal points …")
        for lid, geometry in fetch_geometries(sorted(wanted)).items():
            if geometry["type"] == "Point":
                x, y = geometry["coordinates"][:2]
                geo["points"][lid] = [round(x, 4), round(y, 4)]
            else:  # a polygon at level 4: map it by its centre
                entry = area_entry(geometry, 2)
                if entry:
                    geo["points"][lid] = entry["c"]

    geo["fetchedAt"] = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(geo, separators=(",", ":")))
    print(f"geo: wrote {path} ({len(geo['areas'])} areas, {len(geo['points'])} points, {path.stat().st_size / 1e3:.0f} KB)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True, choices=sorted(COUNTRY_IDS))
    parser.add_argument("--refresh", action="store_true", help="refetch outlines already in geo.json")
    args = parser.parse_args()
    update_geo(args.country, refresh=args.refresh)


if __name__ == "__main__":
    main()
