"""Where the time and the blocks went."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from copytext import DOW, t, tpl

from .. import theme
from ..theme import CATEGORY_COLOR, MONO
from .frame import frame


def category_area(cat_daily: pd.DataFrame, title: str, h: int = 360) -> go.Figure:
    """Minutes per category and day, stacked. Fixed order, never by rank."""
    order = [c for c in CATEGORY_COLOR if c in set(cat_daily["category"])]
    wide = (cat_daily.pivot_table(index="day", columns="category",
                                  values="minutes", aggfunc="sum")
            .reindex(columns=order).fillna(0))
    roll = wide.rolling(3, min_periods=1, center=True).mean()
    fig = go.Figure()
    for cat in order:
        fig.add_trace(go.Scatter(
            x=roll.index, y=roll[cat], mode="lines", stackgroup="one",
            name=t(f"category.{cat}"),
            line=dict(width=1.2, color=theme.CARD),
            fillcolor=CATEGORY_COLOR[cat],
            hovertemplate=tpl("hover.category", category=t(f"category.{cat}")),
        ))
    # the last tick is a date, which needs more room than the template's 24px
    fig.update_layout(title=title, yaxis_title=t("axis.minutes_rolling"),
                      margin=dict(t=48, r=44, b=68, l=56))
    fig.update_xaxes(tickformat="%d %b")
    return frame(fig, h)


def top_bars(tot: pd.DataFrame, title: str, n: int = 10,
             h: int = 380) -> go.Figure:
    """Horizontal ranking by minutes, coloured by category."""
    d = tot.head(n).iloc[::-1]
    fig = go.Figure(go.Bar(
        x=d["minutes"], y=d["label"], orientation="h",
        marker=dict(color=[CATEGORY_COLOR.get(c, theme.MUTED) for c in d["category"]],
                    line=dict(color=theme.CARD, width=1.5)),
        text=[t("text.minutes", minutes=m) for m in d["minutes"]],
        textposition="outside",
        textfont=dict(family=MONO, size=11, color=theme.INK_2),
        customdata=d.assign(cat=[t(f"category.{c}") for c in d["category"]])
                    [["opens", "min_per_open", "cat"]].values,
        hovertemplate=tpl("hover.top_bars"),
    ))
    fig.update_layout(title=title, xaxis_title=t("axis.minutes_month"), bargap=.28,
                      margin=dict(t=48, r=48, b=56, l=110))
    fig.update_xaxes(range=[0, d["minutes"].max() * 1.24])
    fig.update_yaxes(tickfont=dict(family=MONO, size=11, color=theme.INK))
    return frame(fig, h, legend=False)


def hour_heat(hh: pd.DataFrame, user: str, h: int = 330) -> go.Figure:
    """Weekly clock: screen minutes by weekday and hour."""
    grid = (hh.pivot_table(index="dow", columns="hour", values="minutes",
                           aggfunc="sum")
            .reindex(index=range(7), columns=range(24)).fillna(0))
    fig = go.Figure(go.Heatmap(
        z=grid.values, x=list(range(24)), y=DOW,
        colorscale=theme.HEAT,
        xgap=2, ygap=2,
        colorbar=dict(title=dict(text=t("unit.min"),
                                 font=dict(family=MONO, size=10,
                                                      color=theme.INK_2)),
                      tickfont=dict(family=MONO, size=10, color=theme.INK_2),
                      outlinewidth=0, thickness=9, len=.8, x=1.02),
        hovertemplate=tpl("hover.heat"),
    ))
    fig.update_layout(title=t("chart.hour_heat", user=user),
                      xaxis_title=t("axis.local_time"))
    fig.update_xaxes(dtick=2, showgrid=False)
    fig.update_yaxes(showgrid=False, autorange="reversed",
                     tickfont=dict(family=MONO, size=11, color=theme.INK))
    return frame(fig, h, legend=False, hovermode="closest")


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------

def blocks_daily(bf: pd.DataFrame, title: str, h: int = 340) -> go.Figure:
    """Blocked attempts per day, stacked by category."""
    order = [c for c in CATEGORY_COLOR if c in set(bf["category"])]
    wide = (bf.pivot_table(index="day", columns="category", values="target",
                           aggfunc="count").reindex(columns=order).fillna(0))
    fig = go.Figure()
    for cat in order:
        fig.add_trace(go.Bar(
            x=wide.index, y=wide[cat], name=t(f"category.{cat}"),
            marker=dict(color=CATEGORY_COLOR[cat],
                        line=dict(color=theme.CARD, width=1.2)),
            hovertemplate=tpl("hover.blocks_category",
                              category=t(f"category.{cat}")),
        ))
    fig.update_layout(title=title, yaxis_title=t("axis.blocked_attempts"),
                      barmode="stack", bargap=.2)
    fig.update_xaxes(tickformat="%d %b")
    return frame(fig, h)


def blocks_by_hour(bf: pd.DataFrame, title: str, h: int = 300) -> go.Figure:
    """What time the wall gets hit; sensitive against the rest."""
    sens = bf[bf["category"].isin(["ADULT", "GAMBLING"])]
    rest = bf[~bf["category"].isin(["ADULT", "GAMBLING"])]
    fig = go.Figure()
    for name, d, color in ((t("series.ordinary"), rest, "#3987e5"),
                           (t("series.sensitive"), sens, "#e66767")):
        counts = d.groupby("hour").size().reindex(range(24)).fillna(0)
        fig.add_trace(go.Bar(
            x=list(range(24)), y=counts.values, name=name,
            marker=dict(color=color, line=dict(color=theme.CARD, width=1.2)),
            hovertemplate=tpl("hover.blocks_hour", name=name),
        ))
    fig.update_layout(title=title, xaxis_title=t("axis.local_time"),
                      yaxis_title=t("axis.attempts_month"), barmode="stack",
                      bargap=.15,
                      margin=dict(t=48, r=24, b=96, l=56),
                      legend=dict(y=-0.3))
    fig.update_xaxes(dtick=2)
    return frame(fig, h)
