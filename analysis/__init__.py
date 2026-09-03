"""
From a device event log to product decisions.

The event file is the system of record: immutable, the single source of truth.
Everything in this package is derived data, computed as a pure, deterministic
function of that log.

    events  →  metrics  →  score  →  intelligence
     layer 0    layer 1    layer 2      layer 3

    events.py        screen stretches, real unlocks, time attribution
    windows.py       what counts as a day, a night and waking hours
    metrics.py       one row per day, one per week
    score.py         the 0 to 100 index: five components, weighted
    intelligence/    what to say, when to stay quiet, and to whom

Nothing here draws anything or knows a page exists. Two adapters read it:
`run.py` for the command line, and `payload/` for the browser.

See `ARCHITECTURE.md` for the full map and for how to make the usual changes.
"""

__version__ = "1.0.0"
