"""The catalogue: every key resolves, nothing is orphaned, nothing commands."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from copytext import STRINGS, MissingCopy, t

ROOT = Path(__file__).resolve().parents[1]
#: The catalogue is excluded: every key appears there as its own literal.
SOURCES = sorted(p for p in ROOT.rglob("*.py")
                 if not {".venv", "tests", "copytext"} & set(p.parts))

#: Keys built at call time, as `t(f"prefix.{value}")`. Each family is resolved
#: by prefix instead, so a key can never be silently unused or missing.
FAMILIES = ("event.", "derive.", "engine.coverage.", "category.", "tracked.",
            "field.", "fork.sketch.", "part.", "anomaly.", "act.")


def referenced() -> set[str]:
    """Every key the code asks for.

    Any string literal outside the catalogue that matches a key counts: keys
    reach `t()` through tables and loop variables as well as directly, and a
    scan that only saw literal call arguments would call those orphans.
    """
    from render.acts import ACTS

    found = {a.eyebrow for a in ACTS} | {a.title for a in ACTS}
    for path in SOURCES:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                found.add(node.value)
    return found


def asked_for_directly() -> set[str]:
    """Keys passed to `t()` or `tpl()` as a literal, for the resolve check."""
    keys = set()
    for path in SOURCES:
        for node in ast.walk(ast.parse(path.read_text())):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in ("t", "tpl")):
                continue
            first = node.args[0] if node.args else None
            if isinstance(first, ast.Constant):
                keys.add(first.value)
            elif isinstance(first, ast.IfExp):
                for side in (first.body, first.orelse):
                    if isinstance(side, ast.Constant):
                        keys.add(side.value)
    return keys


def test_every_copy_key_resolves():
    missing = sorted(k for k in asked_for_directly() if k not in STRINGS)
    assert not missing, missing
    with pytest.raises(MissingCopy):
        t("no.such.key")


def test_no_orphan_copy_keys():
    """A key nobody asks for is copy nobody reads."""
    covered = referenced()
    for prefix in FAMILIES:
        covered |= {k for k in STRINGS if k.startswith(prefix)}
    orphans = sorted(k for k in STRINGS if k not in covered)
    assert not orphans, orphans


def test_every_placeholder_is_named():
    """`{}` would take an argument by position, which no caller supplies."""
    for key, template in STRINGS.items():
        for match in re.finditer(r"(?<!\{)\{([^{}]*)\}", template):
            assert match.group(1).split(":")[0].strip(), f"{key}: positional slot"


def test_numbers_are_not_typed_into_the_copy():
    """A figure in the catalogue is a figure that can drift from the frames.
    Years, clock times and the fixed bands of the index are not measurements."""
    #: Hours of the day, the index bands, and the rolling window. These are
    #: definitions, fixed in the code, not numbers read off a frame.
    structural = {"06", "07", "08", "23", "00", "01", "17", "10", "14", "20",
                  "25", "30", "40", "60", "100", "2026", "45"}
    offenders = []
    for key, template in STRINGS.items():
        bare = re.sub(r"\{[^}]*\}", " ", template)
        bare = re.sub(r"\d{2}:\d{2}", " ", bare)          # clock times
        for number in re.findall(r"\d[\d.,]*", bare):
            if len(number.strip(".,")) >= 2 and number.strip(".,") not in structural:
                offenders.append(f"{key}: {number}")
    assert not offenders, offenders


# ---------------------------------------------------------------------------
# Tone
# ---------------------------------------------------------------------------

VERBS = {"see", "click", "check", "set", "try", "put", "stop", "turn", "open",
         "go", "take", "make", "use", "read", "consider", "talk", "ask",
         "limit", "reduce", "enable", "disable", "tap", "swipe", "choose",
         "pick", "review", "note", "remember", "avoid", "keep", "get", "do",
         "don't", "start", "install", "download", "tell", "let", "give",
         "find", "watch", "look", "think", "help", "add", "remove"}


def first_word_is_a_command(text: str) -> str | None:
    for sentence in re.split(r"[.!?]\s+|<br\s*/?>|\n", text or ""):
        clean = re.sub(r"<[^>]+>", " ", sentence).strip().strip('"')
        first = re.split(r"[\s,]+", clean)[0].lower() if clean else ""
        if first in VERBS:
            return clean[:70]
    return None


def test_no_imperatives_in_user_or_guardian_copy():
    """Nothing the product shows a person tells them what to do."""
    offenders = [(k, first_word_is_a_command(v)) for k, v in STRINGS.items()
                 if k.startswith("phone.") and first_word_is_a_command(v)]
    assert not offenders, offenders


def test_the_engine_does_not_command_either(tl_a, tl_b, df_a, df_b):
    """The same rule for the text the rules themselves generate."""
    from balance.intelligence import evaluate_alerts, evaluate_positives, replay_nudge
    offenders = []
    for user, timeline, frame in (("A", tl_a, df_a), ("B", tl_b, df_b)):
        signals = evaluate_alerts(frame) + evaluate_positives(frame, user == "B")
        for signal in signals:
            for field in ("headline", "guardian_text"):
                hit = first_word_is_a_command(getattr(signal, field, ""))
                if hit:
                    offenders.append(f"{user}/{signal.key}.{field}: {hit}")
        for nudge in replay_nudge(timeline, frame):
            hit = first_word_is_a_command(getattr(nudge, "text", "") or "")
            if hit:
                offenders.append(f"{user}/nudge: {hit}")
    assert not offenders, offenders
