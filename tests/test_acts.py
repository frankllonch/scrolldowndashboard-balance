"""The act bodies, checked against the ones Python still writes.

Like `test_figures.py`, this is a migration test: it proves the port changed
nothing it did not mean to, and it goes when `render/` does.

Two differences are deliberate and named here rather than papered over:

* **The index weight.** Python writes "25%" in act 02 and "25 %" in act 12,
  from two different format strings for the same number. The TypeScript writes
  "25 %" in both.
* **The block table's row order.** Python's `pd.crosstab` sorts categories
  alphabetically, which put Adult above Social Media in a table sitting
  directly under a chart stacked in the theme's fixed order. The TypeScript
  uses that same fixed order in both.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "index.html"
PAYLOAD = ROOT / "docs" / "payload.json"
MARKER = '<div class="act-body">'

#: (profile, act) pairs whose difference is intended. See the docstring.
EXPECTED_DIFFERENCES = {("A", "02"), ("B", "02"), ("A", "08"), ("B", "08")}


@pytest.fixture(scope="module")
def typescript() -> dict:
    if shutil.which("npx") is None:
        pytest.skip("node is not on the path")
    if not (ROOT / "node_modules").is_dir():
        pytest.skip("run `npm install` first")
    bundle = ROOT / "node_modules" / ".cache" / "dump-acts.cjs"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["npx", "esbuild", "web/tools/dump-acts.ts", "--bundle", "--format=cjs",
         "--platform=node", f"--outfile={bundle}"],
        cwd=ROOT, check=True, capture_output=True)
    built = subprocess.run(["node", str(bundle)], cwd=ROOT, check=True,
                           capture_output=True, text=True)
    return json.loads(built.stdout)


def from_page(html: str) -> dict[str, str]:
    """Each section's act body, as Python wrote it into the page."""
    out: dict[str, str] = {}
    for part in re.split(r'(?=<section[^>]*id="act-\d\d")', html):
        found = re.match(r'<section[^>]*id="act-(\d\d)"', part)
        if not found or MARKER not in part:
            continue
        body = part.split(MARKER, 1)[1].rsplit("</section>", 1)[0].rstrip()
        assert body.endswith("</div>"), found.group(1)
        out[found.group(1)] = body[: -len("</div>")]
    return out


@pytest.fixture(scope="module")
def python_acts() -> dict:
    """Both profiles' act bodies.

    The page carries the default profile's; the other's live in the payload,
    which is how the switch had something to swap in.
    """
    if not PAGE.exists() or not PAYLOAD.exists():
        pytest.skip("run `python build.py` first")
    payload = json.loads(PAYLOAD.read_text())
    default = from_page(PAGE.read_text())
    out = {}
    for user in payload["profiles"]:
        bodies = dict(default)
        bodies.update(payload["profiles"][user].get("acts", {}))
        out[user] = bodies
    return out


def normalise(html: str) -> str:
    """Whitespace between tags carries nothing, and the two sides break lines
    in different places."""
    return re.sub(r"\s+", " ", re.sub(r">\s+<", "><", html)).strip()


def test_every_act_is_built_for_both_profiles(typescript, python_acts):
    for user, bodies in typescript.items():
        assert set(bodies) == set(python_acts[user]), user


def test_the_markup_is_unchanged(typescript, python_acts):
    """Every act body identical, except the two divergences named above."""
    unexpected = []
    for user, bodies in sorted(typescript.items()):
        for act, ours in sorted(bodies.items()):
            same = normalise(python_acts[user][act]) == normalise(ours)
            if same == ((user, act) in EXPECTED_DIFFERENCES):
                unexpected.append(
                    f"{user}/{act}: {'differs' if not same else 'matches'}, "
                    f"which is not what this test expects")
    assert not unexpected, "\n".join(unexpected)


def test_the_deliberate_differences_are_only_what_was_claimed(typescript,
                                                             python_acts):
    """The two divergences are narrow. If one of them starts covering
    something else, the similarity drops and this notices."""
    import difflib
    for user, act in sorted(EXPECTED_DIFFERENCES):
        before = normalise(python_acts[user][act])
        after = normalise(typescript[user][act])
        ratio = difflib.SequenceMatcher(None, before, after).ratio()
        assert ratio > 0.9, f"{user}/{act}: similarity {ratio:.3f}"
