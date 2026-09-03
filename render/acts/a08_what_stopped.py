"""Act 08 · what the filter stopped, and how little of it is named."""

import pandas as pd

from balance.events import SENSITIVE
from copytext import t

from .. import html


def week_table(ctx) -> str:
    bf, df = ctx.bundle["blocks"], ctx.df
    # the month does not fall into 7-day weeks: the last one is a 2-day tail
    # and that has to be said, or blocks look like they collapse at the end.
    per_week = df.groupby("week").size()
    pivot = pd.crosstab(bf.category, bf.week)
    columns = [t("table.col.metric")] + [
        t("table.col.week_days", week=w, days=per_week[w]) for w in pivot.columns]
    rows = [[t(f"category.{name}")] + [f"{v}" for v in row]
            for name, row in pivot.iterrows()]
    return html.table(columns, rows)


def strip(ctx) -> str:
    bf, df = ctx.bundle["blocks"], ctx.df
    sensitive = bf[bf.category.isin(SENSITIVE)]
    return html.kpis([
        {"label": t("blocks.kpi.attempts"), "value": f"{len(bf):,}",
         "delta": t("blocks.kpi.attempts.delta", per_day=len(bf) / len(df))},
        {"label": t("blocks.kpi.apps"), "value": f"{df.blocks_app.sum():,}"},
        {"label": t("blocks.kpi.sites"), "value": f"{df.blocks_url.sum():,}"},
        {"label": t("blocks.kpi.nudity"), "value": f"{df.blocks_nudity.sum():,}",
         "delta": t("blocks.kpi.nudity.delta")},
        {"label": t("blocks.kpi.sensitive"), "value": f"{len(sensitive):,}",
         "delta": t("blocks.kpi.sensitive.delta",
                    pct=len(sensitive) / max(len(bf), 1) * 100)},
        {"label": t("blocks.kpi.opened"), "value": "0",
         "delta": t("blocks.kpi.opened.delta")},
    ])


def reading(ctx) -> str:
    bf, df = ctx.bundle["blocks"], ctx.df
    sensitive = bf[bf.category.isin(SENSITIVE)]
    week = lambda n: df[df["week"] == n]["blocks"].sum()  # noqa: E731
    if ctx.user == "A":
        return html.note(t("blocks.note.a", total=len(bf), first=week(1),
                           last=week(4)), "good")
    mid = len(sensitive[sensitive.week.isin([2, 3])])
    return html.note(t(
        "blocks.note.b", ordinary=len(bf) - len(sensitive),
        first=week(1), last=week(4),
        adult=len(bf[bf.category == "ADULT"]),
        gambling=len(bf[bf.category == "GAMBLING"]),
        nudity=len(bf[bf.block_type == "NUDITY"]),
        mid=mid, sensitive=len(sensitive), mid_pct=mid / len(sensitive) * 100,
        week_four=len(sensitive[sensitive.week == 4])), "warn")


def build(ctx) -> str:
    bf = ctx.bundle["blocks"]
    if bf.empty:
        return html.note(t("blocks.none"))
    return (
        html.tags(t("tag.device_only"), t("tag.aggregate_only"))
        + strip(ctx)
        + html.grid(html.chart("blocks_daily"), html.chart("blocks_by_hour"))
        + week_table(ctx)
        + reading(ctx)
        + html.note(t("blocks.scope.body",
                      sensitive=len(bf[bf.category.isin(SENSITIVE)])))
    )
