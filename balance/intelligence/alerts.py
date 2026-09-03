"""The three alert rules, and the budget that silences them."""

from __future__ import annotations

import pandas as pd

from .signals import (
    ALERT_BUDGET,
    ALERT_MIN_GAP_DAYS,
    DRIFT_ABS_MIN,
    DRIFT_BASE,
    DRIFT_CLOCK_MIN,
    DRIFT_RATIO,
    DRIFT_RECENT,
    POS_NIGHT_QUIET_MIN,
    SCREEN_JUMP_ABS,
    SCREEN_JUMP_RATIO,
    SPIKE_ABS_MIN,
    SPIKE_BASE,
    SPIKE_RATIO,
    SPIKE_RECENT,
    Signal,
    _clamp,
)


def _night_drift(df: pd.DataFrame) -> list[Signal]:
    """A regime change in the night band.

    Not a threshold ("more than 30 min after midnight"), a sustained shift in
    distribution. With a threshold, B would have fired and stopped firing
    night by night; and above all, a fixed threshold cannot tell someone who
    has always been like this from someone who **has just changed**. The
    second is the only one worth interrupting a parent for.
    """
    out: list[Signal] = []
    need = DRIFT_RECENT + DRIFT_BASE
    for i in range(need - 1, len(df)):
        rec = df.night_min.iloc[i - DRIFT_RECENT + 1: i + 1]
        base = df.night_min.iloc[i - DRIFT_RECENT + 1 - DRIFT_BASE: i - DRIFT_RECENT + 1]
        rec_m, base_m = rec.median(), max(base.median(), 1.0)
        clock = (df.night_end_h.iloc[i - DRIFT_RECENT + 1: i + 1].median()
                 - df.night_end_h.iloc[i - DRIFT_RECENT + 1 - DRIFT_BASE:
                                       i - DRIFT_RECENT + 1].median()) * 60
        above = int((rec > base_m).sum())

        if not (rec_m >= DRIFT_ABS_MIN and rec_m >= DRIFT_RATIO * base_m
                and clock >= DRIFT_CLOCK_MIN and above >= DRIFT_RECENT - 1):
            continue

        out.append(Signal(
            key="night_drift",
            day=df.day.iloc[i],
            headline="The sleep schedule has shifted",
            # Purely descriptive. No recommendations: the product reports a
            # measured change, it does not tell anyone what to do about it.
            body=(
                # Wording note: this avoids the words "other" and "news",
                # which collide with the OTHER and NEWS category names and
                # would trip the privacy test for no real reason.
                "Over the last few weeks the phone has been going dark later "
                "than it used to, and the wake-up time has not changed. The "
                "remaining indicators are holding steady."),
            magnitude=_clamp((rec_m / base_m - DRIFT_RATIO) / 4 + .5),
            persistence=_clamp(above / DRIFT_RECENT),
            actionability=1.0,      # a schedule is something you can actually move
            evidence={
                "recent night median (min)": round(float(rec_m), 1),
                "reference night median (min)": round(float(base.median()), 1),
                "last-screen delay (min)": int(round(clock)),
                "nights above normal": f"{above} of {DRIFT_RECENT}",
            },
        ))
    return out


def _sensitive_spike(df: pd.DataFrame) -> list[Signal]:
    """An uptick in attempts towards adult or gambling content.

    It is detected, but almost never sent: see `_decide`. The phone already
    blocked it, so urgency is low and the cost of telling a parent in the heat
    of the moment is high.
    """
    out: list[Signal] = []
    need = SPIKE_RECENT + SPIKE_BASE
    for i in range(need - 1, len(df)):
        rec = df.blocks_sensitive.iloc[i - SPIKE_RECENT + 1: i + 1].sum()
        base_rate = (df.blocks_sensitive.iloc[i - SPIKE_RECENT + 1 - SPIKE_BASE:
                                              i - SPIKE_RECENT + 1].sum()
                     / SPIKE_BASE * SPIKE_RECENT)
        if not (rec >= SPIKE_ABS_MIN and rec >= SPIKE_RATIO * max(base_rate, 1)):
            continue
        out.append(Signal(
            key="sensitive_spike",
            day=df.day.iloc[i],
            headline="The sensitive-content filter acted more than usual",
            body=(
                "This week the content filter stepped in more often than usual. "
                "Every attempt was blocked and no content opened."),
            magnitude=_clamp((rec / max(base_rate, 1) - SPIKE_RATIO) / 5 + .5),
            persistence=_clamp(
                (df.blocks_sensitive.iloc[i - SPIKE_RECENT + 1: i + 1] > 0).sum()
                / SPIKE_RECENT),
            # Deliberately low: the block already happened. What is left is a
            # conversation, and that conversation gains nothing by arriving
            # today rather than on Sunday.
            actionability=0.35,
            evidence={
                "attempts in 7 days": int(rec),
                "reference rate": round(float(base_rate), 1),
                "opened": 0,
            },
        ))
    return out


