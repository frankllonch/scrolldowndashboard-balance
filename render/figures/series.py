"""Time series: one line or one bar per day."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from copytext import t, tpl

from .. import theme
from ..theme import MONO
from .frame import direct_label, frame


def compare_line(frames: dict[str, pd.DataFrame], col: str, title: str,
                 unit: str = "", smooth: int = 7, h: int = 340) -> go.Figure:
    """One smoothed line per user, with the raw daily point behind it."""
    fig = go.Figure()
    for user, df in frames.items():
        c = theme.USER_COLOR[user]
        fig.add_trace(go.Scatter(
            x=df["day"], y=df[col], mode="markers",
            marker=dict(size=4, color=c, opacity=.28),
            name=t("series.daily", user=user), legendgroup=user,
            showlegend=False,
            hovertemplate=tpl("hover.compare_daily", unit=unit, user=user),
        ))
        sm = df[col].rolling(smooth, min_periods=2, center=True).mean()
        fig.add_trace(go.Scatter(
            x=df["day"], y=sm, mode="lines", line=dict(color=c, width=2.4),
            name=t("series.user", user=user), legendgroup=user,
            hovertemplate=tpl("hover.compare_smoothed", unit=unit, user=user,
                              smooth=smooth),
        ))
        direct_label(fig, df["day"].iloc[-1], sm.iloc[-1], user, c)
    fig.update_layout(title=title, yaxis_title=unit)
    fig.update_xaxes(tickformat="%d %b")
    return frame(fig, h)


def daily_bars_vs_baseline(df: pd.DataFrame, col: str, baseline: str,
                           title: str, unit: str, user: str,
                           h: int = 320) -> go.Figure:
    """A daily bar against this user's own 14-day rolling median."""
    c = theme.USER_COLOR[user]
    over = (df[col] > df[baseline]).fillna(False)

    # Two traces instead of one with mixed colours: this way the amber enters
    # the legend and explains itself, with no caption to read.
    fig = go.Figure()
    for mask, name, color in (
        (~over, t("series.at_or_below"), c),
        (over, t("series.above"), theme.WARN),
    ):
        fig.add_trace(go.Bar(
            x=df["day"][mask], y=df[col][mask], name=name,
            marker=dict(color=color, line=dict(color=theme.CARD, width=1.5)),
            hovertemplate=tpl("hover.day_value", unit=unit),
        ))
    fig.add_trace(go.Scatter(
        x=df["day"], y=df[baseline], mode="lines",
        line=dict(color=theme.INK, width=1.6, dash="dot"),
        name=t("series.baseline"),
        hovertemplate=tpl("hover.baseline", unit=unit),
    ))
    fig.update_layout(title=title, yaxis_title=unit, bargap=.25,
                      barmode="overlay", margin=dict(t=48, r=24, b=86, l=56),
                      legend=dict(y=-0.22))
    fig.update_xaxes(tickformat="%d %b")
    return frame(fig, h + 20)


def day_span(df: pd.DataFrame, user: str, h: int = 340) -> go.Figure:
    """From the first unlock to the last screen-off, day by day.

    The axis runs past 24 so the small hours sit at the top rather than
    dropping to the floor: what spills over the top is eating into the night.
    """
    c = theme.USER_COLOR[user]
    start = df["first_pickup_h"]
    end = df["last_use_h"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["day"], y=(end - start), base=start,
        marker=dict(color=c, opacity=.55, line=dict(color=theme.CARD, width=1.2)),
        name=t("series.day_with_phone"),
        customdata=list(zip(df["first_pickup_clock"], df["last_use_clock"])),
        hovertemplate=tpl("hover.day_span"),
    ))
    # Inside the plotting area, not beside it: "right" puts the label past
    # the axis, where the card's own edge cuts it off.
    fig.add_hline(y=23, line=dict(color=theme.WARN, width=1.2, dash="dot"),
                  annotation_text=t("annotation.night_start"),
                  annotation_position="top right",
                  annotation_font=dict(family=MONO, size=10, color=theme.WARN))
    fig.add_trace(go.Scatter(
        x=df["day"], y=end.rolling(7, min_periods=2, center=True).mean(),
        mode="lines", line=dict(color=theme.INK, width=2),
        name=t("series.last_screen_mean"), hoverinfo="skip",
    ))
    lo = max(5, int(start.min()) - 1)
    hi = min(29, int(end.max()) + 2)
    ticks = list(range(lo + lo % 2, hi + 1, 2))
    fig.update_layout(title=t("chart.day_span", user=user),
                      yaxis_title=t("axis.local_time"))
    fig.update_yaxes(tickvals=ticks,
                     ticktext=[t("tick.hour", hour=h % 24) for h in ticks],
                     range=[lo, hi])
    fig.update_xaxes(tickformat="%d %b")
    return frame(fig, h)


def night_drift(frames: dict[str, pd.DataFrame], h: int = 340) -> go.Figure:
    """Screen minutes between 23:00 and 06:00, per night."""
    fig = go.Figure()
    for user, df in frames.items():
        c = theme.USER_COLOR[user]
        # A series flat at zero reads as "data missing" unless you say so, and
        # the note goes in the legend, not in an annotation: over the bars it
        # covered what has to be read, and over the title it collided with it.
        flat = df["night_min"].max() < 0.5
        label = (t("series.night_flat", user=user, nights=len(df)) if flat
                 else t("series.user", user=user))
        fig.add_trace(go.Bar(
            x=df["day"], y=df["night_min"], name=label,
            marker=dict(color=c, line=dict(color=theme.CARD, width=1.2)),
            hovertemplate=tpl("hover.night_drift", user=user),
        ))
    fig.update_layout(title=t("chart.night_drift"),
                      yaxis_title=t("unit.minutes"), barmode="group", bargap=.2)
    fig.update_xaxes(tickformat="%d %b")
    return frame(fig, h)
