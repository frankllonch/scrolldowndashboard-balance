"""Act 03 · the fork. A real choice, full screen, not a dropdown."""

from copytext import t

from .. import html


def card(summary: dict) -> str:
    user = summary["user"]
    return (
        f'<button class="fork-card" data-choose="{user}" type="button">'
        + html.eyebrow(t("profile.card.eyebrow", user=user))
        + f'<p class="fork-sketch">{t(f"fork.sketch.{user}")}</p>'
        + '<div class="fork-stats">'
        + html.stat(summary["screen_mean_hm"], t("fork.stat.screen"))
        + html.stat(f"{summary['score_mean']:.0f}", t("fork.stat.index"))
        + html.stat(f"{summary['nudge_nights']}", t("fork.stat.nights"))
        + "</div>"
        + f'<span class="fork-cta">{t("fork.cta")}</span>'
        + "</button>"
    )


def build(ctx) -> str:
    profiles = ctx.payload["profiles"]
    return (
        html.lede(t("fork.lede"))
        + '<div class="fork">'
        + "".join(card(profiles[u]["summary"])
                  for u in ctx.payload["meta"]["profiles"])
        + "</div>"
    )
