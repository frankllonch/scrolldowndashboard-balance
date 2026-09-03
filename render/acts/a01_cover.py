"""Act 01 · the cover. What Balance is, what this is, and the short version."""

from copytext import t

from .. import html


def summary(ctx) -> str:
    """The whole argument in three lines, before the reader scrolls anywhere.

    A reader who stops here should still leave knowing what the month said.
    """
    a = ctx.payload["profiles"]["A"]["summary"]
    b = ctx.payload["profiles"]["B"]["summary"]
    f = ctx.payload["finding"]
    points = [
        (t("summary.1.label"),
         t("summary.1.body", a_score=a["score_mean"],
           b_first=b["score_first_week"], b_last=b["score_last_week"],
           drop=f["score_drop"])),
        (t("summary.2.label"),
         t("summary.2.body", screen=f["screen_change_pct"],
           night=f["night_multiple"], bed_first=b["last_screen_first_week"],
           bed_last=b["last_screen_last_week"], sleep=f["sleep_loss_min"])),
        (t("summary.3.label"),
         t("summary.3.body", blocks=b["blocks_total"],
           sensitive=b["sensitive_total"], outage=b["outage_day"],
           hours=b["outage_hours"])),
    ]
    return (f'<h3 class="sub">{t("summary.title")}</h3>'
            + html.grid(*(f'<div class="channel">{html.eyebrow(label)}'
                          f'<p class="note">{body}</p></div>'
                          for label, body in points), cols=3))


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
        + summary(ctx)
        + f'<p class="scroll-cue">{t("cover.scroll")}</p>'
    )
