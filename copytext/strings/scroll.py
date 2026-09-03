"""Copy belonging to the scroll: its parts, its acts, its headings.

Part of the catalogue. See copytext/en.py for how the parts come together.
"""

STRINGS: dict[str, str] = {
    # -- the scroll: parts and act headings ---------------------------------
    "part.1": "Setup",
    "part.2": "One person's month",
    "part.3": "The analysis",

    "act.01.eyebrow": "Balance Phone · May 2026",
    "act.01.title": "Balance board",
    "act.02.eyebrow": "Both profiles, thirty days",
    "act.02.title": "A single wellbeing score",
    "act.03.eyebrow": "Pick one",
    "act.03.title": "Choose a profile",
    "act.04.eyebrow": "Week by week",
    "act.04.title": "The week's summary",
    "act.05.eyebrow": "Hour by hour",
    "act.05.title": "A day in the life",
    "act.06.eyebrow": "23:00 to 06:00",
    "act.06.title": "What happens at night",
    "act.07.eyebrow": "Apps, domains, categories",
    "act.07.title": "Where your time goes",
    "act.08.eyebrow": "The filter",
    "act.08.title": "What the phone stopped",
    "act.09.eyebrow": "Alerts, nudges, reinforcements",
    "act.09.title": "The intelligence acting",
    "act.10.eyebrow": "The reveal",
    "act.10.title": "The finding",
    "act.11.eyebrow": "The negative control",
    "act.11.title": "What a screen-time rule would have missed",
    "act.12.eyebrow": "Schema and derivations",
    "act.12.title": "Under the hood",

    # -- the bridge at the close of each act ---------------------------------
    # One line handing the reader to the next scene. The last act has none:
    # nothing follows it, and page.py leaves the slot empty.
    "act.01.next": "First, one number for each of them.",
    "act.02.next": (
        "Two months, two very different shapes. Pick one and read it from the "
        "inside."
    ),
    "act.03.next": "Start where the shape is easiest to see: a week at a time.",
    "act.04.next": (
        "Now zoom in. A week is thirty days seen from a distance — here is a "
        "single day."
    ),
    "act.05.next": (
        "The days look ordinary enough. So look at the hours the days do not "
        "cover."
    ),
    "act.06.next": "Now you know when. The next question is what.",
    "act.07.next": "That is what got through. Here is what did not.",
    "act.08.next": (
        "The phone knew all of this. Here is what it decided to say about it, "
        "and what it kept to itself."
    ),
    "act.09.next": (
        "That is the whole month, and everything the phone did with it. Now "
        "the finding."
    ),
    "act.10.next": (
        "One obvious objection: surely a plain screen-time rule would have "
        "caught this too?"
    ),
    "act.11.next": (
        "Everything above comes from eight fields in a log. Here is how."
    ),

    # -- act 01 · cover -----------------------------------------------------
    "cover.standfirst": (
        "Balance makes a phone that helps people build a healthier "
        "relationship with their device — it blocks distraction, understands "
        "how someone actually uses their phone, and helps keep younger users "
        "safer online. Not a dumbphone, not anti-tech: technology that serves "
        "your life instead of hijacking it."
    ),
    "cover.purpose": (
        "This dashboard takes in the raw behavioural output of two Balance "
        "Phones, with two very different users, across the whole of May 2026. "
        "The goal is to turn that data into meaning and answer one question: "
        "<b>so what?</b>"
    ),

    # -- act 01 · the summary up front --------------------------------------
    "summary.title": "The short version",
    "summary.1.label": "Two adults, same phone, very different months",
    "summary.1.body": (
        "A scores {a_score:.0f} out of 100 and barely moves all month. B "
        "starts at {b_first:.0f} and ends at {b_last:.0f}. Everything below is "
        "the story of those {drop:.0f} points."
    ),
    "summary.2.label": "It is not that B is on the phone more",
    "summary.2.body": (
        "B's screen time only moves {screen:+.0f} % over the month. What "
        "moves is <b>when</b>: late-night use multiplies by {night:.0f}, "
        "bedtime slides from {bed_first} to {bed_last}, and the alarm does "
        "not move. That is {sleep:.0f} minutes of sleep a night, gone."
    ),
    "summary.3.label": "The filter worked, and one day it did not",
    "summary.3.body": (
        "B's phone blocked {blocks:,} attempts, {sensitive} of them adult or "
        "gambling, and none of it ever opened. Except on {outage}, when the "
        "filter went quiet for about {hours:.0f} hours and everything it had "
        "been holding back walked straight in."
    ),
    "cover.stat.profiles": "profiles",
    "cover.stat.events": "events",
    "cover.stat.days": "days each",
    "cover.scroll": "Scroll",

    # -- act 02 · A single wellbeing score -------------------------------------
    "overview.lede": (
        "One month, thirty days of raw on-device events, for two different "
        "people."
    ),
    "overview.person.A": (
        "Likely an adult with a stable relationship with their phone. "
        "WhatsApp, Spotify and the news fill most of their days, consistent "
        "throughout the whole month."
    ),
    "overview.person.B": (
        "Also an adult, and on the surface not that different: WhatsApp, "
        "Spotify, Maps, the papers, Kindle. What sets this month apart is "
        "that the filter is switched on, it stops {blocks:,} attempts, and "
        "the nights get later every week."
    ),
    "overview.hook": (
        "A stays constant throughout the month, whilst B drops {drop:.0f} "
        "points. We will see why below."
    ),
    "profile.card.eyebrow": "User {user}",

    # -- act 02 · what the index actually is ---------------------------------
    "score.explain.title": "What the wellbeing score is",
    "score.explain.body": (
        "It is a compound index: five components, each scored 0 to 100 "
        "against fixed bands, then weighted into one number a day. Nothing "
        "here is scored against your own past — otherwise a steady six hours "
        "a day would score 100 for being steady."
    ),
    "score.explain.note": (
        "Two things the names get asked about. <b>Fragmentation</b> is not "
        "about how many apps you use — it counts how many times a day you "
        "pick the phone up: {frag_good} unlocks scores 100, {frag_bad} scores "
        "0. And <b>intent</b> is how distraction is measured: the share of "
        "your attributed time that went to social, entertainment or gaming. "
        "Opening thirty apps for two minutes each is not distraction by this "
        "definition; one hour of TikTok is."
    ),
    "score.explain.blocks": (
        "Blocked attempts do not score at all. A block means the phone did "
        "its job and nothing opened; docking you for it would charge you for "
        "the product working, and would reward switching the filter off."
    ),
    "table.col.scoring": "Weight",

    # -- act 03 · choose a profile ------------------------------------------
    "fork.lede": "Both months are here. Read one, then the other.",
    "fork.sketch.A": (
        "Likely an adult with a stable relationship with their phone. "
        "WhatsApp, Spotify and the news fill most of their days, consistent "
        "across the whole month."
    ),
    "fork.sketch.B": (
        "Also an adult, and also mostly WhatsApp, Spotify, Maps and the papers"
        "— but with a more erratic pattern. A lot of tries to acces blocked sites. "
        "The days hold steady. The nights slide and sleep is lost."
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
        "worth setting. What happens at night band is ×{night:.0f}."
    ),
}
