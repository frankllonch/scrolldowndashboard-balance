"""
Balance · device behaviour explorer.

A reading dashboard: what is in the events, what metrics come out of them, and
what story the two profiles tell over May 2026.

    streamlit run app.py
"""

from __future__ import annotations

from collections import Counter

import pandas as pd
import streamlit as st

from render import figures, theme
from balance.events import SENSITIVE, load
from balance.metrics import (
    blocks_frame, category_daily, daily_frame, hourly_heat, totals, weekly_frame,
)
from balance.intelligence import (
    ALERT_BUDGET, NUDGE_AFTER_MIN, emissions, evaluate_alerts,
    evaluate_positives, month_replay, nudge_summary, replay_nudge,
)
from balance.score import COMPONENTS, add_score, contributions
from copytext import MONTHS, t

st.set_page_config(page_title=t("site.page_title"),
                   page_icon="◐", layout="wide",
                   initial_sidebar_state="expanded")
theme.register_template()
st.markdown(theme.CSS, unsafe_allow_html=True)
st.markdown(theme.PHONE_CSS, unsafe_allow_html=True)

DATA = {"A": "data/events_user_a.json", "B": "data/events_user_b.json"}

#: Only profile B has a guardian assigned. A is an adult: the alert rules run
#: all the same, but there is no recipient to notify, so their signals only
#: feed their own index and nudges.
HAS_GUARDIAN = {"A": False, "B": True}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=t("loading.spinner"))
def build(user: str):
    tl = load(DATA[user], user)
    df = add_score(daily_frame(tl))
    # days truncated by the file edge stay out of EVERY view, not only the
    # daily frame, or the totals stop matching.
    days = set(df["day"])
    nudges = replay_nudge(tl, df)
    positives = evaluate_positives(df, HAS_GUARDIAN[user])
    replay = month_replay(df, nudges, positives)

    weekly = weekly_frame(df)
    for col, *_ in COMPONENTS:
        weekly[f"score_{col}"] = df.groupby("week")[f"score_{col}"].mean()

    return {
        "df": df,
        "apps": totals(tl, df, "app"),
        "sites": totals(tl, df, "site"),
        "cats": category_daily(df),
        "heat": hourly_heat(tl, days),
        "blocks": blocks_frame(tl, days),
        "events": tl.events,
        "anomalies": dict(tl.anomalies),
        "n_intervals": len(tl.intervals),
        "screen_h": sum(i.seconds for i in tl.intervals) / 3600,
        "attributed_h": sum(u.seconds for u in tl.usages) / 3600,
        "alerts": evaluate_alerts(df),
        "positives": positives,
        "weekly": weekly,
        "nudges": nudges,
        "replay": replay,
        "emissions": emissions(replay),
    }


U = {u: build(u) for u in DATA}
F = {u: U[u]["df"] for u in DATA}


# ---------------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------------

def note(text: str, kind: str = "") -> None:
    st.markdown(f'<div class="note {kind}">{text}</div>', unsafe_allow_html=True)


def eyebrow(text: str) -> None:
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)


def empty_box(text: str) -> None:
    """An explicit gap. A drawn phone saying "nothing is shown" is a
    notification announcing there is no notification: it takes up the same room
    and reads as loud as the ones that do exist."""
    st.markdown(f'<div class="empty">{text}</div>', unsafe_allow_html=True)


def fecha(d) -> str:
    """Short date, locale-independent."""
    return t("fmt.date", day=d.day, month=MONTHS[d.month - 1])


def reloj(h) -> str:
    """Shifted-axis hour (24 to 28 = small hours) to HH:MM. It is None when
    there was no screen in the band, which is user A's normal case."""
    if h is None or pd.isna(h):
        return t("value.no_use")
    return t("fmt.clock", h=int(h % 24), m=int(h % 1 * 60))


def hm(minutes: float) -> str:
    h, m = divmod(int(round(minutes)), 60)
    return t("fmt.hm", h=h, m=m) if h else t("fmt.m", m=m)


def kpis(items: list[tuple[str, str, str | None]]) -> None:
    for col, (label, value, delta) in zip(st.columns(len(items)), items):
        col.metric(label, value, delta, delta_color="off" if delta else "normal")


def wk(df: pd.DataFrame, col: str, week: int, how: str = "mean") -> float:
    s = df[df["week"] == week][col]
    return getattr(s, how)()


def row_pair(label: str, value: str) -> str:
    return f"<div class='phone-row'><span>{label}</span><span>{value}</span></div>"


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title(t("site.brand"))
    st.caption(t("site.tagline"))
    st.markdown("---")
    eyebrow(t("sidebar.footprint.eyebrow"))
    for u in DATA:
        st.caption(t("sidebar.footprint.line", user=u,
                     events=len(U[u]["events"]), days=len(F[u]),
                     intervals=U[u]["n_intervals"]))
    st.markdown("---")
    eyebrow(t("sidebar.scope.eyebrow"))
    st.caption(t("sidebar.scope.body"))
    st.markdown("---")
    eyebrow(t("sidebar.notifications.eyebrow"))
    for u in DATA:
        n = (sum(1 for x in U[u]["alerts"] if x.decision == "sent")
             if HAS_GUARDIAN[u] else None)
        st.caption(t("sidebar.notifications.line", user=u,
                     sent=(t("sidebar.notifications.to_guardian", n=n)
                           if n is not None else t("value.no_guardian")),
                     nudges=sum(1 for x in U[u]["nudges"] if x.fired)))


st.title(t("site.title"))
st.caption(t("site.subtitle", profiles=len(DATA),
             events=sum(len(U[u]["events"]) for u in DATA),
             days=len(F["A"])))

# The selector lives in the body, not the sidebar: if someone collapses it,
# switching profile should not depend on finding the button to reopen it. The
# sidebar keeps context only.
_sel, _rest = st.columns([1, 4])
with _sel:
    who = st.radio(t("profile.label"), ["A", "B"], horizontal=True, key="who",
                   help=t("profile.help"))

