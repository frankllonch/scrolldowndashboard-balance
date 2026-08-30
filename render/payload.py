"""Assembles the payload the static site reads.

Everything the browser needs and nothing it does not: the 2.4 MB of raw events
are resolved here, at build time. Strings arrive already rendered, so the
frontend carries no copy of its own.
"""

from __future__ import annotations

import math

import pandas as pd

from balance.events import SENSITIVE, load
from balance.intelligence import (
    ALERT_BUDGET, emissions, evaluate_alerts, evaluate_positives, month_replay,
    nudge_summary, replay_nudge,
)
from balance.metrics import (
    blocks_frame, category_daily, daily_frame, hourly_heat, totals, weekly_frame,
)
from balance.score import COMPONENTS, add_score, contributions
from copytext import t

from . import figures
from .fmt import clock, date, hm, ordinal, week_value as wk
from .theme import USER_COLOR

DATA = {"A": "data/events_user_a.json", "B": "data/events_user_b.json"}

#: Only profile B has a guardian assigned. A is an adult: the rules run all the
#: same, but there is no recipient to notify.
HAS_GUARDIAN = {"A": False, "B": True}

#: Bar colour of a week that is not the selected one.
DIM = "#2f2f36"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def compute(user: str) -> dict:
    """Run the core over one profile. Same bundle the dashboard used."""
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

    blocks = blocks_frame(tl, days)
    if not blocks.empty:
        week_of = dict(zip(df["day"], df["week"]))
        blocks = blocks.assign(week=[week_of[x] for x in blocks["day"]])

    return {
        "df": df, "weekly": weekly, "blocks": blocks,
        "apps": totals(tl, df, "app"), "sites": totals(tl, df, "site"),
        "cats": category_daily(df), "heat": hourly_heat(tl, days),
        "events": tl.events, "anomalies": dict(tl.anomalies),
        "n_intervals": len(tl.intervals),
        "screen_h": sum(i.seconds for i in tl.intervals) / 3600,
        "attributed_h": sum(u.seconds for u in tl.usages) / 3600,
        "alerts": evaluate_alerts(df), "positives": positives,
        "nudges": nudges, "nudge_summary": nudge_summary(nudges),
        "replay": replay, "emissions": emissions(replay),
    }


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def shared_figures(frames: dict[str, pd.DataFrame]) -> dict:
    """Figures that hold both profiles at once."""
    out = {
        "score_line": figures.score_line(frames),
        "night_drift": figures.night_drift(frames),
    }
    for user, df in frames.items():
        out[f"score_breakdown.{user}"] = figures.score_breakdown(
            contributions(df.mean(numeric_only=True)), user)
    for col, title, unit in (
        ("screen_min", t("chart.screen_per_day"), t("unit.minutes")),
        ("pickups", t("chart.pickups_per_day"), t("unit.unlocks")),
        ("night_min", t("chart.night_per_day"), t("unit.minutes")),
        ("blocks", t("chart.blocks_per_day"), t("unit.blocks")),
        ("night_pickups", t("chart.night_pickups"), t("unit.unlocks")),
    ):
        out[f"compare.{col}"] = figures.compare_line(frames, col, title, unit)
    return out


def profile_figures(user: str, bundle: dict, cursor) -> dict:
    """Figures for one profile. The selection-dependent ones are exported once
    and re-pointed in the browser, except `week_days`, whose data changes."""
    d, w, bf = bundle["df"], bundle["weekly"], bundle["blocks"]
    sel = w.index[-2] if len(w.index) > 1 else w.index[-1]
    out = {
        "week_components": figures.week_components(w, sel),
        "daily_bars.screen_min": figures.daily_bars_vs_baseline(
            d, "screen_min", "screen_min_baseline",
            t("chart.day.screen", user=user), t("unit.minutes"), user),
        "daily_bars.pickups": figures.daily_bars_vs_baseline(
            d, "pickups", "pickups_baseline",
            t("chart.day.pickups", user=user), t("unit.unlocks"), user),
        "hour_heat": figures.hour_heat(bundle["heat"], user),
        "day_span": figures.day_span(d, user),
        "top_bars.apps": figures.top_bars(
            bundle["apps"], t("chart.time.apps", user=user)),
        "top_bars.sites": figures.top_bars(
            bundle["sites"], t("chart.time.domains", user=user)),
        "category_area": figures.category_area(
            bundle["cats"], t("chart.time.categories", user=user)),
        "tracked_series": tracked(user, bundle, cursor),
    }
    for col, title, unit in (
        ("screen_min", t("chart.week.screen"), t("unit.min")),
        ("night_min", t("chart.week.night"), t("unit.min")),
        ("pickups", t("chart.week.pickups"), ""),
        ("blocks", t("chart.week.blocks"), ""),
    ):
        out[f"week_evolution.{col}"] = figures.week_evolution(
            w, col, title, unit, user, sel)
    for week in w.index:
        out[f"week_days.screen_min.{week}"] = figures.week_days(
            d, week, "screen_min", t("chart.week_days.screen", week=week),
            t("unit.min"), user)
        out[f"week_days.night_min.{week}"] = figures.week_days(
            d, week, "night_min", t("chart.week_days.night", week=week),
            t("unit.min"), user)
    if not bf.empty:
        out["blocks_daily"] = figures.blocks_daily(
            bf, t("chart.blocks.daily", user=user))
        out["blocks_by_hour"] = figures.blocks_by_hour(
            bf, t("chart.blocks.hour", user=user))
    return out


