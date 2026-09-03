"""Copy that ends up inside a plotly figure.

Part of the catalogue. See copytext/en.py for how the parts come together.
"""

STRINGS: dict[str, str] = {
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
    "event.alert": "Guardian alert",
    "event.alert.detail": "Notification sent to the guardian",
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
