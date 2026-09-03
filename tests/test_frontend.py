"""The stylesheet, read as a contract.

Two of these are the ones that stop someone shipping a page that is blank in
a browser without scroll-driven animation.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
#: The built sheet, which is what the browser gets. The sections it is
#: concatenated from live in web/styles/.
CSS = (ROOT / "dist" / "style.css").read_text()

#: What the reveal animation is applied to. If any of these is hidden by a
#: plain rule, the page depends on animation to be readable.
CONTENT = (".act", ".act-head", ".act-body", ".kpi", ".hero-number", ".chart",
           ".note", ".lede", ".fork-card", ".stat-value", "body", "main")

MOTION_GUARD = "@media (prefers-reduced-motion: no-preference)"
SUPPORT_GUARD = "@supports (animation-timeline: view())"


def blocks(css: str):
    """Every declaration block, with the at-rules wrapped around it.

    `@keyframes` is treated as one block rather than a context, so its inner
    `from`/`to` never look like content rules.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, stack, head, i = [], [], "", 0
    while i < len(css):
        char = css[i]
        if char == "{":
            selector = head.strip()
            head = ""
            if selector.startswith("@") and not selector.startswith("@keyframes"):
                stack.append(selector)
                i += 1
                continue
            depth, j = 1, i + 1
            while j < len(css) and depth:
                depth += (css[j] == "{") - (css[j] == "}")
                j += 1
            out.append((selector, css[i + 1:j - 1], list(stack)))
            i = j
            continue
        if char == "}":
            if stack:
                stack.pop()
            head = ""
        else:
            head += char
        i += 1
    return out


def test_motion_css_is_guarded():
    """Nothing animates unless the reader wants motion and the browser can
    drive it from scroll."""
    unguarded = []
    for selector, body, wrappers in blocks(CSS):
        if "@keyframes" in " ".join(wrappers) or selector.startswith("@keyframes"):
            continue
        wrapped = " ".join(wrappers)
        if re.search(r"\btransition\s*:", body) and MOTION_GUARD not in wrapped:
            unguarded.append(f"{selector}: transition outside the motion guard")
        if re.search(r"\banimation(-timeline)?\s*:", body):
            if MOTION_GUARD not in wrapped:
                unguarded.append(f"{selector}: animation outside the motion guard")
            if SUPPORT_GUARD not in wrapped:
                unguarded.append(f"{selector}: animation outside the support guard")
        if "scroll-behavior" in body and MOTION_GUARD not in wrapped:
            unguarded.append(f"{selector}: smooth scrolling outside the guard")
    assert not unguarded, unguarded


def test_nothing_is_hidden_without_animation():
    """Default state is visible. A content rule may never hide its element
    outside a keyframe, or the page is blank where animation is unsupported."""
    offenders = []
    for selector, body, wrappers in blocks(CSS):
        if selector.startswith("@keyframes") or "@keyframes" in " ".join(wrappers):
            continue
        if not any(re.search(re.escape(c) + r"\b", selector) for c in CONTENT):
            continue
        opacity = re.search(r"\bopacity\s*:\s*([\d.]+)", body)
        if opacity and float(opacity.group(1)) < 0.99:
            offenders.append(f"{selector}: opacity {opacity.group(1)}")
        if re.search(r"\bvisibility\s*:\s*hidden", body):
            offenders.append(f"{selector}: visibility hidden")
        if re.search(r"\bdisplay\s*:\s*none", body) and "[hidden]" not in selector:
            offenders.append(f"{selector}: display none")
    assert not offenders, offenders


def test_the_reveal_starts_visible_enough_to_paint():
    """`opacity: .001`, never `0`: if the animation never runs, the content is
    still painted rather than absent."""
    frames = re.findall(r"@keyframes\s+\w+\s*\{(.+?)\n\}", CSS, re.S)
    assert frames, "no keyframes found"
    for frame in frames:
        for value in re.findall(r"opacity:\s*([\d.]+)", frame):
            assert float(value) == 0.001 or float(value) == 1, value


def test_every_surface_defines_the_same_tokens():
    """A half-swapped surface is worse than no swap at all: ink that does not
    follow its background is unreadable for the length of one act."""
    root = dict(re.findall(r"(--[\w-]+):\s*([^;]+);", CSS.split(":root")[1]))
    surfaces = re.findall(r':root\[data-surface="(\w+)"\]\s*\{([^}]*)\}', CSS)
    assert len(surfaces) >= 12, f"only {len(surfaces)} surfaces defined"

    required = {"--bg", "--ink", "--ink-2", "--muted", "--rule", "--accent"}
    for name, body in surfaces:
        tokens = set(re.findall(r"(--[\w-]+):", body))
        if not required <= tokens:          # act 06 adds a second, smaller block
            continue
        for token in tokens:
            assert token in root, f"{name} sets {token}, which :root never defines"

    full = [n for n, b in surfaces if required <= set(re.findall(r"(--[\w-]+):", b))]
    assert len(full) == 12, f"{len(full)} acts carry a full palette, expected 12"


def test_the_page_travels_from_light_to_dark():
    """The arc is the point: the cover is paper, the night is black."""
    def background(name):
        block = re.search(r':root\[data-surface="%s"\]\s*\{([^}]*)\}' % name, CSS)
        return re.search(r"--bg:\s*#([0-9a-f]{6})", block.group(1)).group(1)

    def luminance(hex_colour):
        return sum(int(hex_colour[i:i + 2], 16) for i in (0, 2, 4)) / 3

    steps = [luminance(background(f"a{i:02d}")) for i in range(1, 7)]
    assert steps == sorted(steps, reverse=True), f"the run to the night is not monotonic: {steps}"
    assert luminance(background("a01")) > 200, "the cover should be paper"
    assert luminance(background("a06")) == 0, "the night should be black"


def test_no_surface_is_less_readable_than_the_default():
    """The recessive role is recessive, not invisible. The editorial default
    puts muted text at 3.6:1; a new act theme may not do worse."""
    def channels(value):
        return [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def luminance(value):
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
             for x in channels(value)]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

    def contrast(a, b):
        high, low = sorted((luminance(a), luminance(b)), reverse=True)
        return (high + 0.05) / (low + 0.05)

    thin = []
    for name, body in re.findall(r':root\[data-surface="(\w+)"\]\s*\{([^}]*)\}', CSS):
        tokens = dict(re.findall(r"(--[\w-]+):\s*#([0-9a-f]{6})", body))
        if "--bg" not in tokens:
            continue
        for role, floor in (("--muted", 3.5), ("--ink-2", 4.5), ("--ink", 7.0)):
            if role in tokens:
                got = contrast(tokens[role], tokens["--bg"])
                if got < floor:
                    thin.append(f"{name} {role} = {got:.1f}, floor {floor}")
    assert not thin, thin
