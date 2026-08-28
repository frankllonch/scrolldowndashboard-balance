# Rebuild prompt · Balance take-home

Turn a working but badly packaged Streamlit dashboard into a **single guided
scroll page**: static, fast, and readable end to end in 10 to 15 minutes.

Two jobs, equally important:
1. **Replace the delivery surface.** Streamlit goes. The output is a static site.
2. **Cut the slop.** The analysis is good; the packaging is bloated and
   over-written. Most of what you delete will be prose.

Read this whole document first. It is the specification.

---

## 0 · Setup

Source repo, public and working:
**https://github.com/frankllonch/balance-takehome**

```bash
git clone https://github.com/frankllonch/balance-takehome balance-scroll
cd balance-scroll && rm -rf .git && git init
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dashboard,dev]"
.venv/bin/python -m pytest          # 95 passed. Baseline. Do not break this.
.venv/bin/streamlit run app.py      # look at the current thing before deleting it
```

---

## 1 · What exists

A pipeline turning a device event log into metrics, a wellbeing index, guardian
alerts and user reinforcements, over two synthetic profiles: **A** (adult, 30
days, healthy) and **B** (minor with a guardian, night schedule drifting).

```
data/*.json              event log · immutable source of truth
balance/events.py        layer 0 · screen reconstruction, pickups, time attribution
balance/metrics.py       layer 1 · daily_frame(), weekly_frame()
balance/score.py         layer 2 · 0-100 index, five weighted components
balance/intelligence.py  layer 3 · alerts with a silence budget, reinforcements,
                                   night nudge, month_replay()
balance/run.py           CLI
balance/charts.py        18 plotly figure builders
balance/theme.py         dark theme, plotly template, phone mockup CSS
app.py                   Streamlit dashboard · 1,266 lines · being replaced
tests/                   95 tests
```

**Keep untouched:** `balance/events.py`, `metrics.py`, `score.py`,
`intelligence.py`, `run.py`. Pure, framework-free, tested. Add a function only
if a view needs a derivation that does not exist.

The 95 tests keep passing. Several assert published figures on purpose: if a
number moves, you broke something.
`test_the_guardian_payload_contains_no_apps_or_domains` is the most important
test in the repo.

**Replace:** `app.py` and the whole Streamlit layer.

---

## 2 · Stack

**Python builds a payload. A hand-written static page renders it.**

```
balance/          unchanged Python core
build.py          runs the pipeline, writes docs/
site/             index.html, style.css, app.js
docs/             build output · what GitHub Pages serves
  payload.json    ~200 KB: figures + per-day and per-week states + copy
  vendor/plotly.min.js
```

Measured: 18 plotly figures ≈ **113 KB** of JSON, daily frames ≈ **46 KB**. Under
200 KB total. The 2.4 MB of raw events never reach the browser; Python resolves
them at build time.

### Charts: do not re-author them

The 18 builders in `balance/charts.py` are validated and good. Export them:

```python
payload["figures"]["night_drift"] = json.loads(fig.to_json())
```

```js
Plotly.newPlot(el, f.data, f.layout, {displayModeBar: false, responsive: true});
```

Hover, legend toggling and zoom keep working.

### Frontend: vanilla, no framework, no npm

One `index.html`, one `style.css`, one `app.js` under ~300 lines. A reviewer can
read the entire frontend. The only build step is `python build.py`.

---

## 3 · The scroll

Three parts. The reader meets both profiles, lives inside one of them, then gets
the analysis. This is the Spotify Wrapped shape: **your data first, the verdict
after.**

### Part 1 · Setup (everyone sees this)

| # | Act | Content | Figures |
|---|---|---|---|
| 01 | **Cover** | Title, one line, dataset in three numbers, scroll cue | — |
| 02 | **Two people, one phone** | The current Overview: both profiles side by side, both index heroes, the score curves. B's line visibly sagging. **Plant the hook here without explaining it**: one line noting that B's index falls 60 → 41 while their screen time barely moves. Do not resolve it | `score_line` |
| 03 | **Choose a profile** | Full-screen fork. Two large cards, A and B, each with three numbers and a one-line character sketch. Clicking one loads their journey and scrolls to act 04 | — |

Act 02 does the cold open. The reader leaves it knowing something is off with B
and not knowing what. That is what carries them through the personal journey to
the reveal in act 11.

### Part 2 · One person's month (per profile, sticky switcher from here on)

The tabs that exist today, resequenced as a lived month. All of Part 2 re-renders
when the profile switches; scroll position holds.

