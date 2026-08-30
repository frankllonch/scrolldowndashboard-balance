"""Act 10 · the other one. A reader who picked one profile is not stuck here."""

from copytext import t

from .. import html


def build(ctx) -> str:
    return (
        html.lede(t("other.body"))
        + '<div class="switch-prompt" data-slot="other.cta">'
        + "".join(f'<button class="fork-cta-button" type="button" '
                  f'data-choose="{u}" data-other="{u}">'
                  f'{t("other.cta", user=u)}</button>'
                  for u in ctx.payload["meta"]["profiles"])
        + "</div>"
        + f'<p class="caption" data-slot="other.seen" hidden>'
        f'{t("other.seen")}</p>'
    )
