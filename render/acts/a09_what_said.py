"""Act 09 · the alert and nudge engine.

Three destinations and only three: the user's screen, a guardian
notification, the weekly summary. The day slider walks all thirty.
"""

from collections import Counter

from balance.intelligence import NUDGE_AFTER_MIN
from copytext import t

from .. import html
from ..fmt import date


def slider(days: list[dict], current: dict) -> str:
    ticks = "".join(f'<option value="{i}"></option>'
                    for i in range(0, len(days), 7))
    index = next(i for i, d in enumerate(days) if d["iso"] == current["iso"])
    return ('<div class="slider" data-slider="day">'
            f'<label for="day-slider">{t("engine.slider.label")}</label>'
            f'<input type="range" id="day-slider" list="day-ticks" min="0" '
            f'max="{len(days) - 1}" step="1" value="{index}">'
            f'<datalist id="day-ticks">{ticks}</datalist>'
            f'<output for="day-slider" data-slot="day.label">'
            f'{current["label"]}</output></div>')


def cards(ctx, day: dict) -> str:
    guarded = ctx.profile["summary"]["has_guardian"]
    blocks = [html.channel(t("engine.channel.user"), phone_or_gap(day["user"]))]
    if guarded:
        blocks.append(html.channel(t("engine.channel.guardian"),
                                   phone_or_gap(day["guardian"])))
    caption = t("device.caption") + (t("device.caption.guardian")
                                     if guarded else "")
    blocks.append(html.channel(
        t("engine.channel.device"),
        html.pairs(day["device"]) + f'<p class="caption">{caption}</p>'))
    return html.grid(*blocks, cols=len(blocks))


def phone_or_gap(card: dict | None) -> str:
    return html.phone(card) if card else html.empty(t("engine.empty"))


def emissions(ctx) -> str:
    rows = [[date(e["day"]), e["destination"], e["type"], e["detail"]]
            for e in ctx.bundle["emissions"]]
    if not rows:
        return f'<p class="caption">{t("engine.emissions.none")}</p>'
    return html.table([t("table.col.date"), t("table.col.destination"),
                       t("table.col.type"), t("table.col.detail")], rows)


def notifications(ctx) -> str:
    s = ctx.profile["summary"]
    guarded = s["has_guardian"]
    unavailable = t("value.not_available")
    return html.kpis([
        {"label": t("engine.kpi.guardian"),
         "value": f"{s['alerts_sent']}" if guarded else unavailable,
         "delta": (t("engine.kpi.guardian.delta", budget=s["alert_budget"])
                   if guarded else t("value.no_guardian"))},
        {"label": t("engine.kpi.summary"),
         "value": f"{s['alerts_held']}" if guarded else unavailable,
         "delta": t("engine.kpi.summary.delta")},
        {"label": t("engine.kpi.reinforcements"),
         "value": f"{s['positives_sent']}",
         "delta": t("engine.kpi.reinforcements.delta")},
        {"label": t("engine.kpi.nudge_nights"),
         "value": t("engine.kpi.nudge_nights.value",
                    nudged=s["nudge_nights"], nights=s["nights"]),
         "delta": t("engine.kpi.nudge_nights.delta",
                    pct=s["nudge_nights"] / s["nights"] * 100)},
    ])


def nudge(ctx) -> str:
    ns = ctx.bundle["nudge_summary"]
    quiet = Counter(x.quiet_reason for x in ctx.bundle["nudges"] if x.quiet_reason)
    rows = [
        [t("engine.nudge.row.nights"), f"{ns['nights']}"],
        [t("engine.nudge.row.nudged"),
         t("engine.nudge.row.nudged_value", nudged=ns["nights with a nudge"],
           pct=ns["appearance rate"] * 100)],
        [t("engine.nudge.row.night_minutes"), f"{ns['total night minutes']:.0f}"],
        [t("engine.nudge.row.after"),
         t("engine.nudge.row.after_value",
           minutes=ns["minutes at stake after the nudge"],
           pct=ns["share of night total"] * 100)],
        [t("engine.nudge.row.per_night"),
         t("engine.nudge.row.per_night_value",
           minutes=ns["minutes at stake per nudged night"])],
    ]
    from_clock = t("fmt.clock", h=23 + NUDGE_AFTER_MIN // 60,
                   m=NUDGE_AFTER_MIN % 60)
    return (f'<p class="caption">{t("engine.nudge.caption", from_clock=from_clock)}</p>'
            + html.grid(html.pairs(rows),
                        html.pairs([[r, str(n)] for r, n in quiet.most_common()])))


def build(ctx) -> str:
    days = ctx.profile["days"]
    current = next(d for d in days if d["iso"] == ctx.profile["default_day"])
    return (f'<p class="caption">{t("engine.caption")}</p>'
            + slider(days, current)
            + html.chart("tracked_series", size="tall")
            + html.slot("day.title", f'<h3 class="sub">{current["title"]}</h3>')
            + html.slot("day.cards", cards(ctx, current))
            + f'<h3 class="sub">{t("engine.emissions.title")}</h3>'
            + emissions(ctx)
            + notifications(ctx)
            + html.details(t("engine.nudge.title"), nudge(ctx)))
