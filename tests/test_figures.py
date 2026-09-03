"""The port, checked rather than eyeballed.

Every figure is built twice — by the Python builders in `render/figures/` and
by the TypeScript in `web/charts/` — and the two are compared trace by trace.

This is a migration test. It exists to prove the port did not change a single
number, and it goes when `render/` does: at that point there is nothing left
to compare against, and `tests/test_emit.py` plus the type check are what hold
the line.
"""

from __future__ import annotations

import base64
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "docs" / "payload.json"

#: How plotly writes a numpy array into JSON.
DTYPES = {"f8": "<f8", "f4": "<f4", "i8": "<i8", "i4": "<i4", "i2": "<i2",
          "i1": "|i1", "u8": "<u8", "u4": "<u4", "u2": "<u2", "u1": "|u1"}

#: Both sides round: Python at four decimals on the way out of `emit`, and
#: `toFixed` in a few labels. Two parts in a thousand is well inside anything
#: the page displays and well outside a real disagreement.
TOLERANCE = 2e-3


def decode(value):
    """A plotly array, base64 or plain, as a list."""
    if isinstance(value, dict) and "bdata" in value:
        raw = np.frombuffer(base64.b64decode(value["bdata"]),
                            dtype=DTYPES[value["dtype"]])
        if value.get("shape"):
            raw = raw.reshape([int(x) for x in str(value["shape"]).split(",")])
        return raw.tolist()
    return value


def clean(seq):
    seq = decode(seq)
    if seq is None:
        return None
    return [None if isinstance(x, float) and not math.isfinite(x) else x
            for x in seq]


def close(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= TOLERANCE * max(1.0, abs(a), abs(b))
    return str(a)[:10] == str(b)[:10]


@pytest.fixture(scope="module")
def typescript() -> dict:
    """Every figure, built by the TypeScript."""
    if shutil.which("npx") is None:
        pytest.skip("node is not on the path")
    if not (ROOT / "node_modules").is_dir():
        pytest.skip("run `npm install` first")
    bundle = ROOT / "node_modules" / ".cache" / "dump-figures.cjs"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["npx", "esbuild", "web/tools/dump-figures.ts", "--bundle",
         "--format=cjs", "--platform=node", f"--outfile={bundle}"],
        cwd=ROOT, check=True, capture_output=True)
    built = subprocess.run(["node", str(bundle)], cwd=ROOT, check=True,
                           capture_output=True, text=True)
    return json.loads(built.stdout)


@pytest.fixture(scope="module")
def python_figures() -> dict:
    """Every figure, as the old payload carries it."""
    if not PAYLOAD.exists():
        pytest.skip("run `python build.py` first")
    payload = json.loads(PAYLOAD.read_text())
    out = dict(payload["figures"])
    for user, profile in payload["profiles"].items():
        for key, figure in profile["figures"].items():
            out[f"{user}::{key}"] = figure
    return out


def matching(python_figures: dict, user: str, key: str):
    """A figure keyed per profile, or the shared one both profiles show."""
    return python_figures.get(f"{user}::{key}") or python_figures.get(key)


def test_every_figure_exists_on_both_sides(typescript, python_figures):
    built = {full.split("/", 1)[1] for full in typescript}
    expected = {k.split("::", 1)[-1] for k in python_figures}
    assert built == expected


def test_every_trace_carries_the_same_numbers(typescript, python_figures):
    problems = []
    for full, ours in sorted(typescript.items()):
        user, key = full.split("/", 1)
        theirs = matching(python_figures, user, key)
        assert theirs is not None, full
        if len(theirs["data"]) != len(ours["data"]):
            problems.append(f"{full}: {len(theirs['data'])} traces against "
                            f"{len(ours['data'])}")
            continue
        for i, (was, now) in enumerate(zip(theirs["data"], ours["data"])):
            for axis in ("x", "y"):
                before, after = clean(was.get(axis)), clean(now.get(axis))
                if before is None and after is None:
                    continue
                if before is None or after is None or len(before) != len(after):
                    problems.append(f"{full}: trace {i} {axis} does not line up")
                    continue
                for j, (a, b) in enumerate(zip(before, after)):
                    if not close(a, b):
                        problems.append(f"{full}: trace {i} {axis}[{j}] "
                                        f"{a!r} became {b!r}")
                        break
    assert not problems, "\n".join(problems[:12])


def test_every_figure_keeps_its_title_and_surface(typescript, python_figures):
    problems = []
    for full, ours in sorted(typescript.items()):
        user, key = full.split("/", 1)
        theirs = matching(python_figures, user, key)
        was = (theirs.get("layout", {}).get("title") or {}).get("text")
        now = (ours.get("layout", {}).get("title") or {}).get("text")
        if was != now:
            problems.append(f"{full}: title {was!r} became {now!r}")
        if theirs.get("surface") != ours.get("surface"):
            problems.append(f"{full}: surface {theirs.get('surface')!r} "
                            f"became {ours.get('surface')!r}")
    assert not problems, "\n".join(problems[:12])


def test_every_trace_keeps_its_name_and_colour(typescript, python_figures):
    """Identity is carried by name and hue, so a series that quietly changed
    either is a series the reader would follow to the wrong conclusion."""
    problems = []
    for full, ours in sorted(typescript.items()):
        user, key = full.split("/", 1)
        theirs = matching(python_figures, user, key)
        for i, (was, now) in enumerate(zip(theirs["data"], ours["data"])):
            if was.get("name") != now.get("name"):
                problems.append(f"{full}: trace {i} name {was.get('name')!r} "
                                f"became {now.get('name')!r}")
            for where in ("line", "marker"):
                before = (was.get(where) or {}).get("color")
                after = (now.get(where) or {}).get("color")
                if isinstance(before, str) and isinstance(after, str) \
                        and before.lower() != after.lower():
                    problems.append(f"{full}: trace {i} {where} colour "
                                    f"{before} became {after}")
    assert not problems, "\n".join(problems[:12])
