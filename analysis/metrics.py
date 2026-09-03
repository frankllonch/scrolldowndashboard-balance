"""
Layer 1 · Timeline → daily and weekly metrics.

One row per day and user. Everything the dashboard draws comes from here.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from datetime import date, timedelta
from statistics import median

import pandas as pd

from .events import (
    DISTRACTING,
    SENSITIVE,
    Timeline,
    Usage,
    app_label,
    midnight_ms,
    to_dt,
)
from .windows import (
    NIGHT_END,
    WAKE_END,
    WAKE_START,
    _fmt_clock,
    _longest_gap,
    _night_window,
    _overlap_s,
    _shift_h,
    _when,
    _window_ms,
)


def _by_day(items: Iterable) -> dict[date, list]:
    """Anything with a `.day`, grouped by it."""
    out: dict[date, list] = defaultdict(list)
    for item in items:
        out[item.day].append(item)
    return out


def _switches_per_day(usages: list[Usage]) -> Counter:
    """Foreground moves between two different apps, counted per day.

    The counter resets at midnight. Without that the first app of the morning
    counts as a switch from the last one of the night before, which added one
    false switch a day (~5 % of the total) and, worse, made a "switch" span
    eight hours of sleep.
    """
    switches: Counter = Counter()
    previous: dict[date, str] = {}
    for u in sorted(usages, key=lambda x: x.start_ms):
        if u.kind != "app":
            continue
        if previous.get(u.day) not in (None, u.key):
            switches[u.day] += 1
        previous[u.day] = u.key
    return switches


def daily_frame(tl: Timeline) -> pd.DataFrame:
    """One row per day with every base metric."""
    by_day_iv = _by_day(tl.intervals)
    by_day_use = _by_day(tl.usages)
    by_day_block = _by_day(tl.blocks)
    switches_by_day = _switches_per_day(tl.usages)

    file_start = tl.events[0]["timestamp_millis"]
    file_end = tl.events[-1]["timestamp_millis"]

    rows = []
    for d in tl.days:
        ivs = sorted(by_day_iv[d], key=lambda i: i.start_ms)
        uses = by_day_use[d]
        blocks = by_day_block[d]

        screen_s = sum(i.seconds for i in ivs)
        pickups = sum(i.pickups for i in ivs)
        glances = sum(i.glances for i in ivs)

        w0, w1 = _window_ms(d, WAKE_START, WAKE_END)
        screen_wake_s = sum(_overlap_s(i.start_ms, i.end_ms, w0, w1) for i in ivs)
        offline_wake_s = max(0.0, (w1 - w0) / 1000 - screen_wake_s)

        # the night is measured over ALL stretches, not only this day's: the
        # night of day d runs until 06:00 the next day.
        n0, n1 = _night_window(d)
        night_s = sum(_overlap_s(i.start_ms, i.end_ms, n0, n1) for i in tl.intervals)
        night_pickups = sum(i.pickups for i in tl.intervals if n0 <= i.start_ms < n1)
        night_last = max((i.end_ms for i in tl.intervals
                          if i.start_ms < n1 and i.end_ms > n0), default=None)

        # "First pickup" = the first one from 06:00 onwards. Without that
        # floor, a day starting at 00:20 (the tail of the previous night) would
        # register as "started at 00:20", which is not starting the day: it is
        # not having finished it. That phenomenon is measured separately, in
        # `night_*`.
        offline_s, offline_start = _longest_gap(ivs, w0, w1)

        morning = midnight_ms(d) + NIGHT_END * 3600_000
        real = [i for i in ivs if i.is_pickup and i.start_ms >= morning]
        first_pick = min((i.start_ms for i in real), default=None)
        last_use = max((i.end_ms for i in ivs), default=None)

        cat_s: Counter = Counter()
        app_s: Counter = Counter()
        site_s: Counter = Counter()
        for u in uses:
            cat_s[u.category] += u.seconds
            (app_s if u.kind == "app" else site_s)[u.key] += u.seconds
        attributed = sum(cat_s.values())
        distract_s = sum(v for k, v in cat_s.items() if k in DISTRACTING)

        bt = Counter(b.block_type for b in blocks)
        bc = Counter(b.category for b in blocks)

        # how much of the calendar day the file actually covers. The last day
        # of user_b only reaches 00:46; averaging it would sink the means.
        d0, d1 = midnight_ms(d), midnight_ms(d + timedelta(days=1))
        coverage_h = max(0, min(file_end, d1) - max(file_start, d0)) / 3600_000

        rows.append({
            "day": d,
            "dow": d.weekday(),
            "is_weekend": d.weekday() >= 5,
            "week": (d - tl.days[0]).days // 7 + 1,
            "coverage_h": coverage_h,
            "is_partial": coverage_h < 12,

            "screen_s": screen_s,
            "screen_min": screen_s / 60,
            "screen_wake_s": screen_wake_s,
            "offline_wake_s": offline_wake_s,
            "offline_wake_h": offline_wake_s / 3600,
            "sessions": len(ivs),
            "longest_session_s": max((i.seconds for i in ivs), default=0),
            # a real median: with even n, the mean of the two middle values
            "median_session_s": (median(i.seconds for i in ivs) if ivs else 0),

            "pickups": pickups,
            "glances": glances,
            "pickup_rate": pickups / max(1, pickups + glances),
            "pickups_per_wake_hour": pickups / (WAKE_END - WAKE_START),

            "first_pickup_ms": first_pick,
            "first_pickup_h": _shift_h(first_pick),
            "last_use_ms": last_use,
            "last_use_h": _shift_h(last_use),
            "night_s": night_s,
            "night_min": night_s / 60,
            "night_pickups": night_pickups,
            "night_end_h": _shift_h(night_last),
            "longest_offline_s": offline_s,
            "longest_offline_h": offline_s / 3600,
            "longest_offline_start_ms": offline_start,
            "longest_offline_when": (_when(offline_start)
                                     if offline_start else None),

            "distinct_apps": len({u.key for u in uses if u.kind == "app"}),
            "distinct_sites": len({u.key for u in uses if u.kind == "site"}),
            "app_switches": switches_by_day[d],
            "switches_per_screen_hour": (switches_by_day[d] / (screen_s / 3600)
                                         if screen_s > 60 else 0),

            "attributed_s": attributed,
            "distract_s": distract_s,
            "distract_share": distract_s / attributed if attributed else 0,

            "blocks": len(blocks),
            "blocks_app": bt.get("APP", 0),
            "blocks_url": bt.get("URL", 0),
            "blocks_nudity": bt.get("NUDITY", 0),
            "blocks_sensitive": sum(v for k, v in bc.items() if k in SENSITIVE),
            "blocks_adult": bc.get("ADULT", 0),
            "blocks_gambling": bc.get("GAMBLING", 0),
            "blocks_social": bc.get("SOCIAL_MEDIA", 0),
            "blocks_gaming": bc.get("GAMING", 0),
            "blocks_entertainment": bc.get("ENTERTAINMENT", 0),

            "_cat_s": dict(cat_s),
            "_app_s": dict(app_s),
            "_site_s": dict(site_s),
        })

    df = pd.DataFrame(rows).set_index("day", drop=False)
    df = df[~df["is_partial"]].copy()      # drop days truncated by the file edge
    df["first_pickup_clock"] = [_fmt_clock(m) for m in df["first_pickup_ms"]]
    df["last_use_clock"] = [_fmt_clock(m) for m in df["last_use_ms"]]

    # personal baseline: rolling median of the previous 14 days (today excluded).
    # Median rather than mean: one odd holiday should not move "normal for me".
    for col in ("screen_min", "pickups", "night_min", "blocks"):
        df[f"{col}_baseline"] = df[col].shift(1).rolling(14, min_periods=5).median()
        df[f"{col}_delta"] = df[col] - df[f"{col}_baseline"]
    return df


# ---------------------------------------------------------------------------
# Agregados no diarios
# ---------------------------------------------------------------------------

def totals(tl: Timeline, df: pd.DataFrame, kind: str) -> pd.DataFrame:
    """Ranking of apps or domains by total time and openings.

    `df` decides which days count: the ones truncated by the file edge have
    already dropped out of it, and they have to drop out here too so the totals
    match the KPIs.
    """
    days = set(df["day"])
    secs: Counter = Counter()
    opens: Counter = Counter()
    cats: dict[str, str] = {}
    for u in tl.usages:
        if u.kind != kind or u.day not in days:
            continue
        secs[u.key] += u.seconds
        opens[u.key] += 1
        cats[u.key] = u.category
    out = pd.DataFrame({
        "key": list(secs),
        "label": [app_label(k) if kind == "app" else k for k in secs],
        "category": [cats[k] for k in secs],
        "minutes": [secs[k] / 60 for k in secs],
        "opens": [opens[k] for k in secs],
    })
    if out.empty:
        return out
    out["min_per_open"] = out.minutes / out.opens
    return out.sort_values("minutes", ascending=False).reset_index(drop=True)


def category_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Minutes per category and day (long format: one row per pair)."""
    rows = []
    for d, cats in zip(df["day"], df["_cat_s"]):
        for c, s in cats.items():
            rows.append({"day": d, "category": c, "minutes": s / 60})
    return pd.DataFrame(rows)


