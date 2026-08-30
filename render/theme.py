"""
Palette and plotly template, in two surfaces: clear and dark.

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


#: The surface half of the palette. The hues above identify entities and never
#: move; these say what they are sitting on. `use()` rebinds them, so anything
#: reading `theme.CARD` follows the surface it is being drawn for.
SURFACES = {
    "dark": dict(
        CARD="#121214", INK="#f1eee8", INK_2="#a3a09a", MUTED="#6b6862",
        RULE="#2b2b31", GRID="#1c1c21", DIM="#2f2f36", LOST="#33333a",
        HEAT=[[0, "#131317"], [.2, "#17324f"], [.45, "#1f5ca3"],
              [.75, "#3d86d8"], [1, "#7fb6f2"]],
        SEQUENTIAL=[[0.0, "#10243c"], [0.25, "#17406e"], [0.5, "#1f5ca3"],
                    [0.75, "#2f7ad0"], [1.0, "#5ba1ee"]],
        CATEGORICAL=["#3987e5", "#199e70", "#c98500", "#008300",
                     "#9085e9", "#e66767", "#d55181", "#d95926"],
        USER_COLOR={"A": "#199e70", "B": "#d95926"},
        GOOD="#0ca30c", WARN="#fab219", SERIOUS="#ec835a",
    ),
    # The same eight hues, stepped down for a light ground so they keep 3:1
    # against it. Identity survives; only the lightness moves.
    "light": dict(
        CARD="#e4e0d8", INK="#17171b", INK_2="#4a4740", MUTED="#6f6b62",
        RULE="#b6afa1", GRID="#cfc9bd", DIM="#b3ada1", LOST="#c6c1b6",
        HEAT=[[0, "#e8e5de"], [.2, "#b9cbe0"], [.45, "#6f9ac6"],
              [.75, "#3a6ea8"], [1, "#1c4a7d"]],
        SEQUENTIAL=[[0.0, "#e8e5de"], [0.25, "#b9cbe0"], [0.5, "#6f9ac6"],
                    [0.75, "#3a6ea8"], [1.0, "#1c4a7d"]],
        CATEGORICAL=["#1c5fb0", "#0f7150", "#8f5f00", "#005f00",
                     "#6055c0", "#c03b3b", "#a82f5c", "#a63d15"],
        USER_COLOR={"A": "#0f7150", "B": "#a63d15"},
        GOOD="#0a7a0a", WARN="#8a6410", SERIOUS="#a8542c",
    ),
    # Act 05 sits between the paper and the night, on a warm olive ground.
    # The same hues again, desaturated to belong to it rather than shout
    # across it.
    "dusk": dict(
        CARD="#1b1a18", INK="#ece7dd", INK_2="#a8a29a", MUTED="#7d766c",
        RULE="#35322d", GRID="#242220", DIM="#3a3733", LOST="#3d3a35",
        HEAT=[[0, "#1b1a18"], [.2, "#2f4038"], [.45, "#456355"],
              [.75, "#5f8a73"], [1, "#8db69c"]],
        SEQUENTIAL=[[0.0, "#1b1a18"], [0.25, "#2f4038"], [0.5, "#456355"],
                    [0.75, "#5f8a73"], [1.0, "#8db69c"]],
        CATEGORICAL=["#5c86a8", "#57947a", "#a8894f", "#4d7d4d",
                     "#8579a8", "#b57a7a", "#a86b85", "#b5714a"],
        USER_COLOR={"A": "#57947a", "B": "#b5714a"},
        GOOD="#5c9a5c", WARN="#c9a45c", SERIOUS="#c08a6b",
    ),
}

#: Which surface the figures are being built for, and the names `use()`
#: rebinds. Declared here so a reader can see what a builder is reaching for
#: when it says `theme.CARD`.
MODE = "dark"
CARD = INK = INK_2 = MUTED = RULE = GRID = DIM = LOST = ""
GOOD = WARN = SERIOUS = ""
HEAT: list = []
SEQUENTIAL: list = []
CATEGORICAL: list = []
USER_COLOR: dict = {}

#: The names above, in the order a surface defines them.
SURFACE_NAMES = tuple(SURFACES["dark"])


def use(mode: str) -> None:
    """Point the module at one of the surfaces and rebuild the template."""
    global MODE
    MODE = mode
    globals().update(SURFACES[mode])
    register_template()


def register_template() -> None:
    axis = dict(
        showline=True, linecolor=RULE, linewidth=1.2, mirror=False,
        ticks="outside", tickcolor=RULE, ticklen=4,
        tickfont=dict(family=MONO, size=11, color=INK_2),
        gridcolor=GRID, zeroline=False,
        title=dict(font=dict(family=MONO, size=11, color=INK_2)),
    )
    pio.templates[f"balance_{MODE}"] = go.layout.Template(
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
            colorscale=dict(sequential=SEQUENTIAL),
        )
    )
    pio.templates.default = f"balance_{MODE}"


#: The module is never in a half-defined state: importing it picks a surface.
use("dark")
