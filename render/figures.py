"""
Layer 3 · figures. None of them decides anything: they receive frames already
computed.

Rules honoured across all of them (from the `dataviz` skill):
* never two Y axes: two different magnitudes are two charts;
* colour follows the entity (user, category), never its rank;
* with 2 or more series there is always a legend, and with 4 or fewer also
  direct labels;
* 2 px of surface gap between stacked fills (`marker_line` in the panel colour);
* recessive grid and axes, thin marks.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from copytext import DOW, t, tpl

from .theme import (
    CARD, CATEGORICAL, CATEGORY_COLOR, GOOD, INK, INK_2, MONO, MUTED, RULE,
    SERIOUS, USER_COLOR, WARN,
)


def _direct_label(fig, x, y, text, color, dx=6):
    fig.add_annotation(x=x, y=y, text=f" {text}", showarrow=False,
                       xanchor="left", yanchor="middle", xshift=dx,
                       font=dict(family=MONO, size=11, color=color))


def _frame(fig, h=340, legend=True, **kw):
    fig.update_layout(height=h, showlegend=legend, **kw)
    return fig


# ---------------------------------------------------------------------------
# Time series
# ---------------------------------------------------------------------------

def compare_line(frames: dict[str, pd.DataFrame], col: str, title: str,
                 unit: str = "", smooth: int = 7, h: int = 340) -> go.Figure:
    """One smoothed line per user, with the raw daily point behind it."""
    fig = go.Figure()
    for user, df in frames.items():
        c = USER_COLOR[user]
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
        _direct_label(fig, df["day"].iloc[-1], sm.iloc[-1], user, c)
    fig.update_layout(title=title, yaxis_title=unit)
    fig.update_xaxes(tickformat="%d %b")
    return _frame(fig, h)


def daily_bars_vs_baseline(df: pd.DataFrame, col: str, baseline: str,
                           title: str, unit: str, user: str,
                           h: int = 320) -> go.Figure:
    """A daily bar against this user's own 14-day rolling median."""
    c = USER_COLOR[user]
    over = (df[col] > df[baseline]).fillna(False)

    # Two traces instead of one with mixed colours: this way the amber enters
    # the legend and explains itself, with no caption to read.
    fig = go.Figure()
    for mask, name, color in (
        (~over, t("series.at_or_below"), c),
        (over, t("series.above"), WARN),
    ):
        fig.add_trace(go.Bar(
            x=df["day"][mask], y=df[col][mask], name=name,
            marker=dict(color=color, line=dict(color=CARD, width=1.5)),
            hovertemplate=tpl("hover.day_value", unit=unit),
        ))
    fig.add_trace(go.Scatter(
        x=df["day"], y=df[baseline], mode="lines",
        line=dict(color=INK, width=1.6, dash="dot"),
        name=t("series.baseline"),
        hovertemplate=tpl("hover.baseline", unit=unit),
    ))
    fig.update_layout(title=title, yaxis_title=unit, bargap=.25,
                      barmode="overlay", margin=dict(t=48, r=24, b=86, l=56),
                      legend=dict(y=-0.22))
    fig.update_xaxes(tickformat="%d %b")
    return _frame(fig, h + 20)