| # | Act | Content | Figures | Interaction |
|---|---|---|---|---|
| 04 | **The week** | Weekly summary. KPI row with week-on-week deltas, the four weekly evolution charts, index components by week, that week's days | `week_evolution` ×4, `week_components`, `week_days` ×2 | **Week slider.** First interaction of the page. Five weeks, short weeks flagged |
| 05 | **A day in the life** | Daily rhythm: KPI strip, bars against personal baseline, weekly clock heatmap, day span | `daily_bars_vs_baseline` ×2, `hour_heat`, `day_span` | Passive |
| 06 | **The night** | Night band. Bedtime later, wake time flat, sleep window shrinking. **Theme shift, see below** | `night_drift`, `day_span`, `compare_line` | Passive |
| 07 | **Where the time goes** | Apps, domains, categories over the month | `top_bars` ×2, `category_area` | Passive |
| 08 | **What the phone stopped** | Blocks by day, by hour, by week. The privacy scope note | `blocks_daily`, `blocks_by_hour` | Passive |
| 09 | **What the phone said** | The alert and nudge engine. The multi-series chart with the day slider, the three output cards for the selected day (user screen, guardian phone, stored on device), then the full list of everything emitted in the month | `tracked_series` | **Day slider**, 30 days. Plus plotly legend toggling |

Act 09 is the payoff of Part 2 and holds the phone mockups. Keep its behaviour
exactly as it works today, including per-item legend toggling with
`groupclick: "toggleitem"`.

### Part 3 · The analysis (both profiles)

| # | Act | Content | Figures |
|---|---|---|---|
| 10 | **The other one** | A prompt to switch profile and re-read Part 2. One button, which switches and scrolls back to act 04. If both have been seen, this act collapses to a single line and lets the reader through | — |
| 11 | **The finding** | The reveal. One huge number (`×13`), the sleep window shrinking by 95 min a night, the night chart for both profiles together. This resolves the hook from act 02 | `night_drift` (both profiles) |
| 12 | **What a screen-time rule would have missed** | The negative control. Week 1 vs week 4 for B: screen time +8 %, night ×13. `screen_jump` implemented and firing on neither profile | `compare_line` ×2 |
| 13 | **Under the hood** | Schema, stream anomalies, derivations, attribution coverage, index components and weights. All inside `<details>`, closed by default | `score_breakdown` ×2 |

### The profile switch

- Act 03 is a real choice, full screen, not a dropdown.
- From act 04 onwards a **sticky pill** in the top right shows the current
  profile and switches on click.
- Switching re-renders Parts 2 and keeps the reader where they are.
- Act 10 exists so picking one profile is never a dead end.
- Deep link: `?profile=B` selects a profile and skips act 03. Useful for sharing
  a specific reading.

### The night: theme shift

Act 06 is the only act that changes the surface. The site is already near-black;
the shift has to be a mood change, not a brightness change.

| Token | Site | Act 06 |
|---|---|---|
| Background | `#0a0a0b` | `#000000`, plus a soft radial vignette |
| Ink | `#f1eee8` | `#e8dfd0`, warmer |
| Accent | `#e8e4da` bone | `#fab219` amber |
| Chart grid | `#1c1c21` | `#141410`, dimmer |

Transition it on scroll entry over ~600 ms, and back out on exit. It must be
subtle: the reader should notice the room got darker, not that a button was
pressed. Test it with `prefers-reduced-motion: reduce`, where it should apply
instantly rather than transition.

### Navigation

- Thin **scroll progress bar** pinned to the top.
- **Fixed left rail** listing the 13 acts in uppercase mono, current one in ink,
  the rest muted. Grouped visually into the three parts. Hidden below 900 px.
- Sticky profile pill from act 04.
- Nothing else. No hamburger, no footer nav.

### Motion

Editorial restraint, not a parallax showreel.

| Element | Motion |
|---|---|
| Act enters viewport | opacity `.001` → 1, `translateY(16px)` → 0, 420 ms ease-out |
| Hero numbers (acts 02, 11) | same, delayed 120 ms behind their label |
| KPI cards | staggered, 60 ms apart |
| Charts | reveal only. Never animate the data |
| Rail item | muted → ink as its act becomes current |
| Act 06 | surface tokens transition, 600 ms |

**The constraint most likely to be got wrong:**

> Animation must never be what makes content visible. Default state is visible.
> Animation is an enhancement on top. With scroll-driven animations unsupported,
> the page must look like a complete static page.

Guard every animated rule twice:

```css
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .act { animation: reveal linear both;
           animation-timeline: view();
           animation-range: entry 0% entry 40%; }
  }
}
@keyframes reveal {
  from { opacity: .001; transform: translateY(16px); }
  to   { opacity: 1; transform: none; }
}
```

`opacity: .001` rather than `0`: if anything goes wrong the content is still
painted. `animation-timeline: view()` is unsupported in Firefox without a flag,
which is why the fallback is not optional.

---

## 4 · Cut the slop

Half the job. The prose is the main reason a reviewer bounces. Be aggressive.

