"""Act 13 · under the hood. Everything closed by default; nothing hidden."""

from collections import Counter

from balance.score import COMPONENTS
from copytext import t

from .. import html

FIELDS = [
    ("id", "int", "id"),
    ("event_type", "str", "event_type"),
    ("timestamp_millis", "int", "timestamp"),
    ("package_name", "str|null", "package"),
    ("url_domain", "str|null", "domain"),
    ("category", "str|null", "category"),
    ("block_type", "str|null", "block_type"),
    ("is_keyguard_locked", "bool|null", "keyguard"),
]

DERIVATIONS = ("screen_time", "pickup", "glance", "app_time", "domain_time",
               "night", "offline", "switch", "distract", "baseline")


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
    return html.table(
        [t("table.col.field"), t("table.col.field_type"),
         t("table.col.what_it_is"), t("table.col.what_we_use")],
        [[name, kind, t(f"field.{key}.is"), t(f"field.{key}.use")]
         for name, kind, key in FIELDS])


def derivations() -> str:
    return html.table(
        [t("table.col.metric"), t("table.col.how_derived")],
        [[t(f"derive.{k}"), t(f"derive.{k}.how")] for k in DERIVATIONS])


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
    charts = html.grid(*(html.chart("score_breakdown", f"profile:{u}")
                         for u in ctx.payload["meta"]["profiles"]))
    return table + charts + html.note(t("hood.index.note"))


def anomalies(ctx) -> str:
    key = "duplicate USER_PRESENT in stretch"
    return html.note(t("hood.anomalies.body",
                       screen_a=ctx.payload["profiles"]["A"]["summary"]["screen_h"],
                       dup_a=ctx.bundles["A"]["anomalies"][key],
                       dup_b=ctx.bundles["B"]["anomalies"][key]))


def build(ctx) -> str:
    return (
        html.details(t("hood.stream.title"), stream(ctx))
        + html.details(t("hood.fields.title"), fields())
        + html.details(t("hood.anomalies.title"), anomalies(ctx))
        + html.details(t("hood.derivations.title"), derivations())
        + html.details(t("hood.coverage.title"), coverage(ctx))
        + html.details(t("hood.index.title"), index(ctx))
    )
