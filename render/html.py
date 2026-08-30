"""Small HTML builders shared by the acts.

Copy arrives already resolved and is trusted: the catalogue carries `<b>` and
`<code>` on purpose. Values that come from the data are escaped.
"""

from __future__ import annotations

from html import escape


def _attrs(**kw) -> str:
    out = ""
    for key, value in kw.items():
        if value in (None, False):
            continue
        name = key.rstrip("_").replace("_", "-")
        out += f" {name}" if value is True else f' {name}="{escape(str(value), True)}"'
    return out


def eyebrow(text: str) -> str:
    return f'<p class="eyebrow">{text}</p>'


def note(text: str, kind: str = "") -> str:
    return f'<p class="{" ".join(("note", kind)).strip()}">{text}</p>'


def lede(text: str) -> str:
    return f'<p class="lede">{text}</p>'


def tags(*labels: str) -> str:
    return "".join(f'<span class="tag">{x}</span>' for x in labels)


def stat(value: str, label: str) -> str:
    return (f'<div class="stat"><span class="stat-value">{escape(value)}</span>'
            f'<span class="stat-label">{label}</span></div>')


def kpis(items: list[dict]) -> str:
    """One continuous strip. `delta` is optional and never colour-coded: it is
    context, not a verdict."""
    cells = ""
    for item in items:
        delta = item.get("delta")
        cells += (f'<div class="kpi"><span class="kpi-label">{item["label"]}</span>'
                  f'<span class="kpi-value">{escape(str(item["value"]))}</span>'
                  + (f'<span class="kpi-delta">{escape(str(delta))}</span>'
                     if delta else "")
                  + "</div>")
    return f'<div class="kpis">{cells}</div>'


def table(columns: list[str], rows: list[list]) -> str:
    head = "".join(f"<th>{c}</th>" for c in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in row) + "</tr>"
        for row in rows)
    return (f'<div class="scroller"><table><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def pairs(items: list[list[str]]) -> str:
    return "".join(f'<div class="pair"><span>{escape(str(k))}</span>'
                   f"<span>{escape(str(v))}</span></div>" for k, v in items)


def chart(key: str, scope: str = "profile", size: str = "") -> str:
    """A mount point. The figure itself arrives from payload.json."""
    css = " ".join(("chart", size)).strip()
    return (f'<figure class="{css}"'
            f"{_attrs(data_figure=key, data_scope=scope)}></figure>")


def details(summary: str, body: str) -> str:
    return f"<details><summary>{summary}</summary>{body}</details>"


def phone(card: dict) -> str:
    ctas = "".join(
        f'<div class="phone-cta{" ghost" if c["ghost"] else ""}">{c["label"]}</div>'
        for c in card["ctas"])
    return (
        '<div class="phone"><div class="phone-bar">'
        f'<span>{escape(card["time"])}</span><span>{card["brand"]}</span></div>'
        f'<div class="phone-body"><p class="phone-eyebrow">{card["eyebrow"]}</p>'
        f'<p class="phone-h">{card["headline"]}</p>'
        f'<p class="phone-p">{card["body"]}</p>'
        f'{pairs(card["rows"])}{ctas}</div></div>')


def empty(text: str) -> str:
    return f'<div class="empty">{text}</div>'


def channel(label: str, inner: str) -> str:
    return f'<div class="channel">{eyebrow(label)}{inner}</div>'


def grid(*blocks: str, cols: int = 2) -> str:
    return f'<div class="grid cols-{cols}">{"".join(blocks)}</div>'


def slot(name: str, inner: str = "") -> str:
    """Content the sliders replace. Rendered at build time so the page is
    complete before any script runs."""
    return f'<div{_attrs(data_slot=name)}>{inner}</div>'
