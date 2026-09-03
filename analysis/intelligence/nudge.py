"""The on-device night nudge, replayed over the period."""

from __future__ import annotations

import pandas as pd

from ..events import Timeline, to_dt
from ..metrics import _night_window
from .signals import (
    NUDGE_AFTER_MIN,
    NUDGE_MIN_REOPENS,
    NightNudge,
)

NUDGE_COPY = (
    "That is the {n}th time you have opened your phone tonight.\n"
    "A month ago you had already put it down by now."
)


def replay_nudge(tl: Timeline, df: pd.DataFrame) -> list[NightNudge]:
    """Replays the nudge over history: when it would have shown and what was at
    stake when it did.

    You cannot A/B test a closed file, but you can measure the nudge's
    **ceiling**: the night screen minutes that happen *after* the moment it
    would have appeared. That bounds what it can recover, and the number of
    nights without a trigger bounds how much it annoys.
    """
    out: list[NightNudge] = []
    baseline = df.set_index("day")["night_min_baseline"].to_dict()
    recent3 = df.set_index("day")["night_min"].rolling(3, min_periods=1).median().to_dict()

    for d in df.day:
        n0, n1 = _night_window(d)
        ivs = sorted([i for i in tl.intervals if i.end_ms > n0 and i.start_ms < n1],
                     key=lambda i: i.start_ms)
        night_min = sum((min(i.end_ms, n1) - max(i.start_ms, n0)) / 60_000 for i in ivs)
        arm_from = n0 + NUDGE_AFTER_MIN * 60_000
        reopens = [i for i in ivs if i.is_pickup and i.start_ms >= arm_from]

        quiet = ""
        if len(reopens) < NUDGE_MIN_REOPENS:
            quiet = ("A single reopening: staying up late one night is not a "
                     "pattern, and alerting on it teaches people to ignore the "
                     "alert.")
        else:
            base, rec = baseline.get(d), recent3.get(d)
            if base is not None and rec is not None and not pd.isna(base) and rec < base:
                quiet = ("The last few nights are already better than their own "
                         "median; when someone is correcting on their own, the "
                         "useful thing is to stay quiet.")

        fired = not quiet and len(reopens) >= NUDGE_MIN_REOPENS
        at = reopens[NUDGE_MIN_REOPENS - 1].start_ms if fired else None
        after = (sum((min(i.end_ms, n1) - max(i.start_ms, at)) / 60_000
                     for i in ivs if i.end_ms > at) if fired else 0.0)

        out.append(NightNudge(d, fired, at, quiet, len(reopens), after, night_min))
    return out


def nudge_summary(nudges: list[NightNudge]) -> dict:
    fired = [n for n in nudges if n.fired]
    night_total = sum(n.night_minutes for n in nudges)
    after = sum(n.minutes_after for n in fired)
    return {
        "nights": len(nudges),
        "nights with a nudge": len(fired),
        "appearance rate": len(fired) / max(len(nudges), 1),
        "total night minutes": night_total,
        "minutes at stake after the nudge": after,
        "share of night total": after / night_total if night_total else 0.0,
        "minutes at stake per nudged night": after / len(fired) if fired else 0.0,
        "median nudge time": (
            sorted(to_dt(n.at_ms).hour + to_dt(n.at_ms).minute / 60 % 24
                   for n in fired)[len(fired) // 2] if fired else None),
    }