def day_span(df: pd.DataFrame, user: str, h: int = 340) -> go.Figure:
    """From the first unlock to the last screen-off, day by day.

    The axis runs past 24 so the small hours sit at the top rather than
    dropping to the floor: what spills over the top is eating into the night.
    """
    c = USER_COLOR[user]
    start = df["first_pickup_h"]
    end = df["last_use_h"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["day"], y=(end - start), base=start,
        marker=dict(color=c, opacity=.55, line=dict(color=CARD, width=1.2)),
        name=t("series.day_with_phone"),
        customdata=list(zip(df["first_pickup_clock"], df["last_use_clock"])),
        hovertemplate=tpl("hover.day_span"),
    ))
    fig.add_hline(y=23, line=dict(color=WARN, width=1.2, dash="dot"),
                  annotation_text=t("annotation.night_start"),
                  annotation_position="right",
                  annotation_font=dict(family=MONO, size=10, color=WARN))
    fig.add_trace(go.Scatter(
        x=df["day"], y=end.rolling(7, min_periods=2, center=True).mean(),
        mode="lines", line=dict(color=INK, width=2),
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
    return _frame(fig, h)


def night_drift(frames: dict[str, pd.DataFrame], h: int = 340) -> go.Figure:
    """Screen minutes between 23:00 and 06:00, per night."""
    fig = go.Figure()
    for user, df in frames.items():
        c = USER_COLOR[user]
        # A series flat at zero reads as "data missing" unless you say so, and
        # the note goes in the legend, not in an annotation: over the bars it
        # covered what has to be read, and over the title it collided with it.
        flat = df["night_min"].max() < 0.5
        label = (t("series.night_flat", user=user, nights=len(df)) if flat
                 else t("series.user", user=user))
        fig.add_trace(go.Bar(
            x=df["day"], y=df["night_min"], name=label,
            marker=dict(color=c, line=dict(color=CARD, width=1.2)),
            hovertemplate=tpl("hover.night_drift", user=user),
        ))
    fig.update_layout(title=t("chart.night_drift"),
                      yaxis_title=t("unit.minutes"), barmode="group", bargap=.2)
    fig.update_xaxes(tickformat="%d %b")
    return _frame(fig, h)


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

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
            line=dict(width=1.2, color=CARD),
            fillcolor=CATEGORY_COLOR[cat],
            hovertemplate=tpl("hover.category", category=t(f"category.{cat}")),
        ))
    fig.update_layout(title=title, yaxis_title=t("axis.minutes_rolling"))
    fig.update_xaxes(tickformat="%d %b")
    return _frame(fig, h)


def top_bars(tot: pd.DataFrame, title: str, n: int = 10,
             h: int = 380) -> go.Figure:
    """Horizontal ranking by minutes, coloured by category."""
    d = tot.head(n).iloc[::-1]
    fig = go.Figure(go.Bar(
        x=d["minutes"], y=d["label"], orientation="h",
        marker=dict(color=[CATEGORY_COLOR.get(c, MUTED) for c in d["category"]],
                    line=dict(color=CARD, width=1.5)),
        text=[t("text.minutes", minutes=m) for m in d["minutes"]],
        textposition="outside",
        textfont=dict(family=MONO, size=11, color=INK_2),
        customdata=d.assign(cat=[t(f"category.{c}") for c in d["category"]])
                    [["opens", "min_per_open", "cat"]].values,
        hovertemplate=tpl("hover.top_bars"),
    ))
    fig.update_layout(title=title, xaxis_title=t("axis.minutes_month"), bargap=.28,
                      margin=dict(t=48, r=48, b=56, l=110))
    fig.update_xaxes(range=[0, d["minutes"].max() * 1.24])
    fig.update_yaxes(tickfont=dict(family=MONO, size=11, color=INK))
    return _frame(fig, h, legend=False)


def hour_heat(hh: pd.DataFrame, user: str, h: int = 330) -> go.Figure:
    """Weekly clock: screen minutes by weekday and hour."""
    grid = (hh.pivot_table(index="dow", columns="hour", values="minutes",
                           aggfunc="sum")
            .reindex(index=range(7), columns=range(24)).fillna(0))
    fig = go.Figure(go.Heatmap(
        z=grid.values, x=list(range(24)), y=DOW,
        colorscale=[[0, "#131317"], [.2, "#17324f"], [.45, "#1f5ca3"],
                    [.75, "#3d86d8"], [1, "#7fb6f2"]],
        xgap=2, ygap=2,
        colorbar=dict(title=dict(text=t("unit.min"),
                                 font=dict(family=MONO, size=10,
                                                      color=INK_2)),
                      tickfont=dict(family=MONO, size=10, color=INK_2),
                      outlinewidth=0, thickness=9, len=.8, x=1.02),
        hovertemplate=tpl("hover.heat"),
    ))
    fig.update_layout(title=t("chart.hour_heat", user=user),
                      xaxis_title=t("axis.local_time"))
    fig.update_xaxes(dtick=2, showgrid=False)
    fig.update_yaxes(showgrid=False, autorange="reversed",
                     tickfont=dict(family=MONO, size=11, color=INK))
    return _frame(fig, h, legend=False, hovermode="closest")


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
                        line=dict(color=CARD, width=1.2)),
            hovertemplate=tpl("hover.blocks_category",
                              category=t(f"category.{cat}")),
        ))
    fig.update_layout(title=title, yaxis_title=t("axis.blocked_attempts"),
                      barmode="stack", bargap=.2)
    fig.update_xaxes(tickformat="%d %b")
    return _frame(fig, h)


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
            marker=dict(color=color, line=dict(color=CARD, width=1.2)),
            hovertemplate=tpl("hover.blocks_hour", name=name),
        ))
    fig.update_layout(title=title, xaxis_title=t("axis.local_time"),
                      yaxis_title=t("axis.attempts_month"), barmode="stack",
                      bargap=.15,
                      margin=dict(t=48, r=24, b=96, l=56),
                      legend=dict(y=-0.3))
    fig.update_xaxes(dtick=2)
    return _frame(fig, h)


