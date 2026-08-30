"""The index: the curve, the breakdown, and the weekly panels."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from copytext import DOW, t, tpl

from .. import theme
from ..theme import MONO
from .frame import direct_label, frame


def score_line(frames: dict[str, pd.DataFrame], h: int = 340) -> go.Figure:
    fig = go.Figure()
    for user, df in frames.items():
        c = theme.USER_COLOR[user]
        fig.add_trace(go.Scatter(
            x=df["day"], y=df["score"], mode="markers",
            marker=dict(size=4, color=c, opacity=.3),
            name=t("series.daily_plain", user=user), showlegend=False,
            hoverinfo="skip"))
        fig.add_trace(go.Scatter(
            x=df["day"], y=df["score_7d"], mode="lines",
            line=dict(color=c, width=2.6), name=t("series.user", user=user),
            hovertemplate=tpl("hover.score", user=user)))
        direct_label(fig, df["day"].iloc[-1], df["score_7d"].iloc[-1], user, c)
    fig.update_layout(title=t("chart.score_line"),
                      yaxis_title=t("unit.score"))
    fig.update_yaxes(range=[0, 100], dtick=20)
    fig.update_xaxes(tickformat="%d %b")
    return frame(fig, h)


def score_breakdown(contrib: pd.DataFrame, user: str, h: int = 300) -> go.Figure:
    """How many points each component contributes and how many it lets go."""
    d = contrib.iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=d["points"], y=d["component"], orientation="h",
        name=t("series.points_earned"),
        marker=dict(color=theme.USER_COLOR[user], line=dict(color=theme.CARD, width=1.5)),
        hovertemplate=tpl("hover.points_earned"),
        customdata=d["weight"] * 100))
    fig.add_trace(go.Bar(
        x=d["lost"], y=d["component"], orientation="h",
        name=t("series.points_lost"),
        marker=dict(color=theme.LOST, line=dict(color=theme.CARD, width=1.5)),
        hovertemplate=tpl("hover.points_lost")))
    # "Long disconnection" is the longest tick label on the page and it sits
    # in the left margin, so that margin is sized for it rather than the
    # template's 56px, which cut it off on a phone.
    fig.update_layout(title=t("chart.score_breakdown", user=user),
                      barmode="stack", bargap=.3,
                      xaxis_title=t("axis.points"),
                      margin=dict(t=48, r=24, b=68, l=124))
    fig.update_yaxes(tickfont=dict(family=MONO, size=11, color=theme.INK))
    return frame(fig, h)


# ---------------------------------------------------------------------------
# Month walkthrough


def week_evolution(w: pd.DataFrame, col: str, label: str, unit: str,
                   user: str, sel: int, h: int = 260) -> go.Figure:
    """One magnitude week by week, with the selected week highlighted.

    Short weeks carry a mark: a two-day week averaged next to a seven-day one
    reads as a drop that never happened.
    """
    c = theme.USER_COLOR[user]
    labels = [t("label.week_partial" if p else "label.week", week=i)
              for i, p in zip(w.index, w["is_partial"])]
    fig = go.Figure(go.Bar(
        x=labels, y=w[col],
        marker=dict(color=[c if i == sel else theme.DIM for i in w.index],
                    line=dict(color=theme.CARD, width=1.5)),
        text=[f"{v:,.0f}" if abs(v) >= 10 else f"{v:,.1f}" for v in w[col]],
        textposition="outside",
        textfont=dict(family=MONO, size=11, color=theme.INK_2),
        hovertemplate=tpl("hover.week", unit=unit, label=label),
    ))
    fig.update_layout(title=label, yaxis_title=unit, bargap=.35,
                      height=h, showlegend=False,
                      margin=dict(t=44, r=20, b=36, l=54))
    fig.update_yaxes(range=[0, max(w[col].max() * 1.25, 0.1)])
    return fig


def week_days(df: pd.DataFrame, week: int, col: str, label: str, unit: str,
              user: str, h: int = 300) -> go.Figure:
    """The days of the selected week against the mean of previous weeks."""
    cur = df[df["week"] == week]
    prev = df[df["week"] < week]
    ref = prev[col].mean() if len(prev) else None

    fig = go.Figure(go.Bar(
        x=[DOW[d] for d in cur["dow"]], y=cur[col],
        marker=dict(color=theme.USER_COLOR[user], line=dict(color=theme.CARD, width=1.5)),
        name=t("series.week", week=week),
        hovertemplate=tpl("hover.week_day", unit=unit),
    ))
    if ref is not None:
        fig.add_hline(y=ref, line=dict(color=theme.INK, width=1.6, dash="dot"),
                      annotation_text=t("annotation.prev_mean", mean=ref),
                      annotation_position="top left",
                      annotation_font=dict(family=MONO, size=10, color=theme.INK_2))
    if cur[col].abs().max() == 0:
        fig.add_annotation(xref="paper", yref="paper", x=0.5, y=0.5,
                           text=t("annotation.no_activity_week"),
                           showarrow=False,
                           font=dict(family=MONO, size=11, color=theme.MUTED))
        fig.update_yaxes(range=[0, 1], showticklabels=False)
    fig.update_layout(title=label, yaxis_title=unit, bargap=.3, height=h,
                      showlegend=False, margin=dict(t=52, r=20, b=40, l=54))
    return fig


def week_components(w: pd.DataFrame, sel: int, h: int = 320) -> go.Figure:
    """The five index components, week by week."""
    from balance.score import COMPONENTS
    fig = go.Figure()
    labels = [t("label.week", week=i) for i in w.index]
    for (col, label, *_rest), color in zip(COMPONENTS, theme.CATEGORICAL):
        fig.add_trace(go.Scatter(
            x=labels, y=w[f"score_{col}"], mode="lines+markers", name=label,
            line=dict(color=color, width=2.2), marker=dict(size=8, color=color),
            hovertemplate=tpl("hover.component", label=label),
        ))
    fig.add_vline(x=t("label.week", week=sel),
                  line=dict(color=theme.INK, width=1.6, dash="dot"))
    fig.update_layout(title=t("chart.week_components"),
                      yaxis_title=t("unit.score"), height=h,
                      margin=dict(t=44, r=20, b=76, l=54))
    fig.update_yaxes(range=[0, 105], dtick=25)
    return fig
