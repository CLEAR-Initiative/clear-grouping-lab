# clear-grouping-lab

CLEAR sends too many alerts because it splits one real-world occurrence into many
events. This lab tests better ways of grouping signals into events. It takes one
country-day of real signals, groups them with several candidate algorithms, asks
people to judge which signals really belong together, and scores every algorithm
against those judgments.

There are two ways to take part:

- **[Judging](#judging-no-install-needed)**: you get one HTML file, open it,
  judge and send your answers back. No install, no keys, any computer.
- **[Running the lab](#running-the-lab)**: fetch days, run algorithms, build
  judging packs and score. Needs Python and two keys.

Background: the Exponential page
[How CLEAR groups signals into events](https://www.exponential.im/w/clear/pages/cmvqya771000hkx086k80ga6l)
and decision D-0166. Glossary in [CONTEXT.md](CONTEXT.md), session handoff in
[HANDOFF.md](HANDOFF.md).

## Judging (no install needed)

*This section is written so it can be pasted into an email to judges.*

1. **Open the file** you were sent (for example `sudan-2026-10-20.html`) by
   double-clicking it. It opens in your web browser; Chrome or Edge works best.
   Nothing is uploaded anywhere.
2. **Type your name** in the *Judge* box at the top right.
3. **Tab 1 · Grouped events.** Each card is one event that was built from
   several signals (posts and reports). Read the rows. Tick **not this one** on
   any signal that reports something different, then press **Yes, one event**.
4. **Tab 2 · Single signals.** These are signals that ended up alone, sorted by
   state. When two or more report the same thing, tick **select** on each and
   press **Same event** at the bottom. Greyed rows were thrown away as
   irrelevant; judge them like any other.
5. **Tab 3 · My judgments.** Press **Download judgments** and email the
   downloaded file (`2026-10-20.<your name>.json`) back.

What counts as "the same event": the **same thing happening**, at the same
place and time, such as the same strike reported by three accounts. It is *not*
the same actor or the same kind of attack in different places. When one group
does the same thing in many places (a wave of drone strikes on power stations),
select those signals and press **One campaign** instead.

Good to know:

- Your answers save in the browser as you go, so you can close the page and
  come back. Use the same browser and the same file.
- The *Layer* menu switches between algorithms. Your answers are about signals,
  not cards, so any layer works. Stay on the first one unless asked otherwise.
- Posts in Arabic show an English machine translation, with the original in
  grey underneath. Place names that appear in more than one row of a card share
  a colour, even when spelled differently (Sali / Sally). Click a place name to
  search for it.
- Each card has a small map: numbered pins are exact points, and a shaded area
  means the signal only said which district or state, so it could be anywhere
  inside it. Click the map to enlarge it. "date only" means the source gave a
  date but no time.
- The search box filters by text or place name, and selections survive a
  search. That's the quickest way to find every post about one town.
- The source menu next to it shows only one source's signals, for example
  `sudan-war-x` (the X posts). On tab 1 it keeps the cards that contain at
  least one signal from that source, and still shows their other rows.
- Partial answers are useful. Download and send whatever you have.
- The file contains real signal text. Please don't forward it.

## Running the lab

### One-time setup

1. **Get the code.** It is private to the CLEAR-Initiative GitHub org.
   ```bash
   gh repo clone CLEAR-Initiative/clear-grouping-lab
   ```
2. **Check Python.** You need 3.9 or newer and nothing else; the lab uses the
   standard library only, so there's no `pip install`. On Windows, type `py`
   wherever this README says `python3`, and install Python from python.org if
   that command isn't found.
   ```bash
   python3 --version
   ```
3. **Add keys.** Copy `.env.example` to `.env` (gitignored) and fill in:
   - `CLEAR_API_KEY`: the **dev** pipeline key (`sk_live_…`) from clear-pipeline's
     dev env. Ask James. `CLEAR_API_URL` is already set to dev.
   - one Jev key: `OPENROUTER_API_KEY` (`sk-or-…`, the route clear-pipeline uses)
     or `TYPESAFE_API_KEY` (from typesafe.ai, used directly when set).
4. **Check the keys** without printing them. Every line should say OK/set/yes.
   ```bash
   python3 check_env.py
   ```

### Each day you study

Run these from the lab folder. Swap in the country and date you want.

1. **Fetch the day** from the dev API. The first run is slow because the API has
   no date filter. In Claude Code, `/fetch-day sudan 2026-10-21` does the same
   and reports the counts.
   ```bash
   python3 fetch_day.py --country sudan --date 2026-10-20
   ```
2. **Run the algorithms.** Each run adds one layer. `naive-state` needs no
   model. Jev responses are cached, so re-runs with unchanged prompts are free.
   Add `--limit 20` for a cheap smoke test.
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo naive-state
   ```
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo jev-v1
   ```
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo jev-v1 --window-hours 168 --tag 7d
   ```
   The comparison layers below each change one thing from `jev-v1` or from
   today's rule, so a difference in score points at that one thing. See
   [Layers](#layers) for what each one asks. `v2-gazetteer` reads the
   translation file, so run it after step 3.
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo jev-v1 --abs-threshold 0.7 --margin 0.25 --any-threshold 0.7 --tag strict
   ```
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo jev-v1 --abs-threshold 0.35 --margin 0.05 --any-threshold 0.3 --tag loose
   ```
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo jev-v1 --scope country --tag country
   ```
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo v2-replay
   ```
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo v2-gazetteer
   ```
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo v2-gazetteer --type-level 1 --tag l1
   ```
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo embed-v1
   ```
   ```bash
   python3 replay.py --country sudan --date 2026-10-20 --algo embed-v1 --sim-threshold 0.665 --sim-link-threshold 0.58 --tag matched
   ```
3. **Translate the day** into English and list the places each signal names, so
   judges can read the Arabic posts and see which rows mention the same place.
   One cached model call per signal through `OPENROUTER_API_KEY` (about two
   minutes for a day; re-runs are free). The model sees one signal at a time and
   only translates; the viewer shows the original under every translation.
   `fetch_day.py` already refreshed `data/<country>/geo.json` for the maps
   (`python3 fetch_geo.py --country sudan` does it on its own).
   ```bash
   python3 translate.py --country sudan --date 2026-10-20
   ```
4. **Judge it yourself** in the viewer. Start the server, then open
   <http://localhost:8765/viewer.html?day=sudan/2026-10-20>.
   ```bash
   python3 -m http.server 8765
   ```
   <http://localhost:8765/layer-key> explains every layer step by step, with the
   day's numbers and settings read from the layer files. The viewer links to it
   as *What the layers do*.
5. **Send it to judges.** Build a pack: one HTML file with the day built in.
   It writes `packs/sudan-2026-10-20.html` (gitignored, about 2–4 MB) and builds
   in the translations and map outlines when they exist. Email it
   with the [Judging](#judging-no-install-needed) section pasted in. Leave out
   layers that would only confuse judges; `jev-v1-7d` is identical to `jev-v1`
   until the window gap below is fixed.
   ```bash
   python3 make_pack.py --country sudan --date 2026-10-20 --layers clear-as-run,jev-v1,naive-state --send-to "James"
   ```
6. **Collect answers.** Save each returned `2026-10-20.<name>.json` into
   `judgments/sudan/`. To check a judge's answers in the viewer, use
   **Import file** on tab 3.
7. **Score** every layer against every judgment file for the day.
   ```bash
   python3 score.py --country sudan --date 2026-10-20 --all
   ```
   This prints shape metrics for every layer (events, merge ratio, singleton
   share, projected alerts at severity 4+). Once judgments exist, it adds pair
   precision and recall and how many judged sets each layer keeps intact. The
   baseline to beat is a merge ratio of 1.2 and about 41 alerts a day.

### Rules that keep the data safe

- Code lives only in the private repo `CLEAR-Initiative/clear-grouping-lab`,
  never in the public `clear-*` repos.
- `data/`, `layers/`, `judgments/`, `packs/` and `.env` are gitignored and never
  pushed. Only code, docs and `seed/` are committed.
- The lab is read-only against the dev API. `fetch_day.py` refuses any host other
  than `dev-api.clearinitiative.io`, so a `.env` pointing at production fails
  loudly instead of fetching.
- Judging packs carry real signal text (including Dataminr). Send them only to
  the people judging; don't post them in a shared drive or channel.
- Nothing has to be merged into any other repo to run the lab.

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

## Layers

Each layer answers one question. Compare it with the layer named in
*against*; everything else is held the same. The model-free layers reuse
CLEAR's own relevance verdict, so they drop exactly the signals CLEAR dropped.

| Layer | Against | The one change | Question |
|---|---|---|---|
| `clear-as-run` | | What CLEAR produced (V2, with earlier days' open events) | The baseline |
| `v2-replay` | `clear-as-run` | Today's rule replayed from an empty start | Does the replay reproduce production? It is the fair control for the other replay layers. |
| `v2-gazetteer` | `v2-replay` | A state-only signal is promoted to a district when a place it names matches exactly one district, or a named point inside one, in its state | Idea 6: how much do the cheap location fixes recover without Jev? |
| `v2-gazetteer-l1` | `v2-gazetteer` | Key on the top-level type family (conflict) instead of the middle one | Idea 6's other half: does a coarser type stop the drone-strike / attack-on-civilians split without over-merging? |
| `naive-state` | `v2-replay` | Key on (state, glide code) | Idea 7, the admin-1 key we rejected |
| `jev-v1` | `v2-replay` | Jev's choice over the state's open events | Idea 1, D-0166 as decided |
| `jev-v1-strict` / `jev-v1-loose` | `jev-v1` | Join thresholds only (winner, margin, matches-any: 0.7/0.25/0.7 and 0.35/0.05/0.3, against 0.5/0.15/0.5) | Where should the near-misses land? Sets V3's thresholds. |
| `jev-v1-country` | `jev-v1` | Candidates from the whole country: the state's events first, then other states', up to 40 | Do mislocated signals miss their event because it is never offered? |
| `embed-v1` | `jev-v1` | Cosine similarity of Voyage embeddings to the closest signal of each candidate, instead of Jev | Is Jev doing more than text similarity? |
| `embed-v1-matched` | `jev-v1` | `embed-v1` with the threshold lowered to 0.665, where its merge ratio equals `jev-v1`'s | The same question at equal merge levels, so pair precision compares like with like |

`jev-v1-7d` stays identical to `jev-v1` until multi-day replay exists.

`v2-gazetteer` uses the place names `translate.py` already lists for the viewer,
standing in for idea 6's location prompt that returns every place it finds.
The gazetteer is the day file's own location tree (districts and named points),
matched on consonant skeletons like the viewer's place colours. It is loose:
on 20 Oct about 5 of its 38 promotions were wrong, mostly foreign places
(Kufra in Libya matched a point in Bahri). Every promotion is recorded as
`promotedTo` in the layer's decisions.

`embed-v1` uses Voyage directly with `VOYAGE_API_KEY` (clear-pipeline's
`voyage-3-large`), or through OpenRouter with the Jev key otherwise
(`voyageai/voyage-4-large`; OpenRouter does not carry 3-large). The join
threshold 0.78 is about the 99th percentile of similarity between random pairs
of the day's signals; same-incident Tendalti pairs have a median of 0.73.
At 0.78 it barely merges (1.34 on 20 Oct), so `embed-v1-matched` lowers it until
the merge ratio matches `jev-v1` (2.12 against 2.13). Re-tune both with
`--sim-threshold` once judgments exist; every similarity is written to the
layer as the candidates' `p`, and embeddings are cached, so sweeps are free.

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
new-linked | no-candidates | no-district | dropped | retracted; eventId; relevance; matchesAny;
noneP; candidates[] with eventId, summary, p; linked[]; for `v2-*`, key and
promotedTo). `layers/index.json` lists the layers per day for the viewer.

**Translations** `data/<country>/<date>.translations.json`: `model`,
`promptVersion`, `createdAt`, `signals{signalId}` (lang, title, text, places[]).
`title`/`text` are null when the original is English; `places` are spelled as
they appear in the English text.

**Geo** `data/<country>/geo.json`: `areas{locationId}` (l level, c centre,
bb bbox, r outer rings simplified to ~1 km) for the country, states and
districts; `points{locationId}` ([lon, lat]) for the level-4 places signals
resolve to. Shared by every day of the country.

**Judgments** `judgments/<country>/<date>.<judge>.json`: `same[]` (lists of signal
ids that are one event), `apart[]` (pairs that are not), `campaigns[]` (name,
signalIds), `notes{}`. Signal-level, so one file scores every layer.

## Layout

| File | Role |
|---|---|
| `lab_common.py` | `.env` loading, GraphQL call, paths, location tree |
| `fetch_day.py` | dev API → day file + `clear-as-run` layer (then runs `fetch_geo.py`) |
| `fetch_geo.py` | dev API → `geo.json`: outlines and points for the viewer's maps |
| `translate.py` | day file → English translations + place names per signal (OpenRouter) |
| `replay.py` | day file → candidate layers (see [Layers](#layers)) |
| `glide_taxonomy.json` | glide code → type family (level 1 and 2), copied from clear-pipeline's `event_categories.json` for the `v2-*` layers |
| `viewer.html` | static judging UI |
| `layer-key/index.html` | served at `/layer-key`: what each layer does, its settings and the day's numbers |
| `compare.html` | short link to the viewer's *Compare layers* tab: two layers side by side, grouped by the signals either one merged, e.g. `compare.html?day=sudan/2026-10-20&layer=jev-v1` (left defaults to `clear-as-run`; `&vs=` picks another). Hidden in packs |
| `make_pack.py` | day + layers → one self-contained `packs/<country>-<date>.html` for judges |
| `score.py` | layers × judgments → metrics |
| `seed/` | the week's audit: labelled events, scored alerts, reports, old prototype UI |
| `data/ layers/ judgments/ packs/` | generated, gitignored |

## Known gaps (as of 27 Oct)

- **The window can't be tested on one day.** `replay.py` starts with no open
  events, so every candidate comes from the same day and the 72h and 7d layers
  are identical. Testing the window needs consecutive days fetched and replayed
  in sequence, seeding each day with the previous day's events. Not built yet.
- **Projected alerts are not comparable across layers.** `clear-as-run` carries
  CLEAR's event severity (Claude's estimate); replay layers only have signal
  severities, which are null for most X posts, so their alert count reads low.
- Dataminr signals arrive with an empty description and the text in the title;
  the replay and viewer use both, so nothing is lost, but summaries built from
  the title are shorter for them.
