"""Copy discipline, now that the copy is TypeScript.

Two invariants survive the move, and one does not.

* **Numbers come from the data, never from the copy.** A figure typed into a
  sentence drifts from the frames the moment anything is recalibrated. This
  reads the source text, because that is where the offence would be.
* **The engine does not give instructions.** The notification text is written
  in `balance/intelligence/`, so this still tests Python.

What went is "no user-visible string outside the catalogue". Its premise was
the split it enforced: prose in `copytext/`, keys in `render/`. An act now
holds its own words on purpose, and one file per section is the point.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COPY = sorted((ROOT / "web").rglob("*.ts"))

#: Hours of the day, the index bands, the rolling windows, and the year. These
#: are definitions, fixed in the code, not measurements read off a frame.
STRUCTURAL = {"06", "07", "08", "23", "00", "01", "17", "10", "14", "20",
              "25", "30", "40", "60", "100", "2026", "45", "15", "24", "12",
              "50"}

#: A string literal in TypeScript, single or double quoted, no interpolation.
LITERAL = re.compile(r'"([^"\\\n]{4,})"|\'([^\'\\\n]{4,})\'')


def literals(source: str) -> list[str]:
    """Every plain string in a module, comments and template literals aside.

    Template literals are excluded because that is where a value is
    interpolated: `${x.toFixed(0)} min` is the copy doing the right thing.
    """
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    source = re.sub(r"^\s*//.*$", "", source, flags=re.M)
    return [a or b for a, b in LITERAL.findall(source)]


def prose(value: str) -> bool:
    """A sentence a reader sees, rather than a selector, a key or a template."""
    if any(c in value for c in "<>{}=$#"):
        return False
    if value.startswith((".", "/", "data-")):
        return False
    words = [w for w in value.split() if re.search(r"[A-Za-z]", w)]
    return len(words) >= 4


@pytest.mark.parametrize("path", COPY, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_measurement_is_typed_into_the_copy(path: Path):
    offenders = []
    for value in literals(path.read_text()):
        if not prose(value):
            continue
        bare = re.sub(r"\d{2}:\d{2}", " ", value)         # clock times
        for number in re.findall(r"\d[\d.,]*", bare):
            trimmed = number.strip(".,")
            if len(trimmed) >= 2 and trimmed not in STRUCTURAL:
                offenders.append(f"{value[:60]!r} → {number}")
    assert not offenders, offenders


IMPERATIVE = ("you should", "try to", "we recommend", "good time to",
              "you could", "remember to", "make sure you", "consider ")


def test_the_engine_does_not_command(df_a, df_b):
    """The tone is descriptive. A recommendation slipping into a notification
    is what this catches."""
    from balance.intelligence import evaluate_alerts, evaluate_positives

    offenders = []
    for frame in (df_a, df_b):
        for signal in evaluate_alerts(frame) + evaluate_positives(frame):
            for field in ("headline", "body"):
                text = getattr(signal, field, "").lower()
                for phrase in IMPERATIVE:
                    if text.startswith(phrase) or f". {phrase}" in text:
                        offenders.append(f"{signal.key}.{field}: {phrase}")
    assert not offenders, offenders


def test_every_figure_the_page_mounts_has_an_explanation():
    """`explain()` throws for a figure with no line, so the build already
    fails. This says which figures are covered, so removing one is a visible
    decision rather than a chart quietly going bare."""
    source = (ROOT / "web" / "copy" / "explain.ts").read_text()
    keys = set(re.findall(r'^\s+"?([a-z_][a-z_.A-Z]*)"?:\s*\n?\s*"',
                          source, re.M))
    for expected in ("score_line", "night_drift", "tracked_series",
                     "category_area", "hour_heat", "day_span",
                     "week_components", "blocks_daily", "blocks_by_hour"):
        assert expected in keys, expected
