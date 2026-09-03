"""Time windows, and the clock arithmetic the metrics do inside them.

Separate from `metrics.py` because a day, a night and a waking window are
definitions, not measurements: DECISIONS.md says why each is drawn where it is.
"""

from __future__ import annotations

from datetime import date

from .events import Interval, midnight_ms, to_dt

#: Waking window. Outside it, "offline time" is no achievement: you are
#: asleep. Used to normalise offline time and the longest screen-free stretch.
WAKE_START, WAKE_END = 7, 23        # 07:00 - 23:00 local time

#: Protected night band: use here is what costs rest the most.
NIGHT_START, NIGHT_END = 23, 6      # 23:00 - 06:00

def _overlap_s(a0: int, a1: int, b0: int, b1: int) -> float:
    return max(0, min(a1, b1) - max(a0, b0)) / 1000


def _window_ms(d: date, h0: int, h1: int) -> tuple[int, int]:
    base = midnight_ms(d)
    return base + h0 * 3600_000, base + h1 * 3600_000


def _night_window(d: date) -> tuple[int, int]:
    """The **night of day d**: 23:00 on d → 06:00 on d+1.

    The calendar day still cuts at midnight, but sleep does not. A message at
    01:30 on Tuesday belongs to Monday night, and that is how the user counts
    it. Keeping both conventions at once avoids splitting one night across two
    rows.
    """
    base = midnight_ms(d)
    return base + NIGHT_START * 3600_000, base + (24 + NIGHT_END) * 3600_000


def _shift_h(ms: int | None) -> float | None:
    """Time of day on an axis starting at 04:00, so the small hours (00:00 to
    04:00) come out as 24 to 28 rather than 0 to 4. Without this, the mean
    "time of last screen" *drops* when someone goes to bed *later*."""
    if not ms:
        return None
    t = to_dt(ms)
    h = t.hour + t.minute / 60
    return h + 24 if h < 4 else h


def _fmt_clock(ms: int | None) -> str | None:
    return to_dt(ms).strftime("%H:%M") if ms else None


#: Day name and time band, so we can say "Saturday afternoon" instead of just
#: "3 h 47 min". A duration without the when does not situate anything.
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]
# The limit is the *upper* bound of each band: hours below 6 are early
# morning, below 12 morning, and so on. The Spanish version this was
# translated from had the list off by one, so 03:00 read as "morning" and
# 10:00 as "midday".
BANDS = [(6, "early morning"), (12, "morning"), (15, "midday"),
         (20, "afternoon"), (24, "evening")]


def _when(ms: int) -> str:
    """`ms` → "Saturday afternoon"."""
    t = to_dt(ms)
    band = next(name for limit, name in BANDS if t.hour < limit)
    return f"{DAY_NAMES[t.weekday()]} {band}"


def _longest_gap(intervals: list[Interval], w0: int,
                 w1: int) -> tuple[float, int | None]:
    """Longest screen-free stretch inside the waking window, and when it starts.

    Returns the start alongside the duration because a stretch without a moment
    says nothing: "3 h 47 min" is a number, "3 h 47 min on Saturday afternoon"
    is something the person recognises.
    """
    pts = sorted((max(i.start_ms, w0), min(i.end_ms, w1))
                 for i in intervals if i.end_ms > w0 and i.start_ms < w1)
    best, best_start, cursor = 0.0, w0, w0
    for s, e in pts:
        if (s - cursor) / 1000 > best:
            best, best_start = (s - cursor) / 1000, cursor
        cursor = max(cursor, e)
    if (w1 - cursor) / 1000 > best:
        best, best_start = (w1 - cursor) / 1000, cursor
    return best, (best_start if best > 0 else None)
