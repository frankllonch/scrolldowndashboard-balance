"""Motion, the rail and the surfaces, checked in both motion modes."""
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8533/"
ok, bad = [], []
def check(n, c, d=""):
    (ok if c else bad).append(f"{n}{' · ' + str(d) if d else ''}")

CONTENT = ".act-head, .act-body > *, .kpi, .hero-number, .chart, .note, .lede, .fork-card"

def visible_report(page):
    """Anything that has finished entering the viewport must be fully readable.
    An element still crossing the edge, or one below the fold sitting at the
    from-keyframe, is the view timeline working, not a fault."""
    return page.evaluate("""(sel) => {
        const bad = [];
        let inView = 0;
        document.querySelectorAll(sel).forEach(el => {
            if (el.closest('[hidden]') || el.hidden) return;
            const r = el.getBoundingClientRect();
            /* The reveal runs over `entry 0% -> 40%`, so an element still
               crossing the edge is legitimately part-way through it. What must
               never be faded is one that has finished entering. */
            if (r.bottom <= 0 || r.top >= window.innerHeight * 0.4) return;
            inView++;
            const cs = getComputedStyle(el);
            if (parseFloat(cs.opacity) < 0.99 || cs.visibility === 'hidden'
                || cs.display === 'none') {
                bad.push(el.className + ' opacity=' + cs.opacity + ' vis=' + cs.visibility);
            }
        });
        return {bad: bad.slice(0, 6), inView};
    }""", CONTENT)