TABS = st.tabs([t("tab.overview"), t("tab.week"), t("tab.day"), t("tab.night"),
                t("tab.time"), t("tab.blocks"), t("tab.engine"), t("tab.hood")])


# ===========================================================================
# 1 · OVERVIEW
# ===========================================================================
with TABS[0]:
    a, b = F["A"], F["B"]

    st.markdown("### " + t("overview.profiles.title"))
    note(t("overview.profiles.body",
           a_screen=hm(a.screen_min.mean()), a_pickups=a.pickups.mean(),
           a_apps=a.distinct_apps.mean(),
           b_screen=hm(b.screen_min.mean()), b_pickups=b.pickups.mean(),
           b_apps=b.distinct_apps.mean(), b_blocks=b.blocks.sum(),
           b_sensitive=b.blocks_sensitive.sum()))

    c1, c2 = st.columns(2)
    for col, u in ((c1, "A"), (c2, "B")):
        d = F[u]
        with col:
            eyebrow(t("overview.index.eyebrow", user=u))
            st.markdown(
                f"<div style='font-family:{theme.MONO};font-size:3.4rem;"
                f"line-height:1;color:{theme.USER_COLOR[u]};font-weight:600'>"
                f"{d.score.mean():.0f}<span style='font-size:1.1rem;color:{theme.MUTED}'>"
                f"{t('overview.index.scale')}</span></div>"
                f"<div class='eyebrow' style='margin-top:.35rem'>"
                f"{t('overview.index.weeks', first=wk(d, 'score', 1), last=wk(d, 'score', 4))}"
                f"</div>",
                unsafe_allow_html=True)

    st.markdown("")
    for u, d in (("A", a), ("B", b)):
        kpis([
            (t("kpi.screen_day", user=u), hm(d.screen_min.mean()), None),
            (t("kpi.unlocks_day", user=u), f"{d.pickups.mean():.0f}", None),
            (t("kpi.night_day", user=u),
             f"{d.night_min.mean():.0f} {t('unit.min')}", None),
            (t("kpi.blocks_month", user=u), f"{d.blocks.sum():,.0f}", None),
            (t("kpi.sensitive", user=u), f"{d.blocks_sensitive.sum():.0f}", None),
        ])

    st.markdown("### " + t("overview.score.title"))
    st.plotly_chart(figures.score_line(F), width="stretch", key="k_score")
    note(t("overview.score.note",
           a_mean=a.score.mean(), a_min=a.score.min(), a_max=a.score.max(),
           b_first=wk(b, "score", 1), b_last=wk(b, "score", 4),
           b_drop=wk(b, "score", 1) - wk(b, "score", 4),
           b_night_first=wk(b, "score_night_min", 1),
           b_night_last=wk(b, "score_night_min", 4)),
         "warn")

    st.markdown("### " + t("overview.moves.title"))
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(figures.compare_line(F, "screen_min",
                        t("chart.screen_per_day"), t("unit.minutes")),
                        width="stretch", key="k_screen")
        st.plotly_chart(figures.compare_line(F, "pickups",
                        t("chart.pickups_per_day"), t("unit.unlocks")),
                        width="stretch", key="k_pickups")
    with g2:
        st.plotly_chart(figures.compare_line(F, "night_min",
                        t("chart.night_per_day"), t("unit.minutes")),
                        width="stretch", key="k_night")
        st.plotly_chart(figures.compare_line(F, "blocks",
                        t("chart.blocks_per_day"), t("unit.blocks")),
                        width="stretch", key="k_blocks")

    d_screen = (wk(b, "screen_min", 4) / wk(b, "screen_min", 1) - 1) * 100
    d_pick = (wk(b, "pickups", 4) / wk(b, "pickups", 1) - 1) * 100
    d_night = wk(b, "night_min", 4) / max(wk(b, "night_min", 1), .01)
    st.markdown("### " + t("overview.compare.title"))
    st.dataframe(pd.DataFrame([
        (t("row.screen_per_day"), f"{wk(b,'screen_min',1):.0f} {t('unit.min')}",
         f"{wk(b,'screen_min',4):.0f} {t('unit.min')}", f"{d_screen:+.0f} %"),
        (t("row.unlocks_per_day"), f"{wk(b,'pickups',1):.0f}",
         f"{wk(b,'pickups',4):.0f}", f"{d_pick:+.0f} %"),
        (t("row.night_minutes"), f"{wk(b,'night_min',1):.1f} {t('unit.min')}",
         f"{wk(b,'night_min',4):.0f} {t('unit.min')}",
         t("delta.times", n=d_night)),
        (t("row.night_pickups"), f"{wk(b,'night_pickups',1):.1f}",
         f"{wk(b,'night_pickups',4):.1f}",
         t("delta.times",
           n=wk(b, "night_pickups", 4) / max(wk(b, "night_pickups", 1), .01))),
        (t("row.blocks_per_day"), f"{wk(b,'blocks',1):.0f}",
         f"{wk(b,'blocks',4):.0f}",
         f"{(wk(b,'blocks',4)/wk(b,'blocks',1)-1)*100:+.0f} %"),
    ], columns=[t("table.col.metric"), t("table.col.week_one"),
                t("table.col.week_four"), t("table.col.change")]),
        width="stretch", hide_index=True)
    note(t("overview.compare.note", screen=d_screen, pickups=d_pick,
           night=d_night), "serious")

