"""Act 01 · the cover. What Balance is, what this is, and why to read on."""

from copytext import t

from .. import html


def build(ctx) -> str:
    meta = ctx.payload["meta"]
    return (
        html.lede(t("cover.standfirst"))
        + html.note(t("cover.purpose"))
        + html.grid(
            html.stat(f"{len(meta['profiles'])}", t("cover.stat.profiles")),
            html.stat(f"{meta['events']:,}", t("cover.stat.events")),
            html.stat(f"{meta['days']}", t("cover.stat.days")),
            cols=3)
        + html.lede(t("cover.intro",
                      drop=ctx.payload["finding"]["score_drop"]))
    )
