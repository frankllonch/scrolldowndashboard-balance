"""The month on one axis, with the event rail under it."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from copytext import t, tpl

from .. import theme
from ..theme import MONO

# ---------------------------------------------------------------------------

#: (column, unit, colour slot, dash pattern, rules that read it)
#:
#: Divided by the maximum rather than rescaled min-max because zero has to stay
#: zero: for user A, "no late-night minutes" is the finding, and min-max would
#: paint it halfway up the axis.
#:
#: The dash pattern is a second encoding, not decoration. The worst adjacent
#: pair in this palette sits at ΔE 10.3 on this surface, which is inside the
#: floor band for protan colour blindness.
TRACKED = [
    ("night_min", "min", 0, "solid", "night_drift · night_streak"),
    ("night_end_min", "min", 1, "dash", "night_drift"),
    ("screen_min", "min", 2, "solid", "screen_jump"),
    ("longest_offline_h", "h", 3, "dot", "offline_record"),
    ("blocks", "", 4, "dashdot", "calm_week"),
    ("blocks_sensitive", "", 5, "dash", "sensitive_spike · filter_calm"),
    ("distract_pct", "%", 6, "dot", "focus_week"),
]

#: Series visible on open. The rest come in with a legend click: seven lines at
#: once do not read, and starting with all of them on forces the reader to
#: switch things off rather than on.
TRACKED_DEFAULT = {"night_min", "night_end_min", "screen_min"}

#: Height of the event rail, below the data zero.
_RAIL = -9


def _derive_tracked(df: pd.DataFrame) -> pd.DataFrame:
    """Derived columns that exist only for this chart."""
    df = df.copy()
    # The time of the last screen is expressed as minutes past 23:00, so zero
    # means "went dark on time" rather than "midnight".
    df["night_end_min"] = (df["night_end_h"] - 23) * 60
    df["longest_offline_h"] = df["longest_offline_s"] / 3600
    df["distract_pct"] = df["distract_share"] * 100
    return df


def tracked_series(df: pd.DataFrame, user: str, cursor,
                   nudge_days: set, alert_days: dict, positive_days: dict,
                   h: int = 560):
    """Every watched variable on one axis, each as a share of its own maximum.

    Below zero, an event rail sharing the time axis with the data that
    explains it.
    """
    d = _derive_tracked(df)
    fig = go.Figure()

    for i, (col, unit, slot, trazo, reglas) in enumerate(TRACKED):
        label = t(f"tracked.{col}")
        serie = d[col]
        tope = serie.max()
        if pd.isna(tope) or tope <= 0:
            # Series flat at zero: drawn anyway, hugging the axis, so it is
            # visible that the data exists and is zero.
            norm = serie.fillna(0) * 0
            note_ = t("series.no_activity")
        else:
            norm = serie / tope * 100
            note_ = ""
        fig.add_trace(go.Scatter(
            x=d["day"], y=norm, mode="lines+markers",
            name=f"{label}{note_}",
            # The group only titles the legend. With
            # `groupclick="toggleitem"` each entry toggles on its own; without
            # that option, Plotly switches the whole group off in one click.
            legendgroup="datos",
            legendgrouptitle=(dict(text=t("legend.tracked"))
                              if i == 0 else None),
            visible=True if col in TRACKED_DEFAULT else "legendonly",
            line=dict(color=theme.CATEGORICAL[slot], width=2, dash=trazo),
            marker=dict(size=5, color=theme.CATEGORICAL[slot],
                        symbol=["circle", "square", "diamond", "cross",
                                "x", "triangle-up", "pentagon"][slot]),
            customdata=serie,
            hovertemplate=tpl("hover.tracked", label=label, unit=unit,
                              rules=reglas),
        ))

    # --- event rail ---------------------------------------------------------
    events = [
        (t("event.nudge"), sorted(nudge_days), "circle", theme.WARN,
         t("event.nudge.detail")),
        (t("event.alert"),
         sorted(k for k, v in alert_days.items() if v == "sent"),
         "triangle-up", theme.SERIOUS, t("event.alert.detail")),
        (t("event.digest"),
         sorted(k for k, v in alert_days.items() if v == "summary"),
         "diamond", theme.INK_2, t("event.digest.detail")),
        (t("event.positive"), sorted(positive_days), "star", theme.GOOD,
         t("event.positive.detail")),
    ]
    for i, (name, days, symbol, color, detail) in enumerate(events):
        fig.add_trace(go.Scatter(
            x=days, y=[_RAIL] * len(days), mode="markers", name=name,
            legendgroup="events",
            legendgrouptitle=(dict(text=t("legend.emissions"))
                              if i == 0 else None),
            marker=dict(symbol=symbol, size=11, color=color,
                        line=dict(color=theme.CARD, width=1)),
            hovertemplate=tpl("hover.event", detail=detail),
            showlegend=True,
        ))

    fig.add_hline(y=0, line=dict(color=theme.RULE, width=1))
    fig.add_vline(x=cursor, line=dict(color=theme.INK, width=2))

    fig.update_layout(
        height=h, hovermode="x unified",
        yaxis_title=t("axis.pct_of_max"),
        margin=dict(t=44, r=24, b=120, l=64),
        legend=dict(orientation="h", y=-0.24, x=0, xanchor="left",
                    yanchor="top", groupclick="toggleitem",
                    font=dict(family=MONO, size=11, color=theme.INK_2),
                    grouptitlefont=dict(family=MONO, size=11, color=theme.MUTED)),
    )
    fig.update_yaxes(range=[_RAIL - 5, 108], dtick=25,
                     tickvals=[0, 25, 50, 75, 100],
                     ticktext=["0", "25", "50", "75", t("axis.pct_max_tick")])
    fig.update_xaxes(tickformat="%d %b")
    fig.add_annotation(xref="paper", x=0, y=_RAIL, yanchor="middle",
                       xanchor="right", xshift=-8, text=t("annotation.events"),
                       showarrow=False,
                       font=dict(family=MONO, size=10, color=theme.MUTED))
    return fig
