"""Assembles the payload the static site reads.

Everything the browser needs and nothing it does not: the 2.4 MB of raw events
are resolved here, at build time. Strings arrive already rendered, so the
frontend carries no copy of its own.
"""

from __future__ import annotations

import math

import pandas as pd

from balance.events import load
from balance.intelligence import (
    emissions,
    evaluate_alerts,
    evaluate_positives,
    month_replay,
    nudge_summary,
    replay_nudge,
)
from balance.metrics import (
    blocks_frame,
    category_daily,
    daily_frame,
    hourly_heat,
    totals,
    weekly_frame,
)
from balance.score import COMPONENTS, add_score, contributions
from copytext import t

from . import figures, theme
from .profiles import DATA, surface_for
from .states import day_labels, day_states, week_states
from .summary import finding, summary

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
    positives = evaluate_positives(df)
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
    theme.use("light")
    out = {"score_line": figures.score_line(frames)}
    theme.use("dark")
    out["night_drift"] = figures.night_drift(frames)
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
    out = {}
    theme.use("light")
    out["week_components"] = figures.week_components(w, sel)
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
    theme.use("dusk")
    out |= {
        "daily_bars.screen_min": figures.daily_bars_vs_baseline(
            d, "screen_min", "screen_min_baseline",
            t("chart.day.screen", user=user), t("unit.minutes"), user),
        "daily_bars.pickups": figures.daily_bars_vs_baseline(
            d, "pickups", "pickups_baseline",
            t("chart.day.pickups", user=user), t("unit.unlocks"), user),
        "hour_heat": figures.hour_heat(bundle["heat"], user),
        "day_span": figures.day_span(d, user),
    }
    # the same figure appears again in the night, where it belongs to that act
    theme.use("dark")
    out |= {
        "day_span.night": figures.day_span(d, user),
        "top_bars.apps": figures.top_bars(
            bundle["apps"], t("chart.time.apps", user=user)),
        "top_bars.sites": figures.top_bars(
            bundle["sites"], t("chart.time.domains", user=user)),
        "category_area": figures.category_area(
            bundle["cats"], t("chart.time.categories", user=user)),
        "tracked_series": tracked(user, bundle, cursor),
    }
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

    templates: dict[str, dict] = {}

    def as_json(fig, key=""):
        """Serialise, hoisting the theme out of the figure.

        Plotly writes the whole template into every figure. Repeated across
        59 figures that is 95 KB of the payload saying the same thing, so the
        page re-attaches one copy at plot time. There are two now, one per
        surface, and the figure carries the name of the one it was drawn for.
        """
        raw = json.loads(fig.to_json())
        mode = surface_for(key)
        found = raw.get("layout", {}).pop("template", None)
        if found:
            templates.setdefault(mode, found)
        raw["surface"] = mode
        return raw

    payload = {
        "meta": {
            "profiles": list(DATA),
            "days": len(frames["A"]),
            "events": sum(len(bundles[u]["events"]) for u in DATA),
            "weeks": [int(i) for i in bundles["A"]["weekly"].index],
        },
        "templates": templates,
        "finding": finding(summaries),
        "figures": {k: as_json(f, k)
                    for k, f in shared_figures(frames).items()},
        "profiles": {},
    }
    for user, bundle in bundles.items():
        default_day = next((r["day"] for r in bundle["replay"] if r["alert"]),
                           bundle["replay"][-1]["day"])
        weeks = week_states(user, bundle)
        payload["profiles"][user] = {
            "summary": summaries[user],
            "figures": {k: as_json(f, k) for k, f
                        in profile_figures(user, bundle, default_day).items()},
            "days": day_states(user, bundle),
            "ui": day_labels(),
            "weeks": weeks,
            "default_day": default_day.isoformat(),
            "default_week": weeks[-2]["week"] if len(weeks) > 1
            else weeks[-1]["week"],
        }
    payload["templates"] = templates
    return finite(payload), bundles
