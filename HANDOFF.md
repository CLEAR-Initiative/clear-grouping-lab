# clear-grouping-lab — handoff from the 27 Oct 2026 session

Private lab for testing how CLEAR groups signals into events. Code is in the private repo CLEAR-Initiative/clear-grouping-lab (added 27 Oct); never push to the public clear-* repos, and never commit data/, layers/, judgments/ or .env.

## Why this exists (one paragraph)

Andi gets 20–30 alert emails a day; the true dev figure is ~41/day for Sudan. 92% come from BetaMinr X posts (`sudan-war-x`). Root cause is grouping: CLEAR keys events on exact (admin-2 district, level-2 GLIDE type); 81% of X-sourced events only resolve to state/country so grouping never tries, and the per-post type label splits the rest. Week of 20–27 Oct: 771 Sudan events for 927 signals (merge ratio 1.2), 92% single-signal, ~39% restating an earlier event. Decision D-0166 (PROPOSED in Exponential) says: identity by semantic candidate matching (Jev), alert on change not on row creation, roundups to evidence. This lab is where candidate algorithms get tested against human judgments before anything ships.

## Where the context lives

- Exponential page (plain-language explainer, current method, problems, ideas, plan): https://www.exponential.im/w/clear/pages/cmvqya771000hkx086k80ga6l
- Exponential page (formal design decision): https://www.exponential.im/w/clear/pages/cmvqtqvor0007l8087upv524p
- Decision Log: D-0166 (PROPOSED). Accepted D-154/155/156 (22 Oct) define signal/evidence/event.
- Tickets: #1046 alert digest (ship anyway), #646 severity rules, #711 Jev classifier (QA), #144 INFORM severity.
- Code to read first: `clear-pipeline/src/clear_pipeline/providers/event.py` (`group_signal`, the (admin2, level_2) key, 14-day active-event cache), `providers/location.py` (`locate_in_country`: one Claude call picks a state/district from Arabic text; on branch `origin/dev`, not on local feature branches), `providers/jev.py` (`classify_with_jev`: Choice over GLIDE codes + Noul relevance via OpenRouter Decisions API; copy its request shape), `defs/signals/stages.py` (`_group`, `_locate_if_unplaced` on dev), `clear-api/src/routes/x-ingest.ts`, `clear-api/src/resolvers/event.resolver.ts` (`eventsPendingAlert`: severity ≥4, 48h).
- Worked example to keep in mind: Tendalti power station, 20 Oct. Three X posts all containing تندلتي became three events: two at district Tendalti but with different type families (`va` vs `rs`), one at state White Nile because the post's header line said "White Nile". The `rs` event then collected 15 signals (Dataminr/ACLED had coordinates); 8 more X posts about the same strike became isolated White Nile events.

## Seed data in `seed/`

- `sudan-events-2026-10-20-to-27.labelled.psv` — all 771 Sudan events, one per line: `day|time|src|sev|types|signalCount|location|locLevel|kind|short title`. `kind` and `(dup)` markers are Claude's single-reviewer labels: inc/sit/camp/rep/mil/noise. Treat as an estimate, not ground truth.
- `sudan-alerts-2026-10-20-to-27.scored.psv` — the 325 alerts scored on relevance/impact/specificity/novelty.
- Two markdown reports with the tables and method.
- `prototype-review-page.html` — the first review UI (cards cut by Claude's keyword rules: superseded; keep only for the UI pattern: tabs, per-row checkboxes, export JSON, localStorage keyed by stable names).

No per-day raw data is saved: the 20 Oct events+signals were fetched over MCP in the old session and must be re-fetched by `fetch_day.py`. Event/signal ids are cuids from dev-api.clearinitiative.io. Sudan location id `3c7edcfb-85f1-46e4-8a7b-29651f73d740`; Tendalti `9496158a-dbc0-4935-b383-254c620cf800` (level 2, parent White Nile `c11121c4-444d-47d3-b2f3-1d6be4898324`).

## What to build (agreed with James)

1. `fetch_day.py --country sudan --date 2026-10-20` → `data/sudan/2026-10-20.json`: every signal (id, source, publishedAt, original text, resolved location + level) and every event (id, types, severity, location, signal ids, title/description) for that day, via the dev GraphQL API with keys from a local `.env` (copy `CLEAR_API_BASE`/`CLEAR_API_KEY` and `OPENROUTER_API_KEY` from clear-pipeline's env; never commit).
2. Layer contract: `layers/<day>.<algo>.json` = `{algo, params, groups: [{id, title, signalIds[], candidates?: [{eventId, p}]}]}`. `clear-as-run` is derived from the fetch. `jev-v1` comes from `replay.py`: per signal, candidate open events for its state (fallback whole country) in the prior 72h, one Jev Decisions call with a Choice over candidates + "none", Noul "is this an incident report", absolute threshold + margin rule, record candidate probabilities.
3. `viewer.html`: static, loads a day + layers, dropdown to switch layer, cards = groups in time order with original signal text, actions: "pull this signal out", "merge these cards", export `judgments/<day>.<name>.json`. No pre-judgment from Claude on the page.
4. `score.py --day --layer`: merge ratio, pair precision/recall vs judgments, per-cluster hits. Baseline to beat: merge ratio 1.2, ~41 alerts/day.

Agreed constraints: local only, read-only against dev, no merges into any repo required to run, data never leaves this directory.

## Open items for the new session to grill

- Candidate window: 72h vs 7 days (X posts resurface 3–7-day-old incidents).
- Compare signal text to event rewritten title/description vs to all signals.
- How to score campaigns (one actor, one target class, many districts) — separate judgment or part of the same?
- Whether per-type identity criteria go into the Jev prompt in v1 or v2.
