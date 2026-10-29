#!/usr/bin/env python3
"""Dry-run clear-pipeline's location step for text-only signals over fetched days.

Runs clear-pipeline's real `locate_in_country` (the sudan-war-x locator: Claude
picks an admin area, the named place is geocoded inside it) over every signal of
one source in a date range, and compares the result with what CLEAR stored.
Nothing is written to CLEAR:

- point promotion (`findOrCreateLandmarkL4`) is replaced by a local lookup of
  the containing district in `data/<country>/geo.json`;
- the gazetteer and the geocoder cache are only read, from the dev API;
- LocationIQ (with `--locationiq`) caches to `data/.cache/locationiq/` instead
  of clear-api, and is rate-limited in-process instead of through Redis.

Unlike the rest of the lab this needs clear-pipeline's environment, because it
runs clear-pipeline's own code. Run it through that checkout's uv project:

    uv run --project ../clear-pipeline python geo_eval.py --country sudan \\
        --from 2026-10-20 --to 2026-10-27

Options add variants and measurements:

  --locationiq  let LocationIQ run (LOCATIONIQ_API_KEY in .env); reports which
                tier placed each post and how many upstream calls it cost
  --compare     with --locationiq: also ask LocationIQ about posts the gazetteer
                placed, and report how far apart the two answers are
  --arabic      prototype Arabic-first matching against GeoNames' Arabic names
                (needs data/geonames/<CC>.txt; --fetch-geonames downloads it)

Writes data/<country>/geo-eval/<from>_<to>[.<tag>].json and prints a summary.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import difflib
import hashlib
import io
import json
import math
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import lab_common as lc

DEV_HOST = "dev-api.clearinitiative.io"
COUNTRY_CODES = {"sudan": "sd", "venezuela": "ve", "afghanistan": "af"}
DEFAULT_MODEL = "anthropic/claude-haiku-4.5"
LLM_CACHE = lc.DATA / ".cache" / "geo-eval-llm"
LOCATIONIQ_CACHE = lc.DATA / ".cache" / "locationiq"

parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
parser.add_argument("--country", required=True)
parser.add_argument("--from", dest="date_from", required=True, help="first day, YYYY-MM-DD")
parser.add_argument("--to", dest="date_to", required=True, help="last day, inclusive")
parser.add_argument("--source", default="sudan-war-x", help="signal source to locate")
parser.add_argument("--country-code", help="ISO2 the geocoder searches in (default: from --country)")
parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter model for the location call")
parser.add_argument("--limit", type=int, help="only the first N signals (smoke test)")
parser.add_argument("--workers", type=int, default=8)
parser.add_argument("--locationiq", action="store_true", help="let LocationIQ run")
parser.add_argument("--compare", action="store_true", help="with --locationiq: ask both tiers")
parser.add_argument("--arabic", action="store_true", help="add the Arabic-first prototype variant")
parser.add_argument("--fetch-geonames", action="store_true", help="download data/geonames/<CC>.txt")
parser.add_argument("--tag", help="suffix for the output file")
args = parser.parse_args()
if args.compare and not args.locationiq:
    parser.error("--compare needs --locationiq")

lc.load_env()
host = urllib.parse.urlparse(lc.require_env("CLEAR_API_URL", "CLEAR_API_BASE")).hostname
if host != DEV_HOST:
    sys.exit(f"CLEAR_API_URL points at {host!r}; this lab only reads from {DEV_HOST}")
lc.require_env("OPENROUTER_API_KEY")
if args.locationiq:
    lc.require_env("LOCATIONIQ_API_KEY")
else:
    os.environ.pop("LOCATIONIQ_API_KEY", None)  # pipeline settings read the env at import

try:
    from pydantic import BaseModel
    from shapely.geometry import MultiPolygon, Point, Polygon, shape

    from clear_pipeline.providers import geoparser, location, nominatim
except ImportError as exc:
    sys.exit(f"{exc}\nRun through clear-pipeline's environment: "
             "uv run --project ../clear-pipeline python geo_eval.py …")
for needed in ("_geocode_within", "_names_country_or_state", "_area_shape"):
    if not hasattr(location, needed):
        sys.exit(f"clear-pipeline at {Path(location.__file__).parents[3]} predates the "
                 f"area-checked locator (no location.{needed}); pull its dev branch")

cc = (args.country_code or COUNTRY_CODES.get(args.country, "")).lower()
if not cc:
    parser.error(f"no ISO2 known for {args.country!r}; pass --country-code")

# ── fetched days ────────────────────────────────────────────────────────────
start, end = date.fromisoformat(args.date_from), date.fromisoformat(args.date_to)
days = [(start + timedelta(n)).isoformat() for n in range((end - start).days + 1)]
signals, locs, country_id = [], {}, None
for day in days:
    d = lc.load_day(args.country, day)
    locs.update(d["locations"])
    country_id = d["countryLocationId"]
    signals += [s for s in d["signals"] if s["source"] == args.source]
if args.limit:
    signals = signals[: args.limit]
if not signals:
    sys.exit(f"no {args.source} signals in {args.country} {days[0]}..{days[-1]}")
country_name = locs[country_id]["name"]
locations = [
    {"id": i, "name": v["name"], "level": v["level"],
     "parent": {"id": v["parentId"]} if v.get("parentId") else None}
    for i, v in locs.items()
]
geo_path = lc.DATA / args.country / "geo.json"
if not geo_path.exists():
    sys.exit(f"no {geo_path} — run fetch_geo.py --country {args.country}")
geo = json.loads(geo_path.read_text())


def area_geometry(loc_id):
    a = geo["areas"].get(loc_id)
    polys = [Polygon(r) for r in (a or {}).get("r", []) if len(r) >= 4]
    return MultiPolygon(polys).__geo_interface__ if polys else None


districts = [(i, shape(area_geometry(i))) for i, a in geo["areas"].items()
             if str(a["l"]) == "2" and area_geometry(i)]


def containing_district(lat, lng):
    """Smallest-polygon lookup as clear-api does it: containing district, else
    the nearest within ~50 km. geo.json outlines are simplified to ~1 km, so a
    few points near boundaries can land differently than on real polygons."""
    p = Point(lng, lat)
    best = min(districts, key=lambda d: d[1].distance(p))
    return best[0] if best[1].distance(p) < 0.45 else None


def level_of(loc_id):
    if not loc_id:
        return None
    return 4 if loc_id.startswith("pt|") else locs[loc_id]["level"]


def district_of(loc_id):
    if not loc_id:
        return None
    if loc_id.startswith("pt|"):
        return loc_id.split("|")[1] or None
    while loc_id:
        if locs[loc_id]["level"] == 2:
            return loc_id
        loc_id = locs[loc_id].get("parentId")
    return None


def label(loc_id):
    if not loc_id:
        return "—"
    if loc_id.startswith("pt|"):
        _, d, n = loc_id.split("|", 2)
        return f"{n} ▸ {locs[d]['name'] if d in locs else '?'}"
    return locs[loc_id]["name"]


# ── Claude through OpenRouter, cached on disk ──────────────────────────────
class OpenRouterProvider:
    def complete_structured(self, *, system, user, schema, **_):
        LLM_CACHE.mkdir(parents=True, exist_ok=True)
        key = hashlib.sha256(f"{args.model}\n{system}\n{user}".encode()).hexdigest()
        path = LLM_CACHE / f"{key}.json"
        if path.exists():
            text = json.loads(path.read_text())["text"]
        else:
            body = json.dumps({
                "model": args.model, "temperature": 0, "max_tokens": 400,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}],
            }).encode()
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=body,
                headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                text = json.load(resp)["choices"][0]["message"]["content"]
            path.write_text(json.dumps({"text": text}))
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
        match = re.search(r"\{.*\}", text, re.S)
        return schema.model_validate_json(match.group(0) if match else text)


provider = OpenRouterProvider()

# ── dev API, read-only ─────────────────────────────────────────────────────
GAZETTEER_QUERY = """query($name:String!,$cc:String,$min:Float){resolveGazetteerLocation(
  name:$name,countryCode:$cc,minSimilarity:$min){name latitude longitude featureClass
  featureCode countryCode score exact}}"""
CACHE_QUERY = """query($h:String!){nominatimCacheEntry(queryHash:$h){status responseJson}}"""
_memo, _memo_lock = {}, threading.Lock()


def memo(key, fetch):
    with _memo_lock:
        if key in _memo:
            return _memo[key]
    value = fetch()
    with _memo_lock:
        _memo[key] = value
    return value


def gazetteer(name, *, country_code=None, min_similarity=None):
    return memo(("gaz", name, country_code, min_similarity), lambda: lc.graphql(
        GAZETTEER_QUERY, {"name": name, "cc": country_code, "min": min_similarity},
    ).get("resolveGazetteerLocation"))


# ── LocationIQ without Redis or cache writes ───────────────────────────────
class LocalRedis:
    """The few Redis calls nominatim's rate limiter and circuit breaker make."""

    def __init__(self):
        self._d, self._lock = {}, threading.Lock()

    def get(self, k):
        return self._d.get(k)

    def set(self, k, v, ex=None):
        self._d[k] = v

    def delete(self, k):
        self._d.pop(k, None)

    def incr(self, k):
        with self._lock:
            self._d[k] = int(self._d.get(k) or 0) + 1
            return self._d[k]

    def expire(self, k, s):
        pass


