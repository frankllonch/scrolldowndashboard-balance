"""The numbers the headline acts read, and the finding they add up to."""

from __future__ import annotations

from balance.intelligence import ALERT_BUDGET

from .fmt import clock, hm
from .fmt import week_value as wk
from .profiles import HAS_GUARDIAN


def summary(user: str, bundle: dict) -> dict:
    d, w = bundle["df"], bundle["weekly"]
    first, last = w.index[0], w.index[-2] if len(w.index) > 1 else w.index[-1]
    end_first, end_last = wk(d, "night_end_h", first), wk(d, "night_end_h", last)
    wake_first, wake_last = (wk(d, "first_pickup_h", first),
                             wk(d, "first_pickup_h", last))
    night_first = max(wk(d, "night_min", first), .01)
    return {
        "user": user,
        "has_guardian": HAS_GUARDIAN[user],
        "days": len(d),
        "events": len(bundle["events"]),
        "intervals": bundle["n_intervals"],
        "screen_h": bundle["screen_h"],
        "attributed_pct": bundle["attributed_h"] / bundle["screen_h"] * 100,
        "score_mean": d.score.mean(),
        "score_min": d.score.min(),
        "score_max": d.score.max(),
        "score_first_week": wk(d, "score", first),
        "score_last_week": wk(d, "score", last),
        "screen_mean": d.screen_min.mean(),
        "screen_mean_hm": hm(d.screen_min.mean()),
        "screen_first_week": wk(d, "screen_min", first),
        "screen_last_week": wk(d, "screen_min", last),
        "pickups_mean": d.pickups.mean(),
        "pickups_first_week": wk(d, "pickups", first),
        "pickups_last_week": wk(d, "pickups", last),
        "apps_mean": d.distinct_apps.mean(),
        "blocks_total": d.blocks.sum(),
        "sensitive_total": d.blocks_sensitive.sum(),
        "night_mean": d.night_min.mean(),
        "night_first_week": wk(d, "night_min", first),
        "night_last_week": wk(d, "night_min", last),
        "night_multiple": wk(d, "night_min", last) / night_first,
        "night_pickups_first_week": wk(d, "night_pickups", first),
        "night_pickups_last_week": wk(d, "night_pickups", last),
        "last_use_mean": clock(d.last_use_h.mean()),
        "last_screen_first_week": clock(end_first),
        "last_screen_last_week": clock(end_last),
        "last_screen_shift_min": (end_last - end_first) * 60,
        "wake_first_week": clock(wake_first),
        "wake_last_week": clock(wake_last),
        "wake_shift_min": (wake_last - wake_first) * 60,
        "sleep_first_week": (24 + wake_first) - end_first,
        "sleep_last_week": (24 + wake_last) - end_last,
        "alerts_sent": sum(1 for x in bundle["alerts"] if x.decision == "sent"),
        "alerts_held": sum(1 for x in bundle["alerts"]
                           if x.decision == "summary"),
        "alert_budget": ALERT_BUDGET,
        "positives_sent": sum(1 for x in bundle["positives"]
                              if x.decision == "sent"),
        "nudge_nights": bundle["nudge_summary"]["nights with a nudge"],
        "nights": bundle["nudge_summary"]["nights"],
        "emissions_total": len(bundle["emissions"]),
    }


def finding(summaries: dict) -> dict:
    """The reveal in act 11 and the negative control in act 12."""
    b = summaries["B"]
    return {
        "night_multiple": b["night_multiple"],
        "screen_change_pct": (b["screen_last_week"] / b["screen_first_week"]
                              - 1) * 100,
        "pickups_change_pct": (b["pickups_last_week"] / b["pickups_first_week"]
                               - 1) * 100,
        "sleep_loss_min": (b["sleep_first_week"] - b["sleep_last_week"]) * 60,
        "score_drop": b["score_first_week"] - b["score_last_week"],
    }
