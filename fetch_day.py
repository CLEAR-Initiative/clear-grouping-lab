#!/usr/bin/env python3
"""Fetch one country-day from the dev CLEAR API into data/<country>/<date>.json
and derive the `clear-as-run` layer from it. Also refreshes data/<country>/geo.json
(fetch_geo.py) so the viewer can map the day's signals.

    python3 fetch_day.py --country sudan --date 2026-10-20

Read-only. The dev API has no date-filtered signal query, so this pulls every
signal located inside the country (signalsByLocation walks descendants) and
keeps those whose publishedAt falls on the UTC date. Signals that never got a
location are invisible to this query and so to the lab; the count of
located-but-dropped signals is reported so the gap is visible.

Day file shape (see README):
  country, countryLocationId, date, fetchedAt
  locations: {id: {name, level, parentId}}         the country's admin tree
  signals: [{id, source, publishedAt, collectedAt, title, text, url, severity,
             glideCode, status, retracted, location, admin1Id, admin2Id, eventIds}]
  events:  [{id, title, description, types, severity, firstSignalCreatedAt,
             lastSignalCreatedAt, startedAt, location, signalIds, signalIdsInDay}]
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import timedelta

from fetch_geo import update_geo
from lab_common import (
    COUNTRY_IDS,
    Hierarchy,
    day_path,
    graphql,
    layer_path,
    load_env,
    now_iso,
    parse_iso,
    register_layer,
    write_json,
)

DEV_HOST = "dev-api.clearinitiative.io"

LOCATIONS_QUERY = """
query LabLocations {
  locations { id name level parent { id } }
}
"""

SIGNALS_QUERY = """
query LabSignals($locationId: String!) {
  signalsByLocation(locationId: $locationId) {
    id
    source { name }
    status
    retracted
    publishedAt
    collectedAt
    url
    title
    description
    severity
    glideCode
    originLocation { id name level }
    destinationLocation { id name level }
    generalLocation { id name level }
    events { id }
  }
}
"""

EVENT_QUERY = """
query LabEvent($id: String!) {
  event(id: $id) {
    id
    title
    description
    types
    severity
    firstSignalCreatedAt
    lastSignalCreatedAt
    startedAt
    originLocation { id name level }
    destinationLocation { id name level }
    generalLocation { id name level }
    signals { id }
  }
}
"""


def country_subtree(all_locations: list[dict], root_id: str) -> dict[str, dict]:
    by_id = {loc["id"]: loc for loc in all_locations}
    tree: dict[str, dict] = {}
    for loc in all_locations:
        node, seen = loc, set()
        while node and node["id"] not in seen:
            if node["id"] == root_id:
                tree[loc["id"]] = {
                    "name": loc["name"],
                    "level": loc["level"],
                    "parentId": (loc.get("parent") or {}).get("id"),
                }
                break
            seen.add(node["id"])
            node = by_id.get((node.get("parent") or {}).get("id") or "")
    return tree


def primary_location(row: dict) -> dict | None:
    """Same precedence as the pipeline: origin > general > destination."""
    for key in ("originLocation", "generalLocation", "destinationLocation"):
        if row.get(key):
            return row[key]
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True, choices=sorted(COUNTRY_IDS))
    parser.add_argument("--date", required=True, help="UTC calendar date, YYYY-MM-DD")
    parser.add_argument("--allow-host", help="host to accept besides the dev API (normally never needed)")
    args = parser.parse_args()

    load_env()
    host = (os.environ.get("CLEAR_API_URL") or os.environ.get("CLEAR_API_BASE") or "").split("//")[-1].split("/")[0]
    if host != DEV_HOST and host != args.allow_host:
        sys.exit(
            f"CLEAR_API_URL points at {host!r}; this lab only reads from {DEV_HOST}. "
            "Fix .env (the handoff's location ids are dev ids) or pass --allow-host deliberately."
        )

    country_id = COUNTRY_IDS[args.country]
    day_start = parse_iso(args.date + "T00:00:00+00:00")
    day_end = day_start + timedelta(days=1)

    print("fetching locations …")
    locations = country_subtree(graphql(LOCATIONS_QUERY)["locations"], country_id)
    tree = Hierarchy(locations)
    print(f"  {len(locations)} locations in the {args.country} tree")

    print("fetching signals (every located signal in the country; this can take a while) …")
    rows = graphql(SIGNALS_QUERY, {"locationId": country_id})["signalsByLocation"]
    print(f"  {len(rows)} located signals in total")

    signals: list[dict] = []
    for row in rows:
        published = parse_iso(row["publishedAt"])
        if not (day_start <= published < day_end):
            continue
        loc = primary_location(row)
        loc_id = loc["id"] if loc else None
        signals.append(
            {
                "id": row["id"],
                "source": (row.get("source") or {}).get("name"),
                "publishedAt": row["publishedAt"],
                "collectedAt": row.get("collectedAt"),
                "title": row.get("title"),
                "text": row.get("description") or "",
                "url": row.get("url"),
                "severity": row.get("severity"),
                "glideCode": row.get("glideCode"),
                "status": row.get("status"),
                "retracted": bool(row.get("retracted")),
                "location": loc,
                "admin1Id": tree.ancestor_at_level(loc_id, 1),
                "admin2Id": tree.ancestor_at_level(loc_id, 2),
                "eventIds": [e["id"] for e in row.get("events") or []],
            }
        )
    signals.sort(key=lambda s: s["publishedAt"])
    print(f"  {len(signals)} signals published on {args.date}")

    event_ids = sorted({eid for s in signals for eid in s["eventIds"]})
    print(f"fetching {len(event_ids)} events …")
    in_day = {s["id"] for s in signals}
    events: list[dict] = []
    for i, eid in enumerate(event_ids, 1):
        ev = graphql(EVENT_QUERY, {"id": eid})["event"]
        if ev is None:
            continue
        member_ids = [s["id"] for s in ev.get("signals") or []]
        events.append(
            {
                "id": ev["id"],
                "title": ev.get("title"),
                "description": ev.get("description"),
                "types": ev.get("types") or [],
                "severity": ev.get("severity"),
                "firstSignalCreatedAt": ev.get("firstSignalCreatedAt"),
                "lastSignalCreatedAt": ev.get("lastSignalCreatedAt"),
                "startedAt": ev.get("startedAt"),
                "location": primary_location(ev),
                "signalIds": member_ids,
                "signalIdsInDay": [sid for sid in member_ids if sid in in_day],
            }
        )
        if i % 50 == 0:
            print(f"  {i}/{len(event_ids)}")
    events.sort(key=lambda e: e["firstSignalCreatedAt"] or "")

    day = {
        "country": args.country,
        "countryLocationId": country_id,
        "date": args.date,
        "fetchedAt": now_iso(),
        "locations": locations,
        "signals": signals,
        "events": events,
    }
    out = day_path(args.country, args.date)
    write_json(out, day)

    dropped = [s for s in signals if not s["eventIds"]]
    by_source: dict[str, int] = {}
    for s in signals:
        by_source[s["source"] or "?"] = by_source.get(s["source"] or "?", 0) + 1
    print(f"wrote {out}")
    print(f"  signals by source: {by_source}")
    print(f"  signals in no event (dropped or not yet grouped): {len(dropped)}")
    print(f"  events touched: {len(events)}")

    # The layer CLEAR itself produced, restricted to this day's signals.
    layer = {
        "algo": "clear-as-run",
        "params": {"key": "(admin2, level_2)", "windowDays": 7, "source": "fetch_day.py"},
        "country": args.country,
        "date": args.date,
        "createdAt": now_iso(),
        "events": [
            {
                "id": e["id"],
                "title": e["title"],
                "signalIds": e["signalIdsInDay"],
                "locationId": (e["location"] or {}).get("id"),
                "locationName": (e["location"] or {}).get("name"),
                "severity": e["severity"],
                "types": e["types"],
                "firstAt": e["firstSignalCreatedAt"],
                "lastAt": e["lastSignalCreatedAt"],
                "memberCountAllDays": len(e["signalIds"]),
            }
            for e in events
            if e["signalIdsInDay"]
        ],
        "decisions": {s["id"]: {"outcome": "dropped"} for s in dropped},
    }
    lp = layer_path(args.country, args.date, "clear-as-run")
    write_json(lp, layer)
    register_layer(args.country, args.date, "clear-as-run")
    print(f"wrote {lp}")

    # Outlines and points for the viewer's per-card maps (cheap after the first day).
    update_geo(args.country)


if __name__ == "__main__":
    main()