stats = {"locationiq_calls": 0, "dev_cache_hits": 0, "local_cache_hits": 0}
_stats_lock, _upstream_lock = threading.Lock(), threading.Lock()
_real_wait = nominatim._wait_for_rate_limit_slot


def count(key):
    with _stats_lock:
        stats[key] += 1


def wait_for_slot():
    # Serialise upstream calls: the real limiter assumes one Redis-backed clock.
    with _upstream_lock:
        _real_wait()
    count("locationiq_calls")


def cache_lookup(query_hash):
    path = LOCATIONIQ_CACHE / f"{query_hash}.json"
    if path.exists():
        count("local_cache_hits")
        return json.loads(path.read_text())
    entry = memo(("cache", query_hash),
                 lambda: lc.graphql(CACHE_QUERY, {"h": query_hash}).get("nominatimCacheEntry"))
    if entry:
        count("dev_cache_hits")
        return {"status": entry["status"], "responseJson": entry.get("responseJson")}
    return None


def cache_write(*, query_hash, response_json, status, **_):
    if status == "error":
        return  # retry next run rather than remembering an outage
    LOCATIONIQ_CACHE.mkdir(parents=True, exist_ok=True)
    (LOCATIONIQ_CACHE / f"{query_hash}.json").write_text(
        json.dumps({"status": status, "responseJson": response_json}))


