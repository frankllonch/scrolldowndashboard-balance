"""What the metrics are called, and what they mean.

Part of the catalogue. See copytext/en.py for how the parts come together.
"""

STRINGS: dict[str, str] = {
    # -- units and shared fragments -----------------------------------------
    "unit.min": "min",
    "unit.minutes": "minutes",
    "unit.hours": "h",
    "unit.unlocks": "unlocks",
    "unit.blocks": "blocks",
    "unit.percent": "%",
    "fmt.hm": "{h}h {m:02d}m",
    "fmt.m": "{m} min",
    "fmt.clock": "{h:02d}:{m:02d}",
    "fmt.date": "{day} {month}",
    "value.no_use": "no use",
    "value.no_change": "no change",
    "value.not_available": "n/a",
    "value.no_guardian": "no guardian",
    "value.no_stretch": "no stretch",
    "value.does_not_fire": "does not fire",

    # -- site chrome --------------------------------------------------------
    "site.page_title": "Balance · Device event explorer",


    "pill.label": "Reading",


    # -- overview -----------------------------------------------------------
    "overview.index.eyebrow": "User {user} · wellbeing index",
    "overview.index.scale": " /100",
    "overview.index.weeks": (
        "week 1 → {first:.0f} &nbsp;·&nbsp; last full week → {last:.0f}"
    ),

    "kpi.screen_day": "{user} · screen/day",
    "kpi.unlocks_day": "{user} · unlocks/day",
    "kpi.night_day": "{user} · late night/day",
    "kpi.blocks_month": "{user} · blocks/month",
    "kpi.sensitive": "{user} · sensitive",


    "chart.screen_per_day": "Screen time per day",
    "chart.pickups_per_day": "Real unlocks per day",
    "chart.night_per_day": "Late-night screen minutes",
    "chart.blocks_per_day": "Blocked attempts per day",

    "table.col.metric": "Metric",
    "table.col.change": "Change",
    "row.screen_per_day": "Screen per day",
    "row.unlocks_per_day": "Unlocks per day",
    "row.blocks_per_day": "Blocks per day",

    # -- weekly summary -----------------------------------------------------
    "week.slider.label": "Week",
    "week.slider.option": "Week {week}",
    "week.slider.option_short": "Week {week} (short)",
    "week.range": "{start} to {end} · {days} days",
    "week.range.partial": (
        "  ·  short week: the averages are per day, but comparing it against "
        "seven-day weeks is less reliable."
    ),
    "week.kpi.screen": "Screen / day",
    "week.kpi.pickups": "Unlocks / day",
    "week.kpi.night": "Late night / night",
    "week.kpi.offline": "Longest break, average day",
    "week.kpi.best_offline": "Longest break, best day",
    "week.kpi.blocks": "Blocks / day",
    "week.kpi.score": "Index",
    "chart.week.screen": "Screen per day, by week",
    "chart.week.night": "Late night per night, by week",
    "chart.week.pickups": "Unlocks per day, by week",
    "chart.week.blocks": "Blocks per day, by week",
    "week.partial_footnote": "Weeks marked with * are shorter than seven days.",
    "week.days.title": "The days of week {week}",
    "chart.week_days.screen": "Screen per day · week {week}",
    "chart.week_days.night": "Late night per night · week {week}",
    "table.col.week_selected": "Week {week}",
    "table.col.previous_week": "Previous week",
    "table.col.period_median": "Period median",
    "row.night_per_night": "Late night per night",
    "row.longest_offline": "Longest break",
    "row.distinct_apps": "Distinct apps per day",
    "row.switches_per_hour": "App switches per hour",
    "row.distract_share": "Distraction share",
    "row.index": "Index",
    "week.emitted.title": "What the phone emitted in week {week}",
    "table.col.date": "Date",
    "table.col.destination": "Destination",
    "table.col.type": "Type",
    "table.col.detail": "Detail",
    "week.emitted.none": "Nothing this week.",
    "week.recorded.title": "Also recorded this week, not notified",

    # -- daily rhythm -------------------------------------------------------
    "day.title": "User {user} · month at a glance",
    "day.kpi.screen": "Screen / day",
    "day.kpi.screen.delta": "±{sd:.0f} min",
    "day.kpi.sessions": "Sessions / day",
    "day.kpi.sessions.delta": "median {median:.1f} min",
    "day.kpi.pickups": "Real unlocks",
    "day.kpi.pickups.delta": "{glances:.0f} glances",
    "day.kpi.first_pickup": "First unlock",
    "day.kpi.first_pickup.delta": "median {median:.1f} h",
    "day.kpi.offline": "Longest break",
    "day.kpi.offline.delta": "best {best:.1f} h, {when}",
    "day.kpi.switches": "App switches / h",
    "day.kpi.switches.delta": "{apps:.0f} distinct apps",
    "chart.day.screen": "User {user} · screen per day",
    "chart.day.pickups": "User {user} · unlocks per day",
    "day.baseline.caption": (
        "Against this user's own 14-day median. The first two weeks have no "
        "history."
    ),
    "day.note.a": (
        "A working week with a weekend in it: {weekday:.0f} min on weekdays, "
        "{weekend:.0f} at weekends, last screen around {last_use}, nothing "
        "after 23:00 on any day."
    ),
    "day.note.b": (
        "The week has no edges. {weekend:.0f} min at weekends against "
        "{weekday:.0f} on weekdays, spread from 08:00 to midnight all seven "
        "days. Sessions are short at {session:.1f} min but arrive "
        "{switches:.0f} times an hour, {ratio:.1f}× A's rate: checking, not "
        "sitting down with it."
    ),

    # -- the night ----------------------------------------------------------
    "night.kpi.first_week": "Late night, wk 1",
    "night.kpi.last_week": "Late night, wk 4",
    "night.kpi.last_screen_first": "Last screen, wk 1",
    "night.kpi.last_screen_last": "Last screen, wk 4",
    "night.kpi.first_unlock": "First unlock",
    "night.kpi.sleep_window": "Sleep window",
    "delta.times": "×{n:.0f}",
    "delta.minutes": "{n:+.0f} min",
    "night.note.drift": (
        "<b>Bedtime slides; the alarm does not.</b> Last screen {end_first} → "
        "{end_last}, first unlock {wake_first} → {wake_last}. The window "
        "between them closes from {sleep_first:.1f} h to {sleep_last:.1f} h, "
        "<b>{sleep_loss:.0f} min less rest a night</b>. Unlocks after midnight "
        "go from {pick_first:.1f} to {pick_last:.1f}."
    ),
    "chart.night_pickups": "Unlocks after midnight",
    "night.note.user_a": (
        "Nothing here. Zero minutes between 23:00 and 06:00 across all thirty "
        "days, last screen at {last_use} on average. The 23:00 line costs this "
        "profile nothing."
    ),
    "night.weight.body": (
        "The smallest metric here, {night:.0f} min a day against {screen:.0f} "
        "of screen, carries 20 % of the index. An hour at 01:00 comes out of "
        "rest; an hour at 17:00 does not."
    ),

    # -- where the time goes ------------------------------------------------
    "tag.device_only": "device only",
    "tag.never_sent": "never sent to a guardian",
    "time.kpi.attributed": "Attributed time",
    "time.kpi.attributed.delta": "of {pct:.0f} % of screen",
    "time.kpi.apps": "Distinct apps",
    "time.kpi.domains": "Distinct domains",
    "time.kpi.whole_month": "this month",
    "time.kpi.top3": "Top 3 apps",
    "time.kpi.top3.delta": "of app time",
    "time.kpi.distract": "Distraction share",
    "time.kpi.distract.delta": "social + entertainment + games",
    "chart.time.apps": "User {user} · apps by minutes",
    "chart.time.domains": "User {user} · domains by minutes",
    "chart.time.categories": "User {user} · minutes by content category",
    "time.colour.caption": "Colour is the category; openings are in the tooltip.",
    "time.note.a": (
        "A small catalogue: {apps} apps in thirty days, the top three holding "
        "{top3:.0f} % of the time. Browsing is {news:.0f} % news. Distraction "
        "averages {distract:.0f} % and falls, {first:.0f} % to {last:.0f} %."
    ),
    "time.caption.chrome": (
        "Chrome shows {opens:.0f} openings and {minutes:.0f} min: browser time "
        "goes to the domain."
    ),
    "time.note.b": (
        "{apps} apps against A's {apps_a}, with the top three holding only "
        "{top3:.0f} %, and {messaging:,.0f} min of reaching people across "
        "{messaging_apps} apps. Distraction sits at {distract:.0f} % against A's "
        "{distract_a:.0f} %. What this profile spends time on is ordinary; "
        "how much, and when, is not."
    ),
    "time.caption.blocked_absent": (
        "Only content that opened. {names} were stopped {attempts} times and "
        "let through {through}, so they never reach this chart."
    ),

    # -- what the phone stopped ---------------------------------------------
    "tag.aggregate_only": "only the aggregate reaches a guardian",
    "blocks.none": "No blocks in the period.",
    "blocks.kpi.attempts": "Blocked attempts",
    "blocks.kpi.attempts.delta": "{per_day:.1f} per day",
    "blocks.kpi.apps": "Apps blocked",
    "blocks.kpi.sites": "Sites blocked",
    "blocks.kpi.nudity": "Nudity detection",
    "blocks.kpi.nudity.delta": "on device",
    "blocks.kpi.sensitive": "Adult + gambling",
    "blocks.kpi.sensitive.delta": "{pct:.0f} % of the total",
    "blocks.kpi.opened": "Ever opened",
    "blocks.kpi.opened.delta": "of the sensitive",
    "chart.blocks.daily": "User {user} · blocked attempts per day",
    "chart.blocks.hour": "User {user} · blocks by hour of day",
    "table.col.week_days": "Week {week} ({days} d)",
    "blocks.note.a": (
        "{total} attempts in thirty days, all social and entertainment, no "
        "sensitive content. The filter steps in less as the month goes on, "
        "{first:.0f} to {last:.0f} a week."
    ),
    "blocks.note.b": (
        "{ordinary:,} ordinary attempts, {first:.0f} to {last:.0f} a week, "
        "plus {adult} adult and {gambling} gambling and {nudity} detections. "
        "None opened. The sensitive ones spike rather than trend: {mid} of "
        "{sensitive} land in weeks 2 and 3 and {week_four} in week 4. That is "
        "a summary entry, not a phone call."
    ),
    "blocks.scope.body": (
        "This screen stays on the device. A guardian sees the filter's state "
        "and that <b>{sensitive} sensitive attempts were blocked and none "
        "opened</b>. Nothing named."
    ),
}
