"""Act 05 · the daily rhythm. Passive: one month of days, one screen."""

from copytext import t

from .. import html
from ..fmt import hm


def strip(df) -> str:
    return html.kpis([
        {"label": t("day.kpi.screen"),
         "value": hm(df.screen_min.mean()),
         "delta": t("day.kpi.screen.delta", sd=df.screen_min.std())},
        {"label": t("day.kpi.sessions"), "value": f"{df.sessions.mean():.0f}",
         "delta": t("day.kpi.sessions.delta",
                    median=df.median_session_s.mean() / 60)},
        {"label": t("day.kpi.pickups"), "value": f"{df.pickups.mean():.0f}",
         "delta": t("day.kpi.pickups.delta", glances=df.glances.mean())},
        {"label": t("day.kpi.first_pickup"),
         "value": df.first_pickup_clock.mode().iloc[0],
         "delta": t("day.kpi.first_pickup.delta",
                    median=df.first_pickup_h.median())},
        {"label": t("day.kpi.offline"),
         "value": f"{df.longest_offline_s.mean()/3600:.1f} {t('unit.hours')}",
         "delta": t("day.kpi.offline.delta", best=df.longest_offline_h.max(),
                    when=df.loc[df.longest_offline_h.idxmax(),
                                "longest_offline_when"])},
        {"label": t("day.kpi.switches"),
         "value": f"{df.switches_per_screen_hour.mean():.0f}",
         "delta": t("day.kpi.switches.delta", apps=df.distinct_apps.mean())},
    ])


def reading(ctx) -> str:
    df, user = ctx.df, ctx.user
    weekend = df.groupby("is_weekend")[["screen_min", "pickups"]].mean()
    diff = weekend.loc[True, "screen_min"] - weekend.loc[False, "screen_min"]
    shared = dict(weekend=weekend.loc[True, "screen_min"],
                  weekday=weekend.loc[False, "screen_min"],
                  session=df.median_session_s.mean() / 60,
                  switches=df.switches_per_screen_hour.mean())
    if user == "A":
        return html.note(t(
            "day.note.a", last_use=df.last_use_clock.mode().iloc[0],
            diff=abs(diff),
            pickup_diff=weekend.loc[False, "pickups"] - weekend.loc[True, "pickups"],
            apps=df.distinct_apps.mean(), **shared), "good")
    reference = ctx.bundles["A"]["df"].switches_per_screen_hour.mean()
    return html.note(t(
        "day.note.b", diff=diff, night=df.night_min.mean(),
        ratio=df.switches_per_screen_hour.mean() / reference, **shared), "warn")


def build(ctx) -> str:
    return (
        strip(ctx.df)
        + html.grid(html.chart("daily_bars.screen_min"),
                    html.chart("daily_bars.pickups"))
        + f'<p class="caption">{t("day.baseline.caption")}</p>'
        + html.grid(html.chart("hour_heat"), html.chart("day_span"))
        + reading(ctx)
    )
