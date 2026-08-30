"""The sliders, the fork, the pill and the deep link, driven for real."""
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8533/"
ok, bad = [], []
def check(name, cond, detail=""):
    (ok if cond else bad).append(f"{name}{' · ' + str(detail) if detail else ''}")

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1400, "height": 950})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

    page.goto(URL, wait_until="networkidle"); page.wait_for_timeout(2000)
    check("charts drawn", page.eval_on_selector_all(".js-plotly-plot", "e=>e.length") == 26)
    check("profile starts A", page.evaluate("document.documentElement.dataset.profile") == "A")

    # --- week slider -------------------------------------------------------
    before = page.evaluate("""() => ({
        label: document.querySelector('[data-slot="week.label"]').textContent,
        kpi: document.querySelector('[data-slot="week.kpis"] .kpi-value').textContent,
        fig: document.querySelector('[data-figure-week]').dataset.figure,
        row: document.querySelector('[data-slot="week.table"] td:nth-child(2)').textContent,
    })""")
    for wk in (1, 2, 3, 5):
        page.evaluate(f"""() => {{
            const s = document.getElementById('week-slider');
            s.value = '{wk}'; s.dispatchEvent(new Event('input'));
        }}""")
        page.wait_for_timeout(250)
    after = page.evaluate("""() => ({
        label: document.querySelector('[data-slot="week.label"]').textContent,
        kpi: document.querySelector('[data-slot="week.kpis"] .kpi-value').textContent,
        fig: document.querySelector('[data-figure-week]').dataset.figure,
        row: document.querySelector('[data-slot="week.table"] td:nth-child(2)').textContent,
        colors: document.querySelector('[data-figure^="week_evolution."]').data[0].marker.color,
        vline: document.querySelector('[data-figure="week_components"]').layout.shapes[0].x0,
        range: document.querySelector('[data-slot="week.range"]').textContent,
    })""")
    check("week label moves", before["label"] != after["label"], f'{before["label"]} -> {after["label"]}')
    check("week kpis move", before["kpi"] != after["kpi"], f'{before["kpi"]} -> {after["kpi"]}')
    check("week_days figure re-points", after["fig"].endswith(".5"), after["fig"])
    check("week table moves", before["row"] != after["row"], f'{before["row"]} -> {after["row"]}')
    check("week 5 flagged short", "short" in after["range"].lower(), after["range"][:60])
    check("evolution highlights week 5", after["colors"][4] != after["colors"][0], after["colors"])
    check("components vline follows", after["vline"] == "W5", after["vline"])

    # --- day slider --------------------------------------------------------
    d0 = page.evaluate("""() => ({
        label: document.querySelector('[data-slot="day.label"]').textContent,
        cards: document.querySelector('[data-slot="day.cards"]').textContent.slice(0, 80),
        vline: document.querySelector('[data-figure="tracked_series"]').layout.shapes[1].x0,
    })""")
    page.evaluate("""() => { const s = document.getElementById('day-slider');
        s.value = '4'; s.dispatchEvent(new Event('input')); }""")
    page.wait_for_timeout(300)
    d1 = page.evaluate("""() => ({
        label: document.querySelector('[data-slot="day.label"]').textContent,
        cards: document.querySelector('[data-slot="day.cards"]').textContent.slice(0, 80),
        vline: document.querySelector('[data-figure="tracked_series"]').layout.shapes[1].x0,
        max: document.getElementById('day-slider').max,
    })""")
    check("day slider spans 30", d1["max"] == "29", d1["max"])
    check("day label moves", d0["label"] != d1["label"], f'{d0["label"]} -> {d1["label"]}')
    check("day cards move", d0["cards"] != d1["cards"])
    check("cursor vline follows", d0["vline"] != d1["vline"], f'{d0["vline"]} -> {d1["vline"]}')

    # --- the fork ----------------------------------------------------------
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    page.click('.fork-card[data-choose="B"]')
    page.wait_for_timeout(900)
    fork = page.evaluate("""() => ({
        profile: document.documentElement.dataset.profile,
        at: window.scrollY, act4: document.getElementById('act-04').offsetTop,
        guardian: !!document.querySelector('[data-slot="day.cards"]').textContent.match(/Guardian/),
        plots: document.querySelectorAll('#act-04 .js-plotly-plot, #act-09 .js-plotly-plot').length,
    })""")
    check("fork switches to B", fork["profile"] == "B")
    check("fork scrolls to act 04", abs(fork["at"] - fork["act4"]) < 40, f'{fork["at"]} vs {fork["act4"]}')
    check("B shows a guardian channel", fork["guardian"])
    check("part two redrew", fork["plots"] >= 8, fork["plots"])

    # --- the pill ----------------------------------------------------------
    pill = page.evaluate("() => !document.getElementById('profile-pill').hidden")
    check("pill visible from act 04", pill)
    mark = page.evaluate("""() => ({y: window.scrollY,
        id: [...document.querySelectorAll('.act')].filter(a=>a.offsetTop<=window.scrollY+1).pop().id})""")
    page.click("#profile-pill"); page.wait_for_timeout(900)
    after_switch = page.evaluate("""() => ({
        profile: document.documentElement.dataset.profile,
        id: [...document.querySelectorAll('.act')].filter(a=>a.offsetTop<=window.scrollY+1).pop().id,
        nudge: (document.querySelector('[data-slot="day.cards"] .phone-h')||{}).textContent || '',
    })""")
    check("pill switches back", after_switch["profile"] == "A")
    check("scroll holds its act", after_switch["id"] == mark["id"], f'{mark["id"]} -> {after_switch["id"]}')

    # --- deep link ---------------------------------------------------------
    page.goto(URL + "?profile=B", wait_until="networkidle"); page.wait_for_timeout(1800)
    deep = page.evaluate("""() => ({
        profile: document.documentElement.dataset.profile,
        forkHidden: document.getElementById('act-03').hidden,
        railHidden: document.querySelector('[data-rail="03"]').parentNode.hidden,
        plots: document.querySelectorAll('.js-plotly-plot').length,
    })""")
    check("?profile=B selects B", deep["profile"] == "B")
    check("?profile=B skips the fork", deep["forkHidden"] and deep["railHidden"])
    check("charts still drawn", deep["plots"] == 26, deep["plots"])

    b.close()

print("PASS:")
for x in ok: print("  ✓", x)
if bad:
    print("FAIL:")
    for x in bad: print("  ✗", x)
if errs: print("CONSOLE/PAGE ERRORS:", errs[:6])
print(f"\n{len(ok)} passed, {len(bad)} failed")