# ---------------------------------------------------------------------------
# Score
# ---------------------------------------------------------------------------

def score_line(frames: dict[str, pd.DataFrame], h: int = 340) -> go.Figure:
    fig = go.Figure()
    for user, df in frames.items():
        c = USER_COLOR[user]
        fig.add_trace(go.Scatter(
            x=df["day"], y=df["score"], mode="markers",
            marker=dict(size=4, color=c, opacity=.3),
            name=t("series.daily_plain", user=user), showlegend=False,
            hoverinfo="skip"))
        fig.add_trace(go.Scatter(
            x=df["day"], y=df["score_7d"], mode="lines",
            line=dict(color=c, width=2.6), name=t("series.user", user=user),
            hovertemplate=tpl("hover.score", user=user)))
        _direct_label(fig, df["day"].iloc[-1], df["score_7d"].iloc[-1], user, c)
    fig.update_layout(title=t("chart.score_line"),
                      yaxis_title=t("unit.score"))
    fig.update_yaxes(range=[0, 100], dtick=20)
    fig.update_xaxes(tickformat="%d %b")
    return _frame(fig, h)


def score_breakdown(contrib: pd.DataFrame, user: str, h: int = 300) -> go.Figure:
    """How many points each component contributes and how many it lets go."""
    d = contrib.iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=d["points"], y=d["component"], orientation="h",
        name=t("series.points_earned"),
        marker=dict(color=USER_COLOR[user], line=dict(color=CARD, width=1.5)),
        hovertemplate=tpl("hover.points_earned"),
        customdata=d["weight"] * 100))
    fig.add_trace(go.Bar(
        x=d["lost"], y=d["component"], orientation="h",
        name=t("series.points_lost"),
        marker=dict(color="#33333a", line=dict(color=CARD, width=1.5)),
        hovertemplate=tpl("hover.points_lost")))
    fig.update_layout(title=t("chart.score_breakdown", user=user),
                      barmode="stack", bargap=.3,
                      xaxis_title=t("axis.points"))
    fig.update_yaxes(tickfont=dict(family=MONO, size=11, color=INK))
    return _frame(fig, h)


# ---------------------------------------------------------------------------
# Month walkthrough
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
            line=dict(color=CATEGORICAL[slot], width=2, dash=trazo),
            marker=dict(size=5, color=CATEGORICAL[slot],
                        symbol=["circle", "square", "diamond", "cross",
                                "x", "triangle-up", "pentagon"][slot]),
            customdata=serie,
            hovertemplate=tpl("hover.tracked", label=label, unit=unit,
                              rules=reglas),
        ))

    # --- event rail ---------------------------------------------------------
    events = [
        (t("event.nudge"), sorted(nudge_days), "circle", WARN,
         t("event.nudge.detail")),
        (t("event.alert"),
         sorted(k for k, v in alert_days.items() if v == "sent"),
         "triangle-up", SERIOUS, t("event.alert.detail")),
        (t("event.digest"),
         sorted(k for k, v in alert_days.items() if v == "summary"),
         "diamond", INK_2, t("event.digest.detail")),
        (t("event.positive"), sorted(positive_days), "star", GOOD,
         t("event.positive.detail")),
    ]
    for i, (name, days, symbol, color, detail) in enumerate(events):
        fig.add_trace(go.Scatter(
            x=days, y=[_RAIL] * len(days), mode="markers", name=name,
            legendgroup="events",
            legendgrouptitle=(dict(text=t("legend.emissions"))
                              if i == 0 else None),
            marker=dict(symbol=symbol, size=11, color=color,
                        line=dict(color=CARD, width=1)),
            hovertemplate=tpl("hover.event", detail=detail),
            showlegend=True,
        ))

    fig.add_hline(y=0, line=dict(color=RULE, width=1))
    fig.add_vline(x=cursor, line=dict(color=INK, width=2))

    fig.update_layout(
        height=h, hovermode="x unified",
        yaxis_title=t("axis.pct_of_max"),
        margin=dict(t=44, r=24, b=120, l=64),
        legend=dict(orientation="h", y=-0.24, x=0, xanchor="left",
                    yanchor="top", groupclick="toggleitem",
                    font=dict(family=MONO, size=11, color=INK_2),
                    grouptitlefont=dict(family=MONO, size=11, color=MUTED)),
    )
    fig.update_yaxes(range=[_RAIL - 5, 108], dtick=25,
                     tickvals=[0, 25, 50, 75, 100],
                     ticktext=["0", "25", "50", "75", t("axis.pct_max_tick")])
    fig.update_xaxes(tickformat="%d %b")
    fig.add_annotation(xref="paper", x=0, y=_RAIL, yanchor="middle",
                       xanchor="right", xshift=-8, text=t("annotation.events"),
                       showarrow=False,
                       font=dict(family=MONO, size=10, color=MUTED))
    return fig