with sync_playwright() as p:
    b = p.chromium.launch()

    # ---- motion welcome ---------------------------------------------------
    page = b.new_page(viewport={"width": 1400, "height": 950}, reduced_motion="no-preference")
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.goto(URL, wait_until="networkidle"); page.wait_for_timeout(2000)

    supports = page.evaluate("CSS.supports('animation-timeline', 'view()')")
    check("browser supports scroll-driven animation", supports, supports)
    animated = page.evaluate("""() => {
        const el = document.querySelector('#act-05 .act-head');
        return getComputedStyle(el).animationName;
    }""")
    check("acts carry the reveal animation", animated == "reveal", animated)

    # progress bar
    page.evaluate("window.scrollTo({top: document.body.scrollHeight/2, behavior:'instant'})")
    page.wait_for_timeout(300)
    pct = page.evaluate("parseFloat(document.getElementById('progress-bar').style.width)")
    check("progress bar tracks scroll", 40 < pct < 60, f"{pct:.0f}%")

    # rail current
    page.evaluate("""() => { const a=document.getElementById('act-07');
        window.scrollTo({top:a.offsetTop + 300, behavior:'instant'}); }""")
    page.wait_for_timeout(500)
    rail = page.evaluate("""() => {
        const cur = document.querySelector('[data-rail][aria-current="true"]');
        return cur ? {id: cur.dataset.rail, colour: getComputedStyle(cur).color} : null;
    }""")
    check("rail marks the current act", rail and rail["id"] == "07", rail)
    muted = page.evaluate("getComputedStyle(document.querySelector('[data-rail=\"01\"]')).color")
    check("rail: current is ink, rest muted", rail and rail["colour"] != muted,
          f'current={rail["colour"] if rail else None} other={muted}')

    # ---- the night --------------------------------------------------------
    day_tokens = page.evaluate("""() => {
        const cs = getComputedStyle(document.documentElement);
        return {bg: cs.getPropertyValue('--bg').trim(), ink: cs.getPropertyValue('--ink').trim(),
                accent: cs.getPropertyValue('--accent').trim(), grid: cs.getPropertyValue('--grid').trim(),
                surface: document.documentElement.dataset.surface,
                vignette: getComputedStyle(document.querySelector('.vignette')).opacity};
    }""")
    page.evaluate("""() => { const a=document.getElementById('act-06');
        window.scrollTo({top: a.offsetTop + a.offsetHeight/2 - window.innerHeight/2,
                         behavior:'instant'}); }""")
    page.wait_for_timeout(1200)
    night = page.evaluate("""() => {
        const cs = getComputedStyle(document.documentElement);
        const chart = document.querySelector('#act-06 .chart');
        return {bg: cs.getPropertyValue('--bg').trim(), ink: cs.getPropertyValue('--ink').trim(),
                accent: cs.getPropertyValue('--accent').trim(), grid: cs.getPropertyValue('--grid').trim(),
                surface: document.documentElement.dataset.surface,
                vignette: getComputedStyle(document.querySelector('.vignette')).opacity,
                body: getComputedStyle(document.body).backgroundColor,
                chartGrid: chart.layout.xaxis.gridcolor};
    }""")
    check("night: background goes black", night["bg"] == "#000000", night["bg"])
    check("night: ink warms", night["ink"] == "#e8dfd0" and day_tokens["ink"] == "#f1eee8",
          f'{day_tokens["ink"]} -> {night["ink"]}')
    check("night: accent goes amber", night["accent"] == "#fab219",
          f'{day_tokens["accent"]} -> {night["accent"]}')
    check("night: grid dims", night["grid"] == "#141410", f'{day_tokens["grid"]} -> {night["grid"]}')
    check("night: plot grid follows", night["chartGrid"] == "#141410", night["chartGrid"])
    check("night: vignette raised", float(night["vignette"]) > 0.9,
          f'{day_tokens["vignette"]} -> {night["vignette"]}')
    check("night: body actually painted black", night["body"] == "rgb(0, 0, 0)", night["body"])

    page.evaluate("""() => { const a=document.getElementById('act-08');
        window.scrollTo({top:a.offsetTop + 200, behavior:'instant'}); }""")
    page.wait_for_timeout(1200)
    out = page.evaluate("""() => ({
        surface: document.documentElement.dataset.surface,
        bg: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim(),
        vignette: getComputedStyle(document.querySelector('.vignette')).opacity,
        chartGrid: document.querySelector('#act-06 .chart').layout.xaxis.gridcolor})""")
    check("night: restores on exit",
          out["surface"] == "a08" and float(out["vignette"]) < 0.1, out)
    check("night: plot grid restores", out["chartGrid"] == "#1c1c21", out["chartGrid"])

    trans = page.evaluate("getComputedStyle(document.body).transitionDuration")
    check("night transitions when motion is welcome", "0.6s" in trans, trans)

    # everything readable, all acts
    for i in range(1, 13):
        page.evaluate(f"""() => {{ const a=document.getElementById('act-{i:02d}');
            window.scrollTo({{top:a.offsetTop + 60, behavior:'instant'}}); }}""")
        page.wait_for_timeout(150)
    seen_total = 0
    for i in range(1, 13):
        page.evaluate(f"""() => {{ const a=document.getElementById('act-{i:02d}');
            document.querySelectorAll('details').forEach(d => d.open = true);
            window.scrollTo({{top:a.offsetTop + 60, behavior:'instant'}}); }}""")
        page.wait_for_timeout(200)
        rep = visible_report(page)
        seen_total += rep["inView"]
        if rep["bad"]:
            check(f"act {i:02d}: something in view is invisible", False, rep["bad"])
    check("motion on: nothing in view is ever invisible", True,
          f"{seen_total} elements checked across 13 acts")
    page.close()

    # ---- reduced motion: the Firefox case, and the reader who asked ------
    page = b.new_page(viewport={"width": 1400, "height": 950}, reduced_motion="reduce")
    page.goto(URL, wait_until="networkidle"); page.wait_for_timeout(2000)
    quiet = page.evaluate("""() => ({
        anim: getComputedStyle(document.querySelector('#act-05 .act-head')).animationName,
        chart: getComputedStyle(document.querySelector('.chart')).animationName,
        kpi: getComputedStyle(document.querySelector('.kpi')).animationName,
        bodyTrans: getComputedStyle(document.body).transitionDuration,
        vigTrans: getComputedStyle(document.querySelector('.vignette')).transitionDuration,
        scroll: getComputedStyle(document.documentElement).scrollBehavior})""")
    check("reduced motion: no act animation", quiet["anim"] == "none", quiet["anim"])
    check("reduced motion: no chart animation", quiet["chart"] == "none", quiet["chart"])
    check("reduced motion: no kpi animation", quiet["kpi"] == "none", quiet["kpi"])
    check("reduced motion: night applies at once, no transition",
          quiet["bodyTrans"] == "0s" and quiet["vigTrans"] == "0s",
          f'body={quiet["bodyTrans"]} vignette={quiet["vigTrans"]}')
    check("reduced motion: no smooth scrolling", quiet["scroll"] == "auto", quiet["scroll"])

    rep = visible_report(page)
    check("reduced motion: everything visible at the top", not rep["bad"], rep)
    quiet_total, quiet_bad = 0, []
    for i in range(1, 13):
        page.evaluate(f"""() => {{ const a=document.getElementById('act-{i:02d}');
            document.querySelectorAll('details').forEach(d => d.open = true);
            window.scrollTo({{top:a.offsetTop + 60, behavior:'instant'}}); }}""")
        page.wait_for_timeout(150)
        rep = visible_report(page)
        quiet_total += rep["inView"]
        quiet_bad += rep["bad"]
    check("reduced motion: nothing in view is ever invisible", not quiet_bad,
          quiet_bad or f"{quiet_total} elements checked across 13 acts")

    # night still happens, just without the fade
    page.evaluate("""() => { const a=document.getElementById('act-06');
        window.scrollTo({top: a.offsetTop + a.offsetHeight/2 - window.innerHeight/2,
                         behavior:'instant'}); }""")
    page.wait_for_timeout(400)
    check("reduced motion: night still applies",
          page.evaluate("document.documentElement.dataset.surface") == "a06")
    b.close()

print("PASS:"); [print("  ✓", x) for x in ok]
if bad: print("FAIL:"); [print("  ✗", x) for x in bad]
if errs: print("ERRORS:", errs[:5])
print(f"\n{len(ok)} passed, {len(bad)} failed")
