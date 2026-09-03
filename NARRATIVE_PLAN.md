# Narrative rewrite — done, and what is left

Steps 1–12 are complete. This file now records what was decided, so the reasoning
survives the commits.

## Settled

- **Person B is an adult.** r(usage, blocks) = 0.954, and every "leak" app was blocked
  on all 30 days, a median of 14 times a day. They opened only inside one ~22-hour
  window on 18 May when the filter stopped firing. Both profile sketches rewritten.
- **No guardian.** The product notifies the person holding the phone and nobody else.
  Alerts land on the user's own screen; the weekly digest stays on the device.
- **Every chart carries a line** explaining what it shows, resolved in `html.chart()`
  from the figure key, so a new chart cannot ship without one.
- **The wellbeing score is explained where the reader meets it**, including the two
  questions the names invite: fragmentation counts unlocks, not apps; distraction is
  a share of time by category, not a count of apps.
- **Weeks read Monday to Sunday.** A week is still the Nth block of seven days — the
  log opens on a Friday — but the bars are sorted by weekday.
- **Each act hands off to the next** (`act.NN.next`), appended to the act body so the
  bridge survives a profile switch.
- **The pill wears each person's colour**, with a darker step of the same hue on the
  pale card where the chart hues fall under 3:1.

## Still open

1. **Which part of the code is hard to navigate?** ("costa navegar codi") Needed before
   any restructuring — nothing has been done here.
2. **Reading time.** The page is now ~2,760 words, about 14 minutes. The prose budget
   in `tests/test_prose.py` is 2,800 and is nearly spent. Adding more explanation means
   either cutting elsewhere or deciding the page is a report, not a scroll.

## Constraint

`docs/` is build output. `build.py` regenerates it from `site/` and `render/`, so hand
edits to `docs/style.css`, `docs/app.js` or `docs/index.html` are lost. Edit `site/`.
