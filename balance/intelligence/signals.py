"""The vocabulary: thresholds, a Signal, a NightNudge."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

#: Windows for the night-drift detector. 5 recent nights against the previous
#: 14: needs 19 days of history, and in exchange fires early without reacting
#: to a single odd night.
DRIFT_RECENT, DRIFT_BASE = 5, 14
DRIFT_RATIO = 2.0          # the recent median doubles the reference one
DRIFT_ABS_MIN = 20.0       # ...and it is at least 20 min: 2× of 3 min is nothing
DRIFT_CLOCK_MIN = 40.0     # ...and lights-out has moved 40 min or more

#: Sensitive-content spike: 7-day sum against the rate of the previous ones.
SPIKE_RECENT, SPIKE_BASE = 7, 7
SPIKE_RATIO, SPIKE_ABS_MIN = 2.5, 10

#: The "obvious" rule almost anyone would implement, included on purpose so we
#: can show it does NOT fire on this data.
SCREEN_JUMP_RATIO, SCREEN_JUMP_ABS = 1.4, 60.0

#: Alert quota per 30 days, and minimum gap between two. The channel is
#: finite: an app that interrupts freely stops being read.
ALERT_BUDGET = 2
ALERT_MIN_GAP_DAYS = 10

#: Minimum margin before a record counts as genuinely beaten.
POS_RECORD_MARGIN = 1.10
#: Absolute floor for the disconnection record: 90 min without looking at the
#: phone is nobody's achievement.
POS_OFFLINE_FLOOR_H = 3.0
#: Milestones for the protected-night streak.
POS_STREAK_MILESTONES = (7, 14, 30)
#: A night counts as protected below this threshold.
POS_NIGHT_QUIET_MIN = 5.0
#: Weeks shorter than this generate no reinforcement: a three-day week always
#: looks better than a seven-day one.
POS_MIN_WEEK_DAYS = 5
#: Minimum days between two reinforcements.
POS_BUDGET_DAYS = 7

#: Night nudge: arms 30 min after the band opens, and only from the second
#: reopening onwards.
NUDGE_AFTER_MIN = 30
NUDGE_MIN_REOPENS = 2


# ---------------------------------------------------------------------------
# Structures
# ---------------------------------------------------------------------------

@dataclass
class Signal:
    """A candidate alert. It may end up sent, summarised or discarded."""
    key: str
    day: date                   # first day the rule holds
    headline: str
    body: str                   # the exact wording the phone would show
    magnitude: float            # 0 to 1 · how far outside normal
    persistence: float          # 0 to 1 · how long it has been outside
    actionability: float        # 0 to 1 · is there anything to be done about it?
    evidence: dict = field(default_factory=dict)   # NEVER leaves the device
    decision: str = "candidate"                    # sent | summary | discarded
    reason: str = ""
    until: date | None = None   # last day of the episode, if it runs on
    tone: str = "alert"         # alert | reinforcement

    @property
    def days_true(self) -> int:
        return ((self.until - self.day).days + 1) if self.until else 1

    @property
    def priority(self) -> float:
        """Product, not sum: an alert that is huge but one day long, or
        persistent but not actionable, should not sneak through."""
        return round(self.magnitude * self.persistence * self.actionability, 3)


@dataclass
class NightNudge:
    """What the nudge would have done each night, and what was at stake."""
    day: date
    fired: bool
    at_ms: int | None
    quiet_reason: str
    reopens: int
    minutes_after: float        # night screen time after the trigger
    night_minutes: float


def _clamp(x: float) -> float:
    return float(max(0.0, min(1.0, x)))
