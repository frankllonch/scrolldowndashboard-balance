"""Display formatting. Every string it returns comes from the catalogue."""

from __future__ import annotations

import math

import pandas as pd

from copytext import MONTHS, t


def date(d) -> str:
    """Short date, locale-independent."""
    return t("fmt.date", day=d.day, month=MONTHS[d.month - 1])


def clock(h) -> str:
    """Shifted-axis hour (24 to 28 = small hours) to HH:MM."""
    if h is None or pd.isna(h):
        return t("value.no_use")
    return t("fmt.clock", h=int(h % 24), m=int(h % 1 * 60))


def hm(minutes: float) -> str:
    h, m = divmod(int(round(minutes)), 60)
    return t("fmt.hm", h=h, m=m) if h else t("fmt.m", m=m)


def week_value(df: pd.DataFrame, col: str, week: int, how: str = "mean") -> float:
    return getattr(df[df["week"] == week][col], how)()


def maybe(value, spec: str = ".0f", unit: str = "") -> str:
    """Format a number that may not exist.

    User A never uses the phone between 23:00 and 06:00, so their night-band
    metrics are genuinely absent rather than zero. Printing "nan h" would be
    a bug; printing 0 would be a claim the data does not make.
    """
    if value is None or not math.isfinite(float(value)):
        return t("value.no_use")
    return f"{value:{spec}} {unit}".strip()
