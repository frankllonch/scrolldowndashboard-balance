"""One analysis, laid out flat.

Takes what `analysis.pipeline` computed and turns it into the records the page
reads. The column lists below are the whole point: the daily frame carries 67
columns and 33 of them cross, so a new intermediate in `metrics.py` has to be
named here on purpose before it can reach the browser.
"""

from __future__ import annotations

import pandas as pd

from analysis.events import Timeline
from analysis.intelligence import ALERT_BUDGET
from analysis.pipeline import Analysis
from analysis.score import COMPONENTS

from .scalars import nudge, plain, rows, signal, snake

#: Columns of the daily frame that cross the boundary. The frame carries 67;
#: these are the ones the page reads. Anything else is an intermediate.
DAILY_COLUMNS = (
    "day", "dow", "is_weekend", "week", "is_partial",
    "screen_min", "sessions", "median_session_s",
    "pickups", "glances",
    # Both the hour and the millisecond: the hour is what the charts plot, the
    # millisecond is what a clock face is written from. Truncating 21.8833 h to
    # minutes loses one, and the page shows the clock.
    "first_pickup_h", "first_pickup_ms",
    "last_use_h", "last_use_ms",
    "night_min", "night_pickups", "night_end_h",
    "longest_offline_h", "longest_offline_when",
    "distinct_apps", "switches_per_screen_hour", "distract_share",
    "blocks", "blocks_sensitive",
    "screen_min_baseline", "pickups_baseline",
    "score", "score_7d",
) + tuple(f"score_{col}" for col, *_ in COMPONENTS)

WEEKLY_COLUMNS = (
    "week", "days", "start", "end", "is_partial",
    "screen_min", "pickups", "night_min", "night_pickups", "night_end_h",
    "first_pickup_h", "longest_offline_h", "best_offline_h",
    "best_offline_when", "distinct_apps", "switches_per_screen_hour",
    "distract_share", "blocks", "blocks_total", "blocks_sensitive", "score",
) + tuple(f"score_{col}" for col, *_ in COMPONENTS)

#: An app and a domain carry the same five facts, so they cross the same way.
USAGE_COLUMNS = ("key", "label", "category", "minutes", "opens", "min_per_open")


def week_value(df: pd.DataFrame, col: str, week: int) -> float:
    """One measure averaged over one week. The summary compares the first
    against the last, so it asks for the same thing a dozen times."""
    return df[df["week"] == week][col].mean()


def filter_outage(run: Analysis) -> dict:
    """The apps that appear in the usage frame despite being blocked, and the
    hole in the filter that let them in.

    An app that is both used and blocked is the anomaly: the filter had an
    opinion about it every day, and for one stretch the opinion did not fire.
    That stretch is the longest gap between two of its blocks. The block frame
    is at hour resolution, so the gap is measured from the top of the hour the
    last block landed in and slightly overstates the true silence.
    """
    apps, blocks = run.apps, run.blocks
    if blocks.empty:
        return {}
    leaked = set(apps["key"]) & set(blocks.loc[blocks["block_type"] == "APP",
                                               "target"])
    if not leaked:
        return {}
    theirs = blocks[blocks["target"].isin(leaked)]
    stamps = sorted({(row.day, row.hour) for row in theirs.itertuples()})
    hours = [pd.Timestamp(d) + pd.Timedelta(hours=h) for d, h in stamps]
    longest, start = max((b - a, a) for a, b in zip(hours, hours[1:]))
    return {
        "leaked_days": int(theirs.groupby("day").ngroups),
        "leaked_median": float(theirs.groupby("day").size().median()),
        "outage_day": plain(start.date()),
        "outage_hours": longest.total_seconds() / 3600,
    }


def summary(run: Analysis) -> dict:
    """The headline numbers, as numbers.

    Hours stay hours and minutes stay minutes: the clock face, the "2h 02m"
    and the "no use" for a metric user A genuinely does not have are all
    decisions the frontend makes, because they are all wording.
    """
    d, w = run.daily, run.weekly
    first = w.index[0]
    last = w.index[-2] if len(w.index) > 1 else w.index[-1]
    timeline = run.timeline
    screen_h = sum(i.seconds for i in timeline.intervals) / 3600
    attributed_h = sum(u.seconds for u in timeline.usages) / 3600
    end_first, end_last = (week_value(d, "night_end_h", first),
                           week_value(d, "night_end_h", last))
    wake_first, wake_last = (week_value(d, "first_pickup_h", first),
                             week_value(d, "first_pickup_h", last))
    night_first = week_value(d, "night_min", first)

    out = {
        "user": run.user,
        "days": len(d),
        "events": len(timeline.events),
        "intervals": len(timeline.intervals),
        "screen_h": screen_h,
        "attributed_pct": attributed_h / screen_h * 100,

        "score_mean": d.score.mean(),
        "score_min": d.score.min(),
        "score_max": d.score.max(),
        "score_first_week": week_value(d, "score", first),
        "score_last_week": week_value(d, "score", last),

        "screen_mean": d.screen_min.mean(),
        "screen_first_week": week_value(d, "screen_min", first),
        "screen_last_week": week_value(d, "screen_min", last),
        "pickups_mean": d.pickups.mean(),
        "pickups_first_week": week_value(d, "pickups", first),
        "pickups_last_week": week_value(d, "pickups", last),
        "apps_mean": d.distinct_apps.mean(),
        "blocks_total": d.blocks.sum(),
        "sensitive_total": d.blocks_sensitive.sum(),

        "night_mean": d.night_min.mean(),
        "night_first_week": night_first,
        "night_last_week": week_value(d, "night_min", last),
        "night_multiple": week_value(d, "night_min", last) / max(night_first, .01),
        "night_pickups_first_week": week_value(d, "night_pickups", first),
        "night_pickups_last_week": week_value(d, "night_pickups", last),

        "last_use_mean_h": d.last_use_h.mean(),
        "last_screen_first_week_h": end_first,
        "last_screen_last_week_h": end_last,
        "wake_first_week_h": wake_first,
        "wake_last_week_h": wake_last,
        "sleep_first_week_h": (24 + wake_first) - end_first,
        "sleep_last_week_h": (24 + wake_last) - end_last,

        "alerts_sent": sum(1 for s in run.alerts if s.decision == "sent"),
        "alerts_held": sum(1 for s in run.alerts
                           if s.decision == "summary"),
        "alert_budget": ALERT_BUDGET,
        "positives_sent": sum(1 for s in run.positives
                              if s.decision == "sent"),
        "nudge_nights": run.nudge_summary["nights with a nudge"],
        "nights": run.nudge_summary["nights"],
        "emissions_total": len(run.emissions),
    }
    outage = filter_outage(run)
    if outage:
        out["outage"] = outage
    return {k: plain(v) for k, v in out.items()}


