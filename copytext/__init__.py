"""User-visible copy, keyed.

Named `copytext` and not `copy`: a top-level `copy/` package shadows the
stdlib module of that name and breaks pandas on import. See DECISIONS.md.
"""

from .en import MONTHS, STRINGS


class MissingCopy(KeyError):
    """A key was asked for that no catalogue entry defines."""


def t(key: str, /, **kwargs) -> str:
    """Resolve a copy key, interpolating the numbers the frames produced."""
    try:
        template = STRINGS[key]
    except KeyError:
        raise MissingCopy(key) from None
    return template.format(**kwargs)


__all__ = ["MONTHS", "STRINGS", "MissingCopy", "t"]
