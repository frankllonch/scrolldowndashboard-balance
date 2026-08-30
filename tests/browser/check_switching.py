"""Switching deep inside part two, and whether the sliders carry over."""
from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8533/"
ok, bad = [], []
def check(n, c, d=""):
    (ok if c else bad).append(f"{n}{' · ' + str(d) if d else ''}")

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1400, "height": 950})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.goto(URL, wait_until="networkidle"); page.wait_for_timeout(2000)

    # move both sliders off their defaults, then switch from deep in act 08
    page.evaluate("""() => { const w=document.getElementById('week-slider');
        w.value='2'; w.dispatchEvent(new Event('input'));
        const d=document.getElementById('day-slider');
        d.value='11'; d.dispatchEvent(new Event('input')); }""")
    page.wait_for_timeout(400)
    page.evaluate("""() => { const a=document.getElementById('act-08');
        window.scrollTo({top: a.offsetTop + 500, behavior:'instant'}); }""")
    page.wait_for_timeout(200)
    before = page.evaluate("""() => ({
        y: window.scrollY, into: window.scrollY - document.getElementById('act-08').offsetTop,
        week: document.getElementById('week-slider').value,
        day: document.getElementById('day-slider').value,
        weekLabel: document.querySelector('[data-slot="week.label"]').textContent,
        h: document.body.scrollHeight })""")
    page.click("#profile-pill"); page.wait_for_timeout(1200)
    after = page.evaluate("""() => ({
        profile: document.documentElement.dataset.profile,
        into: window.scrollY - document.getElementById('act-08').offsetTop,
        week: document.getElementById('week-slider').value,
        day: document.getElementById('day-slider').value,
        weekLabel: document.querySelector('[data-slot="week.label"]').textContent,
        h: document.body.scrollHeight,
        act: [...document.querySelectorAll('.act')].filter(a=>a.offsetTop<=window.scrollY+1).pop().id })""")
    check("switched to B", after["profile"] == "B")
    check("still inside act 08", after["act"] == "act-08", after["act"])
    check("same offset into the act", abs(before["into"] - after["into"]) < 2,
          f'{before["into"]} -> {after["into"]}')
    check("week carried over", before["week"] == after["week"] == "2",
          f'{before["week"]} -> {after["week"]}')
    check("day carried over", before["day"] == after["day"] == "11",
          f'{before["day"]} -> {after["day"]}')
    check("page height really changed", before["h"] != after["h"],
          f'{before["h"]} -> {after["h"]}')
    b.close()

print("PASS:"); [print("  ✓", x) for x in ok]
if bad: print("FAIL:"); [print("  ✗", x) for x in bad]
if errs: print("ERRORS:", errs[:5])
print(f"\n{len(ok)} passed, {len(bad)} failed")
