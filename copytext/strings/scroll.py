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

    # -- act 01 · cover -----------------------------------------------------
    "cover.standfirst": (
        "One month of usage by two very different users, who used it better? "
    ),
    "cover.stat.profiles": "profiles",
    "cover.stat.events": "events",
    "cover.stat.days": "days each",
    "cover.scroll": "Scroll",

    # -- act 02 · A single wellbeing score -------------------------------------
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
        "worth setting. What happens at night band is ×{night:.0f}."
    ),
}