# ===========================================================================
# 2 · WEEKLY SUMMARY
# ===========================================================================
with TABS[1]:
    d = F[who]
    w = U[who]["weekly"]
    st.markdown("### " + t("week.title", user=who))

    weeks = list(w.index)
    sel = st.select_slider(
        t("week.slider.label"), options=weeks,
        value=weeks[-2] if len(weeks) > 1 else weeks[-1],
        format_func=lambda i: t("week.slider.option_short" if w.loc[i, "is_partial"]
                                else "week.slider.option", week=i),
        key=f"week_{who}")
    cur = w.loc[sel]
    prev = w.loc[sel - 1] if sel - 1 in w.index else None

    st.caption(
        t("week.range", start=fecha(cur["start"]), end=fecha(cur["end"]),
          days=int(cur["days"]))
        + (t("week.range.partial") if cur["is_partial"] else "")
    )

    def delta(col, unit="", dec=0):
        """Change against the previous week, in the metric's own unit.

        A change that rounds to zero is not shown: "+0 min" with a green arrow
        says something improved when nothing moved.
        """
        if prev is None or pd.isna(prev[col]):
            return None
        v = cur[col] - prev[col]
        if abs(round(v, dec)) < 10 ** -dec / 2 or f"{v:.{dec}f}".strip("-+") in ("0", "0.0"):
            return t("value.no_change")
        return f"{v:+.{dec}f} {unit}".strip()

    kpis([
        (t("week.kpi.screen"), hm(cur["screen_min"]),
         delta("screen_min", t("unit.min"))),
        (t("week.kpi.pickups"), f"{cur['pickups']:.0f}", delta("pickups")),
        (t("week.kpi.night"), f"{cur['night_min']:.0f} {t('unit.min')}",
         delta("night_min", t("unit.min"))),
        (t("week.kpi.offline"), f"{cur['longest_offline_h']:.1f} {t('unit.hours')}",
         delta("longest_offline_h", t("unit.hours"), dec=1)),
        (t("week.kpi.best_offline"),
         f"{cur['best_offline_h']:.1f} {t('unit.hours')}",
         cur["best_offline_when"]),
        (t("week.kpi.blocks"), f"{cur['blocks']:.1f}", delta("blocks", dec=1)),
        (t("week.kpi.score"), f"{cur['score']:.0f}", delta("score", dec=0)),
    ])

    st.markdown("")
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(figures.week_evolution(
            w, "screen_min", t("chart.week.screen"), t("unit.min"), who, sel),
            width="stretch", key=f"we_screen_{who}")
        st.plotly_chart(figures.week_evolution(
            w, "night_min", t("chart.week.night"), t("unit.min"), who, sel),
            width="stretch", key=f"we_night_{who}")
    with g2:
        st.plotly_chart(figures.week_evolution(
            w, "pickups", t("chart.week.pickups"), "", who, sel),
            width="stretch", key=f"we_pick_{who}")
        st.plotly_chart(figures.week_evolution(
            w, "blocks", t("chart.week.blocks"), "", who, sel),
            width="stretch", key=f"we_blocks_{who}")
    st.caption(t("week.partial_footnote"))

    st.plotly_chart(figures.week_components(w, sel), width="stretch",
                    key=f"we_comp_{who}")

    st.markdown("#### " + t("week.days.title", week=sel))
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(figures.week_days(
            d, sel, "screen_min", t("chart.week_days.screen", week=sel),
            t("unit.min"), who), width="stretch", key=f"wd_screen_{who}")
    with c2:
        st.plotly_chart(figures.week_days(
            d, sel, "night_min", t("chart.week_days.night", week=sel),
            t("unit.min"), who), width="stretch", key=f"wd_night_{who}")

    st.markdown("#### " + t("week.compare.title"))
    rows = [
        (t("row.screen_per_day"), "screen_min", t("unit.min"), 0),
        (t("row.unlocks_per_day"), "pickups", "", 0),
        (t("row.night_per_night"), "night_min", t("unit.min"), 0),
        (t("row.longest_offline"), "longest_offline_h", t("unit.hours"), 1),
        (t("row.distinct_apps"), "distinct_apps", "", 1),
        (t("row.switches_per_hour"), "switches_per_screen_hour", "", 0),
        (t("row.distract_share"), "distract_share", t("unit.percent"), 0),
        (t("row.blocks_per_day"), "blocks", "", 1),
        (t("row.index"), "score", "", 0),
    ]
    tbl = []
    for label, col, unit, dec in rows:
        mult = 100 if unit == t("unit.percent") else 1
        # Rounded BEFORE subtracting: otherwise the change does not match the
        # two columns beside it and looks like an arithmetic error.
        v = round(cur[col] * mult, dec)
        pv = (round(prev[col] * mult, dec)
              if prev is not None and not pd.isna(prev[col]) else None)
        med = round(w[col].median() * mult, dec)
        if pv is None:
            var = t("value.not_available")
        elif abs(v - pv) < 10 ** -dec / 2:
            var = t("value.no_change")
        else:
            var = f"{v - pv:+.{dec}f} {unit}".strip()
        tbl.append({
            t("table.col.metric"): label,
            t("table.col.week_selected", week=sel): f"{v:.{dec}f} {unit}".strip(),
            t("table.col.previous_week"): (f"{pv:.{dec}f} {unit}".strip()
                                           if pv is not None
                                           else t("value.not_available")),
            t("table.col.period_median"): f"{med:.{dec}f} {unit}".strip(),
            t("table.col.change"): var,
        })
    st.dataframe(pd.DataFrame(tbl), width="stretch", hide_index=True)

    st.markdown("#### " + t("week.emitted.title", week=sel))
    wk_days = set(d[d["week"] == sel]["day"])
    wk_em = [e for e in U[who]["emissions"] if e["day"] in wk_days]
    resumen = [x for x in U[who]["positives"]
               if x.decision == "summary" and x.day in wk_days]

    if wk_em:
        st.dataframe(pd.DataFrame([{
            t("table.col.date"): fecha(e["day"]),
            t("table.col.destination"): e["destination"],
            t("table.col.type"): e["type"],
            t("table.col.detail"): e["detail"],
        } for e in wk_em]), width="stretch", hide_index=True)
    else:
        st.caption(t("week.emitted.none"))

    if resumen:
        st.markdown(t("week.recorded.title"))
        for x in resumen:
            st.markdown(row_pair(x.headline, x.reason.split(".")[0]),
                        unsafe_allow_html=True)


