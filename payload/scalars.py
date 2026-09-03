"""Turning what pandas and the core hold into what JSON can carry.

Nothing here formats for a reader: it converts types and drops precision that
was never real. Wording a value is the frontend's job.
"""

from __future__ import annotations

import math
from datetime import date
from typing import Any

import pandas as pd


def plain(value: Any) -> Any:
    """A numpy scalar, a Timestamp or a date, as something JSON can hold.

    NaN and Infinity are not JSON. A metric that does not exist is null, never
    a zero that would quietly enter an average on the other side.
    """
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return None
    if isinstance(value, (pd.Timestamp, date)):
        return value.isoformat()[:10]
    if hasattr(value, "item"):          # numpy scalar
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def rounded(node: Any) -> Any:
    """Trim binary-float tails, once, on the way out.

    Four decimals is finer than anything the page displays. It happens here
    rather than per value so that everything derived inside this module —
    `finding()` most of all — is computed at full precision first.
    """
    if isinstance(node, dict):
        return {k: rounded(v) for k, v in node.items()}
    if isinstance(node, list):
        return [rounded(v) for v in node]
    if isinstance(node, float):
        return round(node, 4)
    return node


def rows(frame: pd.DataFrame, columns: tuple[str, ...],
         index_as: str | None = None) -> list[dict]:
    """A frame as a list of records, keeping only the declared columns.

    Selecting explicitly rather than dumping the frame is the point: a new
    intermediate column in `metrics.py` must be added here on purpose before
    it can reach the browser.
    """
    out = []
    for key, row in frame.iterrows():
        record = {} if index_as is None else {index_as: plain(key)}
        for column in columns:
            if column in record:
                continue
            record[column] = plain(row[column]) if column in frame else None
        out.append(record)
    return out


def signal(sig) -> dict:
    return {
        "key": sig.key, "day": plain(sig.day), "until": plain(sig.until),
        "decision": sig.decision, "reason": sig.reason,
        "priority": sig.priority, "tone": sig.tone,
        "headline": sig.headline, "body": sig.body,
        "evidence": {k: plain(v) for k, v in sig.evidence.items()},
    }


def nudge(n) -> dict:
    return {
        "day": plain(n.day), "fired": bool(n.fired), "at_ms": plain(n.at_ms),
        "quiet_reason": n.quiet_reason, "reopens": int(n.reopens),
        "minutes_after": plain(n.minutes_after),
        "night_minutes": plain(n.night_minutes),
    }


def snake(text: str) -> str:
    return text.replace(" ", "_")


def week_value(df: pd.DataFrame, col: str, week: int) -> float:
    return df[df["week"] == week][col].mean()
