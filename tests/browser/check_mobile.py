"""Phase 6 acceptance at 375x812. Every claim measured in the browser."""
import pathlib
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8533/"
OUT = pathlib.Path("screenshots"); OUT.mkdir(exist_ok=True)
ok, bad = [], []
def check(n, c, d=""):
    (ok if c else bad).append(f"{n}{' · ' + str(d) if d else ''}")

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 375, "height": 812},
                      device_scale_factor=2, is_mobile=True, has_touch=True)
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.goto(URL, wait_until="networkidle"); page.wait_for_timeout(2500)

    # --- no horizontal page scroll, anywhere in the scroll -----------------
    worst = 0
    escapees = []
    for i in range(1, 14):
        page.evaluate(f"""() => {{ const a=document.getElementById('act-{i:02d}');
            document.querySelectorAll('details').forEach(d => d.open = true);
            window.scrollTo({{top:a.offsetTop, behavior:'instant'}}); }}""")
        page.wait_for_timeout(220)
        r = page.evaluate("""() => {
            const vw = document.documentElement.clientWidth, out = [];
            document.querySelectorAll('.act *').forEach(el => {
                const box = el.getBoundingClientRect();
                if (!box.width) return;
                const cs = getComputedStyle(el);
                if (cs.position === 'fixed') return;
                /* content inside its own scroller is meant to be wider */
                if (el.closest('.scroller, .js-plotly-plot')) return;
                if (box.right > vw + 1 || box.left < -1) {
                    out.push(el.tagName + '.' + String(el.className).slice(0,26) +
                             ' [' + Math.round(box.left) + ',' + Math.round(box.right) + ']');
                }
            });
            return {w: document.documentElement.scrollWidth,
                    vw, out: out.slice(0, 4)};
        }""")
        worst = max(worst, r["w"])
        escapees += r["out"]
    check("no horizontal page scroll in any act", worst <= 375, f"widest document = {worst}px")
    check("nothing escapes the viewport", not escapees, escapees[:4])

    # --- wide content scrolls inside its own box --------------------------
    scrollers = page.evaluate("""() => {
        const out = [];
        document.querySelectorAll('.scroller').forEach(s => {
            out.push({inner: s.scrollWidth, outer: s.clientWidth,
                      overflow: getComputedStyle(s).overflowX});
        });
        return out.filter(s => s.inner > s.outer);
    }""")
    check("wide tables scroll inside their container",
          scrollers and all(s["overflow"] == "auto" for s in scrollers),
          f"{len(scrollers)} scrollers, e.g. {scrollers[0] if scrollers else None}")

    # --- chrome ------------------------------------------------------------
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    page.wait_for_timeout(200)
    chrome = page.evaluate("""() => ({
        rail: getComputedStyle(document.querySelector('.rail')).display,
        progress: getComputedStyle(document.querySelector('.progress')).position,
        pillTop: document.getElementById('profile-pill').hidden })""")
    check("rail hidden", chrome["rail"] == "none", chrome["rail"])
    check("progress bar stays", chrome["progress"] == "fixed", chrome["progress"])
    page.evaluate("""() => { const a=document.getElementById('act-05');
        window.scrollTo({top:a.offsetTop, behavior:'instant'}); }""")
    page.wait_for_timeout(300)
    check("pill stays and appears from act 04",
          chrome["pillTop"] and not page.evaluate("document.getElementById('profile-pill').hidden"))

    # --- layout ------------------------------------------------------------
    layout = page.evaluate("""() => ({
        kpi: getComputedStyle(document.querySelector('.kpis')).gridTemplateColumns,
        fork: getComputedStyle(document.querySelector('.fork')).gridTemplateColumns,
        grid: getComputedStyle(document.querySelector('.grid.cols-2')).gridTemplateColumns,
        chartH: getComputedStyle(document.querySelector('.chart')).minHeight,
        act03: document.getElementById('act-03').offsetHeight,
        modebar: (() => { const el = document.querySelector('.js-plotly-plot');
                  return el && el._context ? el._context.displayModeBar : null; })(),
    })""")
    check("KPI strips reflow to 2 columns", len(layout["kpi"].split()) == 2, layout["kpi"])
    check("fork cards stack", len(layout["fork"].split()) == 1, layout["fork"])
    check("chart grids stack", len(layout["grid"].split()) == 1, layout["grid"])
    check("charts get a mobile height", layout["chartH"] == "260px", layout["chartH"])
    check("modebar off", layout["modebar"] is False, layout["modebar"])
    check("act 03 fits one screen", layout["act03"] <= 812, f'{layout["act03"]}px of 812')

    # --- heroes readable ---------------------------------------------------
    heroes = page.evaluate("""() => {
        const out = [];
        document.querySelectorAll('#act-02 .hero-number, #act-11 .hero-number')
          .forEach(h => { const r = h.getBoundingClientRect();
            out.push({act: h.closest('.act').id, px: getComputedStyle(h).fontSize,
                      w: Math.round(r.width), fits: r.width <= 375,
                      text: h.textContent.trim().slice(0, 12)}); });
        return out; }""")
    check("act 02 and 11 heroes fit without zooming",
          heroes and all(h["fits"] for h in heroes),
          [f'{h["act"]} "{h["text"]}" {h["px"]} {h["w"]}px' for h in heroes])

    # --- touch targets -----------------------------------------------------
    sliders = page.evaluate("""() => ['week','day'].map(k => {
        const s = document.getElementById(k + '-slider');
        if (!s) return {k, h: 0};
        const r = s.getBoundingClientRect();
        return {k, h: Math.round(r.height), w: Math.round(r.width)}; })""")
    check("both sliders have a 44px touch target",
          all(s["h"] >= 44 for s in sliders), sliders)

    # --- it still works ----------------------------------------------------
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    page.tap('.fork-card[data-choose="B"]')
    page.wait_for_timeout(1500)
    after = page.evaluate("""() => ({profile: document.documentElement.dataset.profile,
        w: document.documentElement.scrollWidth})""")
    check("fork works by touch", after["profile"] == "B", after["profile"])
    check("still no horizontal scroll after switching", after["w"] <= 375, after["w"])

    page.evaluate("""() => { const s=document.getElementById('day-slider');
        s.value='18'; s.dispatchEvent(new Event('input')); }""")
    page.wait_for_timeout(400)
    cards = page.evaluate("""() => {
        const g = document.querySelector('[data-slot="day.cards"] .grid');
        return {cols: getComputedStyle(g).gridTemplateColumns.split(' ').length,
                w: document.documentElement.scrollWidth}; }""")
    check("day cards stack on mobile", cards["cols"] == 1, cards["cols"])
    check("no overflow from the phone cards", cards["w"] <= 375, cards["w"])

    for act, name in (("01","cover"), ("02","hook"), ("03","fork"), ("04","week"),
                      ("06","night"), ("09","engine"), ("11","finding")):
        page.evaluate(f"""() => {{ const a=document.getElementById('act-{act}');
            window.scrollTo({{top:a.offsetTop, behavior:'instant'}}); }}""")
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUT / f"375-{act}-{name}.png"))
    b.close()

print("PASS:"); [print("  ✓", x) for x in ok]
if bad: print("FAIL:"); [print("  ✗", x) for x in bad]
if errs: print("ERRORS:", errs[:5])
print(f"\n{len(ok)} passed, {len(bad)} failed")
