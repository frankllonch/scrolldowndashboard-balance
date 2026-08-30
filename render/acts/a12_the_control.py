"""Act 12 · the negative control.

`screen_jump` is real, reads the same frames, and fires on nobody. That is
the point: the rule that looks obvious would have missed this month.
"""

from copytext import t

from .. import html
from ..fmt import date


def coverage(ctx) -> str:
    """Which rule fires on whom. One profile's answer only means something
    next to the other's, so both columns are always here."""
    users = ctx.payload["meta"]["profiles"]
    rows = []
    for key in ("night_drift", "sensitive_spike", "screen_jump"):
        hits = [next((x for x in ctx.bundles[u]["alerts"] if x.key == key), None)
                for u in users]
        rows.append([key, t(f"engine.coverage.{key}")] + [
            t("value.decision_on", decision=h.decision, date=date(h.day))
            if h else t("value.does_not_fire") for h in hits])
    return html.table(
        [t("table.col.rule"), t("table.col.compares")]
        + [t("table.col.user", user=u) for u in users], rows)


def build(ctx) -> str:
    finding = ctx.payload["finding"]
    return (
        html.lede(t("control.lede"))
        + html.grid(
            f'<div class="hero-card"><p class="hero-number huge">'
            f'{finding["screen_change_pct"]:+.0f} %</p>'
            f'<p class="hero-sub">{t("control.screen.label")}</p></div>',
            f'<div class="hero-card"><p class="hero-number huge">'
            f'{t("finding.hero.value", multiple=finding["night_multiple"])}</p>'
            f'<p class="hero-sub">{t("control.night.label")}</p></div>')
        + html.grid(html.chart("compare.screen_min", "shared"),
                    html.chart("compare.night_min", "shared"))
        + html.note(t("control.body", screen=finding["screen_change_pct"],
                      night=finding["night_multiple"]), "warn")
        + coverage(ctx)
    )