def tracked(user: str, bundle: dict, cursor):
    nudge_days, alert_days, positive_days = rails(bundle["replay"])
    return figures.tracked_series(bundle["df"], user, cursor, nudge_days,
                                  alert_days, positive_days)


def rails(replay: list[dict]) -> tuple[set, dict, dict]:
    """The three event rails under the walkthrough chart."""
    nudge_days = {r["day"] for r in replay if r["nudge"] and r["nudge"].fired}
    alert_days, positive_days = {}, {}
    for r in replay:
        if r["alert"]:
            alert_days[r["day"]] = "sent"
        elif r["digest_entry"]:
            alert_days[r["day"]] = "summary"
        if r["positives"]:
            positive_days[r["day"]] = True
    return nudge_days, alert_days, positive_days


# ---------------------------------------------------------------------------
# Day states · the thirty cards behind the day slider
# ---------------------------------------------------------------------------

def phone_card(time: str, brand: str, eyebrow: str, headline: str, body: str,
               rows: list | None = None, ctas: list | None = None) -> dict:
    return {"time": time, "brand": brand, "eyebrow": eyebrow,
            "headline": headline, "body": body, "rows": rows or [],
            "ctas": ctas or []}


def user_card(state: dict) -> dict | None:
    """What the person holding the phone would have seen that day."""
    positives = [x for x in state["positives"] if x.audience == "user"]
    if positives:
        x = positives[0]
        return phone_card(
            t("phone.time.summary"), t("phone.brand"),
            t("phone.eyebrow.summary"), x.headline, x.guardian_text,
            rows=[[k, v] for k, v in x.evidence.items()],
            ctas=[{"label": t("phone.cta.week"), "ghost": True}])
    nudge = state["nudge"]
    if nudge and nudge.fired:
        at = pd.Timestamp(nudge.at_ms, unit="ms")
        return phone_card(
            t("fmt.clock", h=at.hour, m=at.minute), t("phone.brand"),
            t("phone.eyebrow.nudge"),
            t("phone.nudge.headline", ordinal=ordinal(nudge.reopens)),
            t("phone.nudge.body"),
            ctas=[{"label": t("phone.cta.off_until_tomorrow"), "ghost": False},
                  {"label": t("phone.cta.five_more"), "ghost": True}])
    return None


def guardian_card(user: str, state: dict) -> dict | None:
    """What the guardian's phone would have shown. Headline and text only:
    no app, no domain, no category ever crosses this boundary."""
    if not HAS_GUARDIAN[user]:
        return None
    guardian_positives = [x for x in state["positives"]
                          if x.audience == "guardian"]
    signal = state["alert"] or (guardian_positives[0]
                                if guardian_positives else None)
    if signal is None:
        return None
    return phone_card(
        t("phone.time.guardian"), t("phone.brand.guardian", user=user),
        t("phone.eyebrow.alert") if signal.tone == "alert"
        else t("phone.eyebrow.digest"),
        signal.headline, signal.guardian_text,
        ctas=[{"label": t("phone.cta.weekly_summary"), "ghost": True}])


