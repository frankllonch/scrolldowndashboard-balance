"""The stylesheet, read as a contract.

Two of these are the ones that stop someone shipping a page that is blank in
a browser without scroll-driven animation.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "site" / "style.css").read_text()

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


def test_the_night_defines_every_token_it_changes():
    """A half-swapped surface is worse than no swap at all."""
    day = dict(re.findall(r"(--[\w-]+):\s*([^;]+);", CSS.split(":root")[1]))
    night = CSS.split('[data-night="on"]')[1].split("}")[0]
    for token in re.findall(r"(--[\w-]+):", night):
        assert token in day, f"{token} exists only at night"
    for token in ("--bg", "--ink", "--accent", "--grid"):
        assert token in night, f"{token} does not change at night"
