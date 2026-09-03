# Architecture

The event file is the system of record. Everything else is a pure function of
it, computed at build time, so the browser never sees an event.

```
data/*.json              the log · immutable
  │
  ├─ balance/events.py     layer 0 · screen, pickups, time attribution
  ├─ balance/windows.py             day, night and waking windows
  ├─ balance/metrics.py    layer 1 · daily_frame(), weekly_frame()
  ├─ balance/score.py      layer 2 · the 0 to 100 index
  └─ balance/intelligence/ layer 3 · signals, alerts, nudge, positives, replay
       │
       ├─ balance/run.py   adapter · CLI
       └─ render/          adapter · figures/, acts/, payload, states, summary
            │
            └─ build.py  →  docs/  →  GitHub Pages
```

No module is longer than 350 lines; where a concern outgrew that it became a
package whose `__init__.py` re-exports the same names, so no caller changed.

No layer imports plotly, and none of them imports `render/`. The CLI and the
page are two readers of the same core.

## Invariants

| Invariant | Where it holds | If it breaks |
|---|---|---|
| The screen is the union of its stretches | `events.py`, depth counter | screen time moves ±13 % |
| A day cuts at midnight, a night at 23:00 | `metrics.py` | one night lands in two rows |
| First unlock is the first from 06:00 | `metrics.py` | night tails read as mornings |
| Truncated days leave every view | `metrics.py`, `daily_frame` | totals stop matching |
| Browser time belongs to the domain | `events.py` | Chrome tops every ranking |
| At most 2 alerts per 30 days | `intelligence.py`, `_decide` | the channel burns out |
| No app or domain reaches a notification | `intelligence.py`, payload | the privacy line is gone |
| Numbers come from the frames, never from copy | `copytext/`, `render/` | a copy edit moves a figure |

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
`weekly_frame()` if it belongs in the weekly panel, and add its label to
`copytext/en.py`. Nothing else knows the column exists.

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

**Add an act to the page.** Write `render/acts/aNN_name.py` with a
`build(ctx) -> str`, register it in `render/acts/__init__.py`, add a
`<section>` and its `<!--act:NN-->` marker to `site/index.html`, and put its
strings in the right part of `copytext/strings/`. Acts in part 2 render once
per profile.

**Add a figure.** A builder in the right family under `render/figures/`,
exported from its `__init__.py`, a key in `render/payload.py`, and a
`html.chart("key")` mount in the act. Selection-dependent figures ship once and
are re-pointed in the browser unless their data actually changes.

## Known limits

The night band is fixed at 23:00 to 06:00 for everyone, which is wrong for a
shift worker. The baseline is a 14-day median, so the first fortnight of any
file has nothing to compare against. Both profiles are one month; nothing here
has seen a second month, a holiday, or a device change.
