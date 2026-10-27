# clear-grouping-lab

Private, local-only lab for testing how CLEAR clusters signals into events. It
replays one country-day of real dev signals through candidate algorithms, lets a
human judge which signals belong together, and scores every algorithm against
those judgments. Context and language: the Exponential page
[How CLEAR groups signals into events](https://www.exponential.im/w/clear/pages/cmvqya771000hkx086k80ga6l)
and decision D-0166. Glossary in [CONTEXT.md](CONTEXT.md). Session handoff in
[HANDOFF.md](HANDOFF.md).

Non-negotiable constraints:

- The code lives in the private repo `CLEAR-Initiative/clear-grouping-lab`, never in the public `clear-*` repos. Fetched data, layers, judgments and `.env` are gitignored and never pushed.
- It runs read-only against the dev GraphQL API with keys in a local `.env` that is gitignored and never printed.
- Nothing has to be merged into any repo to run it. Fetched data, layers and judgments stay in this directory.

## Setup

Python 3.9+ and nothing else (stdlib only). Copy `.env.example` to `.env` and fill
`CLEAR_API_URL`, `CLEAR_API_KEY` and `OPENROUTER_API_KEY` from clear-pipeline's **dev** env.
Then `python3 check_env.py` confirms the host is dev and the key is accepted, without
printing either.

## Data stays local

`data/`, `layers/` and `judgments/` are gitignored; only code, docs and `seed/`
are committed. `fetch_day.py` refuses any API host other than
`dev-api.clearinitiative.io`, so a `.env` that points at production fails
loudly instead of fetching. In Claude Code, `/fetch-day sudan 2026-10-21`
runs the fetch and reports the counts (skill in `.claude/skills/fetch-day/`).

## The loop

```bash
python3 fetch_day.py --country sudan --date 2026-10-20
```
Writes `data/sudan/2026-10-20.json` (every located signal published that UTC day,
and every event those signals belong to) and the `clear-as-run` layer. Slow on
first run: the dev API has no date filter, so it pulls every located Sudan signal
and filters locally.

```bash
python3 replay.py --country sudan --date 2026-10-20 --algo jev-v1                      # 72h window
python3 replay.py --country sudan --date 2026-10-20 --algo jev-v1 --window-hours 168 --tag 7d
python3 replay.py --country sudan --date 2026-10-20 --algo naive-state                 # no model, control
```
Each run writes `layers/sudan/2026-10-20.<name>.json`. Jev responses are cached
under `layers/.cache/<prompt version>/`, so reruns with unchanged prompts are free.
`--limit 20` is a cheap smoke test.

```bash
python3 -m http.server 8765
# then open http://localhost:8765/viewer.html?day=sudan/2026-10-20
```
The viewer shows one card per event in time order, with every signal's original
text, and a grey card for every signal in no event. Switch layers from the
dropdown. Actions: **Confirm card** (all signals on it are one event), **Pull out**
(this signal is not about the same event as the others), **select + Merge** (these
cards are one event), **select + Mark as one campaign**. Judgments are kept in the
browser per day and exported with **Export judgments**; move the file into
`judgments/sudan/` for scoring. Nothing on the page is pre-judged by a model.

```bash
python3 score.py --country sudan --date 2026-10-20 --all
```
Shape metrics for every layer (events, merge ratio, singleton share, projected
alerts at severity 4+) and, once judgments exist, pair precision and recall and
how many judged sets each layer keeps intact. Baseline to beat: merge ratio 1.2
and about 41 alerts a day.

## Decisions from the 27 Oct grilling

1. **Same event means same real-world occurrence.** A merge in the viewer says
   two signals report the same thing happening. Campaigns (one actor, one target
   class, many places) are a separate parent link, captured with "mark as one
   campaign" and ignored by `score.py` in v1.
2. **Candidate window is a parameter, judged by the lab.** `jev-v1` runs at 72h
   (D-0166 as written) and again at 7 days as a mandatory second layer; the
   decision page gets amended with numbers.
3. **Candidate summaries are rule-built, not model-written.** First title, place,
   signal count, time span, latest title. Deterministic and free; a Claude-written
   summary variant comes only if this scores badly.
4. **Dropped signals are shown.** A signal CLEAR or a layer threw away as
   irrelevant appears as a grey card and can be merged like any other, because a
   wrongly dropped post is a missed alert.
5. **v1 asks the plain question**, no per-type identity rules. A `jev-v2-typed`
   layer adds them later against the same judgments, so their worth is isolated.
6. **Jev asks three questions per signal**: a Choice over the candidates plus
   `none`, a companion yes/no "does it match any listed event" (TypeSafe's docs say
   a bare `none` option is unreliable), and the production relevance gate. The
   join rule uses all three and every probability is written to the layer.

## File contracts

**Day** `data/<country>/<date>.json`: `country`, `countryLocationId`, `date`,
`fetchedAt`, `locations` (id → name, level, parentId for the country's tree),
`signals[]` (id, source, publishedAt, collectedAt, title, text, url, severity,
glideCode, status, retracted, location, admin1Id, admin2Id, eventIds), `events[]`
(id, title, description, types, severity, first/lastSignalCreatedAt, startedAt,
location, signalIds, signalIdsInDay).

**Layer** `layers/<country>/<date>.<algo>.json`: `algo`, `params`, `country`,
`date`, `createdAt`, `events[]` (id, title, signalIds, locationId, locationName,
severity, types, firstAt, lastAt), `decisions{signalId}` (outcome: joined | new |
new-linked | no-candidates | dropped | retracted; eventId; relevance; matchesAny;
noneP; candidates[] with eventId, summary, p; linked[]). `layers/index.json`
lists the layers per day for the viewer.

**Judgments** `judgments/<country>/<date>.<judge>.json`: `same[]` (lists of signal
ids that are one event), `apart[]` (pairs that are not), `campaigns[]` (name,
signalIds), `notes{}`. Signal-level, so one file scores every layer.

## Layout

| File | Role |
|---|---|
| `lab_common.py` | `.env` loading, GraphQL call, paths, location tree |
| `fetch_day.py` | dev API → day file + `clear-as-run` layer |
| `replay.py` | day file → candidate layers (`jev-v1`, `naive-state`) |
| `viewer.html` | static judging UI |
| `score.py` | layers × judgments → metrics |
| `seed/` | the week's audit: labelled events, scored alerts, reports, old prototype UI |
| `data/ layers/ judgments/` | generated, gitignored |
