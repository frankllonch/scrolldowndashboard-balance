"""The backend's only output: the core's frames as one typed JSON document.

This package is the whole boundary between the two halves of the project.
Python computes and hands over numbers; the TypeScript in `web/` decides what
they look like. Nothing here formats a label, builds a figure or writes markup.

    scalars.py   pandas and core objects into JSON-safe values
    profile.py   one profile's frames, laid out flat
    __init__.py  the document, and the command that writes it

The shape is declared in `web/types/` and checked two ways: `npm run
typecheck` compiles the emitted file against it, and `tests/test_emit.py`
asserts the values sit inside the declared unions. The two sides cannot drift
apart quietly.
"""

from __future__ import annotations

from .profile import DATA, compute, profile
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
    """Everything the browser is given. See `web/types.ts` for the shape."""
    bundles = {user: compute(user) for user in DATA}
    profiles = {user: profile(user, bundle)
                for user, bundle in bundles.items()}
    default = next(iter(DATA))
    document = {
        "meta": {
            "profiles": list(DATA),
            "days": len(bundles[default]["df"]),
            "events": sum(len(b["timeline"].events) for b in bundles.values()),
            "weeks": [int(i) for i in bundles[default]["weekly"].index],
            "defaultProfile": default,
        },
        "finding": finding({u: p["summary"] for u, p in profiles.items()}),
        "profiles": profiles,
    }
    return rounded(document)


__all__ = ["DATA", "compute", "finding", "payload", "profile"]
