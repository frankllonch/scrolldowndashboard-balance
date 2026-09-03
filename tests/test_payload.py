"""The payload ships to the browser, so everything in it is public.

These are structural: they check what the build emits, not what it says.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from balance.events import load

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
            "top_bars.apps", "top_bars.sites", "day_span.night",
        }
        expected |= {f"week_evolution.{c}" for c in
                     ("screen_min", "night_min", "pickups", "blocks")}
        expected |= {f"week_days.{c}.{w}" for c in ("screen_min", "night_min")
                     for w in weeks}
        assert expected == set(profile["figures"]), f"user {user}"
        for name, figure in profile["figures"].items():
            assert figure["data"], f"{user}/{name} has no traces"
            # the theme is hoisted to payload["templates"] and re-attached in
            # the browser: 59 copies of it is 95 KB of the same thing
            assert "template" not in figure["layout"], f"{user}/{name}"
            assert figure["surface"] in payload["templates"], f"{user}/{name}"
    assert set(payload["templates"]) == {"light", "dusk", "dark"}, \
        payload["templates"]


def _notification_text(payload: dict) -> str:
    """Every word the payload would put on a phone as a notification."""
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
            walk(day["user"])
    return " ".join(parts).lower()


def test_payload_notifications_name_no_app_or_domain(payload):
    """The privacy contract, at the boundary that now matters: a notification
    says what changed, never what you were on."""
    outbound = _notification_text(payload)
    assert outbound, "no notification copy in the payload to check"

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
            assert stem not in outbound, f'"{stem}" reached a notification'


def test_the_refined_categories_change_nothing_that_is_scored(payload):
    """`taxonomy.py` fills a gap in the vocabulary. It may not move a figure.

    Nothing it assigns belongs to DISTRACTING, and it only ever reclassifies
    OTHER, so the index and everything built on it stay where they were.
    """
    from balance.events import DISTRACTING
    from balance.taxonomy import REFINED

    assert not set(REFINED.values()) & DISTRACTING, \
        "a refined category entered the distraction share"

    # the published index, asserted in tests/test_data_contract.py too
    assert round(payload["profiles"]["A"]["summary"]["score_mean"]) == 83
    assert round(payload["profiles"]["B"]["summary"]["score_mean"]) == 48


def test_other_is_no_longer_most_of_the_day(payload):
    """The point of the exercise: OTHER was 53% of A's time and 38% of B's."""
    from collections import defaultdict

    from balance.events import load

    for user, path in (("A", "data/events_user_a.json"),
                       ("B", "data/events_user_b.json")):
        minutes = defaultdict(float)
        for usage in load(ROOT / path, user).usages:
            minutes[usage.category] += usage.seconds / 60
        share = minutes["OTHER"] / sum(minutes.values())
        assert share < 0.02, f"user {user}: OTHER is still {share:.0%}"
