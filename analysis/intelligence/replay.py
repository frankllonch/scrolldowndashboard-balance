"""The state at the close of each day, and what it emitted."""

from __future__ import annotations

from datetime import date

import pandas as pd

from .alerts import evaluate_alerts
from .signals import NightNudge, Signal


def month_replay(df: pd.DataFrame, nudges: list[NightNudge],
                 positives: list[Signal] | None = None) -> list[dict]:
    """The system state at the close of each day, using the information it had
    that day and not the whole month's.

    **Alerts** are re-evaluated over the history available up to each date:
    their quota allocation sorts by priority, so it depends on the set and has
    to be recomputed to know what would have been sent that day.

    **Reinforcements** are not: each rule only looks backwards and the quota is
    a forward pass with memory, so `evaluate_positives` over the full frame
    already gives the causal result. Recomputing them per prefix would reset
    the quota every day and multiply the sends.
    """
    positives = positives or []
    pos_by_day: dict[date, list[Signal]] = {}
    for s in positives:
        if s.decision == "sent":
            pos_by_day.setdefault(s.day, []).append(s)
    by_day = {n.day: n for n in nudges}
    out: list[dict] = []

    for i, day in enumerate(df["day"]):
        upto = df.iloc[: i + 1]
        sigs = evaluate_alerts(upto)
        pos_today = pos_by_day.get(day, [])
        sent_today = next((s for s in sigs
                           if s.decision == "sent" and s.day == day), None)
        digest_today = next((s for s in sigs
                             if s.decision == "summary" and s.day == day), None)
        nudge = by_day.get(day)

        out.append({
            "day": day,
            "alert": sent_today,
            "digest_entry": digest_today,
            "nudge": nudge,
            "positives": pos_today,
            "positives_so_far": sum(
                len(v) for k, v in pos_by_day.items() if k <= day),
            # running totals at that date, as the phone would show them
            "alerts_so_far": sum(1 for s in sigs if s.decision == "sent"),
            "digest_so_far": sum(1 for s in sigs if s.decision == "summary"),
            "nudges_so_far": sum(1 for n in nudges if n.fired and n.day <= day),
            "status": ("something has changed"
                       if any(s.decision == "sent" for s in sigs)
                       else "all in order"),
        })
    return out


def emissions(replay: list[dict]) -> list[dict]:
    """A flat list of everything the phone emitted, in time order.

    Two possible destinations and only two: the user's screen, and the weekly
    summary a held signal drops into. Nothing leaves the device.
    """
    out: list[dict] = []
    for r in replay:
        if r["nudge"] and r["nudge"].fired:
            out.append({
                "day": r["day"], "destination": "User · screen",
                "type": "Night nudge",
                "detail": (f"reopening no. {r['nudge'].reopens} of the night · "
                           f"{r['nudge'].minutes_after:.0f} min of screen after"),
            })
        if r["alert"]:
            out.append({
                "day": r["day"], "destination": "User · alert",
                "type": r["alert"].key, "detail": r["alert"].headline,
            })
        if r["digest_entry"]:
            out.append({
                "day": r["day"], "destination": "Weekly summary",
                "type": r["digest_entry"].key,
                "detail": r["digest_entry"].headline,
            })
        for s in r.get("positives", []):
            out.append({
                "day": r["day"],
                "destination": "User · reinforcement",
                "type": s.key, "detail": s.headline,
            })
    return sorted(out, key=lambda x: x["day"])