def profile(run: Analysis) -> dict:
    """One profile's whole entry in the document.

    Every key here is declared in `web/types/index.ts` as a `Profile`, and the
    type check compiles the emitted file against it — so adding one means
    adding it there too, and renaming one fails the build.
    """
    # Where the walkthrough opens: the day something was said, else the last.
    # A reader who never touches the slider should land on the interesting day.
    weeks = list(run.weekly.index)
    default_day = next((r["day"] for r in run.replay if r["alert"]),
                       run.replay[-1]["day"])
    return {
        "summary": summary(run),
        "daily": rows(run.daily.reset_index(drop=True), DAILY_COLUMNS),
        "weekly": rows(run.weekly, WEEKLY_COLUMNS, index_as="week"),
        "apps": rows(run.apps.reset_index(drop=True), USAGE_COLUMNS),
        "sites": rows(run.sites.reset_index(drop=True), USAGE_COLUMNS),
        "categoryDaily": rows(run.categories.reset_index(drop=True),
                              ("day", "category", "minutes")),
        "hourHeat": rows(run.heat.reset_index(drop=True),
                         ("dow", "hour", "minutes")),
        "blocks": block_counts(run.blocks),
        "alerts": [signal(s) for s in run.alerts],
        "positives": [signal(s) for s in run.positives],
        "nudges": [nudge(n) for n in run.nudges],
        "nudgeSummary": {snake(k): plain(v)
                         for k, v in run.nudge_summary.items()},
        "replay": [replay_day(r) for r in run.replay],
        "emissions": [{"day": plain(e["day"]), "destination": e["destination"],
                       "type": e["type"], "detail": e["detail"]}
                      for e in run.emissions],
        "anomalies": {k: int(v) for k, v in run.timeline.anomalies.items()},
        "eventCounts": event_counts(run.timeline),
        "defaultDay": plain(default_day),
        # The last full week. The final one is a two-day tail, and opening on
        # it would show a short week's averages as if they were a week's.
        "defaultWeek": int(weeks[-2] if len(weeks) > 1 else weeks[-1]),
    }


def block_counts(blocks: pd.DataFrame) -> dict:
    """The block stream as the tallies the page actually reads.

    Nothing displays a single blocked attempt: every view is a count by day,
    hour, week or target. Counting here rather than in the browser keeps 1,167
    rows off the wire and the arithmetic on the side that owns it.
    """
    if blocks.empty:
        return {"total": 0, "byDay": [], "byHour": [], "byWeek": [],
                "byType": {}, "top": []}

    def tally(field: str) -> list[dict]:
        counts = blocks.groupby([field, "category"]).size()
        return [{field: plain(key), "category": category, "count": int(n)}
                for (key, category), n in counts.items()]

    top = (blocks.groupby(["target", "block_type"]).size()
           .sort_values(ascending=False).head(10))
    return {
        "total": int(len(blocks)),
        "byDay": tally("day"),
        "byHour": tally("hour"),
        "byWeek": tally("week"),
        "byType": {k: int(v) for k, v in
                   blocks["block_type"].value_counts().items()},
        "top": [{"target": target, "block_type": kind, "count": int(n)}
                for (target, kind), n in top.items()],
    }


def event_counts(timeline: Timeline) -> dict:
    """How many of each event type the log carries.

    The events themselves do not cross the boundary — 2.4 MB of them, and the
    page never shows one — but the schema section names each type and says how
    many there were, so the tally does.
    """
    counts: dict[str, int] = {}
    for event in timeline.events:
        kind = event["event_type"]
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def replay_day(r: dict) -> dict:
    """One day of the replay: what the phone knew, and what it did about it."""
    return {
        "day": plain(r["day"]),
        "alert": signal(r["alert"]) if r["alert"] else None,
        "digest_entry": signal(r["digest_entry"]) if r["digest_entry"] else None,
        "positives": [signal(s) for s in r["positives"]],
        "nudge": nudge(r["nudge"]) if r["nudge"] else None,
        "alerts_so_far": r["alerts_so_far"],
        "positives_so_far": r["positives_so_far"],
        "digest_so_far": r["digest_so_far"],
        "nudges_so_far": r["nudges_so_far"],
    }
