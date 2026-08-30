"""The plotly builders, by family.

None of them decides anything: they receive frames already computed. Surface
colours are read through `theme`, so the same builder draws on paper, on the
dusk ground or on near-black without knowing which.

Rules honoured across all of them:
* never two Y axes: two different magnitudes are two charts;
* colour follows the entity (user, category), never its rank;
* with 2 or more series there is always a legend, and with 4 or fewer also
  direct labels;
* 2 px of surface gap between stacked fills;
* recessive grid and axes, thin marks.
"""

from .composition import (
    blocks_by_hour,
    blocks_daily,
    category_area,
    hour_heat,
    top_bars,
)
from .score import (
    score_breakdown,
    score_line,
    week_components,
    week_days,
    week_evolution,
)
from .series import compare_line, daily_bars_vs_baseline, day_span, night_drift
from .walkthrough import TRACKED, TRACKED_DEFAULT, tracked_series

__all__ = [
    "blocks_by_hour", "blocks_daily", "category_area", "compare_line",
    "daily_bars_vs_baseline", "day_span", "hour_heat", "night_drift",
    "score_breakdown", "score_line", "top_bars", "tracked_series",
    "week_components", "week_days", "week_evolution",
    "TRACKED", "TRACKED_DEFAULT",
]
