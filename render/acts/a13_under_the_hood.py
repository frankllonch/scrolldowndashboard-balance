"""Act 13 · under the hood. Everything closed by default; nothing hidden."""

from collections import Counter

from balance.score import COMPONENTS
from copytext import t

from .. import html

#: (name, type, the events that carry it)
FIELDS = [
    ("id", "int", "all"),
    ("event_type", "str", "all"),
    ("timestamp_millis", "int", "all"),
    ("package_name", "str|null", "APP_FOREGROUND, BLOCK"),
    ("url_domain", "str|null", "URL_VISIT, BLOCK"),
    ("category", "str|null", "APP_FOREGROUND, URL_VISIT, BLOCK"),
    ("block_type", "str|null", "BLOCK"),
    ("is_keyguard_locked", "bool|null", "SCREEN_ON, USER_PRESENT"),
]

ANOMALIES = ("overlap", "truncated", "midnight_start", "crossing", "duplicates")

#: The four a reader needs to read the charts. The rest are in
#: ARCHITECTURE.md rather than repeated here.
DERIVATIONS = ("screen_time", "pickup", "glance", "night", "baseline")


def stream(ctx) -> str:
    users = ctx.payload["meta"]["profiles"]
    counts = {u: Counter(e["event_type"] for e in ctx.bundles[u]["events"])
              for u in users}
    kinds = sorted({k for c in counts.values() for k in c})
    rows = [[kind] + [f"{counts[u][kind]:,}" for u in users] + [t(f"event.{kind}")]
            for kind in kinds]
    return html.table(
        [t("table.col.field")] + [t("table.col.user", user=u) for u in users]
        + [t("table.col.means")], rows)


def fields() -> str:
    return html.table([t("table.col.field"), t("table.col.field_type"),
                       t("table.col.on_events")], [list(f) for f in FIELDS])


def derivations() -> str:
    return (html.table([t("table.col.metric"), t("table.col.how_derived")],
                       [[t(f"derive.{k}"), t(f"derive.{k}.how")]
                        for k in DERIVATIONS])
            + f'<p class="caption">{t("hood.derivations.footnote")}</p>')


def coverage(ctx) -> str:
    users = ctx.payload["meta"]["profiles"]
    summaries = {u: ctx.payload["profiles"][u]["summary"] for u in users}
    strip = html.kpis(
        [{"label": t("hood.kpi.reconstructed", user=u),
          "value": f"{summaries[u]['screen_h']:.0f} {t('unit.hours')}"}
         for u in users]
        + [{"label": t("hood.kpi.attributed", user=u),
            "value": f"{summaries[u]['attributed_pct']:.0f} %"} for u in users])
    return strip + f'<p class="caption">' + t(
        "hood.coverage.caption", a=summaries["A"]["attributed_pct"],
        b=summaries["B"]["attributed_pct"]) + "</p>"


def index(ctx) -> str:
    table = html.table(
        [t("table.col.component"), t("table.col.scores_100"),
         t("table.col.scores_0"), t("table.col.weight")],
        [[label, f"{good:g}", f"{bad:g}", f"{weight*100:.0f} %"]
         for _, label, good, bad, weight in COMPONENTS])
    charts = html.grid(*(html.chart(f"score_breakdown.{u}", "shared")
                         for u in ctx.payload["meta"]["profiles"]))
    return table + charts + html.note(t("hood.index.note"))


def anomalies(ctx) -> str:
    """Five things the stream does that the metrics would get wrong."""
    key = "duplicate USER_PRESENT in stretch"
    numbers = dict(screen_a=ctx.payload["profiles"]["A"]["summary"]["screen_h"],
                   dup_a=ctx.bundles["A"]["anomalies"][key],
                   dup_b=ctx.bundles["B"]["anomalies"][key])

    rows = [[t(f"anomaly.{k}", **numbers), t(f"anomaly.{k}.fix", **numbers)]
            for k in ANOMALIES]
    return (html.table([t("table.col.in_the_stream"), t("table.col.handled")],
                       rows)
            + f'<p class="caption">{t("hood.anomalies.footnote")}</p>')


def build(ctx) -> str:
    return (
        html.details(t("hood.stream.title"), stream(ctx))
        + html.details(t("hood.fields.title"), fields())
        + html.details(t("hood.anomalies.title"), anomalies(ctx))
        + html.details(t("hood.derivations.title"), derivations())
        + html.details(t("hood.coverage.title"), coverage(ctx))
        + html.details(t("hood.index.title"), index(ctx))
    )
