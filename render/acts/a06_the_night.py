"""Act 06 · the night band. The only act that changes the surface."""

from copytext import t

from .. import html
from ..fmt import maybe


def strip(summary: dict) -> str:
    night_first = summary["night_first_week"]
    night_last = summary["night_last_week"]
    return html.kpis([
        {"label": t("night.kpi.first_week"),
         "value": f"{night_first:.0f} {t('unit.min')}"},
        {"label": t("night.kpi.last_week"),
         "value": f"{night_last:.0f} {t('unit.min')}",
         "delta": t("delta.times", n=summary["night_multiple"])},
        {"label": t("night.kpi.last_screen_first"),
         "value": summary["last_screen_first_week"]},
        {"label": t("night.kpi.last_screen_last"),
         "value": summary["last_screen_last_week"],
         "delta": shift(summary["last_screen_shift_min"])},
        {"label": t("night.kpi.first_unlock"),
         "value": summary["wake_last_week"],
         "delta": t("delta.minutes", n=summary["wake_shift_min"])},
        {"label": t("night.kpi.sleep_window"),
         "value": maybe(summary["sleep_last_week"], ".1f", t("unit.hours")),
         "delta": shift(sleep_change(summary))},
    ])


def shift(minutes) -> str | None:
    return None if minutes is None else t("delta.minutes", n=minutes)


def sleep_change(summary: dict):
    first, last = summary["sleep_first_week"], summary["sleep_last_week"]
    return None if first is None or last is None else (last - first) * 60


def reading(ctx) -> str:
    summary = ctx.profile["summary"]
    if ctx.user == "A":
        return html.note(t("night.note.user_a",
                           last_use=summary["last_use_mean"]), "good")
    return html.note(t(
        "night.note.drift",
        end_first=summary["last_screen_first_week"],
        end_last=summary["last_screen_last_week"],
        end_shift=summary["last_screen_shift_min"],
        wake_first=summary["wake_first_week"],
        wake_last=summary["wake_last_week"],
        wake_shift=summary["wake_shift_min"],
        sleep_first=summary["sleep_first_week"],
        sleep_last=summary["sleep_last_week"],
        sleep_loss=abs(summary["sleep_last_week"]
                       - summary["sleep_first_week"]) * 60,
        pick_first=summary["night_pickups_first_week"],
        pick_last=summary["night_pickups_last_week"]), "serious")


def build(ctx) -> str:
    return (
        strip(ctx.profile["summary"])
        + html.chart("night_drift", "shared")
        + reading(ctx)
        + html.grid(html.chart("day_span.night"),
                    html.chart("compare.night_pickups", "shared"))
        + html.note(t("night.weight.body", night=ctx.df.night_min.mean(),
                      screen=ctx.df.screen_min.mean()))
    )
