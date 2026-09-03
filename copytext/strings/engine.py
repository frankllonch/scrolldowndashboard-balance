"""What the phone says, to whom, and how it is explained.

Part of the catalogue. See copytext/en.py for how the parts come together.
"""

STRINGS: dict[str, str] = {
    # -- alerts and nudges --------------------------------------------------
    "engine.caption": (
        "Every variable the rules read, each as a share of its own maximum so "
        "the shapes compare. The rail below zero is what the phone emitted."
    ),
    "engine.slider.label": "Day of the period",
    "engine.outputs.title": "Outputs on {date}",
    "engine.channel.user": "User's screen",
    "engine.channel.device": "On the device",
    "engine.empty": "No notifications",

    "phone.brand": "BALANCE",
    "phone.time.summary": "09:00",
    "phone.time.alert": "09:12",
    "phone.eyebrow.summary": "Your summary",
    "phone.eyebrow.nudge": "Night nudge",
    "phone.eyebrow.alert": "Alert",
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
    "device.caption": "Computed and kept on the phone. None of it leaves.",

    "engine.emissions.title": "Everything the phone emitted this month",
    "engine.emissions.none": "The phone emitted nothing in the period.",

    "engine.kpi.alerts": "Alerts sent",
    "engine.kpi.alerts.delta": "quota {budget}/month",
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
}
