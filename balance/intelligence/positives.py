"""Reinforcements: what is worth saying when nothing is wrong."""

from __future__ import annotations

from datetime import date

import pandas as pd

from .signals import (
    POS_BUDGET_DAYS,
    POS_MIN_WEEK_DAYS,
    POS_NIGHT_QUIET_MIN,
    POS_OFFLINE_FLOOR_H,
    POS_RECORD_MARGIN,
    POS_STREAK_MILESTONES,
    Signal,
)

# in the weekly summary, which is where the full picture lives.


def _num(x: float, dec: int = 1) -> str:
    """One decimal place, kept in a helper so the copy stays consistent."""
    return f"{x:.{dec}f}"


def _hm(minutes: float) -> str:
    h, m = divmod(int(round(minutes)), 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def _weeks(df: pd.DataFrame) -> pd.DataFrame:
    """Weekly aggregate, only the weeks that are long enough."""
    w = df.groupby("week").agg(
        days=("day", "count"), last_day=("day", "max"),
        screen=("screen_min", "mean"), pickups=("pickups", "mean"),
        night=("night_min", "mean"), blocks=("blocks", "mean"),
        sensitive=("blocks_sensitive", "sum"),
        distract=("distract_share", "mean"), score=("score", "mean"),
    )
    return w[w.days >= POS_MIN_WEEK_DAYS]


def _pos(key, day, headline, text, evidence, audience="user") -> Signal:
    return Signal(key=key, day=day, headline=headline, guardian_text=text,
                  magnitude=1.0, persistence=1.0, actionability=1.0,
                  evidence=evidence, audience=audience, tone="reinforcement")


def _offline_record(df: pd.DataFrame) -> list[Signal]:
    """Best screen-free stretch of the last two weeks."""
    out = []
    off = (df["longest_offline_s"] / 3600).reset_index(drop=True)
    days = df["day"].reset_index(drop=True)
    for i in range(14, len(df)):
        prev = off.iloc[i - 14:i].max()
        v = off.iloc[i]
        if v >= max(prev * POS_RECORD_MARGIN, POS_OFFLINE_FLOOR_H):
            out.append(_pos(
                "offline_record", days.iloc[i],
                "Longest screen-free stretch of the last two weeks",
                f"{_hm(v * 60)} in a row without turning the screen on. The best "
                f"record of the previous two weeks was {_hm(prev * 60)}.",
                {"stretch (h)": round(float(v), 2),
                 "best of 14 days (h)": round(float(prev), 2)}))
    return out


def _night_streak(df: pd.DataFrame) -> list[Signal]:
    """Consecutive nights with no screen inside the protected band."""
    out, streak = [], 0
    for day, night in zip(df["day"], df["night_min"]):
        streak = streak + 1 if night < POS_NIGHT_QUIET_MIN else 0
        if streak in POS_STREAK_MILESTONES:
            out.append(_pos(
                "night_streak", day,
                f"{streak} nights in a row with no late-night screen",
                f"{streak} consecutive nights without turning the screen on "
                f"between 23:00 and 06:00.",
                {"consecutive nights": streak}))
    return out


def _calm_week(df: pd.DataFrame) -> list[Signal]:
    """A week with fewer filter interventions than the previous two."""
    out, w = [], _weeks(df)
    for i in range(2, len(w)):
        cur, prev = w.iloc[i], w.iloc[i - 2:i]
        base = prev.blocks.mean()
        if base >= 1 and cur.blocks <= base * 0.7:
            out.append(_pos(
                "calm_week", cur.last_day,
                "The filter stepped in less than in previous weeks",
                f"This week the filter acted {_num(cur.blocks)} times a day, "
                f"against {_num(base)} over the previous two weeks.",
                {"blocks/day this week": round(float(cur.blocks), 2),
                 "blocks/day previous 2 weeks": round(float(base), 2)}))
    return out


def _focus_week(df: pd.DataFrame) -> list[Signal]:
    """A week with a smaller share of time in social, entertainment and games."""
    out, w = [], _weeks(df)
    for i in range(1, len(w)):
        cur, prev = w.iloc[i], w.iloc[i - 1]
        if prev.distract >= 0.10 and cur.distract <= prev.distract * 0.8:
            out.append(_pos(
                "focus_week", cur.last_day,
                "Less time in social, entertainment and games than last week",
                f"This week {cur.distract*100:.0f} % of screen time went to "
                f"social, entertainment or games, against "
                f"{prev.distract*100:.0f} % the week before.",
                {"share this week": f"{cur.distract*100:.1f} %",
                 "share last week": f"{prev.distract*100:.1f} %"}))
    return out


def _best_week(df: pd.DataFrame) -> list[Signal]:
    """Highest weekly index in the available history."""
    out, w = [], _weeks(df)
    for i in range(3, len(w)):
        cur, prev = w.iloc[i], w.iloc[:i]
        if cur.score > prev.score.max():
            out.append(_pos(
                "best_week", cur.last_day,
                "Highest weekly index of the period",
                f"This week's index is {cur.score:.0f} out of 100, the highest "
                f"since records began. The previous best was "
                f"{prev.score.max():.0f}.",
                {"index this week": round(float(cur.score), 1),
                 "previous best": round(float(prev.score.max()), 1)}))
    return out


def _filter_calm(df: pd.DataFrame) -> list[Signal]:
    """A clear drop in attempts towards sensitive content. Goes to the guardian.

    It is the exact reverse of `sensitive_spike`, at the same granularity: no
    figures, no objects, no categories. A guardian who only hears from the
    product when something gets worse ends up reading the channel as a threat.
    """
    out, w = [], _weeks(df)
    for i in range(1, len(w)):
        cur, prev = w.iloc[i], w.iloc[i - 1]
        if prev.sensitive >= 10 and cur.sensitive <= prev.sensitive * 0.6:
            out.append(_pos(
                "filter_calm", cur.last_day,
                "The sensitive-content filter stepped in less",
                "This week the sensitive-content filter stepped in considerably "
                "less than last week. No content opened, as in previous weeks.",
                {"attempts this week": int(cur.sensitive),
                 "attempts last week": int(prev.sensitive)},
                audience="guardian"))
    return out


POSITIVE_RULES = (_offline_record, _night_streak, _calm_week,
                  _focus_week, _best_week, _filter_calm)


def evaluate_positives(df: pd.DataFrame, has_guardian: bool = True) -> list[Signal]:
    """Candidate reinforcements, with a quota of one per week and audience.

    Whatever does not fit the quota is not discarded: it drops to the weekly
    summary, where the user sees the full picture without being interrupted.
    """
    signals: list[Signal] = []
    for rule in POSITIVE_RULES:
        signals.extend(rule(df))
    if not has_guardian:
        signals = [s for s in signals if s.audience != "guardian"]

    last_sent: dict[str, date] = {}
    for s in sorted(signals, key=lambda x: x.day):
        prev = last_sent.get(s.audience)
        if prev and (s.day - prev).days < POS_BUDGET_DAYS:
            s.decision = "summary"
            s.reason = (f"A reinforcement went to this audience less than "
                        f"{POS_BUDGET_DAYS} days ago. It enters the weekly "
                        f"summary instead.")
            continue
        s.decision, s.reason = "sent", "Measurable improvement over own history."
        last_sent[s.audience] = s.day
    return sorted(signals, key=lambda x: x.day)
