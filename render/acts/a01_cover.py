"""Act 01 · the cover. Title, one line, the dataset in three numbers."""

from copytext import t

from .. import html


def build(ctx) -> str:
    meta = ctx.payload["meta"]
    return (
        html.lede(t("cover.standfirst"))
        + html.grid(
            html.stat(f"{len(meta['profiles'])}", t("cover.stat.profiles")),
            html.stat(f"{meta['events']:,}", t("cover.stat.events")),
            html.stat(f"{meta['days']}", t("cover.stat.days")),
            cols=3)
        + f'<p class="scroll-cue">{t("cover.scroll")}</p>'
    )
