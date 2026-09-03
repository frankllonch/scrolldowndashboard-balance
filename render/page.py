"""Compose `docs/index.html` from the hand-written shell and the acts.

Parts 1 and 3 are rendered once. Part 2 is rendered for every profile: the
default profile's copy goes into the page so it is complete before any script
runs, and both go into the payload so the switch has something to swap in.
"""

from __future__ import annotations

from pathlib import Path

from copytext import STRINGS, t

from .acts import ACTS, Context

SHELL = Path(__file__).parent.parent / "site" / "index.html"


def section(act, body: str) -> str:
    return (f'<header class="act-head"><p class="eyebrow">{t(act.eyebrow)}</p>'
            f'<h2 class="act-title">{t(act.title)}</h2></header>'
            f'<div class="act-body">{body}</div>')


def bridge(act) -> str:
    """The line that hands the reader to the next act.

    A scroll only works if each scene asks for the next one, so the handoff is
    part of the frame rather than something each act remembers to write. The
    last act has nothing to hand to.

    It is appended to the act body, not to the section around it: the profile
    switch replaces the whole body with the copy it stored, so a bridge added
    outside would survive the first paint and vanish on the first swap.
    """
    key = f"act.{act.id}.next"
    return "" if key not in STRINGS else f'<p class="act-next">{t(key)}</p>' 


def rail() -> str:
    """Thirteen acts in uppercase mono, grouped into the three parts."""
    out, part = "", None
    for act in ACTS:
        if act.part != part:
            out += "</ol>" if part is not None else ""
            out += (f'<p class="rail-part">{t(f"part.{act.part}")}</p><ol>')
            part = act.part
        out += (f'<li><a href="#act-{act.id}" data-rail="{act.id}">'
                f'<span class="num">{act.id}</span>{t(act.title)}</a></li>')
    return out + "</ol>"


def render(payload: dict, bundles: dict) -> str:
    """Returns the page. Part 2 is added to `payload` as a side effect."""
    default = payload["meta"]["profiles"][0]
    per_profile: dict[str, dict[str, str]] = {u: {} for u in payload["profiles"]}

    html = SHELL.read_text()
    for act in ACTS:
        if act.per_profile:
            for user in per_profile:
                ctx = Context(payload, bundles, user)
                per_profile[user][act.id] = act.builder(ctx) + bridge(act)
            body = per_profile[default][act.id]
        else:
            body = act.builder(Context(payload, bundles)) + bridge(act)
        html = html.replace(f"<!--act:{act.id}-->", section(act, body))

    # The default profile's part two is already in the document, so the page
    # keeps that copy rather than downloading it a second time.
    for user, acts in per_profile.items():
        payload["profiles"][user]["acts"] = {} if user == default else acts
    payload["meta"]["default_profile"] = default

    return (html
            .replace("<!--title-->", t("site.page_title"))
            .replace("<!--description-->", t("cover.standfirst"))
            .replace("<!--rail-->", rail())
            .replace("<!--pill-->",
                     f'{t("pill.label")} <span class="who">{default}</span>'))
