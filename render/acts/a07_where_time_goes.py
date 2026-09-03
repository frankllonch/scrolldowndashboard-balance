"""Act 07 · apps, domains and categories. Device-side only."""

from copytext import t

from .. import html


def build(ctx) -> str:
    apps, sites = ctx.bundle["apps"], ctx.bundle["sites"]
    df = ctx.df
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
        + html.chart("category_area")
        + reading(ctx, apps, sites, top3)
        + html.note(t("time.distract.explain"))
    )


def top3_names(apps) -> str:
    """The three apps the reader is about to see at the top of the chart."""
    names = list(apps.label.head(3))
    return ", ".join(names[:-1]) + " and " + names[-1]


def reading(ctx, apps, sites, top3: float) -> str:
    df = ctx.df
    week = lambda col, n: df[df["week"] == n][col].mean()  # noqa: E731
    if ctx.user == "A":
        chrome = apps[apps.key == "com.android.chrome"]
        news = (sites[sites.category == "NEWS"].minutes.sum()
                / sites.minutes.sum() * 100)
        return (html.note(t("time.note.a", apps=len(apps), top3=top3, news=news,
                            top3_names=top3_names(apps),
                            distract=df.distract_share.mean() * 100,
                            first=week("distract_share", 1) * 100,
                            last=week("distract_share", 4) * 100), "good")
                + '<p class="caption">'
                + t("time.caption.chrome", opens=chrome.opens.iloc[0],
                    minutes=chrome.minutes.iloc[0]) + "</p>")
    reference = ctx.bundles["A"]
    summary = ctx.profile["summary"]
    names, through, attempts = most_blocked(ctx, apps)
    return (html.note(t("time.note.b", apps=len(apps),
                        apps_a=len(reference["apps"]), top3=top3,
                        top3_names=top3_names(apps),
                        messaging=apps[apps.category == "MESSAGING"].minutes.sum(),
                        messaging_apps=len(apps[apps.category == "MESSAGING"]),
                        distract=df.distract_share.mean() * 100,
                        distract_a=reference["df"].distract_share.mean() * 100),
                      "warn")
            + '<p class="caption">'
            + t("time.caption.blocked_absent", names=names, through=through,
                attempts=attempts)
            + "</p>"
            + html.note(t("time.leak.explain",
                          days=summary["leaked_days"],
                          median=summary["leaked_median"],
                          outage=summary["outage_day"],
                          hours=summary["outage_hours"])))


def most_blocked(ctx, apps) -> tuple[str, str, str]:
    """The two apps the filter stopped most, and how little got through.

    An app the filter stopped every time never enters the usage frame, so the
    package name is the fallback for its label.
    """
    blocked = ctx.bundle["blocks"]
    top = (blocked[blocked["block_type"] == "APP"]["target"]
           .value_counts().head(2))
    labels = dict(zip(apps["key"], apps["label"]))
    opens = dict(zip(apps["key"], apps["opens"]))
    joined = lambda values: " and ".join(str(v) for v in values)  # noqa: E731
    return (joined(labels.get(k, k) for k in top.index),
            joined(f"{opens.get(k, 0):.0f}" for k in top.index),
            joined(top.values))
