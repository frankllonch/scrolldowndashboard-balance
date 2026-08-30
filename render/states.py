"""The per-day and per-week states the two sliders move through.

Every string is resolved here, so the browser rebuilds these blocks without
knowing a word of the copy.
"""

from __future__ import annotations

import pandas as pd

from copytext import t

from . import theme
from .fmt import clock, date, hm, ordinal
from .profiles import HAS_GUARDIAN


def phone_card(time: str, brand: str, eyebrow: str, headline: str, body: str,
               rows: list | None = None, ctas: list | None = None) -> dict:
    return {"time": time, "brand": brand, "eyebrow": eyebrow,
            "headline": headline, "body": body, "rows": rows or [],
            "ctas": ctas or []}


def user_card(state: dict) -> dict | None:
    """What the person holding the phone would have seen that day."""
    positives = [x for x in state["positives"] if x.audience == "user"]
    if positives:
        x = positives[0]
        return phone_card(
            t("phone.time.summary"), t("phone.brand"),
            t("phone.eyebrow.summary"), x.headline, x.guardian_text,
            rows=[[k, v] for k, v in x.evidence.items()],
            ctas=[{"label": t("phone.cta.week"), "ghost": True}])
    nudge = state["nudge"]
    if nudge and nudge.fired:
        at = pd.Timestamp(nudge.at_ms, unit="ms")
        return phone_card(
            t("fmt.clock", h=at.hour, m=at.minute), t("phone.brand"),
            t("phone.eyebrow.nudge"),
            t("phone.nudge.headline", ordinal=ordinal(nudge.reopens)),
            t("phone.nudge.body"),
            ctas=[{"label": t("phone.cta.off_until_tomorrow"), "ghost": False},
                  {"label": t("phone.cta.five_more"), "ghost": True}])
    return None


def guardian_card(user: str, state: dict) -> dict | None:
    """What the guardian's phone would have shown. Headline and text only:
    no app, no domain, no category ever crosses this boundary."""
    if not HAS_GUARDIAN[user]:
        return None
    guardian_positives = [x for x in state["positives"]
                          if x.audience == "guardian"]
    signal = state["alert"] or (guardian_positives[0]
                                if guardian_positives else None)
    if signal is None:
        return None
    return phone_card(
        t("phone.time.guardian"), t("phone.brand.guardian", user=user),
        t("phone.eyebrow.alert") if signal.tone == "alert"
        else t("phone.eyebrow.digest"),
        signal.headline, signal.guardian_text,
        ctas=[{"label": t("phone.cta.weekly_summary"), "ghost": True}])


def device_rows(row, state: dict) -> list[list[str]]:
    """The figures the phone keeps for itself."""
    return [
        [t("device.row.screen"), f"{row.screen_min:.0f} {t('unit.min')}"],
        [t("device.row.pickups"), f"{row.pickups:.0f}"],
        [t("device.row.night"), f"{row.night_min:.0f} {t('unit.min')}"],
        [t("device.row.night_end"), clock(row.night_end_h)],
        [t("device.row.offline"),
         f"{row.longest_offline_h:.1f} {t('unit.hours')}"],
        [t("device.row.offline_start"),
         row.longest_offline_when or t("value.no_stretch")],
        [t("device.row.distract"), f"{row.distract_share*100:.0f} %"],
        [t("device.row.sensitive"), f"{row.blocks_sensitive:.0f}"],
        [t("device.row.blocks"), f"{row.blocks:.0f}"],
        [t("device.row.score"), t("device.score.value", score=row.score)],
        [t("device.row.nudges"), f"{state['nudges_so_far']}"],
        [t("device.row.reinforcements"), f"{state['positives_so_far']}"],
    ]


def day_labels(user: str) -> dict:
    """The handful of strings the day slider needs when it rebuilds the cards
    in the browser. The page carries no copy of its own."""
    return {
        "channel_user": t("engine.channel.user"),
        "channel_guardian": t("engine.channel.guardian"),
        "channel_device": t("engine.channel.device"),
        "empty": t("engine.empty"),
        "emitted_none": t("week.emitted.none"),
        "device_caption": t("device.caption") + (
            t("device.caption.guardian") if HAS_GUARDIAN[user] else ""),
    }


def day_states(user: str, bundle: dict) -> list[dict]:
    by_day = bundle["df"].set_index("day")
    return [{
        "iso": state["day"].isoformat(),
        "label": date(state["day"]),
        "title": t("engine.outputs.title", date=date(state["day"])),
        "user": user_card(state),
        "guardian": guardian_card(user, state),
        "device": device_rows(by_day.loc[state["day"]], state),
    } for state in bundle["replay"]]


# ---------------------------------------------------------------------------
# Week states · the five panels behind the week slider
# ---------------------------------------------------------------------------

#: (copy key, column, unit, decimals) for the against-the-period table.
WEEK_ROWS = [
    ("row.screen_per_day", "screen_min", "unit.min", 0),
    ("row.unlocks_per_day", "pickups", None, 0),
    ("row.night_per_night", "night_min", "unit.min", 0),
    ("row.longest_offline", "longest_offline_h", "unit.hours", 1),
    ("row.distinct_apps", "distinct_apps", None, 1),
    ("row.switches_per_hour", "switches_per_screen_hour", None, 0),
    ("row.distract_share", "distract_share", "unit.percent", 0),
    ("row.blocks_per_day", "blocks", None, 1),
    ("row.index", "score", None, 0),
]


