"""Act 10 · the finding. This is what act 02 refused to explain."""

from copytext import t

from .. import html


def build(ctx) -> str:
    finding = ctx.payload["finding"]
    b = ctx.payload["profiles"]["B"]["summary"]
    return (
        html.lede(t("finding.lede"))
        + html.grid(
            f'<div class="hero-card"><p class="hero-number huge">'
            f'{t("finding.hero.value", multiple=finding["night_multiple"])}</p>'
            f'<p class="hero-sub">{t("finding.hero.label")}</p></div>',
            f'<div class="hero-card"><p class="hero-number huge">'
            f'{t("finding.sleep.value", minutes=finding["sleep_loss_min"])}</p>'
            f'<p class="hero-sub">{t("finding.sleep.label")}</p></div>')
        + html.chart("night_drift", "shared")
        + html.note(t("finding.body", shift=b["last_screen_shift_min"],
                      first=b["sleep_first_week"], last=b["sleep_last_week"],
                      pick_first=b["night_pickups_first_week"],
                      pick_last=b["night_pickups_last_week"]), "serious")
    )
