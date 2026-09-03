"""Copy you can find by searching for it.

Someone who wants to change a sentence they saw on the page will paste part of
it into their editor's search. That has to land in the file that writes it.

It stopped working once: the copy was wrapped at a column, which split
sentences across two string literals, so a search for anything spanning the
break found nothing. Sentences are wrapped at their own boundaries now — a
line may run long, and that is the trade — and this keeps them there.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dist" / "index.html"

#: The paragraph classes that hold prose. Headings and table cells are values
#: or single words, and nobody searches for those.
PROSE = r'<p class="(?:lede|note[^"]*|caption|chart-explain|act-next)">(.*?)</p>'

#: How many words someone would realistically paste.
RUN = 6

#: What is allowed not to match. A run reaching into `${top3Names}` cannot be
#: found — those words are the reader's own apps and were never written
#: anywhere — and that is the floor, currently around 2 %.
#:
#: This catches the copy being re-wrapped at a column, which takes the figure
#: past 20 %. It will not notice one sentence slipping across a break; that
#: costs half a percent, and a guard tight enough to see it would fail every
#: time a value-heavy sentence was added.
BUDGET = 0.03


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


@pytest.fixture(scope="module")
def page() -> str:
    if not PAGE.exists():
        pytest.skip("run `python build.py` first")
    return PAGE.read_text()


@pytest.fixture(scope="module")
def source() -> str:
    """Every TypeScript file, with inline emphasis removed: the page shows the
    words, not the `<b>` around them."""
    joined = "\n".join(p.read_text() for p in (ROOT / "web").rglob("*.ts"))
    return re.sub(r"\s+", " ", re.sub(r"</?(?:b|code|i)>", "", joined))


def test_any_phrase_on_the_page_can_be_found_in_the_source(page, source):
    unfindable, total = [], 0
    for para in re.findall(PROSE, page, re.S):
        for sentence in re.split(r"(?<=[.!?])\s+", strip_tags(para)):
            words = sentence.split()
            for i in range(len(words) - RUN + 1):
                run = " ".join(words[i:i + RUN])
                # a run holding a number came from the data, not the copy
                if re.search(r"\d", run):
                    continue
                total += 1
                if run not in source:
                    unfindable.append(run)

    assert total > 700, "the page lost most of its prose"
    share = len(unfindable) / total
    assert share <= BUDGET, (
        f"{len(unfindable)} of {total} phrases ({share:.1%}) cannot be "
        f"searched for. A sentence has been split across two literals:\n"
        + "\n".join(f"  {u!r}" for u in unfindable[:10]))
