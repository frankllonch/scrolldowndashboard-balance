"""
Style · dark editorial (NTS Radio), Balance palette.

The same grid as the reference dashboard: uppercase mono type, hard rules, no
rounded corners anywhere, cards chained without gaps. What changes is the
plane: near-black background, bone ink, and the active block goes from blue to
bone.

The categorical palette is the same eight hues as the light theme, re-stepped
for a dark surface (OKLCH L 0.48 to 0.67, at least 3:1 on the surface).
Validated with `validate_palette.js --mode dark --surface #121214`: lightness
band OK, chroma OK, contrast OK, worst adjacent pair ΔE 10.3, which is the
floor band, so anything using 4 or more series carries a legend or a direct
label and never colour alone.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# Surfaces and ink
# ---------------------------------------------------------------------------
BG = "#0a0a0b"
PANEL = "#0f0f11"
CARD = "#121214"
RULE = "#2b2b31"
RULE_SOFT = "#1e1e23"
INK = "#f1eee8"          # bone
INK_2 = "#a3a09a"
MUTED = "#6b6862"
ACCENT = "#e8e4da"       # active block (replaces the light theme blue)
GRID = "#1c1c21"

# ---------------------------------------------------------------------------
# Categorical palette (fixed order, never cycled, never follows the ranking)
# ---------------------------------------------------------------------------
CATEGORICAL = ["#3987e5", "#199e70", "#c98500", "#008300",
               "#9085e9", "#e66767", "#d55181", "#d95926"]

#: Status: reserved, never reused as "series 4".
GOOD = "#0ca30c"
WARN = "#fab219"
SERIOUS = "#ec835a"
CRITICAL = "#e5484d"

#: Colour per content category: follows the entity, not its position.
CATEGORY_COLOR = {
    "SOCIAL_MEDIA":  "#3987e5",
    "MESSAGING":     "#199e70",
    "ENTERTAINMENT": "#c98500",
    "SHOPPING":      "#008300",
    "GAMING":        "#9085e9",
    "ADULT":         "#e66767",
    "NEWS":          "#d55181",
    "GAMBLING":      "#d95926",
    "OTHER":         "#55555c",     # deliberately neutral: it is the catch-all
}

#: One colour per user, stable across the whole dashboard.
USER_COLOR = {"A": "#199e70", "B": "#d95926"}

BLOCK_TYPE_COLOR = {"APP": "#3987e5", "URL": "#c98500", "NUDITY": "#e66767"}

MONO = "IBM Plex Mono, ui-monospace, SFMono-Regular, monospace"
SANS = "Inter, sans-serif"


def register_template() -> None:
    axis = dict(
        showline=True, linecolor=RULE, linewidth=1.2, mirror=False,
        ticks="outside", tickcolor=RULE, ticklen=4,
        tickfont=dict(family=MONO, size=11, color=INK_2),
        gridcolor=GRID, zeroline=False,
        title=dict(font=dict(family=MONO, size=11, color=INK_2)),
    )
    pio.templates["balance_dark"] = go.layout.Template(
        layout=dict(
            font=dict(family=SANS, color=INK_2, size=13),
            title=dict(font=dict(family=SANS, color=INK, size=15),
                       x=0.01, xanchor="left"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=CATEGORICAL,
            xaxis=axis, yaxis=axis,
            legend=dict(bgcolor="rgba(0,0,0,0)",
                        font=dict(family=MONO, size=11, color=INK_2),
                        orientation="h", yanchor="top", y=-0.18,
                        xanchor="left", x=0),
            margin=dict(t=48, r=24, b=68, l=56),
            hoverlabel=dict(bgcolor=CARD, bordercolor=RULE,
                            font=dict(family=MONO, size=12, color=INK)),
            hovermode="x unified",
            colorscale=dict(sequential=[
                [0.0, "#10243c"], [0.25, "#17406e"], [0.5, "#1f5ca3"],
                [0.75, "#2f7ad0"], [1.0, "#5ba1ee"]]),
        )
    )
    pio.templates.default = "balance_dark"