| Surface | Now | Target |
|---|---|---|
| Words of prose in the UI | ~4,284 (21 min read) | **≤ 1,200** |
| `README.md` | 449 lines | **≤ 60 lines** |
| Full scroll at reading pace | n/a | **≤ 5 minutes** |
| Everything: README, one profile, both sliders | n/a | **≤ 15 minutes** |

### What slop looks like here

The current repo does all of these. Not hypothetical.

- **Docstrings that argue instead of describe.** `events.py` opens with a
  five-point essay and a comparison table. The table justifies a real decision:
  move it to `DECISIONS.md` and leave three lines behind.
- **"This is not X, it is Y" constructions.** Cut. State what it is.
- **Comments restating the code.**
- **A "why this matters" paragraph per section.** One per page, maybe.
- **Balanced hedging.** "It is the right convention, but it has an edge, though
  in practice…" Pick the claim, state it, move on.
- **Rhetorical setups.** "The interesting question is not X but Y."
- **The same number repeated in three places.** Say it once, where it lands.

### Rules

1. Every user-visible string lives in `copy/en.py`, keyed, interpolated with
   `t(key, **kwargs)`. Numbers always come from the frames, never typed by hand.
2. `README.md` ≤ 60 lines: what it is, the live URL, how to run it, three
   findings as bullets, where to look in the code. Nothing else.
3. `DECISIONS.md` absorbs the rationale worth keeping (depth counter, the two
   day conventions, the silence budget, index weights, what was deliberately
   left out). One entry per decision, ≤ 10 lines. What does not survive that
   limit was commentary, not a decision.
4. `ARCHITECTURE.md` ≤ 120 lines: layer diagram, invariants table, how to add a
   rule.
5. Code comments only where the code cannot speak: the depth counter, the night
   window, the 06:00 floor, the app-switch reset. A comment says *why it is this
   way*, never *why it is good*.
6. One-line docstrings unless there is a real gotcha.
7. No dashes as sentence separators. Commas, semicolons, or a middot.
8. No imperatives in user-facing or guardian-facing copy. There is a test.

After the cut, read the whole page out loud. Anything you skim is slop.

---

## 5 · Code structure

```
build.py                  ≤ 80 lines · run pipeline, write docs/
balance/                  unchanged core
render/
  payload.py              assembles payload.json
  figures.py              was balance/charts.py
  acts/
    __init__.py           ACTS: ordered list of (id, part, eyebrow, title, builder)
    a01_cover.py … a13_under_the_hood.py
copy/en.py                every string, keyed
site/
  index.html              ≤ 200 lines, semantic, one <section> per act
  style.css               tokens, layout, motion, the act 06 night theme
  app.js                  ≤ 300 lines · sliders, profile switch, rail, plotly init
tests/                    95 existing + new structural tests
```

`balance/theme.py` splits: the plotly template stays in Python (`render/`), the
CSS tokens move to `site/style.css` as custom properties. Same values.
`balance/charts.py` moves to `render/figures.py`; update the two imports in
`tests/test_intelligence.py`.

| File | Budget |
|---|---|
| `build.py` | ≤ 80 |
| any `render/acts/*.py` | ≤ 120 |
| `site/app.js` | ≤ 300 |
| `site/index.html` | ≤ 200 |
| `copy/en.py` | no limit, it is data |

An act that does not fit in 120 lines is doing two things. Split it or push a
block into `<details>`.

---

## 6 · Mobile

The current build fails at 375 px: tabs wrap to four rows, the first act is
5,038 px of scroll, chart axes overflow. A scroll page is naturally better. Do
not assume it.

At 375 px:
- No horizontal page scroll. Wide tables and charts scroll inside their own
  container.
- Rail hidden, progress bar and profile pill stay.
- KPI strips reflow to 2 columns.
- Charts get a mobile height; modebar off.
- Act 02 and act 11 heroes readable without zooming.
- Act 03 profile cards stack vertically, both above the fold if possible.
- Both sliders get a touch target of at least 44 px.

Verify by loading at 375×812. Not by reasoning about it.

---

## 7 · Order of work

Run the tests after every step.

1. **Extract copy.** Every string from `app.py` into `copy/en.py` behind `t()`.
   Streamlit still running. Tests green. Boring, and it makes the rest possible.
2. **Build the payload.** `build.py`, `render/payload.py`, `render/figures.py`.
   Output `docs/payload.json` with every figure, all 30 day-states and all 5
   week-states, for both profiles. No frontend yet.
3. **Static shell.** `index.html` + `style.css`, acts as plain sections, no
   motion, no interaction. Read it. It should already beat the Streamlit version.
4. **Interaction.** Profile fork and sticky pill, week slider, day slider,
   plotly init, deep link.
