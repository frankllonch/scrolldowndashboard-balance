# Architecture

The event log is the system of record. Everything else is a pure, deterministic
function of it, computed at build time, so the browser never sees an event.

Two halves and one boundary. **Python computes. TypeScript draws.** Nothing that
crosses between them is HTML, a figure or a word — it is numbers, and its shape
is declared once in `web/types/` and checked from both sides.

## Where everything is

```
data/*.json                    the log · immutable · the only input
  │
  ▼
analysis/                      ── computes. Draws nothing. Knows no page. ──
  events.py       336   layer 0 · screen stretches, real unlocks, time attribution
  windows.py       92             what counts as a day, a night, waking hours
  taxonomy.py      50             what the stream calls OTHER, and what it is
  metrics.py      302   layer 1 · one row per day, one per week
  score.py         77   layer 2 · the 0 to 100 index · five weighted components
  intelligence/         layer 3 · what to say, when to stay quiet
    signals.py     94             thresholds, and the two records passed around
    alerts.py     230             the three rules, and the budget that silences
    positives.py  179             reinforcements: what to say when nothing is wrong
    nudge.py       78             the on-device night nudge, replayed
    replay.py      96             the state at the close of each day
  pipeline.py     100   every layer in order over one log · wired once
  run.py          242   adapter · the same engine on the command line
  │
  ▼
payload/                       ── packages it. Formats nothing. ──
  profile.py      254   one analysis, laid out flat
  scalars.py       92   pandas and core objects into JSON-safe values
  __init__.py      58   the document, and the finding it adds up to
  │
  ▼
  │
  ▼
web/                           ── draws it. Owns every word. ──
  index.html            the shell: twelve empty sections and two script tags
  main.ts          48   boot · load, draw, bind
  document.ts      32   fetching the document, and reaching one profile in it
  theme.ts        140   palette and three surfaces: paper, dusk, near-black
  format.ts       126   wording a number: clocks, durations, dates, percentages
  html.ts         160   the markup builders every act is made of
  page.ts          67   composing the twelve sections, and the rail
  types/                ═══ the contract ═══
    primitives.ts  36     days, categories, decisions · the vocabulary
    series.ts     150     one row per day, per week, per app, per cell
    signals.ts     77     what the phone worked out and what it emitted
    index.ts      151     the summaries, and the document itself
    contract.ts    34     compiles the emitted file against all of the above
  charts/               ═══ every figure ═══
    plotly.ts     185     the slice of Plotly this project uses, typed by hand
    frame.ts       73     the layout every figure starts from
    series.ts     186     one line or one bar per day
    score.ts      207     the index: the curve, the breakdown, the weekly panels
    composition.ts 169    where the time and the blocks went
    walkthrough.ts 151    the month on one axis, with the event rail under it
    index.ts      166     figure key → builder → which ground it sits on
  acts/                 ═══ one file per section of the page ═══
    act.ts         53     what an act is, and what it is handed
    a01-cover.ts   58     what Balance is, and why to read on
    a02-two-people 133    both profiles, and what the index actually is
    a03-choose.ts  63     the fork: a real choice, full screen
    a04-the-week  272     five weeks on a slider
    a05-a-day     160     one month of days, on one screen
    a06-the-night 112     the 23:00 to 06:00 band
    a07-where-... 189     apps, domains, categories
    a08-what-...  152     what the filter stopped
    a09-what-said 264     the alert and nudge engine, day by day
    a10-the-...    60     the finding
    a11-the-...    90     what a screen-time rule would have missed
    a12-under-... 194     schema, derivations, the pipeline itself
  copy/                 ═══ the words that are not about one section ═══
    explain.ts    123     the line under every chart, by figure key
    figures.ts    148     titles, axes, series names, hover templates
    units.ts       29     units, and the phrases standing in for absent values
  interaction/          ═══ what the page does once it is on screen ═══
    dom.ts         41     every selector the page depends on, in one file
    plots.ts       44     build a figure and draw it into its mount
    reader.ts     121     the travelling surface, the rail, resize, scroll
    sliders.ts    166     the week and the day, continuous thumbs, discrete data
    switch.ts      81     changing profile without losing the reader's place
  styles/        1434   ten stylesheets, concatenated into one at build time
  vendor/               plotly, cartesian build only, committed not fetched
  tools/prerender.ts    writes every section into the page at build time
  │
  ▼
build.py          101   python -m payload · typecheck · prerender · bundle
  │
  ▼
dist/                          ── the built site · five files, one request each ──
  index.html      39 KB  ← web/index.html + every act, prerendered by node
  data.json      163 KB  ← python -m payload · fetched, not bundled, so it caches
  app.js          75 KB  ← web/main.ts and everything it imports, bundled
  style.css       28 KB  ← web/styles/*.css, concatenated in filename order
  vendor/       1450 KB  ← web/vendor/, copied
```

