"""The payload ships to the browser, so everything in it is public.

These are structural: they check what the build emits, not what it says.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from balance.events import CATEGORIES, load

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "docs" / "payload.json"


@pytest.fixture(scope="module")
def payload() -> dict:
    if not PAYLOAD.exists():
        pytest.skip("run `python build.py` first")
    return json.loads(PAYLOAD.read_text())


def test_payload_has_every_figure_day_and_week_for_both_profiles(payload):
    assert set(payload["profiles"]) == {"A", "B"}
    # act 13 puts both breakdowns side by side, so they are shared, not
    # "the current profile's"
    shared = {"score_line", "night_drift", "compare.screen_min",
              "compare.pickups", "compare.night_min", "compare.blocks",
              "compare.night_pickups", "score_breakdown.A", "score_breakdown.B"}
    assert shared <= set(payload["figures"])

    weeks = payload["meta"]["weeks"]
    for user, profile in payload["profiles"].items():
        assert len(profile["days"]) == payload["meta"]["days"] == 30
        assert [w["week"] for w in profile["weeks"]] == weeks
        expected = {
            "week_components", "hour_heat", "day_span", "category_area",
            "tracked_series", "blocks_daily", "blocks_by_hour",
            "daily_bars.screen_min", "daily_bars.pickups",
            "top_bars.apps", "top_bars.sites",
        }
        expected |= {f"week_evolution.{c}" for c in
                     ("screen_min", "night_min", "pickups", "blocks")}
        expected |= {f"week_days.{c}.{w}" for c in ("screen_min", "night_min")
                     for w in weeks}
        assert expected == set(profile["figures"]), f"user {user}"
        for name, figure in profile["figures"].items():
            assert figure["data"], f"{user}/{name} has no traces"
            # the theme is hoisted to payload["template"] and re-attached in
            # the browser: 59 copies of it is 95 KB of the same thing
            assert "template" not in figure["layout"], f"{user}/{name}"
    assert payload["template"], "the hoisted theme is missing"


def _guardian_text(payload: dict) -> str:
    """Every string that would reach a guardian's phone, lowercased."""
    parts: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str):
            parts.append(node)

    for profile in payload["profiles"].values():
        for day in profile["days"]:
            walk(day["guardian"])
    return " ".join(parts).lower()


def test_payload_guardian_section_has_no_app_domain_or_category(payload):
    """The privacy contract, moved to the boundary that now matters."""
    outbound = _guardian_text(payload)
    assert outbound, "no guardian copy in the payload to check"

    events = []
    for path in ("data/events_user_a.json", "data/events_user_b.json"):
        events += load(ROOT / path, "X").events
    packages = {e["package_name"] for e in events if e["package_name"]}
    domains = {e["url_domain"] for e in events if e["url_domain"]}

    # The full identifier is checked and so is its stem ("pornhub" from
    # pornhub.com, "whatsapp" from com.whatsapp), which is how a value would
    # actually leak. Stems under four letters are skipped: the "x" of x.com
    # appears in any prose and would be a false positive.
    def stems(ident: str) -> list[str]:
        parts = [ident] + ident.replace("/", ".").split(".")
        return [p.lower() for p in parts if len(p) >= 4]

    for ident in packages | domains:
        for stem in stems(ident):
            assert stem not in outbound, f'"{stem}" leaked to the guardian'

    for category in CATEGORIES:
        assert category.lower() not in outbound, f"{category} named to a guardian"
