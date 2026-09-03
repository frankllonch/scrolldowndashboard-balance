"""Act 02 · both profiles at once.

The cold open. It plants what is wrong with B and does not say what it is;
act 11 answers it.
"""

from balance.score import COMPONENTS
from copytext import t

from .. import html


def hero(summary: dict) -> str:
    """The index, and one line on who this month belonged to."""
    user = summary["user"]
    return (
        f'<div class="hero-card" data-user="{user}">'
        + html.eyebrow(t("overview.index.eyebrow", user=user))
        + f'<p class="hero-number">{summary["score_mean"]:.0f}'
        f'<span class="hero-unit">{t("overview.index.scale")}</span></p>'
        + f'<p class="hero-sub">'
        f'{t("overview.index.weeks", first=summary["score_first_week"], last=summary["score_last_week"])}'
        "</p>"
        + f'<p class="note">{t(f"overview.person.{user}", blocks=summary["blocks_total"])}</p>'
        "</div>"
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
    return (
        html.lede(t("overview.lede"))
        + html.grid(*(hero(summaries[u]) for u in summaries))
        + html.chart("score_line", "shared")
        + "".join(strip(summaries[u]) for u in summaries)
        + html.note(t("overview.hook",
                      drop=ctx.payload["finding"]["score_drop"]), "warn")
        + score_explainer(ctx)
    )


def score_explainer(ctx) -> str:
    """What the number on the hero cards actually is, said where the reader
    first meets it rather than in the appendix."""
    frag = next(c for c in COMPONENTS if c[1] == "Fragmentation")
    return (f'<h3 class="sub">{t("score.explain.title")}</h3>'
            + html.lede(t("score.explain.body"))
            + html.table([t("table.col.component"),
                          t("table.col.scores_100"),
                          t("table.col.scores_0"),
                          t("table.col.scoring")],
                         [[label, good, bad, f"{weight:.0%}"]
                          for _col, label, good, bad, weight in COMPONENTS])
            + html.note(t("score.explain.note",
                          frag_good=frag[2], frag_bad=frag[3]))
            + html.note(t("score.explain.blocks")))
