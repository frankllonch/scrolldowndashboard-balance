"""User-visible copy, keyed.

Named `copytext` and not `copy`: a top-level `copy/` package shadows the
stdlib module of that name and breaks pandas on import. See DECISIONS.md.

Two resolvers, because two syntaxes have to coexist:

    t()    prose. `{name}` placeholders, `str.format` rules.
    tpl()  plotly hover and tick templates. Plotly owns `%{...}`, so these
           interpolate with `$name` and leave every brace alone.
"""

from string import Template

from .en import DOW, MONTHS, STRINGS


class MissingCopy(KeyError):
    """A key was asked for that no catalogue entry defines."""


def _lookup(key: str) -> str:
    try:
        return STRINGS[key]
    except KeyError:
        raise MissingCopy(key) from None


def t(key: str, /, **kwargs) -> str:
    """Resolve a copy key, interpolating the numbers the frames produced."""
    return _lookup(key).format(**kwargs)


def tpl(key: str, /, **kwargs) -> str:
    """Resolve a plotly template: `$name` interpolates, `%{...}` survives."""
    return Template(_lookup(key)).substitute(**kwargs)


__all__ = ["DOW", "MONTHS", "STRINGS", "MissingCopy", "t", "tpl"]