def device_rows(row, state: dict) -> list[list[str]]:
    """The figures the phone keeps for itself."""
    return [
        [t("device.row.screen"), f"{row.screen_min:.0f} {t('unit.min')}"],
        [t("device.row.pickups"), f"{row.pickups:.0f}"],
        [t("device.row.night"), f"{row.night_min:.0f} {t('unit.min')}"],
        [t("device.row.night_end"), clock(row.night_end_h)],
        [t("device.row.offline"),
         f"{row.longest_offline_h:.1f} {t('unit.hours')}"],
        [t("device.row.offline_start"),
         row.longest_offline_when or t("value.no_stretch")],
        [t("device.row.distract"), f"{row.distract_share*100:.0f} %"],
        [t("device.row.sensitive"), f"{row.blocks_sensitive:.0f}"],
        [t("device.row.blocks"), f"{row.blocks:.0f}"],
        [t("device.row.score"), t("device.score.value", score=row.score)],
        [t("device.row.nudges"), f"{state['nudges_so_far']}"],
        [t("device.row.reinforcements"), f"{state['positives_so_far']}"],
    ]


def day_labels(user: str) -> dict:
    """The handful of strings the day slider needs when it rebuilds the cards
    in the browser. The page carries no copy of its own."""
    return {
        "channel_user": t("engine.channel.user"),
        "channel_guardian": t("engine.channel.guardian"),
        "channel_device": t("engine.channel.device"),
        "empty": t("engine.empty"),
        "device_caption": t("device.caption") + (
            t("device.caption.guardian") if HAS_GUARDIAN[user] else ""),
    }


def day_states(user: str, bundle: dict) -> list[dict]:
    by_day = bundle["df"].set_index("day")
    return [{
        "iso": state["day"].isoformat(),
        "label": date(state["day"]),
        "title": t("engine.outputs.title", date=date(state["day"])),
        "user": user_card(state),
        "guardian": guardian_card(user, state),
        "device": device_rows(by_day.loc[state["day"]], state),
    } for state in bundle["replay"]]


# ---------------------------------------------------------------------------
# Week states · the five panels behind the week slider
# ---------------------------------------------------------------------------

#: (copy key, column, unit, decimals) for the against-the-period table.
WEEK_ROWS = [
    ("row.screen_per_day", "screen_min", "unit.min", 0),
    ("row.unlocks_per_day", "pickups", None, 0),
    ("row.night_per_night", "night_min", "unit.min", 0),
    ("row.longest_offline", "longest_offline_h", "unit.hours", 1),
    ("row.distinct_apps", "distinct_apps", None, 1),
    ("row.switches_per_hour", "switches_per_screen_hour", None, 0),
    ("row.distract_share", "distract_share", "unit.percent", 0),
    ("row.blocks_per_day", "blocks", None, 1),
    ("row.index", "score", None, 0),
]


def _delta(cur, prev, col: str, unit: str = "", dec: int = 0) -> str | None:
    """Change against the previous week, in the metric's own unit.

    A change that rounds to zero is not shown: "+0 min" with a green arrow says
    something improved when nothing moved.
    """
    if prev is None or pd.isna(prev[col]):
        return None
    v = cur[col] - prev[col]
    if abs(round(v, dec)) < 10 ** -dec / 2:
        return t("value.no_change")
    return f"{v:+.{dec}f} {unit}".strip()


def week_kpis(cur, prev) -> list[dict]:
    items = [
        (t("week.kpi.screen"), hm(cur["screen_min"]),
         _delta(cur, prev, "screen_min", t("unit.min"))),
        (t("week.kpi.pickups"), f"{cur['pickups']:.0f}",
         _delta(cur, prev, "pickups")),
        (t("week.kpi.night"), f"{cur['night_min']:.0f} {t('unit.min')}",
         _delta(cur, prev, "night_min", t("unit.min"))),
        (t("week.kpi.offline"),
         f"{cur['longest_offline_h']:.1f} {t('unit.hours')}",
         _delta(cur, prev, "longest_offline_h", t("unit.hours"), 1)),
        (t("week.kpi.best_offline"),
         f"{cur['best_offline_h']:.1f} {t('unit.hours')}",
         cur["best_offline_when"]),
        (t("week.kpi.blocks"), f"{cur['blocks']:.1f}",
         _delta(cur, prev, "blocks", dec=1)),
        (t("week.kpi.score"), f"{cur['score']:.0f}",
         _delta(cur, prev, "score")),
    ]
    return [{"label": a, "value": b, "delta": c} for a, b, c in items]