# ── Arabic-first prototype (GeoNames' Arabic names, local file) ─────────────
AR = re.compile("[؀-ۿ]")
TASHKEEL = re.compile("[ً-ٰٟـ]")
ARTICLE = re.compile(r"^(al|el|ad|ed|as|es|at|an|ar|az|ash)[\s-]+")


def ar_norm(s):
    s = TASHKEEL.sub("", s)
    s = re.sub("[أإآٱ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    return re.sub(r"\s+", " ", s).strip()


def skeleton(s):
    s = ARTICLE.sub("", s.lower().strip()).replace("q", "g").replace("ou", "u")
    s = re.sub(r"[aeiouy]", "", re.sub(r"[^a-z]", "", s))
    return re.sub(r"(.)\1+", r"\1", s)


def agrees(english, row):
    """The Arabic hit's Latin names must match Claude's English spelling. Catches
    GeoNames errors such as Kosti carrying Rabak's Arabic name (ربك)."""
    e = skeleton(english or "")
    return bool(e) and any(
        (k := skeleton(n)) and (k == e or difflib.SequenceMatcher(None, k, e).ratio() >= 0.8)
        for n in row["latin"])


def fetch_geonames(path: Path):
    """HTTPS only, no redirects, expected zip members only; prints the SHA-256 so
    the extract used can be recorded (GeoNames publishes no checksums)."""
    url = f"https://download.geonames.org/export/dump/{cc.upper()}.zip"

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    with urllib.request.build_opener(NoRedirect).open(url, timeout=120) as resp:
        blob = resp.read()
    archive = zipfile.ZipFile(io.BytesIO(blob))
    names = set(archive.namelist())
    if names - {f"{cc.upper()}.txt", "readme.txt"}:
        sys.exit(f"unexpected members in {url}: {sorted(names)}")
    text = archive.read(f"{cc.upper()}.txt").decode("utf8")
    bad = sum(1 for line in text.splitlines() if len(line.split("\t")) != 19)
    if bad:
        sys.exit(f"{bad} malformed rows in {url}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf8")
    print(f"geonames: {url} {len(blob)} bytes sha256={hashlib.sha256(blob).hexdigest()}")


ar_index: dict[str, list[dict]] = {}
if args.arabic:
    gn_path = lc.DATA / "geonames" / f"{cc.upper()}.txt"
    if args.fetch_geonames or not gn_path.exists():
        if not args.fetch_geonames:
            sys.exit(f"no {gn_path} — add --fetch-geonames to download it")
        fetch_geonames(gn_path)
    for line in gn_path.read_text(encoding="utf8").splitlines():
        c = line.split("\t")
        if c[6] not in ("P", "A"):
            continue
        alts = c[3].split(",") if c[3] else []
        row = {"name": c[1], "code": c[7], "lat": float(c[4]), "lng": float(c[5]),
               "pop": int(c[14] or 0),
               "latin": [c[1], c[2]] + [a for a in alts if a and not AR.search(a)]}
        for a in alts:
            if AR.search(a):
                ar_index.setdefault(ar_norm(a), []).append(row)


class _ArabicName(BaseModel):
    place_name_ar: str | None = None


AR_SYSTEM = ("You copy place names out of Arabic text. Given a post and an English place "
             "name, return that place's name exactly as the post writes it in Arabic, "
             "without attached prefixes (ب، و، ل، ف، ك). Return null if the post does not "
             "write it in Arabic. Respond with JSON only: {\"place_name_ar\": ...}")

# ── tracing the pipeline's calls ───────────────────────────────────────────
tls = threading.local()
real_resolve = location.resolve_signal_location
real_geocode = geoparser.geocode_place_name
real_gazetteer_tier = geoparser._resolve_via_gazetteer


def traced_resolve(*a, **kw):
    tls.trace["resolved"] = result = real_resolve(*a, **kw)
    return result


def traced_gazetteer_tier(top, expected):
    hit = real_gazetteer_tier(top, expected)
    tls.trace["gazetteer_hit"] = None if hit is None else {
        "name": hit.display_name, "lat": hit.lat, "lng": hit.lng, "score": hit.importance}
    return hit


def traced_geocode(name, **kw):
    tls.trace["geocode_called"] = True
    tls.trace["accept"] = kw.get("accept")
    result = real_geocode(name, **kw)
    tls.trace["geocode"] = None if result is None else {
        "name": result.display_name, "lat": result.lat, "lng": result.lng,
        "tier": "gazetteer" if (result.osm_type or "").startswith("geonames:") else "locationiq",
        "score": result.importance}
    return result


def fake_promote(*, name, lat, lng, kind, **_):
    d = containing_district(lat, lng)
    return {"locationId": f"pt|{d}|{name}" if d else None, "reused": False,
            "abortedReason": None if d else "no_district"}


def outcome(tr):
    r = tr.get("resolved") or {}
    if not r.get("place_name"):
        return "no place named"
    if not tr.get("geocode_called"):
        return "skipped: state/country name or explicit country answer"
    g = tr.get("geocode")
    gaz = tr.get("gazetteer_hit")
    if g and g["tier"] == "gazetteer":
        return "point via gazetteer"
    if g:
        return ("point via LocationIQ, after a gazetteer match outside the area" if gaz
                else "point via LocationIQ, after a gazetteer miss")
    if gaz:
        return "no point: gazetteer match outside the area" + (
            ", LocationIQ found none inside" if args.locationiq else "")
    return "no point: gazetteer miss" + (", LocationIQ miss" if args.locationiq else "")


def km(a_lat, a_lng, b_lat, b_lng):
    p = math.pi / 180
    h = (math.sin((b_lat - a_lat) * p / 2) ** 2
         + math.cos(a_lat * p) * math.cos(b_lat * p) * math.sin((b_lng - a_lng) * p / 2) ** 2)
    return 12742 * math.asin(math.sqrt(h))


def compare_locationiq(tr):
    """Ask LocationIQ the same question the gazetteer answered (same area test)."""
    g = tr.get("geocode")
    if not (g and g["tier"] == "gazetteer" and tr.get("accept")):
        return None
    name = tr["resolved"]["place_name"]
    best = None
    for variant in geoparser._query_variants(name):
        results = nominatim.search(variant, country_codes=cc, limit=5)
        best = geoparser._pick_best_nominatim_result(results or [], {cc}, tr["accept"])
        if best:
            break
    if not best:
        return {"locationiq": None}
    lat, lng = float(best["lat"]), float(best["lon"])
    return {"locationiq": {"name": best.get("display_name", "")[:80], "lat": lat, "lng": lng},
            "km": round(km(g["lat"], g["lng"], lat, lng), 1)}


def arabic_variant(s, tr):
    r = tr.get("resolved") or {}
    english = r.get("place_name")
    text = f"{s['title']}\n{s['text']}"
    area_id = (r.get("location_id") or r.get("origin_id") or r.get("destination_id")
               or country_id)
    if (not english or not AR.search(text)
            or location._names_country_or_state(english, country_name)):
        return tr["branch"], "no attempt"
    ar = provider.complete_structured(
        system=AR_SYSTEM, user=f"POST:\n{text}\n\nENGLISH PLACE NAME: {english}",
        schema=_ArabicName).place_name_ar
    tr["place_name_ar"] = ar
    if not ar:
        return tr["branch"], "no Arabic name"
    rows = ar_index.get(ar_norm(ar)) or ar_index.get(ar_norm(re.sub("^ال", "", ar)))
    if not rows:
        return tr["branch"], "not in GeoNames"
    ok = [x for x in rows if agrees(english, x)]
    if not ok:
        return tr["branch"], "disagrees with English"
    best = max(ok, key=lambda x: (x["code"].startswith(("PPL", "ADM")), x["pop"]))
    area = location._area_shape(area_id)
    if area is None or not area.contains(Point(best["lng"], best["lat"])):
        return tr["branch"], "outside area"
    d = containing_district(best["lat"], best["lng"])
    return (f"pt|{d}|{english}" if d else tr["branch"]), "hit"


def run_one(s):
    tls.trace = {}
    tr = tls.trace
    tr["branch"] = location.locate_in_country(
        s["title"], s["text"], country_name, country_code=cc)
    tr["outcome"] = outcome(tr)
    if args.compare:
        tr["compare"] = compare_locationiq(tr)
    if args.arabic:
        try:
            tr["arabic"], tr["arabic_path"] = arabic_variant(s, tr)
        except Exception as exc:  # noqa: BLE001
            tr["arabic"], tr["arabic_path"] = tr["branch"], f"error: {exc}"
    return s, tr


started = time.monotonic()
with (
    patch.object(location, "get_locations", return_value=locations),
    patch.object(location, "get_locations_by_level",
                 return_value=[x for x in locations if x["level"] == 0]),
    patch.object(location, "make_llm_provider", return_value=provider),
    patch.object(location, "resolve_signal_location", traced_resolve),
    patch.object(location, "geocode_place_name", traced_geocode),
    patch.object(location, "find_or_create_landmark_l4", fake_promote),
    patch.object(location, "get_location_with_geometry",
                 side_effect=lambda i: {"id": i, "geometry": area_geometry(i)}),
    patch.object(geoparser, "_resolve_via_gazetteer", traced_gazetteer_tier),
    patch.object(geoparser.graphql, "resolve_gazetteer_location", gazetteer),
    patch.object(geoparser.settings, "geoparser_use_gazetteer", True),
    patch.object(nominatim, "_redis", LocalRedis()),
    patch.object(nominatim, "_wait_for_rate_limit_slot", wait_for_slot),
    patch.object(nominatim, "_cache_lookup", cache_lookup),
    patch.object(nominatim, "_cache_write", cache_write),
):
    location.invalidate_locations_cache()
    with cf.ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(run_one, signals))
