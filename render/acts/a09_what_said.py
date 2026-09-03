"""Act 09 · the alert and nudge engine.

Two destinations and only two: the user's own screen, and the weekly summary
a held signal drops into. The day slider walks all thirty days.
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
            f'<output for="day-slider" data-slot="day.label">'
            f'{current["label"]}</output>'
            f'<input type="range" id="day-slider" list="day-ticks" min="0" '
            f'max="{len(days) - 1}" step="any" value="{index}">'
            f'<datalist id="day-ticks">{ticks}</datalist></div>')


def cards(ctx, day: dict) -> str:
    return html.grid(
        html.channel(t("engine.channel.user"), phones_or_gap(day["user"])),
        html.channel(t("engine.channel.device"),
                     html.pairs(day["device"])
                     + f'<p class="caption">{t("device.caption")}</p>'),
        cols=2)


def phones_or_gap(cards: list[dict]) -> str:
    return ("".join(html.phone(c) for c in cards) if cards
            else html.empty(t("engine.empty")))


def emissions(ctx) -> str:
    rows = [[date(e["day"]), e["destination"], e["type"], e["detail"]]
            for e in ctx.bundle["emissions"]]
    if not rows:
        return f'<p class="caption">{t("engine.emissions.none")}</p>'
    return html.table([t("table.col.date"), t("table.col.destination"),
                       t("table.col.type"), t("table.col.detail")], rows)


def notifications(ctx) -> str:
    s = ctx.profile["summary"]
    return html.kpis([
        {"label": t("engine.kpi.alerts"),
         "value": f"{s['alerts_sent']}",
         "delta": t("engine.kpi.alerts.delta", budget=s["alert_budget"])},
        {"label": t("engine.kpi.summary"),
         "value": f"{s['alerts_held']}",
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
