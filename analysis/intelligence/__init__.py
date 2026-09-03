"""
Layer 3 · from metric to decision: what gets surfaced, when, and what stays
quiet.

Everything here runs on the phone and is read by the person holding it.
**Alerts** are coarse, object-free and on a budget: the failure mode of a
channel like this is not missing an event, it is interrupting until nobody
reads it, so every candidate earns its slot and the rest drop to the weekly
summary. **Nudges** are immediate, carry detail, and have their own silence
rules.

    signals.py    the thresholds, and the two records everything passes around
    alerts.py     the three rules, and the budget that decides between them
    nudge.py      the on-device night nudge, replayed over the period
    positives.py  reinforcements: what to say when nothing is wrong
    replay.py     the state at the close of each day, and what it emitted

DECISIONS.md has the reasoning; this package has the code.
"""

from .alerts import (
    ALERT_BUDGET,
    ALERT_MIN_GAP_DAYS,
    RULES,
    evaluate_alerts,
    weekly_digest,
)
from .nudge import nudge_summary, replay_nudge
from .positives import evaluate_positives
from .replay import emissions, month_replay
from .signals import (
    NUDGE_AFTER_MIN,
    NUDGE_MIN_REOPENS,
    POS_BUDGET_DAYS,
    POS_MIN_WEEK_DAYS,
    POS_NIGHT_QUIET_MIN,
    POS_OFFLINE_FLOOR_H,
    POS_RECORD_MARGIN,
    POS_STREAK_MILESTONES,
    NightNudge,
    Signal,
)

__all__ = [
    "ALERT_BUDGET", "ALERT_MIN_GAP_DAYS", "NUDGE_AFTER_MIN",
    "NUDGE_MIN_REOPENS", "POS_BUDGET_DAYS", "POS_MIN_WEEK_DAYS",
    "POS_NIGHT_QUIET_MIN", "POS_OFFLINE_FLOOR_H", "POS_RECORD_MARGIN",
    "POS_STREAK_MILESTONES", "RULES", "NightNudge", "Signal", "emissions",
    "evaluate_alerts", "evaluate_positives", "weekly_digest", "month_replay",
    "nudge_summary", "replay_nudge",
]
