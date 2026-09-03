# Architecture

The event file is the system of record. Everything else is a pure function of
it, computed at build time, so the browser never sees an event.

Two halves, one boundary. Python computes; TypeScript draws. Everything that
crosses is declared in `web/types/` and checked from both sides.

```
data/*.json              the log · immutable
  │
  ├─ analysis/events.py     layer 0 · screen, pickups, time attribution
  ├─ analysis/windows.py             day, night and waking windows
  ├─ analysis/metrics.py    layer 1 · daily_frame(), weekly_frame()
  ├─ analysis/score.py      layer 2 · the 0 to 100 index
  └─ analysis/intelligence/ layer 3 · signals, alerts, nudge, positives, replay
       │
       ├─ analysis/run.py   adapter · the command line
       └─ payload/            adapter · the frames as one typed JSON document
            │
            ▼
       docs/data.json      ─── the boundary. No HTML, no figures, no copy ───
            │
            ▼
       web/                the page: types, charts, acts, copy, interaction
            │
            └─ build.py  →  docs/  →  GitHub Pages
```

Want to change something? The section it belongs to is one file:

| To change | Open |
|---|---|
| What a section says, or the charts it mounts | `web/acts/aNN-*.ts` |
| The line under a chart | `web/copy/explain.ts` |
| How a chart is drawn | `web/charts/` |
| The palette, or which ground an act sits on | `web/theme.ts`, `web/charts/index.ts` |
| What a slider does | `web/sliders.ts` |
| What crosses from Python | `web/types/`, then `payload/` |
| A metric, a threshold, a rule | `analysis/` |
| Spacing, type, colour tokens | `web/styles/` |

No module is longer than 350 lines; where a concern outgrew that it became a
package or a folder whose index re-exports the same names, so no caller
changed.

Nothing in `analysis/` imports plotly or knows the page exists, and nothing in
`payload/` builds a figure or writes markup. The command line and the page are
two readers of the same core.

## Invariants

| Invariant | Where it holds | If it breaks |
|---|---|---|
| The screen is the union of its stretches | `events.py`, depth counter | screen time moves ±13 % |
| A day cuts at midnight, a night at 23:00 | `metrics.py` | one night lands in two rows |
| First unlock is the first from 06:00 | `metrics.py` | night tails read as mornings |
| Truncated days leave every view | `metrics.py`, `daily_frame` | totals stop matching |
| Browser time belongs to the domain | `events.py` | Chrome tops every ranking |
| At most 2 alerts per 30 days | `intelligence.py`, `_decide` | the channel burns out |
| No app or domain reaches a notification | `intelligence.py`, `payload/` | the privacy line is gone |
| Numbers come from the frames, never from copy | `web/`, `test_copy.py` | a copy edit moves a figure |
| Nothing but data crosses the boundary | `payload/`, `test_emit.py` | Python starts rendering again |

## From event to metric

| Metric | How it is derived |
|---|---|
| Screen time | Union of on-to-off intervals, split at midnight |
| Real pickup | A screen-on with an unlock before the next one |
| Glance | A screen-on with no unlock |
| Time per app | Foreground to the next change or screen off, capped at 45 min |
| Time per domain | The same, with the time moved off the browser |
| Night band | 23:00 to 06:00 the next morning |
| Longest break | Longest screen-free gap between 07:00 and 23:00 |
| App switch | A move between two different apps, reset daily |
| Distraction share | Social, entertainment and gaming over attributed time |
| Your normal | Rolling median of this user's last 14 days |

## How to make the likely changes

**Add a daily metric.** Compute it per day in `daily_frame()`, aggregate it in
`weekly_frame()` if it belongs in the weekly panel, name it in
`payload/profile.py`'s column list, and declare it in `web/types/series.ts`. The
type check fails until both sides agree, which is the point.

**Add an alert rule.** Write `_your_rule(df) -> list[Signal]` in
`intelligence/alerts.py`, put its thresholds in `intelligence/signals.py`, and
register it in `RULES`. The silence budget in
`_decide` applies to it automatically; give it an honest `actionability` or it
will crowd out something that deserves the slot.

**Add a reinforcement.** Same shape, in `intelligence/positives.py`. One a week reaches
the user at most.

**Change the index weights.** `COMPONENTS` in `score.py`. The weights must sum
to 1; `tests/test_score.py` asserts it, and `tests/test_data_contract.py`
asserts the published figures, so a weight change will show up as a failing
number rather than a silent drift.

**Add an act to the page.** Write `web/acts/aNN-name.ts` exporting an `Act`
with its own `copy` object and a `build(ctx)`, add it to `ACTS` in
`web/acts/index.ts`, and add a `<section>` with its `<!--act:NN-->` marker to
`web/index.html`. Its words live in that file: one section, one place. Acts
in part 2 are rebuilt when the reader switches profile.

**Add a figure.** A builder in the right family under `web/charts/`, a case in
`build()` in `web/charts/index.ts`, a line in `web/copy/explain.ts`, and a
`chart("key", explain("key"))` mount in the act. A figure with no line does not
build. If it needs a series the document does not carry, add that first: the
column list in `payload/profile.py` and the type in `web/types/`.

## Known limits

The night band is fixed at 23:00 to 06:00 for everyone, which is wrong for a
shift worker. The baseline is a 14-day median, so the first fortnight of any
file has nothing to compare against. Both profiles are one month; nothing here
has seen a second month, a holiday, or a device change.
