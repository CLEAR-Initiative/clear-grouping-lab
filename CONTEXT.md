# Language of the grouping lab

The lab inherits CLEAR's language from the Exponential page "How CLEAR groups
signals into events" (cmvqya771000hkx086k80ga6l). Terms below are either
restated from there or specific to the lab. "Incident" is not a term here.

## Language

### From CLEAR

- **Signal**: one raw piece of input, unaltered: an X post, a Dataminr alert, an ACLED row.
- **Event**: one real-world occurrence, built from one or more signals. The unit of truth (D-156).
- **Clustering** (also grouping): deciding which signals belong to the same event.
- **Alert**: a published advisory raised on an event.
- **Campaign**: an event that is the parent of other events (one actor, one target class, many places). Membership is a parent link, not a merge.
- **Merge ratio**: signals divided by events. 1.0 means nothing merged.
- **Jev**: the classifier called through OpenRouter; typed answers with calibrated probabilities.

### Lab-specific

- **Day**: the fetched set of every signal and event for one country on one calendar date (UTC), as the dev API holds them.
- **Layer**: one clustering of a day's signals into events, produced by one algorithm with one set of parameters. `clear-as-run` is the layer CLEAR itself produced; every other layer is a candidate.
- **Candidate**: an open event offered to the algorithm as a possible home for a signal.
- **Judgment**: a human's statement that two signals belong to the same event (a merge) or do not (a pull-out), recorded once per day and reused to score every layer.
