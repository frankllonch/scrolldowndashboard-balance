"""The acts, in reading order.

Parts 1 and 3 are the same for everyone and render once. Part 2 is one
person's month: it renders for both profiles, and the page swaps it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from . import (
    a01_cover, a02_two_people, a03_choose, a04_the_week, a05_a_day,
    a06_the_night, a07_where_time_goes, a08_what_stopped, a09_what_said,
    a10_the_finding, a11_the_control, a12_under_the_hood,
)


@dataclass(frozen=True)
class Act:
    id: str
    part: int
    eyebrow: str      # copy key
    title: str        # copy key
    builder: Callable

    @property
    def per_profile(self) -> bool:
        """Part 2 is lived from inside one profile; the rest is not."""
        return self.part == 2


ACTS = [
    Act("01", 1, "act.01.eyebrow", "act.01.title", a01_cover.build),
    Act("02", 1, "act.02.eyebrow", "act.02.title", a02_two_people.build),
    Act("03", 1, "act.03.eyebrow", "act.03.title", a03_choose.build),
    Act("04", 2, "act.04.eyebrow", "act.04.title", a04_the_week.build),
    Act("05", 2, "act.05.eyebrow", "act.05.title", a05_a_day.build),
    Act("06", 2, "act.06.eyebrow", "act.06.title", a06_the_night.build),
    Act("07", 2, "act.07.eyebrow", "act.07.title", a07_where_time_goes.build),
    Act("08", 2, "act.08.eyebrow", "act.08.title", a08_what_stopped.build),
    Act("09", 2, "act.09.eyebrow", "act.09.title", a09_what_said.build),
    Act("10", 3, "act.10.eyebrow", "act.10.title", a10_the_finding.build),
    Act("11", 3, "act.11.eyebrow", "act.11.title", a11_the_control.build),
    Act("12", 3, "act.12.eyebrow", "act.12.title", a12_under_the_hood.build),
]


@dataclass
class Context:
    """What every builder gets. `user` is set only for part 2."""
    payload: dict
    bundles: dict
    user: str | None = None

    @property
    def bundle(self) -> dict:
        return self.bundles[self.user]

    @property
    def profile(self) -> dict:
        return self.payload["profiles"][self.user]

    @property
    def df(self):
        return self.bundle["df"]


__all__ = ["ACTS", "Act", "Context"]