5. **Motion, rail, night theme.**
6. **Mobile.**
7. **Cut the slop.** Do this near the end, when you know what is load-bearing.
8. **Tests.** §8.
9. **Delete `app.py`,** Streamlit and its extras from `pyproject.toml`.

---

## 8 · Tests

Keep the 95. Add:

```python
def test_no_act_exceeds_its_line_budget()
def test_no_user_visible_string_outside_copy()
def test_every_copy_key_resolves()
def test_no_orphan_copy_keys()
def test_the_act_registry_is_ordered_and_unique()
def test_payload_has_every_figure_day_and_week_for_both_profiles()
def test_payload_guardian_section_has_no_app_domain_or_category()
def test_readme_is_under_sixty_lines()
def test_ui_word_count_is_under_budget()
def test_motion_css_is_guarded()
def test_nothing_is_hidden_without_animation()
```

`test_payload_guardian_section_has_no_app_domain_or_category` is the old privacy
test moved to the new boundary. The payload ships to the browser, so everything
in it is public: assert no `package_name`, no `url_domain` and no category name
appears anywhere in the guardian-facing part of `payload.json`.

The last two tests are what stop someone shipping a page that is blank in
Firefox.

---

## 9 · Deploy

GitHub Pages from `docs/` on `main`. No CI; `build.py` runs locally and the
output is committed.

```bash
python build.py && git add docs && git commit -m "rebuild" && git push
```

Live URL goes on the README's second line.

---

## 10 · Acceptance criteria

**Structure**
- [ ] `build.py` ≤ 80 lines, `site/app.js` ≤ 300, every act ≤ 120
- [ ] no user-visible string outside `copy/`
- [ ] `balance/events.py`, `metrics.py`, `score.py`, `intelligence.py`, `run.py`
      unchanged except import paths
- [ ] no Streamlit, no Dash, no `node_modules`, no JS build step
- [ ] `app.py` deleted

**Slop**
- [ ] `README.md` ≤ 60 lines, `ARCHITECTURE.md` ≤ 120
- [ ] UI prose ≤ 1,200 words
- [ ] `DECISIONS.md` entries ≤ 10 lines each

**Behaviour**
- [ ] 95 original tests pass, only import paths edited
- [ ] new structural tests pass
- [ ] `python -m balance.run --user B --format json` byte-identical to the
      original repo's output
- [ ] every figure on the page matches `tests/test_data_contract.py`

**Experience**
- [ ] act 02 plants the hook without resolving it
- [ ] act 03 is a real choice and `?profile=B` skips it
- [ ] the profile pill switches Part 2 without losing scroll position
- [ ] the week slider moves through all 5 weeks; the day slider through all 30
      days, both updating charts and cards
- [ ] act 06 shifts the surface on entry and restores it on exit
- [ ] act 11 resolves the hook from act 02
- [ ] act 10 is not a dead end for a reader who picked one profile
- [ ] all 13 acts render for both profiles
- [ ] no horizontal scroll at 375 px
- [ ] with `prefers-reduced-motion: reduce`, everything visible and static
- [ ] with scroll-driven animations unsupported, everything visible
- [ ] page loads in under 2 s on a cold cache

**Verification method**

Do not claim any experience criterion from reasoning. Load the built page at
1400×950 and 375×812, scroll every act for both profiles, move both sliders,
switch profile mid-scroll, and screenshot. Report what you saw, including what
still looks wrong.

---

## 11 · Visual language

Keep it. It is NTS Radio editorial and it works.

- Surfaces `#0a0a0b` / `#0f0f11` / `#121214`, hairline `#2b2b31`
- Bone ink `#f1eee8`, secondary `#a3a09a`, muted `#6b6862`
- IBM Plex Mono for labels, eyebrows and numbers. Inter for prose
- Uppercase mono eyebrows, wide letter-spacing
- Hard 1.5 px borders, `border-radius: 0` everywhere
- The eight-hue categorical palette is validated for this dark surface. Do not
  change it. Worst adjacent pair is ΔE 10.3, which is why series carry dash
  patterns as a secondary encoding

What changes is **rhythm**, not vocabulary: more vertical space between acts,
one idea per screen, hero numbers at 6 to 10 rem, silence around them.

Reference feel, in order: Apple Screen Time weekly report (pacing), Spotify
Wrapped (hero cadence and the your-data-first shape), NTS Radio (typography,
already implemented).

---

## 12 · Report back

- File tree with line counts
- Before/after on every number in §4
- Screenshots at both viewports, both profiles
- What you could not do, and why
- Anything broken you found that is not in this document

Use Playwright to verify the implementation.
Start the local site, open it in a browser at 1400x950 and 375x812,
and inspect every act. Test both profiles, the week slider,
the day slider, ?profile=B, profile switching, and the night theme.
Take screenshots and fix any issues you find.
Do not claim visual acceptance criteria are satisfied without
actually checking them in the browser.