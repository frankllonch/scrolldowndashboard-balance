"""The acceptance list from the brief, walked in a browser.

Nothing here is claimed from reading the source. Every line is something the
page did while being driven.
"""
import pathlib
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8533/"
OUT = pathlib.Path("screenshots"); OUT.mkdir(exist_ok=True)
ok, bad, notes = [], [], []


def check(name, condition, detail=""):
    (ok if condition else bad).append(f"{name}{' · ' + str(detail) if detail else ''}")


def settle(page, tries=30):
    last = -1
    for _ in range(tries):
        page.wait_for_timeout(150)
        now = page.evaluate("Math.round(window.scrollY)")
        if now == last:
            return now
        last = now
    return last


def walk_every_act(page, tag):
    """Scroll every act, opening the collapsed blocks, and report what is
    unreadable or wider than the screen."""
    unreadable, overflow, empty = [], [], []
    acts = page.evaluate("""() => [...document.querySelectorAll('.act')]
        .filter(a => !a.hidden).map(a => a.id)""")
    for act in acts:
        page.evaluate(f"""() => {{
            document.querySelectorAll('details').forEach(d => d.open = true);
            window.scrollTo({{top: document.getElementById('{act}').offsetTop + 40,
                             behavior: 'instant'}});
        }}""")
        page.wait_for_timeout(260)
        state = page.evaluate(f"""(id) => {{
            const el = document.getElementById(id);
            const vw = document.documentElement.clientWidth;
            const faded = [], wide = [];
            el.querySelectorAll('.act-head, .act-body > *, .kpi, .hero-number,'
                              + ' .chart, .note, .lede, .fork-card').forEach(n => {{
                const r = n.getBoundingClientRect();
                if (r.bottom <= 0 || r.top >= window.innerHeight * 0.4) return;
                if (parseFloat(getComputedStyle(n).opacity) < 0.99) {{
                    faded.push(n.className);
                }}
            }});
            el.querySelectorAll('*').forEach(n => {{
                if (n.closest('.scroller, .js-plotly-plot')) return;
                const r = n.getBoundingClientRect();
                if (r.width && (r.right > vw + 1 || r.left < -1)) wide.push(n.tagName);
            }});
            return {{faded, wide: wide.slice(0, 3),
                     text: el.innerText.trim().length,
                     plots: el.querySelectorAll('.js-plotly-plot').length,
                     charts: el.querySelectorAll('.chart').length}};
        }}""", act)
        if state["faded"]:
            unreadable.append(f"{act}: {state['faded'][:2]}")
        if state["wide"]:
            overflow.append(f"{act}: {state['wide']}")
        if state["text"] < 40:
            empty.append(act)
        if state["charts"] != state["plots"]:
            empty.append(f"{act}: {state['plots']}/{state['charts']} charts drew")
        page.screenshot(path=str(OUT / f"{tag}-{act}.png"))
    return unreadable, overflow, empty


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---- cold load ------------------------------------------------------
    page = browser.new_page(viewport={"width": 1400, "height": 950})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(URL, wait_until="load")
    timing = page.evaluate("""() => {
        const n = performance.getEntriesByType('navigation')[0];
        const rs = performance.getEntriesByType('resource');
        return {load: Math.round(n.loadEventEnd),
                dom: Math.round(n.domContentLoadedEventEnd),
                bytes: rs.reduce((a, r) => a + (r.transferSize || 0), 0),
                heaviest: rs.map(r => [r.name.split('/').pop(),
                                       Math.round((r.transferSize || 0) / 1024)])
                            .sort((a, b) => b[1] - a[1]).slice(0, 3)};
    }""")
    page.wait_for_timeout(2500)
    check("page load event under 2 s", timing["load"] < 2000, f"{timing['load']} ms")
    notes.append(f"transfer {timing['bytes'] // 1024} KB uncompressed, "
                 f"heaviest {timing['heaviest']}")

    # ---- profile A, desktop --------------------------------------------
    faded, wide, empty = walk_every_act(page, "1400-A")
    check("A/1400: every act readable", not faded, faded)
    check("A/1400: nothing wider than the viewport", not wide, wide)
    check("A/1400: every act has content and every chart drew", not empty, empty)

    # ---- both sliders ---------------------------------------------------
    page.evaluate("""() => window.scrollTo({top: document.getElementById('act-04')
        .offsetTop, behavior: 'instant'})""")
    page.wait_for_timeout(200)
    seen_weeks = []
    for week in (1, 2, 3, 4, 5):
        page.evaluate(f"""() => {{ const s = document.getElementById('week-slider');
            s.value = '{week}'; s.dispatchEvent(new Event('input')); }}""")
        page.wait_for_timeout(220)
        seen_weeks.append(page.evaluate("""() => [
            document.querySelector('[data-slot="week.label"]').textContent,
            document.querySelector('[data-slot="week.kpis"] .kpi-value').textContent,
            document.querySelector('[data-figure-week]').dataset.figure]"""))
    check("the week slider moves through all five",
          len({tuple(x) for x in seen_weeks}) == 5,
          [w[0] for w in seen_weeks])

    seen_days = []
    for day in (0, 7, 15, 22, 29):
        page.evaluate(f"""() => {{ const s = document.getElementById('day-slider');
            s.value = '{day}'; s.dispatchEvent(new Event('input')); }}""")
        page.wait_for_timeout(200)
        seen_days.append(page.evaluate("""() => [
            document.querySelector('[data-slot="day.label"]').textContent,
            document.querySelector('[data-figure="tracked_series"]').layout.shapes[1].x0]"""))
    check("the day slider moves through the month",
          len({tuple(x) for x in seen_days}) == 5, [d[0] for d in seen_days])

    # ---- switch mid-scroll ----------------------------------------------
    page.evaluate("""() => window.scrollTo({top: document.getElementById('act-07')
        .offsetTop + 420, behavior: 'instant'})""")
    page.wait_for_timeout(200)
    before = page.evaluate("""() => ({into: window.scrollY -
        document.getElementById('act-07').offsetTop, h: document.body.scrollHeight})""")
    page.click("#profile-pill")
    page.wait_for_timeout(1400)
    after = page.evaluate("""() => ({profile: document.documentElement.dataset.profile,
        into: window.scrollY - document.getElementById('act-07').offsetTop,
        h: document.body.scrollHeight})""")
    check("switching mid-scroll holds the reader's place",
          after["profile"] == "B" and abs(before["into"] - after["into"]) < 4,
          f"{before['into']}px -> {after['into']}px, page {before['h']} -> {after['h']}")

    # ---- profile B, desktop --------------------------------------------
    faded, wide, empty = walk_every_act(page, "1400-B")
    check("B/1400: every act readable", not faded, faded)
    check("B/1400: nothing wider than the viewport", not wide, wide)
    check("B/1400: every act has content and every chart drew", not empty, empty)
    page.close()

    # ---- mobile, both profiles ------------------------------------------
    for profile in ("A", "B"):
        page = browser.new_page(viewport={"width": 375, "height": 812},
                                is_mobile=True, has_touch=True, device_scale_factor=2)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(URL + f"?profile={profile}", wait_until="networkidle")
        page.wait_for_timeout(2500)
        faded, wide, empty = walk_every_act(page, f"375-{profile}")
        check(f"{profile}/375: every act readable", not faded, faded)
        check(f"{profile}/375: no horizontal overflow", not wide, wide)
        check(f"{profile}/375: every act has content and every chart drew",
              not empty, empty)
        page.close()

    browser.close()

print("PASS:"); [print("  ✓", x) for x in ok]
if bad:
    print("FAIL:"); [print("  ✗", x) for x in bad]
if notes:
    print("NOTES:"); [print("  ·", x) for x in notes]
if errors:
    print("CONSOLE/PAGE ERRORS:", errors[:6])
print(f"\n{len(ok)} passed, {len(bad)} failed · "
      f"{len(list(OUT.glob('*.png')))} screenshots in {OUT}")
sys.exit(1 if bad else 0)
