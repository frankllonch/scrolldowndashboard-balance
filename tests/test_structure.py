"""Budgets and boundaries. These fail loudly when the shape drifts."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

#: Files whose size is part of the design, not an accident.
BUDGETS = {
    "build.py": 105,
    "site/index.html": 200,
    "README.md": 60,
    "ARCHITECTURE.md": 120,
}

#: No file in the repo goes past this. Where a concern outgrew it, it became a
#: package or a folder whose index re-exports the same names.
CEILING = 350

#: An act over this is doing two things.
ACT_BUDGET = 280


def lines(path: Path) -> int:
    return len(path.read_text().rstrip("\n").split("\n"))


def sources() -> list[Path]:
    out = []
    for pattern in ("balance/**/*.py", "emit/**/*.py", "tests/**/*.py",
                    "web/**/*.ts", "site/css/*.css", "site/index.html",
                    "build.py"):
        out += [p for p in ROOT.glob(pattern) if p.is_file()]
    return sorted(out)


def test_no_file_passes_the_ceiling():
    over = {str(p.relative_to(ROOT)): lines(p)
            for p in sources() if lines(p) > CEILING}
    assert not over, over


@pytest.mark.parametrize("name,budget", sorted(BUDGETS.items()))
def test_file_is_within_its_budget(name, budget):
    assert lines(ROOT / name) <= budget, f"{name} is {lines(ROOT / name)} lines"


def test_no_act_exceeds_its_line_budget():
    acts = sorted((ROOT / "web" / "acts").glob("a[0-9][0-9]-*.ts"))
    assert len(acts) == 12, [p.name for p in acts]
    over = {p.name: lines(p) for p in acts if lines(p) > ACT_BUDGET}
    assert not over, over


def test_decisions_entries_are_short():
    """A decision that needs more than ten lines was commentary."""
    body, name, over = [], None, {}
    for line in (ROOT / "DECISIONS.md").read_text().split("\n"):
        if line.startswith("## "):
            if name and len([x for x in body if x.strip()]) > 10:
                over[name] = len([x for x in body if x.strip()])
            name, body = line[3:], []
        else:
            body.append(line)
    if name and len([x for x in body if x.strip()]) > 10:
        over[name] = len([x for x in body if x.strip()])
    assert not over, over


def test_the_act_registry_is_ordered_and_unique():
    """Twelve acts, in order, each with a section and a marker in the shell."""
    index = (ROOT / "web" / "acts" / "index.ts").read_text()
    listed = re.search(r"export const ACTS = \[(.+?)\];", index, re.S)
    assert listed, "no ACTS array in web/acts/index.ts"
    order = re.findall(r"a(\d\d)", listed.group(1))
    assert order == [f"{i:02d}" for i in range(1, 13)], order

    modules = sorted(p.name for p in (ROOT / "web" / "acts")
                     .glob("a[0-9][0-9]-*.ts"))
    assert [m[1:3] for m in modules] == order, modules

    shell = (ROOT / "site" / "index.html").read_text()
    for act in order:
        assert f'id="act-{act}"' in shell, f"act {act} has no section"
        assert f"<!--act:{act}-->" in shell, f"act {act} has no marker"


def test_the_core_imports_no_presentation():
    """`balance/` computes. Nothing in it knows plotly or the page exists."""
    for path in sorted((ROOT / "balance").rglob("*.py")):
        source = path.read_text()
        for banned in ("import plotly", "from plotly", "import streamlit",
                       "from render", "import render", "from emit",
                       "import emit"):
            assert banned not in source, f"{path.name} imports {banned}"


def test_the_backend_builds_no_presentation():
    """`emit/` hands over numbers. It draws nothing and words nothing."""
    for path in sorted((ROOT / "emit").glob("*.py")):
        source = path.read_text()
        for banned in ("import plotly", "from plotly", "<div", "<p ",
                       "go.Figure"):
            assert banned not in source, f"{path.name} contains {banned}"


def test_the_shell_carries_no_copy():
    """`index.html` is a skeleton. Every word in the page comes from `web/`."""
    shell = (ROOT / "site" / "index.html").read_text()
    text = re.sub(r"<[^>]*>", " ", re.sub(r"<!--.*?-->", " ", shell, flags=re.S))
    stray = [w for w in re.split(r"\s+", text) if re.search(r"[A-Za-z]", w)]
    assert not stray, f"text in the shell: {stray}"


def test_the_page_loads_one_script_and_one_stylesheet():
    shell = (ROOT / "site" / "index.html").read_text()
    scripts = re.findall(r'<script src="([^"]+)"', shell)
    assert scripts == ["vendor/plotly-cartesian.min.js", "app.js"], scripts
    sheets = re.findall(r'<link rel="stylesheet"[^>]*href="([^"]+)"', shell)
    assert [s for s in sheets if not s.startswith("http")] == ["style.css"]