`dist/` is build output and is not in the repository: the workflow in
`.github/workflows/` builds it on every push and publishes that. Nothing here
is edited by hand — a change made in `dist/` is gone at the next build. It is
also gitignored, so an editor's search will not look in it: search `web/`
instead, where every sentence on the page is written. The arrows say which
file produces which.

The page needs four of the five. `data.json` is fetched rather than bundled so
the browser caches it apart from the code, and `index.html` already contains
every section, so the page reads with JavaScript switched off — what `app.js`
adds is the plots and the interaction.

## To change something, open one file

| To change | Open |
|---|---|
| What a section says, or which charts it mounts | `web/acts/aNN-*.ts` |
| The line under a chart | `web/copy/explain.ts` |
| How a chart is drawn | `web/charts/` |
| The palette, or which ground an act sits on | `web/theme.ts`, `web/charts/index.ts` |
| What a slider does | `web/interaction/sliders.ts` |
| Spacing, type, colour tokens | `web/styles/` |
| A metric, a threshold, a rule | `analysis/` |
| The order the layers run in | `analysis/pipeline.py` |
| What crosses the boundary | `web/types/`, then `payload/profile.py` |

## Invariants

| Invariant | Where it holds | If it breaks |
|---|---|---|
| The screen is the union of its stretches | `events.py`, depth counter | screen time moves ±13 % |
| A day cuts at midnight, a night at 23:00 | `metrics.py` | one night lands in two rows |
| First unlock is the first from 06:00 | `metrics.py` | night tails read as mornings |
| Truncated days leave every view | `metrics.py`, `daily_frame` | totals stop matching |
| Browser time belongs to the domain | `events.py` | Chrome tops every ranking |
| At most 2 alerts per 30 days | `alerts.py`, `_decide` | the channel burns out |
| No app or domain reaches a notification | `intelligence/`, `payload/` | the privacy line is gone |
| Numbers come from the frames, never from copy | `web/`, `test_copy.py` | a copy edit moves a figure |
| Nothing but data crosses the boundary | `payload/`, `test_payload.py` | Python starts rendering again |
| No file over 350 lines | `test_structure.py` | a file starts doing two things |

## How to make the likely changes

**Add a daily metric.** Compute it per day in `daily_frame()`, aggregate it in
`weekly_frame()` if it belongs in the weekly panel, name it in
`payload/profile.py`'s column list, and declare it in `web/types/series.ts`.
The type check fails until both sides agree, which is the point.

**Add an alert rule.** Write `_your_rule(df) -> list[Signal]` in
`intelligence/alerts.py`, put its thresholds in `intelligence/signals.py`, and
register it in `RULES`. The silence budget applies to it automatically; give it
an honest `actionability` or it will crowd out something that deserves the slot.

**Add a reinforcement.** Same shape, in `intelligence/positives.py`. One a week
reaches the reader at most.

**Change the index weights.** `COMPONENTS` in `score.py`, and the mirror of it
in `web/charts/score.ts`. The weights must sum to 1; `tests/test_score.py`
asserts it and `tests/test_data_contract.py` asserts the published figures, so a
weight change shows up as a failing number rather than a silent drift.

**Add an act.** Write `web/acts/aNN-name.ts` exporting an `Act` with its own
`copy` object and a `build(ctx)`, add it to `ACTS` in `web/acts/index.ts`, and
add a `<section>` with its `<!--act:NN-->` marker to `web/index.html`. Its words
live in that file: one section, one place.

**Add a figure.** A builder in the right family under `web/charts/`, a case in
`build()` in `web/charts/index.ts`, a line in `web/copy/explain.ts`, and a
`chart("key", explain("key"))` mount in the act. A figure with no line does not
build. If it needs a series the document does not carry, add that first.

## Known limits

The night band is fixed at 23:00 to 06:00 for everyone, which is wrong for a
shift worker. The baseline is a 14-day median, so the first fortnight of any
file has nothing to compare against. Both profiles are one month; nothing here
has seen a second month, a holiday, or a device change.