def week_table(w: pd.DataFrame, cur, prev, week: int) -> dict:
    rows = []
    for key, col, unit_key, dec in WEEK_ROWS:
        unit = t(unit_key) if unit_key else ""
        mult = 100 if unit_key == "unit.percent" else 1
        # Rounded BEFORE subtracting: otherwise the change does not match the
        # two columns beside it and looks like an arithmetic error.
        v = round(cur[col] * mult, dec)
        pv = (round(prev[col] * mult, dec)
              if prev is not None and not pd.isna(prev[col]) else None)
        med = round(w[col].median() * mult, dec)
        if pv is None:
            change = t("value.not_available")
        elif abs(v - pv) < 10 ** -dec / 2:
            change = t("value.no_change")
        else:
            change = f"{v - pv:+.{dec}f} {unit}".strip()
        rows.append([
            t(key), f"{v:.{dec}f} {unit}".strip(),
            f"{pv:.{dec}f} {unit}".strip() if pv is not None
            else t("value.not_available"),
            f"{med:.{dec}f} {unit}".strip(), change,
        ])
    return {"columns": [t("table.col.metric"),
                        t("table.col.week_selected", week=week),
                        t("table.col.previous_week"),
                        t("table.col.period_median"),
                        t("table.col.change")],
            "rows": rows}


def week_emissions(bundle: dict, days: set) -> dict:
    rows = [[date(e["day"]), e["destination"], e["type"], e["detail"]]
            for e in bundle["emissions"] if e["day"] in days]
    return {"columns": [t("table.col.date"), t("table.col.destination"),
                        t("table.col.type"), t("table.col.detail")],
            "rows": rows}


def week_states(user: str, bundle: dict) -> list[dict]:
    df, w = bundle["df"], bundle["weekly"]
    colour = USER_COLOR[user]
    out = []
    for week in w.index:
        cur = w.loc[week]
        prev = w.loc[week - 1] if week - 1 in w.index else None
        days = set(df[df["week"] == week]["day"])
        held = [x for x in bundle["positives"]
                if x.decision == "summary" and x.day in days]
        out.append({
            "week": int(week),
            "partial": bool(cur["is_partial"]),
            "label": t("week.slider.option_short" if cur["is_partial"]
                       else "week.slider.option", week=week),
            "range": (t("week.range", start=date(cur["start"]),
                        end=date(cur["end"]), days=int(cur["days"]))
                      + (t("week.range.partial") if cur["is_partial"] else "")),
            "days_title": t("week.days.title", week=week),
            "kpis": week_kpis(cur, prev),
            "table": week_table(w, cur, prev, week),
            "emitted_title": t("week.emitted.title", week=week),
            "emissions": week_emissions(bundle, days),
            "held": [[x.headline, x.reason.split(".")[0]] for x in held],
            # what the browser re-points rather than re-downloads
            "evolution_colors": [colour if i == week else DIM for i in w.index],
            "components_vline": t("label.week", week=week),
        })
    return out


# ---------------------------------------------------------------------------
# Summary · the numbers the headline acts read
# ---------------------------------------------------------------------------