# ===========================================================================
# 3 · DAILY RHYTHM
# ===========================================================================
with TABS[2]:
    d = F[who]
    st.markdown("### " + t("day.title", user=who))

    kpis([
        (t("day.kpi.screen"), hm(d.screen_min.mean()),
         t("day.kpi.screen.delta", sd=d.screen_min.std())),
        (t("day.kpi.sessions"), f"{d.sessions.mean():.0f}",
         t("day.kpi.sessions.delta", median=d.median_session_s.mean() / 60)),
        (t("day.kpi.pickups"), f"{d.pickups.mean():.0f}",
         t("day.kpi.pickups.delta", glances=d.glances.mean())),
        (t("day.kpi.first_pickup"), d.first_pickup_clock.mode().iloc[0],
         t("day.kpi.first_pickup.delta", median=d.first_pickup_h.median())),
        (t("day.kpi.offline"), f"{d.longest_offline_s.mean()/3600:.1f} {t('unit.hours')}",
         t("day.kpi.offline.delta", best=d.longest_offline_h.max(),
           when=d.loc[d.longest_offline_h.idxmax(), "longest_offline_when"])),
        (t("day.kpi.switches"), f"{d.switches_per_screen_hour.mean():.0f}",
         t("day.kpi.switches.delta", apps=d.distinct_apps.mean())),
    ])

    st.markdown("")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(figures.daily_bars_vs_baseline(
            d, "screen_min", "screen_min_baseline",
            t("chart.day.screen", user=who), t("unit.minutes"), who),
            width="stretch", key="k_bar_screen")
    with c2:
        st.plotly_chart(figures.daily_bars_vs_baseline(
            d, "pickups", "pickups_baseline",
            t("chart.day.pickups", user=who), t("unit.unlocks"), who),
            width="stretch", key="k_bar_pickups")
    st.caption(t("day.baseline.caption"))

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(figures.hour_heat(U[who]["heat"], who),
                        width="stretch", key="k_heat")
    with c4:
        st.plotly_chart(figures.day_span(d, who), width="stretch", key="k_span")

    wknd = d.groupby("is_weekend")[["screen_min", "pickups", "night_min"]].mean()
    diff = wknd.loc[True, "screen_min"] - wknd.loc[False, "screen_min"]
    if who == "A":
        note(t("day.note.a",
               last_use=d.last_use_clock.mode().iloc[0],
               weekend=wknd.loc[True, "screen_min"],
               weekday=wknd.loc[False, "screen_min"], diff=abs(diff),
               pickup_diff=wknd.loc[False, "pickups"] - wknd.loc[True, "pickups"],
               session=d.median_session_s.mean() / 60,
               switches=d.switches_per_screen_hour.mean(),
               apps=d.distinct_apps.mean()),
             "good")
    else:
        note(t("day.note.b",
               weekend=wknd.loc[True, "screen_min"],
               weekday=wknd.loc[False, "screen_min"], diff=diff,
               session=d.median_session_s.mean() / 60,
               switches=d.switches_per_screen_hour.mean(),
               ratio=(d.switches_per_screen_hour.mean()
                      / F["A"].switches_per_screen_hour.mean()),
               night=d.night_min.mean()),
             "warn")

    with st.expander(t("day.table.expander")):
        cols = ["day", "score", "screen_min", "pickups", "glances", "sessions",
                "night_min", "night_pickups", "first_pickup_clock",
                "last_use_clock", "longest_offline_s", "longest_offline_when",
                "distinct_apps",
                "app_switches", "distract_share", "blocks", "blocks_sensitive"]
        show = d[cols].copy()
        show["longest_offline_s"] = (show["longest_offline_s"] / 3600).round(1)
        show = show.rename(columns={"longest_offline_s": "offline_max_h"})
        st.dataframe(show.round(1), width="stretch", hide_index=True)
        st.download_button(t("day.table.download"),
                           d.drop(columns=["_cat_s", "_app_s", "_site_s"]).to_csv(index=False),
                           file_name=f"balance_daily_{who}.csv", mime="text/csv")


# ===========================================================================
# 4 · THE NIGHT
# ===========================================================================
with TABS[3]:
    b = F["B"]
    st.markdown("### " + t("night.title"))

    n1, n4 = wk(b, "night_min", 1), wk(b, "night_min", 4)
    e1, e4 = wk(b, "night_end_h", 1), wk(b, "night_end_h", 4)
    f1, f4 = wk(b, "first_pickup_h", 1), wk(b, "first_pickup_h", 4)
    sleep1 = (24 + f1) - e1
    sleep4 = (24 + f4) - e4
    clock_e1 = t("fmt.clock", h=int(e1 % 24), m=int(e1 % 1 * 60))
    clock_e4 = t("fmt.clock", h=int(e4 % 24), m=int(e4 % 1 * 60))
    clock_f1 = t("fmt.clock", h=int(f1), m=int(f1 % 1 * 60))
    clock_f4 = t("fmt.clock", h=int(f4), m=int(f4 % 1 * 60))

    kpis([
        (t("night.kpi.first_week"), f"{n1:.0f} {t('unit.min')}", None),
        (t("night.kpi.last_week"), f"{n4:.0f} {t('unit.min')}",
         t("delta.times", n=n4 / max(n1, .01))),
        (t("night.kpi.last_screen_first"), clock_e1, None),
        (t("night.kpi.last_screen_last"), clock_e4,
         t("delta.minutes", n=(e4 - e1) * 60)),
        (t("night.kpi.first_unlock"), clock_f4,
         t("delta.minutes", n=(f4 - f1) * 60)),
        (t("night.kpi.sleep_window"), f"{sleep4:.1f} {t('unit.hours')}",
         t("delta.minutes", n=(sleep4 - sleep1) * 60)),
    ])

    st.markdown("")
    st.plotly_chart(figures.night_drift(F), width="stretch", key="k_nightdrift")

    note(t("night.note.drift", end_first=clock_e1, end_last=clock_e4,
           end_shift=(e4 - e1) * 60, wake_first=clock_f1, wake_last=clock_f4,
           wake_shift=(f4 - f1) * 60, sleep_first=sleep1, sleep_last=sleep4,
           sleep_loss=abs(sleep4 - sleep1) * 60,
           pick_first=wk(b, "night_pickups", 1),
           pick_last=wk(b, "night_pickups", 4)),
         "serious")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(figures.day_span(b, "B"), width="stretch", key="k_span_night")
    with c2:
        st.plotly_chart(figures.compare_line(F, "night_pickups",
                        t("chart.night_pickups"), t("unit.unlocks"), 5),
                        width="stretch", key="k_nightpick")

    note(t("night.note.user_a",
           last_use=t("fmt.clock", h=int(F["A"].last_use_h.mean()),
                      m=int(F["A"].last_use_h.mean() % 1 * 60))),
         "good")

    st.markdown("### " + t("night.weight.title"))
    note(t("night.weight.body", night=b.night_min.mean(),
           screen=b.screen_min.mean()))