def hourly_heat(tl: Timeline, days: set[date] | None = None) -> pd.DataFrame:
    """Screen minutes per (weekday, hour): a usage clock."""
    grid: Counter = Counter()
    for iv in tl.intervals:
        if days is not None and iv.day not in days:
            continue
        start = iv.start_ms
        while start < iv.end_ms:
            dtm = to_dt(start)
            hour_end = midnight_ms(dtm.date()) + (dtm.hour + 1) * 3600_000
            end = min(iv.end_ms, hour_end)
            grid[(dtm.weekday(), dtm.hour)] += (end - start) / 60_000
            start = end
    return pd.DataFrame(
        [{"dow": k[0], "hour": k[1], "minutes": v} for k, v in grid.items()]
    )


def blocks_frame(tl: Timeline, days: set[date] | None = None) -> pd.DataFrame:
    """One row per blocked attempt. Nothing in it ever opened.

    `days` is the set of complete days: a block on a day the file cut short
    has to leave this frame too, or the per-day counts stop matching the
    daily frame beside them.
    """
    return pd.DataFrame([{
        "day": b.day, "hour": to_dt(b.ts_ms).hour,
        "block_type": b.block_type, "category": b.category, "target": b.target,
    } for b in tl.blocks if days is None or b.day in days])


def weekly_frame(df: pd.DataFrame) -> pd.DataFrame:
    """One row per week, with the change against the previous week.

    The same magnitudes as the daily frame but averaged per day, so a short
    week (the last one of the period usually is) does not look better just for
    having fewer days. `is_partial` flags the ones under 7.
    """
    w = df.groupby("week").agg(
        days=("day", "count"),
        start=("day", "min"), end=("day", "max"),
        screen_min=("screen_min", "mean"),
        pickups=("pickups", "mean"),
        glances=("glances", "mean"),
        night_min=("night_min", "mean"),
        night_pickups=("night_pickups", "mean"),
        night_end_h=("night_end_h", "median"),
        first_pickup_h=("first_pickup_h", "median"),
        longest_offline_h=("longest_offline_s", lambda s: s.mean() / 3600),
        best_offline_h=("longest_offline_h", "max"),
        distinct_apps=("distinct_apps", "mean"),
        switches_per_screen_hour=("switches_per_screen_hour", "mean"),
        distract_share=("distract_share", "mean"),
        blocks=("blocks", "mean"),
        blocks_total=("blocks", "sum"),
        blocks_sensitive=("blocks_sensitive", "sum"),
        score=("score", "mean"),
    )
    # The "when" of each week's best stretch: the phrase that turns a duration
    # into something the person recognises.
    mejor = df.loc[df.groupby("week")["longest_offline_s"].idxmax()]
    w["best_offline_when"] = mejor.set_index("week")["longest_offline_when"]
    w["best_offline_day"] = mejor.set_index("week")["day"]

    w["is_partial"] = w["days"] < 7
    for col in ("screen_min", "pickups", "night_min", "blocks", "score",
                "distract_share", "longest_offline_h", "night_end_h"):
        w[f"{col}_prev"] = w[col].shift(1)
        w[f"{col}_delta"] = w[col] - w[f"{col}_prev"]
    return w