def summary(user: str, bundle: dict) -> dict:
    d, w = bundle["df"], bundle["weekly"]
    first, last = w.index[0], w.index[-2] if len(w.index) > 1 else w.index[-1]
    end_first, end_last = wk(d, "night_end_h", first), wk(d, "night_end_h", last)
    wake_first, wake_last = (wk(d, "first_pickup_h", first),
                             wk(d, "first_pickup_h", last))
    night_first = max(wk(d, "night_min", first), .01)
    return {
        "user": user,
        "has_guardian": HAS_GUARDIAN[user],
        "days": len(d),
        "events": len(bundle["events"]),
        "intervals": bundle["n_intervals"],
        "screen_h": bundle["screen_h"],
        "attributed_pct": bundle["attributed_h"] / bundle["screen_h"] * 100,
        "score_mean": d.score.mean(),
        "score_min": d.score.min(),
        "score_max": d.score.max(),
        "score_first_week": wk(d, "score", first),
        "score_last_week": wk(d, "score", last),
        "screen_mean": d.screen_min.mean(),
        "screen_mean_hm": hm(d.screen_min.mean()),
        "screen_first_week": wk(d, "screen_min", first),
        "screen_last_week": wk(d, "screen_min", last),
        "pickups_mean": d.pickups.mean(),
        "pickups_first_week": wk(d, "pickups", first),
        "pickups_last_week": wk(d, "pickups", last),
        "apps_mean": d.distinct_apps.mean(),
        "blocks_total": d.blocks.sum(),
        "sensitive_total": d.blocks_sensitive.sum(),
        "night_mean": d.night_min.mean(),
        "night_first_week": wk(d, "night_min", first),
        "night_last_week": wk(d, "night_min", last),
        "night_multiple": wk(d, "night_min", last) / night_first,
        "night_pickups_first_week": wk(d, "night_pickups", first),
        "night_pickups_last_week": wk(d, "night_pickups", last),
        "last_use_mean": clock(d.last_use_h.mean()),
        "last_screen_first_week": clock(end_first),
        "last_screen_last_week": clock(end_last),
        "last_screen_shift_min": (end_last - end_first) * 60,
        "wake_first_week": clock(wake_first),
        "wake_last_week": clock(wake_last),
        "wake_shift_min": (wake_last - wake_first) * 60,
        "sleep_first_week": (24 + wake_first) - end_first,
        "sleep_last_week": (24 + wake_last) - end_last,
        "alerts_sent": sum(1 for x in bundle["alerts"] if x.decision == "sent"),
        "alerts_held": sum(1 for x in bundle["alerts"]
                           if x.decision == "summary"),
        "alert_budget": ALERT_BUDGET,
        "positives_sent": sum(1 for x in bundle["positives"]
                              if x.decision == "sent"),
        "nudge_nights": bundle["nudge_summary"]["nights with a nudge"],
        "nights": bundle["nudge_summary"]["nights"],
        "emissions_total": len(bundle["emissions"]),
    }


def finding(summaries: dict) -> dict:
    """The reveal in act 11 and the negative control in act 12."""
    b = summaries["B"]
    return {
        "night_multiple": b["night_multiple"],
        "screen_change_pct": (b["screen_last_week"] / b["screen_first_week"]
                              - 1) * 100,
        "pickups_change_pct": (b["pickups_last_week"] / b["pickups_first_week"]
                               - 1) * 100,
        "sleep_loss_min": (b["sleep_first_week"] - b["sleep_last_week"]) * 60,
        "score_drop": b["score_first_week"] - b["score_last_week"],
    }


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def finite(node):
    """NaN and Infinity are not JSON. A metric that does not exist is null."""
    if isinstance(node, dict):
        return {k: finite(v) for k, v in node.items()}
    if isinstance(node, list):
        return [finite(v) for v in node]
    if isinstance(node, float) and not math.isfinite(node):
        return None
    return node


def assemble() -> tuple[dict, dict]:
    """Return (payload, bundles). The bundles stay in Python for the acts."""
    import json

    bundles = {u: compute(u) for u in DATA}
    frames = {u: bundles[u]["df"] for u in DATA}
    summaries = {u: summary(u, bundles[u]) for u in DATA}

    template = {}

    def as_json(fig):
        """Serialise, hoisting the theme out of the figure.

        Plotly writes the whole template into every figure. Repeated across
        59 figures that is 95 KB of the payload saying the same thing; the
        page re-attaches it once at plot time.
        """
        raw = json.loads(fig.to_json())
        found = raw.get("layout", {}).pop("template", None)
        if found and not template:
            template.update(found)
        return raw

    payload = {
        "meta": {
            "profiles": list(DATA),
            "days": len(frames["A"]),
            "events": sum(len(bundles[u]["events"]) for u in DATA),
            "weeks": [int(i) for i in bundles["A"]["weekly"].index],
        },
        "template": template,
        "finding": finding(summaries),
        "figures": {k: as_json(f)
                    for k, f in shared_figures(frames).items()},
        "profiles": {},
    }
    for user, bundle in bundles.items():
        default_day = next((r["day"] for r in bundle["replay"] if r["alert"]),
                           bundle["replay"][-1]["day"])
        weeks = week_states(user, bundle)
        payload["profiles"][user] = {
            "summary": summaries[user],
            "figures": {k: as_json(f) for k, f
                        in profile_figures(user, bundle, default_day).items()},
            "days": day_states(user, bundle),
            "ui": day_labels(user),
            "weeks": weeks,
            "default_day": default_day.isoformat(),
            "default_week": weeks[-2]["week"] if len(weeks) > 1
            else weeks[-1]["week"],
        }
    payload["template"] = template
    return finite(payload), bundles
