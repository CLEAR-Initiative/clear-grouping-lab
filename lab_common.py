"""Shared helpers for the grouping lab: .env loading, GraphQL calls, paths,
location hierarchy. Stdlib only so the lab runs with a bare python3.

Keys are read from .env and never printed. Every API call is a query; the lab
has no mutations.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date as Date, datetime, timedelta, timezone
from pathlib import Path

LAB = Path(__file__).resolve().parent
DATA = LAB / "data"
LAYERS = LAB / "layers"
JUDGMENTS = LAB / "judgments"

COUNTRY_IDS = {
    "sudan": "3c7edcfb-85f1-46e4-8a7b-29651f73d740",
}


def load_env() -> None:
    """Read KEY=VALUE lines from .env into os.environ (existing vars win)."""
    path = LAB / ".env"
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def require_env(*names: str) -> str:
    """First set variable among `names`, else exit with a hint (never echoes values)."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    sys.exit(f"missing {' / '.join(names)} — copy .env.example to .env and fill it in")


def graphql(query: str, variables: dict | None = None, *, timeout: int = 600) -> dict:
    """POST one GraphQL query to the dev API with the bearer key from .env."""
    load_env()
    url = require_env("CLEAR_API_URL", "CLEAR_API_BASE")
    if not url.rstrip("/").endswith("/graphql"):
        url = url.rstrip("/") + "/graphql"
    key = require_env("CLEAR_API_KEY")
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        sys.exit(f"GraphQL HTTP {exc.code}: {detail}")
    if payload.get("errors"):
        sys.exit("GraphQL errors: " + json.dumps(payload["errors"])[:1000])
    return payload["data"]


def day_path(country: str, date: str) -> Path:
    return DATA / country / f"{date}.json"


def layer_path(country: str, date: str, algo: str) -> Path:
    return LAYERS / country / f"{date}.{algo}.json"


def judgments_path(country: str, date: str, name: str) -> Path:
    return JUDGMENTS / country / f"{date}.{name}.json"


def load_day(country: str, date: str) -> dict:
    path = day_path(country, date)
    if not path.exists():
        sys.exit(f"no day file at {path} — run fetch_day.py --country {country} --date {date}")
    return json.loads(path.read_text())


def dates_between(start: str, end: str) -> list[str]:
    """Every calendar date from start to end inclusive, as YYYY-MM-DD."""
    first, last = Date.fromisoformat(start), Date.fromisoformat(end)
    if first > last:
        sys.exit(f"--from {start} is after --to {end}")
    return [(first + timedelta(days=i)).isoformat() for i in range((last - first).days + 1)]


def load_range(country: str, start: str, end: str) -> dict:
    """Several day files as one day: every signal in publication order, the
    union of their location trees, and `dates` listing the days. `date` is
    "<start>..<end>", the same label the viewer uses for a range. Exits if a
    day in the range hasn't been fetched, so a gap can't pass for a quiet day."""
    dates = dates_between(start, end)
    missing = [d for d in dates if not day_path(country, d).exists()]
    if missing:
        sys.exit(f"no day files for {', '.join(missing)} — run fetch_day.py for each")
    signals: list[dict] = []
    locations: dict[str, dict] = {}
    seen: set[str] = set()
    for d in dates:
        day = load_day(country, d)
        locations.update(day["locations"])
        for signal in day["signals"]:
            if signal["id"] not in seen:
                seen.add(signal["id"])
                signals.append({**signal, "day": d})
    signals.sort(key=lambda s: s["publishedAt"])
    return {"country": country, "date": f"{start}..{end}", "dates": dates,
            "locations": locations, "signals": signals}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1))


def register_layer(country: str, date: str, algo: str) -> None:
    """Keep layers/index.json current so the static viewer can list layers
    without a directory listing."""
    index_path = LAYERS / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    key = f"{country}/{date}"
    entries = index.setdefault(key, [])
    if algo not in entries:
        entries.append(algo)
    write_json(index_path, index)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class Hierarchy:
    """Walk the location tree stored in a day file."""

    def __init__(self, locations: dict[str, dict]):
        self.locations = locations

    def ancestor_at_level(self, location_id: str | None, level: int) -> str | None:
        node_id = location_id
        seen: set[str] = set()
        while node_id and node_id not in seen:
            seen.add(node_id)
            node = self.locations.get(node_id)
            if node is None:
                return None
            if node["level"] == level:
                return node_id
            if node["level"] < level:
                return None
            node_id = node.get("parentId")
        return None

    def name(self, location_id: str | None) -> str | None:
        node = self.locations.get(location_id or "")
        return node["name"] if node else None