# ===========================================================================
# 5 · WHERE THE TIME GOES
# ===========================================================================
with TABS[4]:
    d = F[who]
    apps, sites = U[who]["apps"], U[who]["sites"]
    st.markdown("### " + t("time.title", user=who))

    st.markdown(f'<span class="tag">{t("tag.device_only")}</span>'
                f'<span class="tag">{t("tag.never_sent")}</span>',
                unsafe_allow_html=True)

    top_share = apps.minutes.head(3).sum() / apps.minutes.sum() * 100
    kpis([
        (t("time.kpi.attributed"), f"{U[who]['attributed_h']:.0f} {t('unit.hours')}",
         t("time.kpi.attributed.delta",
           pct=U[who]["attributed_h"] / U[who]["screen_h"] * 100)),
        (t("time.kpi.apps"), f"{len(apps)}", t("time.kpi.whole_month")),
        (t("time.kpi.domains"), f"{len(sites)}", t("time.kpi.whole_month")),
        (t("time.kpi.top3"), f"{top_share:.0f} %", t("time.kpi.top3.delta")),
        (t("time.kpi.distract"), f"{d.distract_share.mean()*100:.0f} %",
         t("time.kpi.distract.delta")),
    ])

    st.markdown("")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(figures.top_bars(apps, t("chart.time.apps", user=who)),
                        width="stretch", key="k_apps")
    with c2:
        st.plotly_chart(figures.top_bars(sites, t("chart.time.domains", user=who)),
                        width="stretch", key="k_sites")

    st.caption(t("time.colour.caption"))

    st.plotly_chart(figures.category_area(
        U[who]["cats"], t("chart.time.categories", user=who)),
        width="stretch", key="k_cats")

    chrome = apps[apps.key == "com.android.chrome"]
    if who == "A":
        news = sites[sites.category == "NEWS"].minutes.sum() / sites.minutes.sum() * 100
        note(t("time.note.a", apps=len(apps), top3=top_share, news=news,
               distract=d.distract_share.mean() * 100,
               first=wk(d, "distract_share", 1) * 100,
               last=wk(d, "distract_share", 4) * 100),
             "good")
        st.caption(t("time.caption.chrome", opens=chrome.opens.iloc[0],
                     minutes=chrome.minutes.iloc[0]))
    else:
        msg = apps[apps.category == "MESSAGING"].minutes.sum()
        note(t("time.note.b", apps=len(apps), apps_a=len(U["A"]["apps"]),
               top3=top_share, messaging=msg,
               distract=d.distract_share.mean() * 100,
               distract_a=F["A"].distract_share.mean() * 100),
             "warn")
        st.caption(t("time.caption.blocked_absent"))

    with st.expander(t("time.table.expander")):
        c1, c2 = st.columns(2)
        c1.dataframe(apps.round(1), width="stretch", hide_index=True)
        c2.dataframe(sites.round(1), width="stretch", hide_index=True)


# ===========================================================================
# 6 · BLOCKS
# ===========================================================================
with TABS[5]:
    d = F[who]
    bf = U[who]["blocks"]
    st.markdown("### " + t("blocks.title", user=who))

    st.markdown(f'<span class="tag">{t("tag.device_only")}</span>'
                f'<span class="tag">{t("tag.aggregate_only")}</span>',
                unsafe_allow_html=True)

    if bf.empty:
        st.info(t("blocks.none"))
    else:
        # The week is assigned by `daily_frame` and only looked up here.
        # Recomputing it from the frame's first day would drift as soon as the
        # file's first day was partial and dropped out.
        week_of = dict(zip(d["day"], d["week"]))
        bf = bf.assign(week=[week_of[x] for x in bf["day"]])
        sens = bf[bf.category.isin(SENSITIVE)]
        kpis([
            (t("blocks.kpi.attempts"), f"{len(bf):,}",
             t("blocks.kpi.attempts.delta", per_day=len(bf) / len(d))),
            (t("blocks.kpi.apps"), f"{d.blocks_app.sum():,}", None),
            (t("blocks.kpi.sites"), f"{d.blocks_url.sum():,}", None),
            (t("blocks.kpi.nudity"), f"{d.blocks_nudity.sum():,}",
             t("blocks.kpi.nudity.delta")),
            (t("blocks.kpi.sensitive"), f"{len(sens):,}",
             t("blocks.kpi.sensitive.delta",
               pct=len(sens) / max(len(bf), 1) * 100)),
            (t("blocks.kpi.opened"), "0", t("blocks.kpi.opened.delta")),
        ])

        st.markdown("")
        c1, c2 = st.columns([3, 2])
        with c1:
            st.plotly_chart(figures.blocks_daily(
                bf, t("chart.blocks.daily", user=who)),
                width="stretch", key="k_blocks_daily")
        with c2:
            st.plotly_chart(figures.blocks_by_hour(
                bf, t("chart.blocks.hour", user=who)),
                width="stretch", key="k_blocks_hour")

        # the month does not fall into 7-day weeks: the last one is a 2-day
        # tail and that has to be said, or blocks look like they collapse at
        # the end.
        n_days = d.groupby("week").size()
        pivot = pd.crosstab(bf.category, bf.week)
        pivot.columns = [t("table.col.week_days", week=c, days=n_days[c])
                         for c in pivot.columns]
        st.dataframe(pivot, width="stretch")

        if who == "A":
            note(t("blocks.note.a", total=len(bf),
                   first=wk(d, "blocks", 1, "sum"),
                   last=wk(d, "blocks", 4, "sum")),
                 "good")
        else:
            adult = bf[bf.category == "ADULT"]
            gamb = bf[bf.category == "GAMBLING"]
            nud = bf[bf.block_type == "NUDITY"]
            wk23 = len(sens[sens.week.isin([2, 3])])
            note(t("blocks.note.b", ordinary=len(bf) - len(sens),
                   first=wk(d, "blocks", 1, "sum"),
                   last=wk(d, "blocks", 4, "sum"),
                   adult=len(adult), gambling=len(gamb), nudity=len(nud),
                   mid=wk23, sensitive=len(sens),
                   mid_pct=wk23 / len(sens) * 100,
                   week_four=len(sens[sens.week == 4])),
                 "warn")

    st.markdown("### " + t("blocks.scope.title"))
    note(t("blocks.scope.body",
           sensitive=(len(bf[bf.category.isin(SENSITIVE)])
                      if not bf.empty else 0)))

