"""Act 04 · the week. First interaction of the page: five weeks on a slider."""

from copytext import t

from .. import html

EVOLUTION = ("screen_min", "night_min", "pickups", "blocks")


def slider(weeks: list[dict], current: dict) -> str:
    numbers = [w["week"] for w in weeks]
    ticks = "".join(f'<option value="{w["week"]}" label="{w["week"]}"></option>'
                    for w in weeks)
    return (
        '<div class="slider" data-slider="week">'
        f'<label for="week-slider">{t("week.slider.label")}</label>'
        f'<output for="week-slider" data-slot="week.label">{current["label"]}'
        "</output>"
        f'<input type="range" id="week-slider" list="week-ticks" '
        f'min="{min(numbers)}" max="{max(numbers)}" step="any" '
        f'value="{current["week"]}">'
        f'<datalist id="week-ticks">{ticks}</datalist></div>'
    )


def days_chart(column: str, week: int) -> str:
    """The only figure whose data really changes with the week, so it ships as
    one variant per week and the mount re-points."""
    key = f"week_days.{column}"
    return html.chart_block(
        f'<figure class="chart" data-figure="{key}.{week}" '
        f'data-figure-week="{key}" data-scope="profile"></figure>', key)


def reading(ctx) -> str:
    """What the five weeks add up to, for this profile."""
    df = ctx.df
    week = lambda n: df[df["week"] == n]["blocks"].mean()  # noqa: E731
    if ctx.user == "A":
        return html.note(t("week.reading.A",
                           blocks=int(df["blocks"].sum())), "good")
    return html.note(t("week.reading.B", first=week(1), last=week(4)), "warn")


def build(ctx) -> str:
    profile = ctx.profile
    current = next(w for w in profile["weeks"]
                   if w["week"] == profile["default_week"])
    return (
        html.lede(t("week.lede"))
        + slider(profile["weeks"], current)
        + html.slot("week.range", f'<p class="caption">{current["range"]}</p>')
        + html.slot("week.kpis", html.kpis(current["kpis"]))
        + html.grid(*(html.chart(f"week_evolution.{c}") for c in EVOLUTION))
        + f'<p class="caption">{t("week.partial_footnote")}</p>'
        + html.chart("week_components")
        + html.slot("week.days_title",
                    f'<h3 class="sub">{current["days_title"]}</h3>')
        + html.grid(days_chart("screen_min", current["week"]),
                    days_chart("night_min", current["week"]))
        + html.slot("week.table", html.table(current["table"]["columns"],
                                             current["table"]["rows"]))
        + html.slot("week.emitted_title",
                    f'<h3 class="sub">{current["emitted_title"]}</h3>')
        + html.slot("week.emissions", emissions(current))
        + html.slot("week.held", held(current))
        + reading(ctx)
    )


def held(week: dict) -> str:
    """A signal the engine recorded and chose not to send is still a signal."""
    if not week["held"]:
        return ""
    return (f'<h3 class="sub">{week["held_title"]}</h3>'
            + html.pairs(week["held"]))


def emissions(week: dict) -> str:
    table = week["emissions"]
    if not table["rows"]:
        return f'<p class="caption">{t("week.emitted.none")}</p>'
    return html.table(table["columns"], table["rows"])
