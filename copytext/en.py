"""Every user-visible string in the product, keyed.

Numbers are never written here as literals: they arrive as format arguments
from the frames, so a copy edit can never move a published figure.
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
    "week.kpi.offline": "Longest break / day",
    "week.kpi.best_offline": "Best break this week",
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
        "{top3:.0f} %, and {messaging:,.0f} min of messaging split across "
        "three apps at once. Distraction sits at {distract:.0f} % against A's "
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

    # -- alerts and nudges --------------------------------------------------
    "engine.caption": (
        "Every variable the rules read, each as a share of its own maximum so "
        "the shapes compare. The rail below zero is what the phone emitted."
    ),
    "engine.slider.label": "Day of the period",
    "engine.outputs.title": "Outputs on {date}",
    "engine.channel.user": "User's screen",
    "engine.channel.guardian": "Guardian's phone",
    "engine.channel.device": "On the device",
    "engine.empty": "No notifications",

    "phone.brand": "BALANCE",
    "phone.brand.guardian": "BALANCE · GUARDIAN OF {user}",
    "phone.time.summary": "09:00",
    "phone.time.guardian": "09:12",
    "phone.eyebrow.summary": "Your summary",
    "phone.eyebrow.nudge": "Night nudge",
    "phone.eyebrow.alert": "Alert",
    "phone.eyebrow.digest": "Summary",
    "phone.cta.week": "Your week",
    "phone.cta.weekly_summary": "Weekly summary",
    "phone.cta.off_until_tomorrow": "Off until tomorrow",
    "phone.cta.five_more": "5 more minutes",
    "phone.nudge.headline": (
        "That is the {ordinal} time you have opened your phone tonight."
    ),
    "phone.nudge.body": "A month ago you had already put it down by now.",

    "device.row.screen": "Screen",
    "device.row.pickups": "Unlocks",
    "device.row.night": "Late night",
    "device.row.night_end": "Night ended",
    "device.row.offline": "Longest break",
    "device.row.offline_start": "· started",
    "device.row.distract": "Distraction share",
    "device.row.sensitive": "Sensitive attempts",
    "device.row.blocks": "Total blocks",
    "device.row.score": "Index",
    "device.row.nudges": "Nudges so far",
    "device.row.reinforcements": "Reinforcements",
    "device.score.value": "{score:.0f} / 100",
    "device.caption": "Computed and kept on the phone.",
    "device.caption.guardian": (
        " Only the weekly digest's rounded aggregate leaves it."
    ),

    "engine.emissions.title": "Everything the phone emitted this month",
    "engine.emissions.none": "The phone emitted nothing in the period.",

    "engine.kpi.guardian": "Guardian notifications",
    "engine.kpi.guardian.delta": "quota {budget}/month",
    "engine.kpi.summary": "Into weekly summary",
    "engine.kpi.summary.delta": "not notified",
    "engine.kpi.reinforcements": "Reinforcements sent",
    "engine.kpi.reinforcements.delta": "one a week at most",
    "engine.kpi.nudge_nights": "Nights with a nudge",
    "engine.kpi.nudge_nights.value": "{nudged}/{nights}",
    "engine.kpi.nudge_nights.delta": "{pct:.0f} % of nights",


    "table.col.rule": "Rule",


    "engine.coverage.title": "Rule coverage",
    "engine.coverage.night_drift": "5 nights against the previous 14, plus bedtime",
    "engine.coverage.sensitive_spike": "Sensitive attempts, 7 days against 7",
    "engine.coverage.screen_jump": "Screen time, 5 days against the previous 14",
    "table.col.compares": "What it compares",
    "table.col.user": "User {user}",
    "value.decision_on": "{decision} · {date}",
    "engine.coverage.note": (
        "<code>screen_jump</code> fires on neither profile. User B's daily use "
        "grows {screen:.0f} % over the month, below the threshold of any "
        "reasonable volume rule, while their night band multiplies by "
        "{night:.0f}. Catching this case depends on watching the schedule, not "
        "the total."
    ),

    "engine.nudge.title": "On-device nudge",
    "engine.nudge.caption": (
        "Second reopening from {from_clock}, once a night at most. Replayed "
        "over the thirty days."
    ),
    "engine.nudge.row.nights": "Nights evaluated",
    "engine.nudge.row.nudged": "Nights with a nudge",
    "engine.nudge.row.nudged_value": "{nudged} ({pct:.0f} %)",
    "engine.nudge.row.night_minutes": "Night minutes",
    "engine.nudge.row.after": "Minutes after the nudge",
    "engine.nudge.row.after_value": "{minutes:.0f} ({pct:.0f} %)",
    "engine.nudge.row.per_night": "Per night",
    "engine.nudge.row.per_night_value": "{minutes:.0f} min",

    # -- under the hood -----------------------------------------------------
    "hood.stream.title": "The stream",
    "table.col.means": "What it means",
    "event.SCREEN_ON": "May be a glance.",
    "event.SCREEN_OFF": "",
    "event.USER_PRESENT": "A real unlock. This is what makes a pickup.",
    "event.APP_FOREGROUND": "",
    "event.URL_VISIT": "Domain only, never a path.",
    "event.BLOCK": "Nothing opened.",

    "hood.fields.title": "The eight fields",
    "table.col.field": "Field",
    "table.col.field_type": "Type",
    "table.col.on_events": "On",


    "hood.anomalies.title": "Awkward things in the stream",
    "table.col.in_the_stream": "Stream",
    "table.col.handled": "Handled",
    "anomaly.overlap": "A screen-on while the screen is already on.",
    "anomaly.overlap.fix": "A depth counter, giving the union: {screen_a:.1f} h for A.",
    "anomaly.truncated": "The file ends mid-day.",
    "anomaly.truncated.fix": (
        "That day leaves every average, but still counts towards the night "
        "before."
    ),
    "anomaly.midnight_start": "A day opens at 00:20, the tail of the night before.",
    "anomaly.midnight_start.fix": "First unlock means the first from 06:00.",
    "anomaly.crossing": "A screen stretch runs through midnight.",
    "anomaly.crossing.fix": "Split at the boundary.",
    "anomaly.duplicates": (
        "One unlock recorded twice, {dup_a} times in A and {dup_b} in B."
    ),
    "anomaly.duplicates.fix": "Counted, not dropped in silence.",
    "hood.anomalies.footnote": "Why a depth counter is in DECISIONS.md.",

    "hood.derivations.title": "From event to metric",
    "hood.derivations.footnote": "The rest are in ARCHITECTURE.md.",
    "table.col.how_derived": "How it is derived",
    "derive.screen_time": "Screen time",
    "derive.screen_time.how": "Union of on-to-off intervals, split at midnight.",
    "derive.pickup": "Real pickup",
    "derive.pickup.how": "A screen-on with an unlock before the next one.",
    "derive.glance": "Glance",
    "derive.glance.how": "A screen-on with no unlock. It lit; it never opened.",
    "derive.app_time": "Time per app",
    "derive.app_time.how": "Foreground to the next change or screen off, capped at 45 min.",
    "derive.domain_time": "Time per domain",
    "derive.domain_time.how": "The same, with the time moved off the browser.",
    "derive.night": "Night band",
    "derive.night.how": "23:00 to 06:00 the next morning. Sleep does not cut at midnight.",
    "derive.offline": "Longest break",
    "derive.offline.how": "Longest screen-free gap between 07:00 and 23:00.",
    "derive.switch": "App switch",
    "derive.switch.how": "A move between two different apps. Reset daily.",
    "derive.distract": "Distraction share",
    "derive.distract.how": "Social, entertainment and gaming over attributed time.",
    "derive.baseline": "Your normal",
    "derive.baseline.how": "Rolling median of this user's last 14 days.",

    "hood.coverage.title": "Screen time explained",
    "hood.kpi.reconstructed": "{user} · screen reconstructed",
    "hood.kpi.attributed": "{user} · attributed to app/site",
    "hood.coverage.caption": (
        "The rest is lock screen and notifications. B's {b:.0f} % against A's "
        "{a:.0f} % is the checking pattern."
    ),

    "hood.index.title": "The index",
    "table.col.component": "Component",
    "table.col.scores_100": "Value scoring 100",
    "table.col.scores_0": "Value scoring 0",
    "table.col.weight": "Weight",
    "hood.index.note": (
        "Blocks do not score. Docking points for an attempt the filter already "
        "stopped charges the user for the product working."
    ),
    # -- figures: titles and axes -------------------------------------------
    "unit.score": "0 to 100",
    "chart.day_span": "User {user} · from what time to what time",
    "chart.night_drift": "Screen in the night band (23:00 to 06:00)",
    "chart.hour_heat": "User {user} · weekly screen clock",
    "chart.score_line": "Digital wellbeing index (7-day mean)",
    "chart.score_breakdown": "User {user} · where the index comes from (month mean)",
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
    # -- the scroll: parts and act headings ---------------------------------
    "part.1": "Setup",
    "part.2": "One person's month",
    "part.3": "The analysis",

    "act.01.eyebrow": "Balance · May 2026",
    "act.01.title": "Device behaviour",
    "act.02.eyebrow": "Both profiles, thirty days",
    "act.02.title": "Two people, one phone",
    "act.03.eyebrow": "Pick one",
    "act.03.title": "Choose a profile",
    "act.04.eyebrow": "Week by week",
    "act.04.title": "The week",
    "act.05.eyebrow": "Hour by hour",
    "act.05.title": "A day in the life",
    "act.06.eyebrow": "23:00 to 06:00",
    "act.06.title": "The night",
    "act.07.eyebrow": "Apps, domains, categories",
    "act.07.title": "Where the time goes",
    "act.08.eyebrow": "The filter",
    "act.08.title": "What the phone stopped",
    "act.09.eyebrow": "Alerts, nudges, reinforcements",
    "act.09.title": "What the phone said",
    "act.10.eyebrow": "The reveal",
    "act.10.title": "The finding",
    "act.11.eyebrow": "The negative control",
    "act.11.title": "What a screen-time rule would have missed",
    "act.12.eyebrow": "Schema and derivations",
    "act.12.title": "Under the hood",

    # -- act 01 · cover -----------------------------------------------------
    "cover.standfirst": (
        "One device event log, read end to end: what the phone recorded, what "
        "it computed, and what it said out loud."
    ),
    "cover.stat.profiles": "profiles",
    "cover.stat.events": "events",
    "cover.stat.days": "days each",
    "cover.scroll": "Scroll",

    # -- act 02 · two people, one phone -------------------------------------
    "overview.lede": "Two kinds of profile, the same thirty days.",
    "overview.hook": (
        "Watch B. The index falls from {first:.0f} to {last:.0f} while screen "
        "time moves {screen:+.0f} %."
    ),
    "profile.card.eyebrow": "User {user}",

    # -- act 03 · choose a profile ------------------------------------------
    "fork.lede": "Both months are here. Read one, then the other.",
    "fork.sketch.A": (
        "An adult with no guardian. A routine that holds for thirty days."
    ),
    "fork.sketch.B": (
        "A minor with a guardian. A schedule that slides, week by week."
    ),
    "fork.stat.screen": "screen / day",
    "fork.stat.index": "index",
    "fork.stat.nights": "nights with a nudge",
    "fork.cta": "Read this month",

    # -- act 10 · the finding -----------------------------------------------
    "finding.lede": "B's index fell as their night-time use rose.",
    "finding.hero.value": "×{multiple:.0f}",
    "finding.hero.label": "late-night screen, week 1 against week 4",
    "finding.sleep.value": "{minutes:.0f} min",
    "finding.sleep.label": "less rest available per night",
    "finding.body": (
        "The last screen moves {shift:.0f} minutes later, the first unlock "
        "stays put, and the window closes from {first:.1f} h to {last:.1f} h. "
        "Unlocks after midnight go {pick_first:.1f} to {pick_last:.1f}. A "
        "records zero night minutes over the same thirty days."
    ),

    # -- act 11 · the negative control --------------------------------------
    "control.lede": "Screen time against the night band.",
    "control.screen.label": "screen time, week 1 to week 4",
    "control.night.label": "late-night screen, same weeks",
    "control.body": (
        "<code>screen_jump</code> is implemented, reads the same frames, and "
        "fires on neither profile. {screen:+.0f} % is under any threshold "
        "worth setting. The night band is ×{night:.0f}."
    ),
}

#: Month abbreviations. Written out rather than taken from `strftime` so the
#: label does not depend on the process locale.
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

#: Weekday abbreviations, Monday first. Written out for the same reason as
#: MONTHS.
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