# ---------------------------------------------------------------------------
# Weekly summary
# ---------------------------------------------------------------------------

def week_evolution(w: pd.DataFrame, col: str, label: str, unit: str,
                   user: str, sel: int, h: int = 260) -> go.Figure:
    """One magnitude week by week, with the selected week highlighted.

    Short weeks carry a mark: a two-day week averaged next to a seven-day one
    reads as a drop that never happened.
    """
    c = USER_COLOR[user]
    labels = [t("label.week_partial" if p else "label.week", week=i)
              for i, p in zip(w.index, w["is_partial"])]
    fig = go.Figure(go.Bar(
        x=labels, y=w[col],
        marker=dict(color=[c if i == sel else "#2f2f36" for i in w.index],
                    line=dict(color=CARD, width=1.5)),
        text=[f"{v:,.0f}" if abs(v) >= 10 else f"{v:,.1f}" for v in w[col]],
        textposition="outside",
        textfont=dict(family=MONO, size=11, color=INK_2),
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
        marker=dict(color=USER_COLOR[user], line=dict(color=CARD, width=1.5)),
        name=t("series.week", week=week),
        hovertemplate=tpl("hover.week_day", unit=unit),
    ))
    if ref is not None:
        fig.add_hline(y=ref, line=dict(color=INK, width=1.6, dash="dot"),
                      annotation_text=t("annotation.prev_mean", mean=ref),
                      annotation_position="top left",
                      annotation_font=dict(family=MONO, size=10, color=INK_2))
    if cur[col].abs().max() == 0:
        fig.add_annotation(xref="paper", yref="paper", x=0.5, y=0.5,
                           text=t("annotation.no_activity_week"),
                           showarrow=False,
                           font=dict(family=MONO, size=11, color=MUTED))
        fig.update_yaxes(range=[0, 1], showticklabels=False)
    fig.update_layout(title=label, yaxis_title=unit, bargap=.3, height=h,
                      showlegend=False, margin=dict(t=52, r=20, b=40, l=54))
    return fig


def week_components(w: pd.DataFrame, sel: int, h: int = 320) -> go.Figure:
    """The five index components, week by week."""
    from balance.score import COMPONENTS
    fig = go.Figure()
    labels = [t("label.week", week=i) for i in w.index]
    for (col, label, *_rest), color in zip(COMPONENTS, CATEGORICAL):
        fig.add_trace(go.Scatter(
            x=labels, y=w[f"score_{col}"], mode="lines+markers", name=label,
            line=dict(color=color, width=2.2), marker=dict(size=8, color=color),
            hovertemplate=tpl("hover.component", label=label),
        ))
    fig.add_vline(x=t("label.week", week=sel),
                  line=dict(color=INK, width=1.6, dash="dot"))
    fig.update_layout(title=t("chart.week_components"),
                      yaxis_title=t("unit.score"), height=h,
                      margin=dict(t=44, r=20, b=76, l=54))
    fig.update_yaxes(range=[0, 105], dtick=25)
    return fig