def _delta(cur, prev, col: str, unit: str = "", dec: int = 0) -> str | None:
    """Change against the previous week, in the metric's own unit.

    A change that rounds to zero is not shown: "+0 min" with a green arrow says
    something improved when nothing moved.
    """
    if prev is None or pd.isna(prev[col]):
        return None
    v = cur[col] - prev[col]
    if abs(round(v, dec)) < 10 ** -dec / 2:
        return t("value.no_change")
    return f"{v:+.{dec}f} {unit}".strip()


def week_kpis(cur, prev) -> list[dict]:
    items = [
        (t("week.kpi.screen"), hm(cur["screen_min"]),
         _delta(cur, prev, "screen_min", t("unit.min"))),
        (t("week.kpi.pickups"), f"{cur['pickups']:.0f}",
         _delta(cur, prev, "pickups")),
        (t("week.kpi.night"), f"{cur['night_min']:.0f} {t('unit.min')}",
         _delta(cur, prev, "night_min", t("unit.min"))),
        (t("week.kpi.offline"),
         f"{cur['longest_offline_h']:.1f} {t('unit.hours')}",
         _delta(cur, prev, "longest_offline_h", t("unit.hours"), 1)),
        (t("week.kpi.best_offline"),
         f"{cur['best_offline_h']:.1f} {t('unit.hours')}",
         cur["best_offline_when"]),
        (t("week.kpi.blocks"), f"{cur['blocks']:.1f}",
         _delta(cur, prev, "blocks", dec=1)),
        (t("week.kpi.score"), f"{cur['score']:.0f}",
         _delta(cur, prev, "score")),
    ]
    return [{"label": a, "value": b, "delta": c} for a, b, c in items]


def week_table(w: pd.DataFrame, cur, prev, week: int) -> dict:
    rows = []
    for key, col, unit_key, dec in WEEK_ROWS:
        unit = t(unit_key) if unit_key else ""
        mult = 100 if unit_key == "unit.percent" else 1
        # Rounded BEFORE subtracting: otherwise the change does not match the
        # two columns beside it and looks like an arithmetic error.
        v = round(cur[col] * mult, dec)
        pv = (round(prev[col] * mult, dec)
              if prev is not None and not pd.isna(prev[col]) else None)
        med = round(w[col].median() * mult, dec)
        if pv is None:
            change = t("value.not_available")
        elif abs(v - pv) < 10 ** -dec / 2:
            change = t("value.no_change")
        else:
            change = f"{v - pv:+.{dec}f} {unit}".strip()
        rows.append([
            t(key), f"{v:.{dec}f} {unit}".strip(),
            f"{pv:.{dec}f} {unit}".strip() if pv is not None
            else t("value.not_available"),
            f"{med:.{dec}f} {unit}".strip(), change,
        ])
    return {"columns": [t("table.col.metric"),
                        t("table.col.week_selected", week=week),
                        t("table.col.previous_week"),
                        t("table.col.period_median"),
                        t("table.col.change")],
            "rows": rows}


def week_emissions(bundle: dict, days: set) -> dict:
    rows = [[date(e["day"]), e["destination"], e["type"], e["detail"]]
            for e in bundle["emissions"] if e["day"] in days]
    return {"columns": [t("table.col.date"), t("table.col.destination"),
                        t("table.col.type"), t("table.col.detail")],
            "rows": rows}


def week_states(user: str, bundle: dict) -> list[dict]:
    df, w = bundle["df"], bundle["weekly"]
    light = theme.SURFACES["light"]
    colour, dim = light["USER_COLOR"][user], light["DIM"]
    out = []
    for week in w.index:
        cur = w.loc[week]
        prev = w.loc[week - 1] if week - 1 in w.index else None
        days = set(df[df["week"] == week]["day"])
        held = [x for x in bundle["positives"]
                if x.decision == "summary" and x.day in days]
        out.append({
            "week": int(week),
            "partial": bool(cur["is_partial"]),
            "label": t("week.slider.option_short" if cur["is_partial"]
                       else "week.slider.option", week=week),
            "range": (t("week.range", start=date(cur["start"]),
                        end=date(cur["end"]), days=int(cur["days"]))
                      + (t("week.range.partial") if cur["is_partial"] else "")),
            "days_title": t("week.days.title", week=week),
            "kpis": week_kpis(cur, prev),
            "table": week_table(w, cur, prev, week),
            "emitted_title": t("week.emitted.title", week=week),
            "emissions": week_emissions(bundle, days),
            "held_title": t("week.recorded.title"),
            "held": [[x.headline, x.reason.split(".")[0]] for x in held],
            # what the browser re-points rather than re-downloads
            "evolution_colors": [colour if i == week else dim for i in w.index],
            "components_vline": t("label.week", week=week),
        })
    return out
