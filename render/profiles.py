"""What the two source files are, and which ground each figure is drawn for."""

DATA = {"A": "data/events_user_a.json", "B": "data/events_user_b.json"}

#: Acts 01 to 04 sit on paper, act 05 on the warm olive between paper and
#: night, the rest on near-black. See SURFACES in render/theme.py.
LIGHT_FIGURES = {"score_line", "week_components"}
LIGHT_PREFIXES = ("week_evolution.", "week_days.")
DUSK_FIGURES = {"hour_heat", "day_span", "daily_bars.screen_min",
                "daily_bars.pickups"}


def surface_for(key: str) -> str:
    if key in LIGHT_FIGURES or key.startswith(LIGHT_PREFIXES):
        return "light"
    return "dusk" if key in DUSK_FIGURES else "dark"
