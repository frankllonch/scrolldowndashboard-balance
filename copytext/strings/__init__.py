"""The catalogue, in four parts.

Split by what the words are for, not by size: what the metrics are called,
what the phone says, what a figure is labelled with, and what the scroll
itself says.
"""

from . import engine, figures, product, scroll

#: Merged in a fixed order. A key defined twice is a mistake, so it raises
#: rather than letting the last one win.
STRINGS: dict[str, str] = {}
for part in (product, engine, figures, scroll):
    clash = STRINGS.keys() & part.STRINGS.keys()
    if clash:
        raise ValueError(f"copy key defined twice: {sorted(clash)}")
    STRINGS |= part.STRINGS

__all__ = ["STRINGS"]
