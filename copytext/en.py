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
    "loading.spinner": "Rebuilding sessions from the event log…",
    "site.brand": "Balance",
    "site.tagline": "Device event explorer · May 2026",
    "site.title": "Device behaviour · May 2026",
    "site.subtitle": (
        "{profiles} profiles · {events:,} events · {days} days · screen time, "
        "unlocks, night band, categories, blocks, wellbeing index and alerts"
    ),

    "sidebar.footprint.eyebrow": "Data footprint",
    "sidebar.footprint.line": (
        "**User {user}**: {events:,} events · {days} complete days · "
        "{intervals} screen stretches"
    ),
    "sidebar.scope.eyebrow": "Scope of this data",
    "sidebar.scope.body": (
        "This is the device-side view. Per-app, per-site and block detail is "
        "never transmitted off the phone. What a guardian receives is in "
        "**Alerts and nudges**."
    ),
    "sidebar.notifications.eyebrow": "Notifications in the period",
    "sidebar.notifications.line": "**User {user}**: {sent} · {nudges} nudges",
    "sidebar.notifications.to_guardian": "{n} to the guardian",

    "profile.label": "Profile to inspect",
    "profile.help": (
        "Affects Daily rhythm, Where the time goes and What the phone "
        "stopped. Overview and The night always compare both."
    ),

    "tab.overview": "Overview",
    "tab.week": "Weekly summary",
    "tab.day": "Daily rhythm",
    "tab.night": "The night",
    "tab.time": "Where the time goes",
    "tab.blocks": "What the phone stopped",
    "tab.engine": "Alerts and nudges",
    "tab.hood": "The data",

    # -- overview -----------------------------------------------------------
    "overview.profiles.title": "Profiles",
    "overview.profiles.body": (
        "The two files are different kinds of profile and need different "
        "configurations.<br><br>"
        "<b>User A</b> · adult, no guardian. {a_screen} of screen per day, "
        "{a_pickups:.0f} unlocks, {a_apps:.0f} apps. No night-band use and no "
        "sensitive content across the 30 days.<br>"
        "<b>User B</b> · minor with a guardian. {b_screen}, {b_pickups:.0f} "
        "unlocks, {b_apps:.0f} apps. {b_blocks:,.0f} blocked attempts, of "
        "which {b_sensitive:.0f} are <code>ADULT</code> or "
        "<code>GAMBLING</code>. App catalogue consistent with a minor: "
        "Duolingo and Kindle in daily use, Roblox and Clash of Clans blocked "
        "73 and 71 times."
    ),
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

    "overview.score.title": "Wellbeing index",
    "overview.score.note": (
        "<b>A</b> holds at {a_mean:.0f} across the four weeks (range "
        "{a_min:.0f} to {a_max:.0f}), with no change of trend.<br>"
        "<b>B</b> goes from {b_first:.0f} to {b_last:.0f}, {b_drop:.0f} points "
        "in three weeks. The drop comes almost entirely from the night "
        "component: their night score falls from {b_night_first:.0f} to "
        "{b_night_last:.0f} while every other component moves less than 10 "
        "points. Detail in \"The night\"."
    ),

    "overview.moves.title": "What moves and what does not",
    "chart.screen_per_day": "Screen time per day",
    "chart.pickups_per_day": "Real unlocks per day",
    "chart.night_per_day": "Late-night screen minutes",
    "chart.blocks_per_day": "Blocked attempts per day",

    "overview.compare.title": "User B, week 1 against week 4",
    "table.col.metric": "Metric",
    "table.col.week_one": "Week 1",
    "table.col.week_four": "Week 4",
    "table.col.change": "Change",
    "row.screen_per_day": "Screen per day",
    "row.unlocks_per_day": "Unlocks per day",
    "row.night_minutes": "Late-night minutes",
    "row.night_pickups": "Unlocks after midnight",
    "row.blocks_per_day": "Blocks per day",
    "overview.compare.note": (
        "Volume barely moves ({screen:+.0f} % of screen time, {pickups:+.0f} % "
        "of unlocks) while the night band multiplies by {night:.0f}. A "
        "threshold on screen time would not have caught this case: detection "
        "runs on the night band, not on the total (see \"Alerts and nudges\")."
    ),

    # -- weekly summary -----------------------------------------------------
    "week.title": "User {user} · week by week",
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
    "week.kpi.offline": "Longest disconnection",
    "week.kpi.best_offline": "Best stretch this week",
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
    "week.compare.title": "Against the rest of the period",
    "table.col.week_selected": "Week {week}",
    "table.col.previous_week": "Previous week",
    "table.col.period_median": "Period median",
    "row.night_per_night": "Late night per night",
    "row.longest_offline": "Longest disconnection",
    "row.distinct_apps": "Distinct apps per day",
    "row.switches_per_hour": "App switches per hour",
    "row.distract_share": "Distraction share",
    "row.index": "Index",
    "week.emitted.title": "What the phone emitted in week {week}",
    "table.col.date": "Date",
    "table.col.destination": "Destination",
    "table.col.type": "Type",
    "table.col.detail": "Detail",
    "week.emitted.none": "No notification and no nudge this week.",
    "week.recorded.title": "**Also recorded this week, not notified**",

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
    "day.kpi.offline": "Longest disconnection",
    "day.kpi.offline.delta": "best: {best:.1f} h on {when}",
    "day.kpi.switches": "App switches / h",
    "day.kpi.switches.delta": "{apps:.0f} distinct apps",
    "chart.day.screen": "User {user} · screen per day",
    "chart.day.pickups": "User {user} · unlocks per day",
    "day.baseline.caption": (
        "Reference: median of the same user's previous 14 days. The first 14 "
        "days of the period have no history to compare against and are shown "
        "uncompared."
    ),
    "day.note.a": (
        "<b>Stable routine.</b> First unlock between 07:30 and 09:00, last "
        "screen around {last_use}, no activity after 23:00 on any day of the "
        "period.<br><br>"
        "<b>Work-shaped use.</b> Weekends drop to {weekend:.0f} min against "
        "{weekday:.0f} on weekdays ({diff:.0f} min less), with "
        "{pickup_diff:.0f} fewer unlocks.<br><br>"
        "<b>Short, clean sessions.</b> Median of {session:.1f} min and "
        "{switches:.0f} app switches per screen hour, over {apps:.0f} distinct "
        "apps a day. No intervention needed."
    ),
    "day.note.b": (
        "<b>No weekend break.</b> {weekend:.0f} min at weekends against "
        "{weekday:.0f} on weekdays ({diff:+.0f}). Use spreads from 08:00 to "
        "00:00 all seven days, with the midnight band gaining weight through "
        "the month.<br><br>"
        "<b>Fragmented use.</b> Sessions of {session:.1f} min median but "
        "{switches:.0f} app switches per hour, {ratio:.1f}× user A's rate. The "
        "pattern is frequent checking, not long sessions.<br><br>"
        "<b>Active night band.</b> {night:.0f} min on average between 23:00 "
        "and 06:00, and rising. This is what generated the guardian alert."
    ),
    "day.table.expander": "See the full daily table",
    "day.table.download": "Download CSV",

    # -- the night ----------------------------------------------------------
    "night.title": "Night band · user B",
    "night.kpi.first_week": "B · late night wk 1",
    "night.kpi.last_week": "B · late night wk 4",
    "night.kpi.last_screen_first": "B · last screen wk 1",
    "night.kpi.last_screen_last": "B · last screen wk 4",
    "night.kpi.first_unlock": "B · first unlock",
    "night.kpi.sleep_window": "B · sleep window",
    "delta.times": "×{n:.0f}",
    "delta.minutes": "{n:+.0f} min",
    "night.note.drift": (
        "<b>Bedtime slides later; wake-up time does not.</b><br><br>"
        "Last screen: {end_first} in week 1, {end_last} in week 4 "
        "({end_shift:.0f} min later).<br>"
        "First unlock: {wake_first} → {wake_last} ({wake_shift:+.0f} min).<br>"
        "Window between the two: {sleep_first:.1f} h → {sleep_last:.1f} h, "
        "<b>{sleep_loss:.0f} min less rest available per night</b>.<br><br>"
        "Unlocks after midnight go from {pick_first:.1f} to {pick_last:.1f} per "
        "night. This is not one day running long: it is {pick_last:.0f} returns "
        "to the phone every night."
    ),
    "chart.night_pickups": "Unlocks after midnight",
    "night.note.user_a": (
        "<b>User A, same period:</b> 0.0 min of screen between 23:00 and 06:00 "
        "across all 30 days. Last screen at {last_use} on average, with no "
        "reopenings after that. The 23:00 cut does not penalise every profile "
        "equally: A respects it with no product intervention at all."
    ),
    "night.weight.title": "Why the night carries 20 % of the index",
    "night.weight.body": (
        "The night band carries 20 % of the index, the same as fragmentation "
        "and more than long disconnection, despite being the smallest metric "
        "in absolute terms ({night:.0f} min on average against {screen:.0f} of "
        "total screen time).<br><br>"
        "The reasoning: an hour of screen at 01:00 comes out of rest and an "
        "hour at 17:00 does not, and the room for improvement is far more "
        "reachable. Cutting two hours of daily use means changing a whole "
        "routine; moving the last screen 40 minutes earlier is one change."
    ),

    # -- where the time goes ------------------------------------------------
    "time.title": "User {user} · how the time splits",
    "tag.device_only": "device only",
    "tag.never_sent": "never sent to a guardian",
    "time.kpi.attributed": "Attributed time",
    "time.kpi.attributed.delta": "{pct:.0f} % of screen time",
    "time.kpi.apps": "Distinct apps",
    "time.kpi.domains": "Distinct domains",
    "time.kpi.whole_month": "over the whole month",
    "time.kpi.top3": "Top 3 apps",
    "time.kpi.top3.delta": "of time spent in apps",
    "time.kpi.distract": "Distraction share",
    "time.kpi.distract.delta": "social + entertainment + games",
    "chart.time.apps": "User {user} · apps by minutes",
    "chart.time.domains": "User {user} · domains by minutes",
    "chart.time.categories": "User {user} · minutes by content category",
    "time.colour.caption": (
        "Colour is the content category, the same scale as the chart below. "
        "Openings and minutes per opening are in the tooltip and the full "
        "table."
    ),
    "time.note.a": (
        "<b>Small catalogue.</b> {apps} apps in 30 days: WhatsApp, Spotify, "
        "Gmail, Maps, Phone and Calendar take up almost all of it, and the top "
        "3 accounts for {top3:.0f} % of app time.<br><br>"
        "<b>Browsing.</b> {news:.0f} % of the minutes are news sites; the rest "
        "is occasional shopping and lookups.<br><br>"
        "<b>Distraction falling.</b> Averaging {distract:.0f} %, from "
        "{first:.0f} % in week 1 to {last:.0f} % in week 4."
    ),
    "time.caption.chrome": (
        "Chrome shows {opens:.0f} openings and only {minutes:.0f} min because "
        "browser time is attributed to the domain visited, not to the browser."
    ),
    "time.note.b": (
        "<b>Spread-out use.</b> {apps} apps against user A's {apps_a}, and the "
        "top 3 holds only {top3:.0f} % of the time.<br><br>"
        "<b>Parallel messaging.</b> {messaging:,.0f} min split across WhatsApp, "
        "Messages and Telegram.<br><br>"
        "<b>Distraction share in the normal range.</b> {distract:.0f} %, "
        "against user A's {distract_a:.0f} %. The category split is not this "
        "profile's problem; the total volume and the timing are."
    ),
    "time.caption.blocked_absent": (
        "This chart only holds content that actually opened. Roblox and Clash "
        "of Clans do not appear despite 75 and 71 attempts, because the filter "
        "let 2 and 0 through respectively. The detail of blocked attempts is in "
        "\"What the phone stopped\"."
    ),
    "time.table.expander": "Full table of apps and domains",

    # -- what the phone stopped ---------------------------------------------
    "blocks.title": "User {user} · blocked attempts",
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
    "blocks.kpi.opened.delta": "of the sensitive ones",
    "chart.blocks.daily": "User {user} · blocked attempts per day",
    "chart.blocks.hour": "User {user} · blocks by hour of day",
    "table.col.week_days": "Week {week} ({days} d)",
    "blocks.note.a": (
        "<b>{total} attempts in 30 days</b>, all of them "
        "<code>SOCIAL_MEDIA</code> and <code>ENTERTAINMENT</code>. Zero "
        "sensitive content in the period.<br><br>"
        "<b>Falling trend:</b> {first:.0f} blocks in week 1, {last:.0f} in "
        "week 4. The filter steps in less and less, which suggests the opening "
        "habit has moved rather than the barrier merely holding it "
        "back.<br><br>"
        "This profile needs no action and generates no alerts."
    ),
    "blocks.note.b": (
        "<b>Ordinary distraction: {ordinary:,} attempts</b>, rising "
        "({first:.0f} → {last:.0f} per week). Mostly social and "
        "entertainment.<br><br>"
        "<b>Sensitive content: {adult} adult attempts and {gambling} gambling "
        "ones</b>, with {nudity} on-device nudity detections. All blocked; none "
        "ever opened.<br><br>"
        "<b>Shape over time: a spike, not a trend.</b> {mid} of the "
        "{sensitive} sensitive attempts ({mid_pct:.0f} %) fall in weeks 2 and "
        "3; in week 4 they drop to {week_four}.<br><br>"
        "<b>Low persistence.</b> Grouped into 10-minute bursts: 1.2 attempts "
        "on average, 3 at most. The pattern is an isolated attempt followed by "
        "giving up, not insistence on the same content. That is why this block "
        "generates no immediate guardian notification, only a weekly summary "
        "entry (see \"Alerts and nudges\")."
    ),
    "blocks.scope.title": "Scope of this data",
    "blocks.scope.body": (
        "This tab is the device-side view. App and domain names, per-object "
        "counts and exact times are transmitted to no guardian and no "
        "server.<br><br>"
        "On profiles with a guardian, what can appear in their digest is the "
        "aggregate state of the filter (<i>\"acted as usual\"</i> / "
        "<i>\"acted more than usual\"</i>) and the fact that <b>{sensitive} "
        "sensitive-content attempts were blocked and none ever opened</b>. "
        "Verified against the stream: there is no <code>URL_VISIT</code> nor "
        "<code>APP_FOREGROUND</code> with category <code>ADULT</code> or "
        "<code>GAMBLING</code> in either file."
    ),

    # -- alerts and nudges --------------------------------------------------
    "engine.title": "User {user} · month walkthrough",
    "engine.caption": (
        "Every variable the rules read, on one axis. Each series runs as a "
        "percentage of its own maximum for the period, which is what lets them "
        "be compared without a second scale: what you read is the shape and "
        "the coincidence in time, and the real value with its unit is in the "
        "tooltip. **Click the legend** to switch any series on or off. Below "
        "zero, the rail showing what the phone emitted each day. The white "
        "line is the selected day."
    ),
    "engine.slider.label": "Day of the period",
    "engine.outputs.title": "Outputs on {date}",
    "engine.channel.user": "User's screen",
    "engine.channel.guardian": "Guardian's phone",
    "engine.channel.device": "Stored on the device",
    "engine.empty": "No notifications",

    "phone.brand": "BALANCE",
    "phone.brand.guardian": "BALANCE · GUARDIAN OF {user}",
    "phone.time.summary": "09:00",
    "phone.time.guardian": "09:12",
    "phone.eyebrow.summary": "Your summary",
    "phone.eyebrow.nudge": "Night nudge",
    "phone.eyebrow.alert": "Alert",
    "phone.eyebrow.digest": "Summary",
    "phone.cta.week": "See the week",
    "phone.cta.weekly_summary": "See weekly summary",
    "phone.cta.off_until_tomorrow": "Off until tomorrow",
    "phone.cta.five_more": "5 more minutes",
    "phone.nudge.headline": (
        "That is the {reopens}th time you have opened your phone tonight."
    ),
    "phone.nudge.body": "A month ago you had already put it down by now.",

    "device.row.screen": "Screen",
    "device.row.pickups": "Unlocks",
    "device.row.night": "Late night",
    "device.row.night_end": "Last night-band screen",
    "device.row.offline": "Longest disconnection",
    "device.row.offline_start": "· started",
    "device.row.distract": "Distraction share",
    "device.row.sensitive": "Sensitive attempts",
    "device.row.blocks": "Total blocks",
    "device.row.score": "Index for the day",
    "device.row.nudges": "Nudges so far",
    "device.row.reinforcements": "Reinforcements so far",
    "device.score.value": "{score:.0f} / 100",
    "device.caption": "These figures are computed and stored on the phone.",
    "device.caption.guardian": (
        "  Only the rounded aggregate of the weekly digest reaches the guardian."
    ),

    "engine.emissions.title": "Everything the phone emitted this month",
    "engine.emissions.caption": (
        "{total} outputs over 30 days: {to_user} to the user, {to_guardian} as "
        "a guardian notification and {to_summary} as a weekly summary entry."
    ),
    "engine.emissions.none": "The phone emitted nothing in the period.",

    "engine.notifications.title": "User {user} · notifications in the period",
    "engine.kpi.guardian": "Guardian notifications",
    "engine.kpi.guardian.delta": "quota {budget}/month",
    "engine.kpi.summary": "Into weekly summary",
    "engine.kpi.summary.delta": "not notified",
    "engine.kpi.reinforcements": "Reinforcements sent",
    "engine.kpi.reinforcements.delta": "one per week at most",
    "engine.kpi.nudge_nights": "Nights with a nudge",
    "engine.kpi.nudge_nights.value": "{nudged}/{nights}",
    "engine.kpi.nudge_nights.delta": "{pct:.0f} % of nights",
    "engine.kpi.nudge_minutes": "Min after the nudge",
    "engine.kpi.nudge_minutes.delta": "{pct:.0f} % of the night total",

    "engine.guardian.title": "Notifications sent to the guardian",
    "engine.guardian.none_assigned": (
        "<b>No guardian assigned.</b> User {user} is an adult: there is no "
        "recipient to notify, so the alert rules run all the same but their "
        "output only feeds the index and the nudges on the device "
        "itself.<br><br>"
        "None of the three rules fired in the period: {night:.0f} minutes of "
        "night-band screen over 30 days and {nudged} nights with a nudge."
    ),
    "engine.guardian.none_sent": (
        "<b>None in the period.</b> User {user} fired no rule at all: "
        "{night:.0f} minutes of night-band screen over 30 days and {nudged} "
        "nights with a nudge. The guardian receives only the weekly digest, in "
        "the \"all in order\" state."
    ),
    "engine.alert.eyebrow": (
        "Notification · {date} · recipient: guardian of user {user}"
    ),
    "engine.alert.rule": (
        "<b>Rule:</b> <code>{key}</code> · active from {start} to {end} "
        "({days} days) · priority {priority:.2f}.<br><br>"
        "The rule stops holding on {end} because the rolling 14-day reference "
        "absorbs the new behaviour. The alert is issued once, on detecting the "
        "change. The absolute level stays visible in the index and the weekly "
        "digest, which use no rolling reference."
    ),
    "engine.alert.expander": "Data behind the alert (never leaves the device)",
    "engine.alert.evidence_caption": (
        "The guardian receives the notification text. These figures are "
        "computed and stay on the phone."
    ),

    "engine.positives.title": "Reinforcements sent",
    "engine.positives.eyebrow": "{date} · recipient: {recipient}",
    "engine.positives.recipient.user": "the user themselves",
    "engine.positives.recipient.guardian": "guardian of user {user}",
    "engine.positives.body": "<b>{headline}</b><br>\"{text}\"",
    "engine.positives.none": "No reinforcement in the period.",
    "engine.positives.held_expander": (
        "{n} reinforcements recorded, not notified"
    ),
    "table.col.rule": "Rule",
    "table.col.recipient": "Recipient",
    "table.col.reason": "Reason",
    "table.col.detected": "Detected",
    "table.col.priority": "Priority",

    "engine.held.title": "Held signals",
    "engine.held.none": "No signal held in the period.",

    "engine.coverage.title": "Rule coverage",
    "engine.coverage.night_drift": (
        "Median of 5 nights against the previous 14, plus the delay in the "
        "time of the last screen"
    ),
    "engine.coverage.sensitive_spike": (
        "ADULT or GAMBLING attempts over 7 days against the rate of the "
        "previous 7"
    ),
    "engine.coverage.screen_jump": (
        "Median screen time over 5 days against the previous 14"
    ),
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
        "Shown on the second reopening from {from_clock} onwards, at most once "
        "per night. The figures come from replaying the rule over the 30 days "
        "of the period."
    ),
    "engine.nudge.activation": "**User {user} · activation**",
    "engine.nudge.row.nights": "Nights evaluated",
    "engine.nudge.row.nudged": "Nights with a nudge",
    "engine.nudge.row.nudged_value": "{nudged} ({pct:.0f} %)",
    "engine.nudge.row.night_minutes": "Night minutes this month",
    "engine.nudge.row.after": "Minutes after the nudge",
    "engine.nudge.row.after_value": "{minutes:.0f} ({pct:.0f} %)",
    "engine.nudge.row.per_night": "Per nudged night",
    "engine.nudge.row.per_night_value": "{minutes:.0f} min",
    "engine.nudge.quiet.title": "**Nights without a nudge · reason**",
    "engine.nudge.note": (
        "The minutes after the nudge bound its headroom: {after:.0f} of user "
        "B's {total:.0f} night minutes ({pct:.0f} %), about {per_night:.0f} "
        "per night it appears. That is the theoretical maximum recoverable, "
        "not the expected effect.<br><br>"
        "The activation rate on user A is 0 %: the rule fires on none of their "
        "30 nights, with no per-profile configuration."
    ),

    # -- under the hood -----------------------------------------------------
    "hood.stream.title": "What is actually in the files",
    "table.col.means": "What it means",
    "event.SCREEN_ON": (
        "The screen lights up. May be a glance or the start of real use."
    ),
    "event.SCREEN_OFF": "The screen goes dark.",
    "event.USER_PRESENT": (
        "A real unlock (PIN / biometrics). This is what turns a SCREEN_ON into "
        "a pickup."
    ),
    "event.APP_FOREGROUND": (
        "An app comes to the foreground. Carries package_name and category."
    ),
    "event.URL_VISIT": (
        "A page viewed in the browser. Carries url_domain and category. Domain "
        "only, never a path."
    ),
    "event.BLOCK": (
        "An attempt stopped. The content did NOT open. Carries block_type."
    ),

    "hood.fields.title": "The eight fields, and what we do with each",
    "table.col.field": "Field",
    "table.col.field_type": "Type",
    "table.col.what_it_is": "What it is",
    "table.col.what_we_use": "What we use it for",
    "field.id.is": "Monotonic within the file, in time order.",
    "field.id.use": "Tie-breaking when sorting, nothing else.",
    "field.event_type.is": "One of the six types above.",
    "field.event_type.use": "Screen state machine, time attribution, blocks.",
    "field.timestamp.is": "Epoch milliseconds, wall clock normalised to UTC.",
    "field.timestamp.use": (
        "Everything. Day = local midnight; the night runs 23:00→06:00 the next "
        "day."
    ),
    "field.package.is": "Android package. On APP_FOREGROUND and on app BLOCKs.",
    "field.package.use": "App ranking, app switches, distinct apps.",
    "field.domain.is": "Domain only. On URL_VISIT and on site BLOCKs.",
    "field.domain.use": (
        "Domain ranking. Browser time is reassigned to the domain."
    ),
    "field.category.is": "One shared vocabulary for apps and sites.",
    "field.category.use": (
        "Minutes per category, distraction share, sensitive (ADULT/GAMBLING)."
    ),
    "field.block_type.is": "APP · URL · NUDITY. Only on BLOCK.",
    "field.block_type.use": (
        "Separates list filtering from on-device nudity detection."
    ),
    "field.keyguard.is": (
        "true on a passive SCREEN_ON, false on USER_PRESENT."
    ),
    "field.keyguard.use": "Tells a glance from a real pickup.",

    "hood.anomalies.title": "Stream anomalies and how they are handled",
    "hood.anomalies.body": (
        "<b>1 · Overlapping screen stretches.</b> 77 <code>SCREEN_ON</code> in "
        "user A and 411 in user B fire while the screen is already on, "
        "balanced later by consecutive <code>SCREEN_OFF</code>. The data does "
        "not say which OFF closes which ON, and choosing wrong changes the "
        "result in both directions: pairing as a stack gives 64.9 h for user A "
        "(+6 %, the overlap counted twice) and as a queue 56.7 h (−7 %, the "
        "trailing stretch lost).<br>"
        "The screen is modelled as a <b>depth counter</b> (ON adds, OFF "
        "subtracts; on while &gt; 0), which returns the <b>union</b> of the "
        "stretches: <b>{screen_a:.1f} h</b>. The union does not depend on the "
        "pairing chosen, and it is what \"the screen was on\" means.<br><br>"
        "<b>2 · Days truncated by the file edge.</b> User B's file ends at "
        "00:46 on 31 May. That day has 0.8 h of coverage and is excluded from "
        "averages, rankings, the heatmap and blocks; its events do still count "
        "towards the night of the 30th. Without that filter, user B's mean "
        "screen time drops from 261.8 to 253.7 min.<br><br>"
        "<b>3 · First unlock floored at 06:00.</b> With the day cutting at "
        "midnight, a day starting at 00:20 (the tail of the previous night) "
        "would register as the start of a working day. The first unlock is "
        "defined as the first one from 06:00 onwards; the small hours are "
        "counted separately.<br><br>"
        "<b>4 · Stretches crossing midnight.</b> They are split at the day "
        "boundary so daily screen time adds up to exactly that day.<br><br>"
        "<b>5 · Guards that never trigger here.</b> App or URL events with the "
        "screen off, <code>USER_PRESENT</code> with no preceding "
        "<code>SCREEN_ON</code>, and apps in the foreground for more than 45 "
        "minutes are all handled in the code and do not occur in these two "
        "files. The one anomaly that does show up is {dup_a} duplicate "
        "<code>USER_PRESENT</code> inside a single stretch in user A and "
        "{dup_b} in user B, recorded rather than dropped silently."
    ),

    "hood.derivations.title": "From event to metric",
    "table.col.how_derived": "How it is derived",
    "derive.screen_time": "Screen time",
    "derive.screen_time.how": (
        "Union of SCREEN_ON→SCREEN_OFF intervals, split at midnight."
    ),
    "derive.pickup": "Real pickup",
    "derive.pickup.how": (
        "A SCREEN_ON with a USER_PRESENT before the next ON/OFF."
    ),
    "derive.glance": "Glance",
    "derive.glance.how": (
        "A SCREEN_ON with no USER_PRESENT: the screen came on, the phone never "
        "opened."
    ),
    "derive.app_time": "Time per app",
    "derive.app_time.how": (
        "From APP_FOREGROUND to the next foreground change, BLOCK or screen "
        "off. Capped at 45 min."
    ),
    "derive.domain_time": "Time per domain",
    "derive.domain_time.how": (
        "The same, but a URL_VISIT takes the time off the browser and the "
        "domain keeps it."
    ),
    "derive.night": "Night band",
    "derive.night.how": (
        "23:00 on day D → 06:00 on day D+1. The calendar day cuts at midnight; "
        "sleep does not."
    ),
    "derive.offline": "Longest disconnection",
    "derive.offline.how": (
        "Largest screen-free gap inside the waking window (07:00–23:00), with "
        "the moment it starts."
    ),
    "derive.switch": "App switch",
    "derive.switch.how": (
        "A real foreground transition between different packages, reset each "
        "day."
    ),
    "derive.distract": "Distraction share",
    "derive.distract.how": (
        "Minutes in SOCIAL_MEDIA + ENTERTAINMENT + GAMING over attributed time."
    ),
    "derive.baseline": "Your normal",
    "derive.baseline.how": (
        "Rolling median of the same user's previous 14 days (median, not mean: "
        "one odd day should not move the bar)."
    ),

    "hood.coverage.title": "How much screen time we manage to explain",
    "hood.kpi.reconstructed": "{user} · screen reconstructed",
    "hood.kpi.attributed": "{user} · attributed to app/site",
    "hood.coverage.caption": (
        "The rest is screen-on time with no app in the foreground: lock "
        "screen, home screen and notifications. User B's {b:.0f} % against "
        "user A's {a:.0f} % is consistent with their pattern of frequent "
        "wake-ups that never open anything."
    ),

    "hood.index.title": "The index, component by component",
    "table.col.component": "Component",
    "table.col.scores_100": "Value scoring 100",
    "table.col.scores_0": "Value scoring 0",
    "table.col.weight": "Weight",
    "hood.index.note": (
        "Blocks do not score in the index. A <code>BLOCK</code> means the "
        "filter acted and the content never opened; docking points for the "
        "attempt would penalise the user for something the product already "
        "handled and would create an incentive to turn the protection off. "
        "Blocks feed the alert rules and the guardian digest, not the score."
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
    "tracked.longest_offline_h": "Longest disconnection",
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

#: Month abbreviations. Written out rather than taken from `strftime` so the
#: label does not depend on the process locale.
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

#: Weekday abbreviations, Monday first. Written out for the same reason as
#: MONTHS.
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
