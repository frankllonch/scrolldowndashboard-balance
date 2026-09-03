# Rewriting the frontend in TypeScript

The brief: Python processes data and returns it structured; TypeScript does all
the representation; every input typed; the backend holds the intelligence and the
frontend does no juggling. And the code should be easier to navigate than it is.

## Why it was hard to navigate

Changing one section meant touching six files across two languages — the copy in
`copytext/strings/product.py`, the markup in `render/acts/aNN_*.py`, the chart in
`render/figures/*.py`, the pre-rendered cards in `render/states.py`, the CSS in
`site/css/`, and the behaviour in `site/app.js`. The 236 KB `payload.json` carried
26 built Plotly figures and 6 acts of pre-rendered HTML.

After: one TypeScript module per act, holding its markup, its copy and its chart.
Python holds only the numbers.

## Phases

- [x] **1 · The contract.** `web/types/` declares the whole payload shape; `emit/`
      produces it. Checked from both sides: `npm run typecheck` compiles the
      emitted document against the declarations, and `tests/test_emit.py` asserts
      the values sit inside the unions, that no string is markup, and that no
      figure or copy key crosses the line.
- [x] **2 · Scaffolding.** npm, `tsc --strict` (with `noUncheckedIndexedAccess`
      and `exactOptionalPropertyTypes`), esbuild. Output goes to `docs/bundle.js`
      for now so it cannot clobber the `docs/app.js` still serving the page.
- [ ] **3 · Figures.** The 26 charts, from Python to TypeScript. Plotly stays, so
      this is a port with something to compare against.
- [ ] **4 · Acts.** One module each, carrying markup and copy.
- [ ] **5 · Cutover.** `bundle.js` becomes `app.js`; `render/`, `copytext/` and
      `page.py` are deleted; `build.py` runs `python -m emit` and `npm run build`.
- [ ] **6 · The map.** An `ARCHITECTURE.md` that says "want to change X? it is
      here", replacing the current one.

## Decided

- npm + esbuild, not Vite: one dev dependency, sub-second builds.
- Plotly stays. Swapping the chart library would mean redesigning 26 figures with
  nothing to check the result against.
- Blocks cross as tallies, not 1,167 rows. Nothing displays a single attempt, and
  counting belongs on the side that owns the arithmetic.
- Hours cross as numbers. The clock face, "2h 02m" and the "no use" for a metric
  user A genuinely lacks are all wording.

## Constraint

`docs/` is build output. Editing `docs/style.css`, `docs/app.js` or
`docs/index.html` by hand loses the change on the next build. Edit `site/`, and
after phase 5, `web/`.