elapsed = time.monotonic() - started

# ── write + summarise ───────────────────────────────────────────────────────
rows = []
for s, tr in results:
    r = tr.get("resolved") or {}
    asrun = (s.get("location") or {}).get("id")
    row = {
        "id": s["id"], "day": s["publishedAt"][:10], "url": s["url"], "title": s["title"][:140],
        "asrun": asrun, "asrunName": label(asrun), "asrunLevel": level_of(asrun),
        "areaId": r.get("location_id") or r.get("origin_id") or r.get("destination_id"),
        "placeName": r.get("place_name"), "outcome": tr["outcome"],
        "gazetteerHit": tr.get("gazetteer_hit"), "geocode": tr.get("geocode"),
        "branch": tr["branch"], "branchName": label(tr["branch"]),
        "branchLevel": level_of(tr["branch"]), "branchDistrict": district_of(tr["branch"]),
    }
    if args.compare:
        row["compare"] = tr.get("compare")
    if args.arabic:
        row.update({"placeNameAr": tr.get("place_name_ar"), "arabic": tr["arabic"],
                    "arabicName": label(tr["arabic"]), "arabicLevel": level_of(tr["arabic"]),
                    "arabicPath": tr["arabic_path"]})
    rows.append(row)

params = {k: v for k, v in vars(args).items() if k not in ("fetch_geonames",)}
out = lc.DATA / args.country / "geo-eval" / (
    f"{days[0]}_{days[-1]}" + (f".{args.tag}" if args.tag else "") + ".json")
