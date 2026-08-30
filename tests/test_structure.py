"""Budgets and boundaries. These fail loudly when the shape drifts."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

#: Files whose size is part of the design, not an accident.
BUDGETS = {
    "build.py": 80,
    "site/app.js": 300,
    "site/index.html": 200,
    "README.md": 60,
    "ARCHITECTURE.md": 120,
}

ACT_BUDGET = 120


def lines(path: Path) -> int:
    return len(path.read_text().rstrip("\n").split("\n"))


def test_no_act_exceeds_its_line_budget():
    """An act over 120 lines is doing two things."""
    acts = sorted(ROOT.glob("render/acts/a*.py"))
    assert len(acts) == 13, [p.name for p in acts]
    over = {p.name: lines(p) for p in acts if lines(p) > ACT_BUDGET}
    assert not over, over


@pytest.mark.parametrize("name,budget", sorted(BUDGETS.items()))
def test_file_is_within_its_budget(name, budget):
    assert lines(ROOT / name) <= budget, f"{name} is {lines(ROOT / name)} lines"


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
    from copytext import STRINGS
    from render.acts import ACTS

    ids = [a.id for a in ACTS]
    assert ids == sorted(ids), "acts are out of order"
    assert len(set(ids)) == len(ids), "duplicate act id"
    assert ids == [f"{i:02d}" for i in range(1, 14)], ids

    parts = [a.part for a in ACTS]
    assert parts == sorted(parts), "the three parts are interleaved"
    assert set(parts) == {1, 2, 3}

    shell = (ROOT / "site" / "index.html").read_text()
    for act in ACTS:
        assert callable(act.builder), act.id
        assert act.eyebrow in STRINGS and act.title in STRINGS, act.id
        assert f'id="act-{act.id}"' in shell, f"act {act.id} has no section"
        assert f"<!--act:{act.id}-->" in shell, f"act {act.id} has no marker"


def test_the_core_imports_no_presentation():
    """`balance/` computes. Nothing in it knows plotly or `render/` exists."""
    for path in sorted((ROOT / "balance").glob("*.py")):
        source = path.read_text()
        for banned in ("import plotly", "from plotly", "import streamlit",
                       "from render", "import render"):
            assert banned not in source, f"{path.name} imports {banned}"


# ---------------------------------------------------------------------------
# Copy discipline
# ---------------------------------------------------------------------------

#: Where a user-visible string would be a bug. `figures.py` is included: its
#: axis titles and series names are read by people too.
RENDER_FILES = sorted(
    list((ROOT / "render").rglob("*.py")) + [ROOT / "build.py"])

#: A literal that looks like a sentence rather than markup or an identifier.
def is_prose(value: str) -> bool:
    if any(c in value for c in "<>{}=$_"):
        return False
    if value.strip().startswith(("#", ".", "/")):
        return False
    words = [w for w in re.split(r"\s+", value.strip()) if re.search(r"[A-Za-z]", w)]
    return len(words) >= 3


def test_no_user_visible_string_outside_copy():
    """Prose lives in the catalogue. The renderer only knows keys."""
    offenders = []
    for path in RENDER_FILES:
        tree = ast.parse(path.read_text())
        # `get_docstring` returns cleaned text, which never matches the raw
        # node, so the nodes themselves are what gets excluded.
        exempt = set()
        for holder in ast.walk(tree):
            if isinstance(holder, (ast.Module, ast.FunctionDef,
                                   ast.AsyncFunctionDef, ast.ClassDef)):
                first = holder.body[0] if holder.body else None
                if (isinstance(first, ast.Expr)
                        and isinstance(first.value, ast.Constant)
                        and isinstance(first.value.value, str)):
                    exempt.add(id(first.value))
            # `nudge_summary` is keyed by English phrases, so a lookup like
            # ns["nights with a nudge"] is an API call, not a sentence.
            if isinstance(holder, ast.Subscript):
                exempt.add(id(holder.slice))
            # messages for whoever is running the build, not for a reader
            if isinstance(holder, ast.Raise):
                for inner in ast.walk(holder):
                    exempt.add(id(inner))
            # An ALL_CAPS constant is configuration. Copy never lives in one:
            # it lives in the catalogue, which this scan does not cover.
            if isinstance(holder, ast.Assign):
                names = [t.id for t in holder.targets if isinstance(t, ast.Name)]
                if names and all(n.isupper() for n in names):
                    for inner in ast.walk(holder.value):
                        exempt.add(id(inner))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if id(node) in exempt or not is_prose(node.value):
                continue
            offenders.append(f"{path.relative_to(ROOT)}:{node.lineno} "
                             f"{node.value[:52]!r}")
    assert not offenders, offenders


def test_the_shell_and_the_script_carry_no_copy():
    """`index.html` is a skeleton and `app.js` is behaviour. Neither writes."""
    shell = (ROOT / "site" / "index.html").read_text()
    text = re.sub(r"<[^>]*>", " ", re.sub(r"<!--.*?-->", " ", shell, flags=re.S))
    stray = [w for w in re.split(r"\s+", text) if re.search(r"[A-Za-z]", w)]
    assert not stray, f"text in the shell: {stray}"

    script = (ROOT / "site" / "app.js").read_text()
    script = re.sub(r"/\*.*?\*/|//[^\n]*", " ", script, flags=re.S)
    offenders = [m for m in re.findall(r'"([^"\\\n]{4,})"|\'([^\'\\\n]{4,})\'', script)
                 for m in m if m and is_prose(m)]
    assert not offenders, offenders
