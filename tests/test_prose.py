"""How much there is to read.

The budget is on prose, meaning words that were written. A short table cell
is a value the pipeline produced and no amount of editing shortens it, so
those are counted apart. A cell holding a sentence is prose: a table is not a
loophole.

The budget started at 1200, when the brief was to cut. It moved when the
brief did: every chart now carries a line explaining it, and the page opens
with a summary. The number is here to catch drift, not to hold a page that
was deliberately made longer — raise it on purpose or not at all. The test
below it, that no act may hold a third of the words, is the one guarding
shape.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "index.html"

WORD_BUDGET = 2800
DATA_CELL_WORDS = 6


def words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text) if re.search(r"[A-Za-z]", w)]


class Reader(HTMLParser):
    SKIP = {"script", "style", "title"}

    def __init__(self):
        super().__init__()
        self.prose, self.data, self.acts = [], 0, []
        self.skip, self.in_cell = 0, 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        if tag == "td":
            self.in_cell += 1
        found = dict(attrs).get("id", "")
        if tag == "section" and found.startswith("act-"):
            self.acts.append((found, len(self.prose)))

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
        if tag == "td":
            self.in_cell = max(0, self.in_cell - 1)

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_cell and len(words(data)) < DATA_CELL_WORDS:
            self.data += len(words(data))
            return
        self.prose.append(data)


@pytest.fixture(scope="module")
def page():
    if not PAGE.exists():
        pytest.skip("run `python build.py` first")
    reader = Reader()
    reader.feed(PAGE.read_text())
    return reader


def test_ui_word_count_is_under_budget(page):
    total = len(words(" ".join(page.prose)))
    assert total <= WORD_BUDGET, (
        f"{total} words of prose, budget {WORD_BUDGET} "
        f"({total / 200:.1f} min at reading pace)")


def test_no_single_act_dominates_the_read(page):
    """One act holding a third of the words is a section that got away."""
    marks = page.acts + [("end", len(page.prose))]
    per_act = {name: len(words(" ".join(page.prose[start:end])))
               for (name, start), (_, end) in zip(marks, marks[1:])}
    total = sum(per_act.values())
    worst, count = max(per_act.items(), key=lambda kv: kv[1])
    assert count <= total * 0.30, f"{worst} holds {count} of {total} words"
