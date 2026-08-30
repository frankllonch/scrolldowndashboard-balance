# Balance

A device event log, read end to end: what the phone recorded, what it computed,
and what it said out loud. One scrolling page, twelve acts, two profiles.

**Live:** <https://frankllonch.github.io/scrolldowndashboard-balance/>

## Run it

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/python -m pytest        # 122 tests
.venv/bin/python build.py         # writes docs/
.venv/bin/python -m http.server -d docs 8000
```

`python -m balance.run --user B --format json` prints the same analysis without
the page.

## Where to look

| Path | What is in it |
|---|---|
| `balance/events.py` | screen reconstruction, pickups, time attribution |
| `balance/metrics.py` | the daily and weekly frames |
| `balance/score.py` | the 0 to 100 index, five weighted components |
| `balance/intelligence/` | alerts, the silence budget, nudges, reinforcements |
| `render/acts/` | one module per act of the page |
| `render/payload.py` | everything the browser gets, resolved at build time |
| `copytext/strings/` | every user-visible string |
| `site/` | `index.html`, `css/`, `app.js`, hand-written, no build step |

`tests/test_intelligence.py::test_the_guardian_payload_contains_no_apps_or_domains`
and `tests/test_payload.py::test_payload_guardian_section_has_no_app_domain_or_category`
are the privacy contract. Nothing about an app, a domain or a category reaches a
guardian.

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
