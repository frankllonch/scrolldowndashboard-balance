"""The pipeline, wired once.

Every layer in the right order over one event log, with the awkward joins the
readers would otherwise each have to remember. Both of them — the command line
and `payload/` — call this, so there is one answer to "what does the system
derive from a log", not two that can drift.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .events import Timeline, load
from .intelligence import (
    emissions,
    evaluate_alerts,
    evaluate_positives,
    month_replay,
    nudge_summary,
    replay_nudge,
)
from .metrics import (
    blocks_frame,
    category_daily,
    daily_frame,
    hourly_heat,
    totals,
    weekly_frame,
)
from .score import COMPONENTS, add_score

#: Where each profile's log lives, relative to the repository root.
PROFILES = {"A": "data/events_user_a.json", "B": "data/events_user_b.json"}


@dataclass(frozen=True)
class Analysis:
    """Everything the system derives from one log.

    A pure function of that file: same input, same result, no external state
    and no dependency on the time of execution.
    """

    user: str
    timeline: Timeline
    #: One row per day, with the index and its five components.
    daily: pd.DataFrame
    #: One row per week, with each component averaged over it.
    weekly: pd.DataFrame
    #: Minutes per app and per domain over the period.
    apps: pd.DataFrame
    sites: pd.DataFrame
    #: Minutes per category and day, and per weekday and hour.
    categories: pd.DataFrame
    heat: pd.DataFrame
    #: One row per blocked attempt, tagged with the week it fell in.
    blocks: pd.DataFrame
    alerts: list
    positives: list
    nudges: list
    nudge_summary: dict
    #: The state at the close of each day, and what the phone emitted.
    replay: list
    emissions: list


def analyse(user: str, root: Path | str = ".") -> Analysis:
    """Run every layer over one profile's log, in order.

    The joins here are the ones a reader would get wrong: the truncated days
    have to leave every view rather than only the daily frame, the component
    scores have to be averaged onto the weekly rows, and the blocks have to
    know which week they fell in.
    """
    timeline = load(Path(root) / PROFILES[user], user)
    daily = add_score(daily_frame(timeline))
    # Days truncated by the file edge stay out of EVERY view, not only the
    # daily frame, or the totals stop matching.
    days = set(daily["day"])

    nudges = replay_nudge(timeline, daily)
    alerts = evaluate_alerts(daily)
    positives = evaluate_positives(daily)
    replay = month_replay(daily, nudges, positives)

    weekly = weekly_frame(daily)
    for column, *_ in COMPONENTS:
        weekly[f"score_{column}"] = daily.groupby("week")[f"score_{column}"].mean()

    blocks = blocks_frame(timeline, days)
    if not blocks.empty:
        week_of = dict(zip(daily["day"], daily["week"]))
        blocks = blocks.assign(week=[week_of[d] for d in blocks["day"]])

    return Analysis(
        user=user, timeline=timeline, daily=daily, weekly=weekly,
        apps=totals(timeline, daily, "app"),
        sites=totals(timeline, daily, "site"),
        categories=category_daily(daily),
        heat=hourly_heat(timeline, days),
        blocks=blocks, alerts=alerts, positives=positives, nudges=nudges,
        nudge_summary=nudge_summary(nudges), replay=replay,
        emissions=emissions(replay),
    )
