# Balance

A device event log, read end to end: what the phone recorded, what it computed,
and what it said out loud. One scrolling page, twelve acts, two profiles.

**Live:** <https://frankllonch.github.io/scrolldowndashboard-balance/>

## Run it

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dev]"
npm install
.venv/bin/python build.py         # writes dist/, type-checking on the way
.venv/bin/python -m pytest        # 169 tests, several of which read dist/
.venv/bin/python -m http.server -d dist 8000
```

`python -m analysis.run --user B --format json` prints the same analysis without
the page.

## Where to look

| Path | What is in it |
|---|---|
| `data/` | the event logs · the only input |
| `analysis/` | events → metrics → the index → the rules. Draws nothing |
| `payload/` | the frames as one typed JSON document · the whole boundary |
| `web/types/` | what crosses that boundary, declared |
| `web/acts/` | one file per section, holding its markup and its words |
| `web/charts/` | every figure, built in the browser |
| `web/interaction/` | sliders, the profile switch, the travelling surface |
| `dist/` | the built site. Output, and gitignored — edit `web/`, not this |

Python computes; TypeScript draws. Nothing crossing between them is HTML, a
figure or a word — `tests/test_payload.py` asserts it, and `npm run typecheck`
compiles the emitted document against `web/types/`, so a field one side renames
fails the build rather than a chart. And
`test_intelligence.py::test_notifications_contain_no_apps_or_domains` is the
privacy contract: a notification says what changed, never what you were on.

## Also here

[`ARCHITECTURE.md`](ARCHITECTURE.md) for the layers and how to change them ·
[`DECISIONS.md`](DECISIONS.md) for why things are the way they are ·
[`INPUT_FORMAT.md`](INPUT_FORMAT.md) for the shape of the input files.

## Findings

- **User B's wellbeing index falls 60 → 40 while their screen time moves
  +8 %.** The drop is almost entirely the night component.
- **Late-night screen multiplies by 13** between week 1 and week 4, and the
  sleep window closes by **95 minutes a night**: bedtime slides, the alarm does
  not.
- **`screen_jump` fires on neither profile.** A cap on screen time, the obvious
  rule, would have missed this month completely. Catching it means watching the
  schedule.