# ===========================================================================
# 7 · ALERTS AND NUDGES
# ===========================================================================
with TABS[6]:
    d = F[who]
    sigs = U[who]["alerts"]
    nud = U[who]["nudges"]
    ns = nudge_summary(nud)
    sent = [x for x in sigs if x.decision == "sent"]

    st.markdown("### " + t("engine.title", user=who))
    st.caption(t("engine.caption"))

    replay = U[who]["replay"]
    by_day = {r["day"]: r for r in replay}
    days_list = [r["day"] for r in replay]
    default_day = next((r["day"] for r in replay if r["alert"]), days_list[-1])

    cursor = st.select_slider(t("engine.slider.label"), options=days_list,
                              value=default_day, format_func=fecha,
                              key=f"cursor_{who}")
    st_now = by_day[cursor]

    nudge_days = {r["day"] for r in replay if r["nudge"] and r["nudge"].fired}
    alert_days, positive_days = {}, {}
    for r in replay:
        if r["alert"]:
            alert_days[r["day"]] = "sent"
        elif r["digest_entry"]:
            alert_days[r["day"]] = "summary"
        if r["positives"]:
            positive_days[r["day"]] = True

    st.plotly_chart(
        figures.tracked_series(F[who], who, cursor, nudge_days, alert_days,
                              positive_days),
        width="stretch", key=f"k_tracked_{who}")

    st.markdown("#### " + t("engine.outputs.title", date=fecha(cursor)))
    row = F[who].set_index("day").loc[cursor]
    n = st_now["nudge"]
    pos_user = [x for x in st_now["positives"] if x.audience == "user"]
    pos_guard = [x for x in st_now["positives"] if x.audience == "guardian"]

    cols = st.columns(3 if HAS_GUARDIAN[who] else 2)

    with cols[0]:
        eyebrow(t("engine.channel.user"))
        if pos_user:
            x = pos_user[0]
            st.markdown(theme.phone(
                t("phone.time.summary"), t("phone.brand"),
                f"<div class='phone-eyebrow'>{t('phone.eyebrow.summary')}</div>"
                f"<div class='phone-h'>{x.headline}</div>"
                f"<div class='phone-p'>{x.guardian_text}</div>"
                + "".join(row_pair(k, v) for k, v in x.evidence.items())
                + f"<div class='phone-cta ghost'>{t('phone.cta.week')}</div>"),
                unsafe_allow_html=True)
        elif n and n.fired:
            st.markdown(theme.phone(
                pd.Timestamp(n.at_ms, unit="ms").strftime("%H:%M"),
                t("phone.brand"),
                f"<div class='phone-eyebrow'>{t('phone.eyebrow.nudge')}</div>"
                f"<div class='phone-h'>"
                f"{t('phone.nudge.headline', reopens=n.reopens)}</div>"
                f"<div class='phone-p'>{t('phone.nudge.body')}</div>"
                f"<div class='phone-cta'>{t('phone.cta.off_until_tomorrow')}</div>"
                f"<div class='phone-cta ghost'>{t('phone.cta.five_more')}</div>"),
                unsafe_allow_html=True)
        else:
            empty_box(t("engine.empty"))

    if HAS_GUARDIAN[who]:
        with cols[1]:
            eyebrow(t("engine.channel.guardian"))
            g = st_now["alert"] or (pos_guard[0] if pos_guard else None)
            if g is not None:
                st.markdown(theme.phone(
                    t("phone.time.guardian"),
                    t("phone.brand.guardian", user=who),
                    f"<div class='phone-eyebrow'>"
                    f"{t('phone.eyebrow.alert') if g.tone == 'alert' else t('phone.eyebrow.digest')}"
                    f"</div>"
                    f"<div class='phone-h'>{g.headline}</div>"
                    f"<div class='phone-p'>{g.guardian_text}</div>"
                    f"<div class='phone-cta ghost'>"
                    f"{t('phone.cta.weekly_summary')}</div>"),
                    unsafe_allow_html=True)
            else:
                empty_box(t("engine.empty"))

    with cols[-1]:
        eyebrow(t("engine.channel.device"))
        st.markdown(
            row_pair(t("device.row.screen"),
                     f"{row.screen_min:.0f} {t('unit.min')}")
            + row_pair(t("device.row.pickups"), f"{row.pickups:.0f}")
            + row_pair(t("device.row.night"),
                       f"{row.night_min:.0f} {t('unit.min')}")
            + row_pair(t("device.row.night_end"), reloj(row.night_end_h))
            + row_pair(t("device.row.offline"),
                       f"{row.longest_offline_h:.1f} {t('unit.hours')}")
            + row_pair(t("device.row.offline_start"),
                       row.longest_offline_when or t("value.no_stretch"))
            + row_pair(t("device.row.distract"),
                       f"{row.distract_share*100:.0f} %")
            + row_pair(t("device.row.sensitive"), f"{row.blocks_sensitive:.0f}")
            + row_pair(t("device.row.blocks"), f"{row.blocks:.0f}")
            + row_pair(t("device.row.score"),
                       t("device.score.value", score=row.score))
            + row_pair(t("device.row.nudges"), f"{st_now['nudges_so_far']}")
            + row_pair(t("device.row.reinforcements"),
                       f"{st_now['positives_so_far']}"),
            unsafe_allow_html=True)
        st.caption(t("device.caption")
                   + (t("device.caption.guardian") if HAS_GUARDIAN[who] else ""))

    st.markdown("### " + t("engine.emissions.title"))
    em = U[who]["emissions"]
    if em:
        st.dataframe(pd.DataFrame([{
            t("table.col.date"): fecha(e["day"]),
            t("table.col.destination"): e["destination"],
            t("table.col.type"): e["type"],
            t("table.col.detail"): e["detail"],
        # height to the content: a 3-row table with room for 10 looks like the
        # load failed.
        } for e in em]), width="stretch", hide_index=True,
            height=min(320, 38 + 35 * len(em)))
        st.caption(t(
            "engine.emissions.caption", total=len(em),
            to_user=sum(1 for e in em if e["destination"].startswith("User")),
            to_guardian=sum(1 for e in em
                            if e["destination"] == "Guardian · notification"),
            to_summary=sum(1 for e in em
                           if e["destination"] == "Guardian · weekly summary")))
    else:
        st.caption(t("engine.emissions.none"))

    st.markdown("### " + t("engine.notifications.title", user=who))
    kpis([
        (t("engine.kpi.guardian"),
         f"{len(sent)}" if HAS_GUARDIAN[who] else t("value.not_available"),
         t("engine.kpi.guardian.delta", budget=ALERT_BUDGET)
         if HAS_GUARDIAN[who] else t("value.no_guardian")),
        (t("engine.kpi.summary"),
         f"{sum(1 for x in sigs if x.decision == 'summary')}"
         if HAS_GUARDIAN[who] else t("value.not_available"),
         t("engine.kpi.summary.delta")),
        (t("engine.kpi.reinforcements"),
         f"{sum(1 for x in U[who]['positives'] if x.decision == 'sent')}",
         t("engine.kpi.reinforcements.delta")),
        (t("engine.kpi.nudge_nights"),
         t("engine.kpi.nudge_nights.value", nudged=ns["nights with a nudge"],
           nights=ns["nights"]),
         t("engine.kpi.nudge_nights.delta", pct=ns["appearance rate"] * 100)),
        (t("engine.kpi.nudge_minutes"),
         f"{ns['minutes at stake after the nudge']:.0f}",
         t("engine.kpi.nudge_minutes.delta",
           pct=ns["share of night total"] * 100)),
    ])

    st.markdown("### " + t("engine.guardian.title"))
    if not HAS_GUARDIAN[who]:
        note(t("engine.guardian.none_assigned", user=who, night=d.night_min.sum(),
               nudged=ns["nights with a nudge"]), "good")
    elif not sent:
        note(t("engine.guardian.none_sent", user=who, night=d.night_min.sum(),
               nudged=ns["nights with a nudge"]), "good")
    for x in sent:
        ev = "".join(row_pair(k, v) for k, v in x.evidence.items())
        eyebrow(t("engine.alert.eyebrow", date=fecha(x.day), user=who))
        _pc, _pr = st.columns([1, 2])
        with _pc:
            st.markdown(theme.phone(
                t("phone.time.guardian"), t("phone.brand.guardian", user=who),
                f"<div class='phone-eyebrow'>{t('phone.eyebrow.alert')}</div>"
                f"<div class='phone-h'>{x.headline}</div>"
                f"<div class='phone-p'>{x.guardian_text}</div>"
                f"<div class='phone-cta ghost'>"
                f"{t('phone.cta.weekly_summary')}</div>"),
                unsafe_allow_html=True)
        note(t("engine.alert.rule", key=x.key, start=fecha(x.day),
               end=fecha(x.until), days=x.days_true, priority=x.priority),
             "serious")
        with st.expander(t("engine.alert.expander")):
            st.markdown(ev, unsafe_allow_html=True)
            st.caption(t("engine.alert.evidence_caption"))

    st.markdown("### " + t("engine.positives.title"))
    pos = U[who]["positives"]
    pos_sent = [x for x in pos if x.decision == "sent"]
    if pos_sent:
        for x in pos_sent:
            eyebrow(t("engine.positives.eyebrow", date=fecha(x.day),
                      recipient=(t("engine.positives.recipient.user")
                                 if x.audience == "user"
                                 else t("engine.positives.recipient.guardian",
                                        user=who))))
            note(t("engine.positives.body", headline=x.headline,
                   text=x.guardian_text), "good")
    else:
        st.caption(t("engine.positives.none"))
    pos_held = [x for x in pos if x.decision != "sent"]
    if pos_held:
        with st.expander(t("engine.positives.held_expander", n=len(pos_held))):
            st.dataframe(pd.DataFrame([{
                t("table.col.date"): fecha(x.day),
                t("table.col.rule"): x.key,
                t("table.col.recipient"): x.audience,
                t("table.col.detail"): x.guardian_text,
                t("table.col.reason"): x.reason,
            } for x in pos_held]), width="stretch", hide_index=True)

    st.markdown("### " + t("engine.held.title"))
    rest = [x for x in sigs if x.decision != "sent"]
    if rest:
        st.dataframe(pd.DataFrame([{
            t("table.col.rule"): x.key,
            t("table.col.detected"): fecha(x.day),
            t("table.col.priority"): x.priority,
            t("table.col.destination"): x.decision,
            t("table.col.reason"): x.reason,
        } for x in rest]), width="stretch", hide_index=True)
    else:
        st.caption(t("engine.held.none"))

    st.markdown("### " + t("engine.coverage.title"))
    rows = []
    for key in ("night_drift", "sensitive_spike", "screen_jump"):
        rows.append({
            t("table.col.rule"): key,
            t("table.col.compares"): t(f"engine.coverage.{key}"),
            t("table.col.user", user="A"): next(
                (t("value.decision_on", decision=x.decision, date=fecha(x.day))
                 for x in U["A"]["alerts"] if x.key == key),
                t("value.does_not_fire")),
            t("table.col.user", user="B"): next(
                (t("value.decision_on", decision=x.decision, date=fecha(x.day))
                 for x in U["B"]["alerts"] if x.key == key),
                t("value.does_not_fire")),
        })
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    note(t("engine.coverage.note",
           screen=(wk(F["B"], "screen_min", 4) / wk(F["B"], "screen_min", 1) - 1) * 100,
           night=wk(F["B"], "night_min", 4) / max(wk(F["B"], "night_min", 1), .01)),
         "warn")

    st.markdown("### " + t("engine.nudge.title"))
    st.caption(t("engine.nudge.caption",
                 from_clock=t("fmt.clock", h=int(23 + NUDGE_AFTER_MIN // 60),
                              m=NUDGE_AFTER_MIN % 60)))
    ca, cb = st.columns(2)
    with ca:
        st.markdown(t("engine.nudge.activation", user=who))
        st.markdown(
            row_pair(t("engine.nudge.row.nights"), f"{ns['nights']}")
            + row_pair(t("engine.nudge.row.nudged"),
                       t("engine.nudge.row.nudged_value",
                         nudged=ns["nights with a nudge"],
                         pct=ns["appearance rate"] * 100))
            + row_pair(t("engine.nudge.row.night_minutes"),
                       f"{ns['total night minutes']:.0f}")
            + row_pair(t("engine.nudge.row.after"),
                       t("engine.nudge.row.after_value",
                         minutes=ns["minutes at stake after the nudge"],
                         pct=ns["share of night total"] * 100))
            + row_pair(t("engine.nudge.row.per_night"),
                       t("engine.nudge.row.per_night_value",
                         minutes=ns["minutes at stake per nudged night"])),
            unsafe_allow_html=True)
    with cb:
        quiet = Counter(x.quiet_reason for x in nud if x.quiet_reason)
        st.markdown(t("engine.nudge.quiet.title"))
        for reason, count in quiet.most_common():
            st.markdown(row_pair(reason, str(count)), unsafe_allow_html=True)

    nsb = nudge_summary(U["B"]["nudges"])
    note(t("engine.nudge.note",
           after=nsb["minutes at stake after the nudge"],
           total=nsb["total night minutes"],
           pct=nsb["share of night total"] * 100,
           per_night=nsb["minutes at stake per nudged night"]))

# ===========================================================================
# 8 · THE DATA
# ===========================================================================
with TABS[7]:
    st.markdown("### " + t("hood.stream.title"))

    ev = pd.DataFrame([
        {"User": u, **Counter(e["event_type"] for e in U[u]["events"])}
        for u in DATA]).set_index("User").T.fillna(0).astype(int)
    ev[t("table.col.means")] = [t(f"event.{i}") for i in ev.index]
    st.dataframe(ev, width="stretch")

    st.markdown("### " + t("hood.fields.title"))
    st.dataframe(pd.DataFrame([
        ("id", "int", t("field.id.is"), t("field.id.use")),
        ("event_type", "str", t("field.event_type.is"), t("field.event_type.use")),
        ("timestamp_millis", "int", t("field.timestamp.is"), t("field.timestamp.use")),
        ("package_name", "str|null", t("field.package.is"), t("field.package.use")),
        ("url_domain", "str|null", t("field.domain.is"), t("field.domain.use")),
        ("category", "str|null", t("field.category.is"), t("field.category.use")),
        ("block_type", "str|null", t("field.block_type.is"), t("field.block_type.use")),
        ("is_keyguard_locked", "bool|null", t("field.keyguard.is"),
         t("field.keyguard.use")),
    ], columns=[t("table.col.field"), t("table.col.field_type"),
                t("table.col.what_it_is"), t("table.col.what_we_use")]),
        width="stretch", hide_index=True)

    st.markdown("### " + t("hood.anomalies.title"))
    note(t("hood.anomalies.body", screen_a=U["A"]["screen_h"],
           dup_a=U["A"]["anomalies"]["duplicate USER_PRESENT in stretch"],
           dup_b=U["B"]["anomalies"]["duplicate USER_PRESENT in stretch"]))

    st.markdown("### " + t("hood.derivations.title"))
    st.dataframe(pd.DataFrame([
        (t(f"derive.{k}"), t(f"derive.{k}.how")) for k in (
            "screen_time", "pickup", "glance", "app_time", "domain_time",
            "night", "offline", "switch", "distract", "baseline")
    ], columns=[t("table.col.metric"), t("table.col.how_derived")]),
        width="stretch", hide_index=True)

    st.markdown("### " + t("hood.coverage.title"))
    kpis([(t("hood.kpi.reconstructed", user=u),
           f"{U[u]['screen_h']:.0f} {t('unit.hours')}", None) for u in DATA] +
         [(t("hood.kpi.attributed", user=u),
           f"{U[u]['attributed_h']/U[u]['screen_h']*100:.0f} %", None)
          for u in DATA])
    st.caption(t("hood.coverage.caption",
                 a=U["A"]["attributed_h"] / U["A"]["screen_h"] * 100,
                 b=U["B"]["attributed_h"] / U["B"]["screen_h"] * 100))

    st.markdown("### " + t("hood.index.title"))
    st.dataframe(pd.DataFrame([
        (label, f"{good:g}", f"{bad:g}", f"{weight*100:.0f} %")
        for col, label, good, bad, weight in COMPONENTS],
        columns=[t("table.col.component"), t("table.col.scores_100"),
                 t("table.col.scores_0"), t("table.col.weight")]),
        width="stretch", hide_index=True)
    c1, c2 = st.columns(2)
    for col, u in ((c1, "A"), (c2, "B")):
        mean_row = F[u].mean(numeric_only=True)
        col.plotly_chart(figures.score_breakdown(contributions(mean_row), u),
                         width="stretch", key=f"k_breakdown_{u}")
    note(t("hood.index.note"))
