"""Act 02 · both profiles at once.

The cold open. It plants what is wrong with B and does not say what it is;
act 11 answers it.
"""

from copytext import t

from .. import html


def hero(summary: dict) -> str:
    user = summary["user"]
    return (
        f'<div class="hero-card" data-user="{user}">'
        + html.eyebrow(t("overview.index.eyebrow", user=user))
        + f'<p class="hero-number">{summary["score_mean"]:.0f}'
        f'<span class="hero-unit">{t("overview.index.scale")}</span></p>'
        + f'<p class="hero-sub">'
        f'{t("overview.index.weeks", first=summary["score_first_week"], last=summary["score_last_week"])}'
        "</p></div>"
    )


def strip(summary: dict) -> str:
    user = summary["user"]
    return html.kpis([
        {"label": t("kpi.screen_day", user=user),
         "value": summary["screen_mean_hm"]},
        {"label": t("kpi.unlocks_day", user=user),
         "value": f"{summary['pickups_mean']:.0f}"},
        {"label": t("kpi.night_day", user=user),
         "value": f"{summary['night_mean']:.0f} {t('unit.min')}"},
        {"label": t("kpi.blocks_month", user=user),
         "value": f"{summary['blocks_total']:,.0f}"},
        {"label": t("kpi.sensitive", user=user),
         "value": f"{summary['sensitive_total']:.0f}"},
    ])


def build(ctx) -> str:
    summaries = {u: ctx.payload["profiles"][u]["summary"]
                 for u in ctx.payload["meta"]["profiles"]}
    b = summaries["B"]
    return (
        html.lede(t("overview.lede"))
        + html.grid(*(hero(summaries[u]) for u in summaries))
        + html.chart("score_line", "shared")
        + "".join(strip(summaries[u]) for u in summaries)
        + html.note(t("overview.hook", first=b["score_first_week"],
                      last=b["score_last_week"],
                      screen=ctx.payload["finding"]["screen_change_pct"]),
                    "warn")
    )
