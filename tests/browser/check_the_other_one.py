"""Act 10 must not be a dead end, and must not lie about what was read."""
from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8533/"
ok, bad = [], []
def check(n, c, d=""):
    (ok if c else bad).append(f"{n}{' · ' + str(d) if d else ''}")

def settle(page, tries=25):
    """Chrome's smooth scroll over ten thousand pixels takes well over a
    second. Wait for it to stop moving rather than guessing a timeout."""
    last = -1
    for _ in range(tries):
        page.wait_for_timeout(200)
        now = page.evaluate("Math.round(window.scrollY)")
        if now == last:
            return now
        last = now
    return last


def state(page):
    return page.evaluate("""() => ({
        profile: document.documentElement.dataset.profile,
        seen: !document.querySelector('[data-slot="other.seen"]').hidden,
        offers: [...document.querySelectorAll('[data-other]')].filter(b=>!b.hidden)
                 .map(b=>b.dataset.other),
        nudge: (document.querySelector('[data-slot="day.cards"] .phone-h')||{}).textContent || '',
    })""")

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1400, "height": 950})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

    page.goto(URL + "?profile=B", wait_until="networkidle"); page.wait_for_timeout(2000)
    s = state(page)
    check("deep link: only B read", not s["seen"] and s["offers"] == ["A"],
          f'seen={s["seen"]} offers={s["offers"]}')
    fork = page.evaluate("""() => ({
        display: getComputedStyle(document.getElementById('act-03')).display,
        height: document.getElementById('act-03').offsetHeight,
        rail: document.querySelector('[data-rail=\"03\"]').offsetParent === null })""")
    check("?profile=B really removes the fork",
          fork["display"] == "none" and fork["height"] == 0 and fork["rail"],
          f'display={fork["display"]} h={fork["height"]} railGone={fork["rail"]}')
    check("ordinal reads correctly", "3th" not in s["nudge"] and "rd time" in s["nudge"],
          s["nudge"][:52])

    page.click('[data-other="A"]')
    settle(page)
    s2 = state(page)
    check("act 10 button switches", s2["profile"] == "A")
    check("now both read", s2["seen"] and s2["offers"] == [],
          f'seen={s2["seen"]} offers={s2["offers"]}')
    at = page.evaluate("() => ({y: window.scrollY, act4: document.getElementById('act-04').offsetTop})")
    check("button returns to act 04", abs(at["y"] - at["act4"]) < 40, f'{at["y"]} vs {at["act4"]}')

    # fresh load, no deep link
    page.goto(URL, wait_until="networkidle"); page.wait_for_timeout(2000)
    s3 = state(page)
    check("fresh load: only A read", not s3["seen"] and s3["offers"] == ["B"],
          f'seen={s3["seen"]} offers={s3["offers"]}')
    b.close()

print("PASS:"); [print("  ✓", x) for x in ok]
if bad: print("FAIL:"); [print("  ✗", x) for x in bad]
if errs: print("ERRORS:", errs[:5])
print(f"\n{len(ok)} passed, {len(bad)} failed")
