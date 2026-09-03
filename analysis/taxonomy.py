"""What the stream calls OTHER, and what it actually is.

The device labels a third of user A's day and a fifth of user B's `OTHER`,
which is not a finding, it is a gap. Gmail, Maps, the dialer and the calendar
are not unclassifiable; they were simply never classified.

The event file is the system of record and is never edited. This is a
refinement applied on read: it only ever moves something out of `OTHER`, so
no figure computed from a category the stream did assert can move because of
it. Nothing here enters `DISTRACTING`, so the index is untouched.
"""

from __future__ import annotations

#: package or domain -> the category it belongs to
REFINED = {
    # Written to a person. A voice call is a different thing and gets its own
    # category, or nearly half the day disappears into one bar.
    "com.google.android.gm": "MESSAGING",
    "com.microsoft.office.outlook": "MESSAGING",

    "com.google.android.dialer": "CALLS",

    "com.google.android.apps.maps": "NAVIGATION",

    "com.google.android.calendar": "PRODUCTIVITY",
    "com.google.android.keep": "PRODUCTIVITY",

    "chatgpt.com": "AI_TOOLS",
    "openai.com": "AI_TOOLS",

    "wikipedia.org": "REFERENCE",
    "google.com": "REFERENCE",

    "com.amazon.kindle": "LEARNING",
    "com.duolingo": "LEARNING",
}


def refine(key: str | None, category: str | None) -> str:
    """The category for one app or domain.

    A label the stream asserted always wins: this fills a gap, it does not
    overrule the device. `com.android.chrome` stays `OTHER` on purpose, since
    browser time is reassigned to the domain visited and what is left is the
    container itself.
    """
    if category and category != "OTHER":
        return category
    return REFINED.get(key or "", "OTHER")
