"""Every user-visible string in the product, keyed.

Numbers are never written here as literals: they arrive as format arguments
from the frames, so a copy edit can never move a published figure.

The strings themselves live in `copytext/strings/`, split by what they are
for. This module is where they come together, with the calendar names.
"""

from .strings import STRINGS

#: Month abbreviations. Written out rather than taken from `strftime` so the
#: label does not depend on the process locale.
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

#: Weekday abbreviations, Monday first. Written out for the same reason as
#: MONTHS.
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

__all__ = ["DOW", "MONTHS", "STRINGS"]
