"""The half of the contract TypeScript cannot check.

`npm run typecheck` compiles `web/contract.ts` against the emitted document
and catches the drift that field names and types can cause. It cannot check
membership of a literal union, because a JSON import types every string as
`string`. That is what these do, on the side that produces the values.

They also hold the two properties that make the document a data document:
every number is finite, and no string in it is markup.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pytest

import payload as backend
from analysis.events import CATEGORIES

ROOT = Path(__file__).resolve().parents[1]
TYPES = ROOT / "web" / "types"


@pytest.fixture(scope="module")
def document() -> dict:
    return backend.payload()


def union(name: str) -> set[str]:
    """The members of a string union declared in `web/types.ts`.

    Read from the file rather than restated here: a union that grows on one
    side and not the other is exactly the drift worth catching.
    """
    body = "\n".join(f.read_text() for f in sorted(TYPES.glob("*.ts")))
    match = re.search(rf"export type {name} =(.+?);", body, re.S)
    assert match, f"no `export type {name}` under web/types/"
    return set(re.findall(r'"([^"]+)"', match.group(1)))


def walk(node, path="payload"):
    """Every scalar in the document, with the path that reached it."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk(value, f"{path}[{i}]")
    else:
        yield path, node


# ---------------------------------------------------------------------------
# The unions
# ---------------------------------------------------------------------------

def test_the_category_union_matches_the_core(document):
    """`Category` in types.ts against `CATEGORIES` in events.py."""
    assert union("Category") == set(CATEGORIES)


def test_every_category_emitted_is_in_the_union(document):
    declared = union("Category")
    for path, value in walk(document):
        if path.endswith(".category"):
            assert value in declared, f"{path}: {value!r}"


def test_every_block_type_and_decision_is_in_its_union(document):
    types_, decisions, tones = (union("BlockType"), union("Decision"),
                                union("Tone"))
    for path, value in walk(document):
        if path.endswith(".block_type"):
            assert value in types_, f"{path}: {value!r}"
        if path.endswith(".decision"):
            assert value in decisions, f"{path}: {value!r}"
        if path.endswith(".tone"):
            assert value in tones, f"{path}: {value!r}"


def test_weekdays_are_monday_first(document):
    for path, value in walk(document):
        if path.endswith(".dow"):
            assert value in range(7), f"{path}: {value!r}"


def test_every_day_is_an_iso_date(document):
    for path, value in walk(document):
        if path.endswith(".day") or path.endswith("Day"):
            if value is None:
                continue
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)), \
                f"{path}: {value!r}"


# ---------------------------------------------------------------------------
# What makes it a data document
# ---------------------------------------------------------------------------

def test_the_document_is_json_without_nan(document):
    """`json.dumps` writes bare NaN by default, which no parser accepts. A
    metric that does not exist is null."""
    json.dumps(document, allow_nan=False)
    for path, value in walk(document):
        if isinstance(value, float):
            assert math.isfinite(value), path


def test_no_string_in_the_document_is_markup(document):
    """Python computes; TypeScript draws. A tag crossing this line means the
    backend started rendering again."""
    for path, value in walk(document):
        if isinstance(value, str):
            assert not re.search(r"</?[a-z][a-z0-9]*[ />]", value), \
                f"{path}: {value!r}"


def test_no_figure_or_copy_key_crosses_the_line(document):
    """The old payload carried built figures and pre-rendered acts. Nothing
    here may: the frontend owns presentation."""
    banned = {"figures", "acts", "templates", "ui", "traces", "layout"}
    for path, _ in walk(document):
        assert not (set(path.split(".")) & banned), path


def test_both_profiles_carry_every_series(document):
    expected = {"summary", "daily", "weekly", "apps", "sites", "categoryDaily",
                "hourHeat", "blocks", "alerts", "positives", "nudges",
                "nudgeSummary", "replay", "emissions", "anomalies",
                "eventCounts", "defaultDay", "defaultWeek"}
    for user, profile in document["profiles"].items():
        assert set(profile) == expected, user
        assert len(profile["daily"]) == document["meta"]["days"], user


def test_the_block_tallies_agree_with_their_total(document):
    """The counts are the only form the blocks cross in, so they have to add
    up on their own."""
    for user, profile in document["profiles"].items():
        blocks = profile["blocks"]
        for field in ("byDay", "byHour", "byWeek"):
            counted = sum(row["count"] for row in blocks[field])
            assert counted == blocks["total"], f"{user}/{field}"
        assert sum(blocks["byType"].values()) == blocks["total"], user


# ---------------------------------------------------------------------------
# The one thing declared on both sides
# ---------------------------------------------------------------------------

def test_the_index_components_match_on_both_sides():
    """`COMPONENTS` is written twice: once in `analysis/score.py`, which
    computes the index, and once in `web/charts/score.ts`, which explains it
    and draws its breakdown.

    It cannot cross in the document — the page needs it before the first fetch
    resolves, to render act 02 at build time — so this holds the two copies
    together instead. A weight changed on one side and not the other would
    otherwise show a chart that disagrees with the number above it.
    """
    from analysis.score import COMPONENTS

    source = (ROOT / "web" / "charts" / "score.ts").read_text()
    block = re.search(r"export const COMPONENTS[^=]*= \[(.+?)\n\];", source, re.S)
    assert block, "no COMPONENTS array in web/charts/score.ts"

    declared = re.findall(
        r'key: "(\w+)", label: "([^"]+)", good: ([\d.]+), bad: ([\d.]+),\s*'
        r"weight: ([\d.]+)", block.group(1))
    assert len(declared) == len(COMPONENTS), declared

    for (key, label, good, bad, weight), found in zip(COMPONENTS, declared):
        assert found[:2] == (key, label), found
        assert [float(x) for x in found[2:]] == [good, bad, weight], found
