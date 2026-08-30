"""
Balance · from a device event log to product decisions.

The event file is the system of record: immutable, the single source of truth.
Everything in this package is derived data, computed as a pure, deterministic
function of that log.

    events  →  metrics  →  score  →  intelligence
     layer 0    layer 1    layer 2      layer 3

None of those four layers imports plotly. `run.py` (CLI) and `render/` (the
page) are two adapters over the same core.

See `ARCHITECTURE.md` for the full map and for how to make the usual changes.
"""

__version__ = "1.0.0"