lc.write_json(out, {"createdAt": lc.now_iso(), "params": params, "countryCode": cc,
                    "pipeline": str(Path(location.__file__).parents[3]),
                    "stats": stats if args.locationiq else None, "signals": rows})

n = len(rows)


def levels(key):
    bucket = {None: "none", 0: "country", 1: "state", 2: "district or finer", 4: "district or finer"}
    counts = {}
    for x in rows:
        counts[bucket[x[key]]] = counts.get(bucket[x[key]], 0) + 1
    return "  ".join(f"{k} {counts.get(k, 0)} ({100 * counts.get(k, 0) / n:.0f}%)"
                     for k in ("district or finer", "state", "country", "none"))


print(f"\n{args.source} · {args.country} {days[0]}..{days[-1]} · {n} signals · "
      f"{args.model} · {elapsed:.0f}s → {out.relative_to(lc.LAB)}")
print(f"  as run     {levels('asrunLevel')}")
print(f"  pipeline   {levels('branchLevel')}")
if args.arabic:
    print(f"  + Arabic   {levels('arabicLevel')}")
print("\nwhat happened to the place name:")
tally = {}
for x in rows:
    tally[x["outcome"]] = tally.get(x["outcome"], 0) + 1
for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
    print(f"  {v:5}  {k}")
if args.locationiq:
    print(f"\nLocationIQ: {stats['locationiq_calls']} upstream calls, "
          f"{stats['dev_cache_hits']} dev-cache hits, {stats['local_cache_hits']} local-cache hits")
if args.compare:
    cmp_rows = [x["compare"] for x in rows if x.get("compare")]
    found = [c for c in cmp_rows if c["locationiq"]]
    near = sum(c["km"] <= 5 for c in found)
    mid = sum(5 < c["km"] <= 25 for c in found)
    print(f"gazetteer points re-asked of LocationIQ: {len(cmp_rows)}; LocationIQ found "
          f"{len(found)} inside the area: {near} within 5 km, {mid} at 5–25 km, "
          f"{len(found) - near - mid} further")
if args.arabic:
    tally = {}
    for x in rows:
        tally[x["arabicPath"]] = tally.get(x["arabicPath"], 0) + 1
    print("\nArabic prototype: " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))
