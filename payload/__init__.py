"""The backend's only output: the core's frames as one typed JSON document.

This package is the whole boundary between the two halves of the project.
Python computes and hands over numbers; the TypeScript in `web/` decides what
they look like. Nothing here formats a label, builds a figure or writes markup.

    scalars.py   pandas and core objects into JSON-safe values
    profile.py   one analysis, laid out flat
    __init__.py  the document, and the finding it adds up to

The shape is declared in `web/types/` and checked two ways: `npm run
typecheck` compiles the emitted file against it, and `tests/test_payload.py`
asserts the values sit inside the declared unions. The two sides cannot drift
apart quietly.
"""

from __future__ import annotations

from analysis.pipeline import PROFILES, analyse

from .profile import profile
from .scalars import rounded


def finding(summaries: dict) -> dict:
    """What the whole month adds up to: the reveal, and its negative control."""
    b = summaries["B"]
    return {
        "night_multiple": b["night_multiple"],
        "screen_change_pct": (b["screen_last_week"] / b["screen_first_week"]
                              - 1) * 100,
        "pickups_change_pct": (b["pickups_last_week"] / b["pickups_first_week"]
                               - 1) * 100,
        "sleep_loss_min": (b["sleep_first_week_h"] - b["sleep_last_week_h"]) * 60,
        "score_drop": b["score_first_week"] - b["score_last_week"],
    }


def payload() -> dict:
    """Everything the browser is given. See `web/types/` for the shape."""
    runs = {user: analyse(user) for user in PROFILES}
    profiles = {user: profile(run) for user, run in runs.items()}
    default = next(iter(PROFILES))
    document = {
        "meta": {
            "profiles": list(PROFILES),
            "days": len(runs[default].daily),
            "events": sum(len(r.timeline.events) for r in runs.values()),
            "weeks": [int(i) for i in runs[default].weekly.index],
            "defaultProfile": default,
        },
        "finding": finding({u: p["summary"] for u, p in profiles.items()}),
        "profiles": profiles,
    }
    return rounded(document)


__all__ = ["finding", "payload", "profile"]
