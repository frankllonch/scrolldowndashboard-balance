"""Act 07 · apps, domains and categories. Device-side only."""

from copytext import t

from .. import html


def build(ctx) -> str:
    apps, sites = ctx.bundle["apps"], ctx.bundle["sites"]
    df, user = ctx.df, ctx.user
    top3 = apps.minutes.head(3).sum() / apps.minutes.sum() * 100
    summary = ctx.profile["summary"]
    return (
        html.tags(t("tag.device_only"), t("tag.never_sent"))
        + html.kpis([
            {"label": t("time.kpi.attributed"),
             "value": f"{summary['screen_h'] * summary['attributed_pct'] / 100:.0f}"
                      f" {t('unit.hours')}",
             "delta": t("time.kpi.attributed.delta",
                        pct=summary["attributed_pct"])},
            {"label": t("time.kpi.apps"), "value": f"{len(apps)}",
             "delta": t("time.kpi.whole_month")},
            {"label": t("time.kpi.domains"), "value": f"{len(sites)}",
             "delta": t("time.kpi.whole_month")},
            {"label": t("time.kpi.top3"), "value": f"{top3:.0f} %",
             "delta": t("time.kpi.top3.delta")},
            {"label": t("time.kpi.distract"),
             "value": f"{df.distract_share.mean()*100:.0f} %",
             "delta": t("time.kpi.distract.delta")},
        ])
        + html.grid(html.chart("top_bars.apps"), html.chart("top_bars.sites"))
        + f'<p class="caption">{t("time.colour.caption")}</p>'
        + html.chart("category_area")
        + reading(ctx, apps, sites, top3)
    )


def reading(ctx, apps, sites, top3: float) -> str:
    df = ctx.df
    week = lambda col, n: df[df["week"] == n][col].mean()  # noqa: E731
    if ctx.user == "A":
        chrome = apps[apps.key == "com.android.chrome"]
        news = (sites[sites.category == "NEWS"].minutes.sum()
                / sites.minutes.sum() * 100)
        return (html.note(t("time.note.a", apps=len(apps), top3=top3, news=news,
                            distract=df.distract_share.mean() * 100,
                            first=week("distract_share", 1) * 100,
                            last=week("distract_share", 4) * 100), "good")
                + f'<p class="caption">'
                + t("time.caption.chrome", opens=chrome.opens.iloc[0],
                    minutes=chrome.minutes.iloc[0]) + "</p>")
    reference = ctx.bundles["A"]
    return (html.note(t("time.note.b", apps=len(apps),
                        apps_a=len(reference["apps"]), top3=top3,
                        messaging=apps[apps.category == "MESSAGING"].minutes.sum(),
                        distract=df.distract_share.mean() * 100,
                        distract_a=reference["df"].distract_share.mean() * 100),
                      "warn")
            + f'<p class="caption">{t("time.caption.blocked_absent")}</p>')
