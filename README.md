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
- The search box filters by text or place name, and selections survive a
  search. That's the quickest way to find every post about one town.
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
3. **Judge it yourself** in the viewer. Start the server, then open
   <http://localhost:8765/viewer.html?day=sudan/2026-10-20>.
   ```bash
   python3 -m http.server 8765
   ```
4. **Send it to judges.** Build a pack: one HTML file with the day built in.
   It writes `packs/sudan-2026-10-20.html` (gitignored, about 2–4 MB). Email it
   with the [Judging](#judging-no-install-needed) section pasted in. Leave out
   layers that would only confuse judges; `jev-v1-7d` is identical to `jev-v1`
   until the window gap below is fixed.
   ```bash
   python3 make_pack.py --country sudan --date 2026-10-20 --layers clear-as-run,jev-v1,naive-state --send-to "James"
   ```
5. **Collect answers.** Save each returned `2026-10-20.<name>.json` into
   `judgments/sudan/`. To check a judge's answers in the viewer, use
   **Import file** on tab 3.
6. **Score** every layer against every judgment file for the day.
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