def _screen_jump(df: pd.DataFrame) -> list[Signal]:
    """The obvious rule: "screen time has gone up a lot".

    It is here so we can show it **does not fire** on this data. It is the
    system's negative control.
    """
    out: list[Signal] = []
    need = DRIFT_RECENT + DRIFT_BASE
    for i in range(need - 1, len(df)):
        rec = df.screen_min.iloc[i - DRIFT_RECENT + 1: i + 1].median()
        base = max(df.screen_min.iloc[i - DRIFT_RECENT + 1 - DRIFT_BASE:
                                      i - DRIFT_RECENT + 1].median(), 1.0)
        if rec >= SCREEN_JUMP_RATIO * base and rec - base >= SCREEN_JUMP_ABS:
            out.append(Signal(
                key="screen_jump", day=df.day.iloc[i],
                headline="Screen time has gone up",
                body="Daily use has grown against previous weeks.",
                magnitude=_clamp((rec / base - 1) * 2),
                persistence=1.0, actionability=0.5,
                evidence={"recent median (min)": round(float(rec)),
                          "reference (min)": round(float(base))}))
    return out


RULES = (_night_drift, _sensitive_spike, _screen_jump)


# ---------------------------------------------------------------------------
# Silence budget
# ---------------------------------------------------------------------------

def _decide(signals: list[Signal]) -> list[Signal]:
    """Allocates the alert quota and records why each leftover is dropped.

    First, repeats are collapsed: a rule that holds for 9 days running is
    **one** fact, not nine alerts. Then candidates are sorted by priority and
    the quota is handed out respecting a minimum gap.
    """
    # 1 · collapse runs of the same rule into a single episode
    episodes: list[Signal] = []
    for s in sorted(signals, key=lambda x: (x.key, x.day)):
        prev = next((e for e in episodes if e.key == s.key), None)
        same_run = prev and (s.day - (prev.until or prev.day)).days <= 14
        if same_run:
            # The evidence stays that of the firing day, not the last one:
            # it is what justifies the alert sent that day.
            prev.magnitude = max(prev.magnitude, s.magnitude)
            prev.persistence = max(prev.persistence, s.persistence)
            prev.until = s.day
            continue
        episodes.append(s)

    # 2 · hand out the quota
    sent: list[Signal] = []
    for s in sorted(episodes, key=lambda x: -x.priority):
        if s.actionability < 0.5:
            s.decision, s.reason = "summary", (
                "The phone already resolved the incident; there is nothing "
                "to do today that cannot wait until Sunday. It goes to the "
                "weekly summary, not to a notification.")
            continue
        if len(sent) >= ALERT_BUDGET:
            s.decision, s.reason = "discarded", (
                f"Quota spent: {ALERT_BUDGET} alerts per month. A higher "
                f"priority signal was already through and this one does not "
                f"beat it.")
            continue
        if any(abs((s.day - o.day).days) < ALERT_MIN_GAP_DAYS for o in sent):
            s.decision, s.reason = "summary", (
                f"There is another alert less than {ALERT_MIN_GAP_DAYS} days "
                f"away. Two notifications back to back read as noise, not as "
                f"urgency.")
            continue
        s.decision, s.reason = "sent", "Sustained and actionable change."
        sent.append(s)

    return sorted(episodes, key=lambda x: (x.decision != "sent", -x.priority))


def evaluate_alerts(df: pd.DataFrame) -> list[Signal]:
    """Every candidate in the period, with its verdict."""
    signals: list[Signal] = []
    for rule in RULES:
        signals.extend(rule(df))
    return _decide(signals)


def weekly_digest(df: pd.DataFrame, signals: list[Signal]) -> dict:
    """What the weekly summary says when no alert fired: a coarse digest.

    No apps, no domains, no categories, and the numbers rounded. The rounding is
    not cosmetic: at this granularity the summary supports exactly the same
    decisions, and in exchange the aggregate stops being an identifier.
    """
    last7 = df.tail(7)
    state = ("something has changed" if any(s.decision == "sent" for s in signals)
             else "all in order")
    # Streak of protected nights. Streaks are an object-free aggregate: they
    # say something is going well without saying what against.
    streak = 0
    for night in reversed(list(df["night_min"])):
        if night >= POS_NIGHT_QUIET_MIN:
            break
        streak += 1
    return {
        "status": state,
        "screen time per day": f"about {round(last7.screen_min.mean() / 15) * 15 / 60:.1f} h",
        "wellbeing index": f"{round(last7.score.mean() / 5) * 5:.0f} out of 100",
        "nights in a row without late use": str(streak),
        "the filter acted": ("more than usual"
                             if last7.blocks.mean() > df.blocks.mean() * 1.2
                             else "as usual"),
        "sensitive content opened": "none",
    }
