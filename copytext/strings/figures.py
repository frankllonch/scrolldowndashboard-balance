"""Copy that ends up inside a plotly figure.

Part of the catalogue. See copytext/en.py for how the parts come together.
"""

STRINGS: dict[str, str] = {
    # -- one line under every chart, in reading order ------------------------
    # Resolved by html.chart(), which walks the figure key from the most
    # specific name to the least, so a variant inherits its family's line.
    "chart.explain.score_line": (
        "Both people's wellbeing index, every day of the month. The line is a "
        "7-day average so it does not jump around; the faint dots behind it "
        "are the actual daily scores."
    ),
    # A week marked * is short; that caveat is on the footnote under the group
    # rather than repeated in all four lines.
    "chart.explain.week_evolution.screen_min": (
        "Your average screen time per day, week by week. The highlighted bar "
        "is the week you have selected."
    ),
    "chart.explain.week_evolution.night_min": (
        "The same weeks, but only the minutes between 23:00 and 06:00. Watch "
        "this one against the bar chart beside it."
    ),
    "chart.explain.week_evolution.pickups": (
        "How many times a day you really unlocked the phone, week by week. A "
        "screen that lit up without being unlocked is a glance, and is not "
        "counted here."
    ),
    "chart.explain.week_evolution.blocks": (
        "How many attempts the filter stopped per day, week by week. Rising "
        "bars mean the phone is being asked more often, not that more is "
        "getting through."
    ),
    "chart.explain.week_components": (
        "The five parts of the index, scored 0 to 100, week by week. The "
        "dotted line marks the week you have selected. A part that falls here "
        "is a part that is pulling your score down."
    ),
    "chart.explain.week_days.screen_min": (
        "Screen time for each day of the week you picked, Monday to Sunday. "
        "The dotted line is your average across every week before this one, "
        "so a bar above it is a day above your own normal."
    ),
    "chart.explain.week_days.night_min": (
        "The same seven days, counting only what happened after 23:00. Most "
        "weeks this should be a flat row of nothing."
    ),
    "chart.explain.daily_bars.screen_min": (
        "Your screen time on every day of the month, against your own rolling "
        "14-day median — not against the other user, and not against a "
        "target. The first two weeks have no history to compare with yet."
    ),
    "chart.explain.daily_bars.pickups": (
        "The same thirty days, counting unlocks instead of minutes. A day can "
        "sit under your median for time and over it for unlocks: that is a "
        "day you checked the phone a lot without settling into it."
    ),
    "chart.explain.hour_heat": (
        "Your week as a grid: days down, hours across. The darker the cell, "
        "the more screen time in that hour. It shows the shape of your week "
        "at a glance — where the phone lives in your day."
    ),
    "chart.explain.day_span": (
        "One bar per day, running from your first unlock to your last screen. "
        "It is not how much you used the phone, it is how much of the day the "
        "phone was part of."
    ),
    "chart.explain.day_span.night": (
        "The same day-length bars, with the 23:00 to 06:00 band marked. What "
        "you are looking for is bars leaking into the band."
    ),
    "chart.explain.night_drift": (
        "Screen minutes between 23:00 and 06:00, night by night, for both "
        "people. This is the single chart the whole month turns on."
    ),
    "chart.explain.compare.night_pickups": (
        "Unlocks after midnight, both people on the same scale. One of these "
        "two lines stays on the floor for thirty days."
    ),
    "chart.explain.compare.screen_min": (
        "Total screen time per day for both people, week 1 to the last. This "
        "is the measure a plain screen-time rule would watch — and it barely "
        "moves."
    ),
    "chart.explain.compare.night_min": (
        "The same weeks, same scale, but only the night band. This is the "
        "measure that moves, and it is why watching the total would have "
        "missed the whole month."
    ),
    "chart.explain.top_bars.apps": (
        "Your ten biggest apps by minutes. Colour is the content category; "
        "hover for how many times you opened each one."
    ),
    "chart.explain.top_bars.sites": (
        "The same, for websites. Only the domain is ever recorded, never the "
        "page — so time spent in the browser lands here rather than under "
        "Chrome."
    ),
    "chart.explain.category_area": (
        "What your minutes were made of, day by day, stacked. The order of "
        "the bands is fixed, so a band that grows really is growing and has "
        "not just been re-ranked."
    ),
    "chart.explain.blocks_daily": (
        "How many attempts the filter stopped each day, split by what kind. "
        "Nothing here opened — a block is an attempt that went nowhere."
    ),
    "chart.explain.blocks_by_hour": (
        "What time of day you hit the wall. Sensitive attempts are drawn "
        "separately from ordinary distraction."
    ),
    "chart.explain.tracked_series": (
        "Every variable the alert rules watch, on one axis. Each is drawn as "
        "a share of its own maximum, so shapes can be compared even though "
        "the units cannot. The rail below zero is what the phone actually "
        "did that day."
    ),
    "chart.explain.score_breakdown.A": (
        "Where A's index came from: what each of the five parts contributed "
        "on an average day, and how many points it let go."
    ),
    "chart.explain.score_breakdown.B": (
        "The same breakdown for B. Compare the bars, not the totals — the "
        "gap between the two people is one component doing most of the work."
    ),
    # -- figures: titles and axes -------------------------------------------
    "unit.score": "0 to 100",
    "chart.day_span": "User {user} · from what time to what time",
    "chart.night_drift": "Screen in the night band (23:00 to 06:00)",
    "chart.hour_heat": "User {user} · weekly screen clock",
    "chart.score_line": "Digital wellbeing index (7-day mean)",
    "chart.score_breakdown": "User {user} · where the index comes from",
    "chart.week_components": "Index components by week",
    "axis.local_time": "local time",
    "axis.minutes_rolling": "minutes (3-day rolling mean)",
    "axis.minutes_month": "minutes this month",
    "axis.blocked_attempts": "blocked attempts",
    "axis.attempts_month": "attempts this month",
    "axis.points": "points out of 100",
    "axis.pct_of_max": "% of the period maximum",
    "axis.pct_max_tick": "100 %",

    # -- figures: series and annotations ------------------------------------
    "series.user": "User {user}",
    "series.daily": "{user} · daily",
    "series.daily_plain": "{user} daily",
    "series.night_flat": "User {user}: 0 min across {nights} nights",
    "series.at_or_below": "At or below your normal",
    "series.above": "Above your normal",
    "series.baseline": "Your normal (14-day median)",
    "series.day_with_phone": "Day with the phone",
    "series.last_screen_mean": "Last screen (7-day mean)",
    "series.ordinary": "Ordinary distraction",
    "series.sensitive": "Adult / gambling",
    "series.points_earned": "Points earned",
    "series.points_lost": "Points lost",
    "series.week": "Week {week}",
    "series.no_activity": " · no activity",
    "annotation.night_start": "23:00",
    "annotation.events": "events",
    "annotation.prev_mean": "mean of previous weeks: {mean:,.0f}",
    "annotation.no_activity_week": "No activity this week",
    "label.week": "W{week}",
    "label.week_partial": "W{week} *",

    # -- figures: content categories ----------------------------------------
    "category.SOCIAL_MEDIA": "Social Media",
    "category.MESSAGING": "Messaging",
    "category.ENTERTAINMENT": "Entertainment",
    "category.SHOPPING": "Shopping",
    "category.GAMING": "Gaming",
    "category.ADULT": "Adult",
    "category.NEWS": "News",
    "category.GAMBLING": "Gambling",
    "category.CALLS": "Calls",
    "category.NAVIGATION": "Navigation",
    "category.PRODUCTIVITY": "Productivity",
    "category.LEARNING": "Learning",
    "category.AI_TOOLS": "AI tools",
    "category.REFERENCE": "Research",
    "category.OTHER": "Other",

    # -- figures: the month walkthrough -------------------------------------
    "tracked.night_min": "Late-night screen",
    "tracked.night_end_min": "Last screen (from 23:00)",
    "tracked.screen_min": "Screen per day",
    "tracked.longest_offline_h": "Longest break",
    "tracked.blocks": "Blocks per day",
    "tracked.blocks_sensitive": "Sensitive attempts",
    "tracked.distract_pct": "Distraction share",
    "legend.tracked": "Watched variables",
    "legend.emissions": "Emissions",
    "event.nudge": "Night with a nudge",
    "event.nudge.detail": "Night nudge on the device",
    "event.alert": "Alert",
    "event.alert.detail": "Notification shown on the phone",
    "event.digest": "Summary entry",
    "event.digest.detail": "Signal held for the weekly summary",
    "event.positive": "Reinforcement",
    "event.positive.detail": "Reinforcement sent",

    # -- figures: hover and tick templates ($name interpolates, %{} does not)
    "hover.compare_daily": "%{y:.0f} $unit<extra>User $user</extra>",
    "hover.compare_smoothed": (
        "%{y:.0f} $unit ($smooth d mean)<extra>User $user</extra>"
    ),
    "hover.day_value": "%{x|%a %d %b}<br>%{y:.0f} $unit<extra></extra>",
    "hover.baseline": "normal: %{y:.0f} $unit<extra></extra>",
    "hover.day_span": (
        "%{x|%a %d %b}<br>from %{customdata[0]} to %{customdata[1]}"
        "<extra></extra>"
    ),
    "hover.night_drift": (
        "%{x|%a %d %b}<br>%{y:.0f} late-night min<extra>User $user</extra>"
    ),
    "hover.category": "%{y:.0f} min<extra>$category</extra>",
    "hover.top_bars": (
        "<b>%{y}</b><br>%{x:.0f} min in total<br>"
        "%{customdata[0]} openings · %{customdata[1]:.1f} min per opening"
        "<br>%{customdata[2]}<extra></extra>"
    ),
    "hover.heat": "%{y} · %{x}:00<br>%{z:.0f} min<extra></extra>",
    "hover.blocks_category": "%{y:.0f}<extra>$category</extra>",
    "hover.blocks_hour": "%{x}:00 → %{y:.0f}<extra>$name</extra>",
    "hover.score": "%{y:.0f}/100<extra>User $user</extra>",
    "hover.points_earned": "%{x:.1f} of %{customdata:.0f} possible<extra></extra>",
    "hover.points_lost": "%{x:.1f} lost<extra></extra>",
    "hover.tracked": (
        "<b>$label</b>: %{customdata:.1f} $unit<br>$rules<extra></extra>"
    ),
    "hover.event": "%{x|%d %b}<br>$detail<extra></extra>",
    "hover.week": "%{x}<br>%{y:.1f} $unit<extra>$label</extra>",
    "hover.week_day": "%{x}<br>%{y:.0f} $unit<extra></extra>",
    "hover.component": "%{y:.0f}/100<extra>$label</extra>",
    "text.minutes": "{minutes:,.0f} min",
    "tick.hour": "{hour:02d}:00",
}
