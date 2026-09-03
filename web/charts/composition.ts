/**
 * Where the time and the blocks went.
 *
 * Every stack here uses the fixed category order from the theme, never the
 * ranking: a band that grows really is growing, and has not just overtaken
 * its neighbour and swapped places with it.
 */

import { CATEGORY_LABEL, axis as unit, hover, series, title } from "../copy/figures";
import { DOW } from "../copy/figures";
import { rollingMean, thousands } from "../format";
import { CATEGORY_COLOR, CATEGORY_ORDER, MONO, type Surface } from "../theme";
import type {
  Blocks, Category, CategoryDay, HeatCell, UsageTotal, UserId,
} from "../types/index";
import { frame } from "./frame";
import type { Figure, Trace } from "./plotly";

/** The categories present in this data, in the theme's order. */
function present(found: Iterable<Category>): Category[] {
  const seen = new Set(found);
  return CATEGORY_ORDER.filter((c) => seen.has(c));
}

/** Minutes per category and day, stacked. */
export function categoryArea(s: Surface, rows: CategoryDay[],
                             heading: string): Figure {
  const days = [...new Set(rows.map((r) => r.day))].sort();
  const order = present(rows.map((r) => r.category));
  const byKey = new Map(rows.map((r) => [`${r.day}|${r.category}`, r.minutes]));

  const data: Trace[] = order.map((category) => {
    const values = days.map((day) => byKey.get(`${day}|${category}`) ?? 0);
    return {
      type: "scatter", mode: "lines", stackgroup: "one",
      x: days, y: rollingMean(values, 3, 1),
      name: CATEGORY_LABEL[category],
      line: { width: 1.2, color: s.card },
      fillcolor: CATEGORY_COLOR[category],
      hovertemplate: hover.category(CATEGORY_LABEL[category]),
    };
  });

  return frame(s, data, {
    title: { text: heading },
    yaxis: { title: { text: unit.minutesRolling } },
    xaxis: { tickformat: "%d %b" },
    // The last tick is a date, which needs more room than the template's 24.
    margin: { t: 48, r: 44, b: 68, l: 56 },
  }, 360);
}

/** Horizontal ranking by minutes, coloured by category. */
export function topBars(s: Surface, totals: UsageTotal[], heading: string,
                        n = 10): Figure {
  // Plotly draws a horizontal bar chart bottom-up, so the biggest goes last.
  const rows = totals.slice(0, n).reverse();
  const most = Math.max(...rows.map((r) => r.minutes), 1);
  return frame(s, [{
    type: "bar", orientation: "h",
    x: rows.map((r) => r.minutes), y: rows.map((r) => r.label),
    marker: {
      color: rows.map((r) => CATEGORY_COLOR[r.category] ?? s.muted),
      line: { color: s.card, width: 1.5 },
    },
    text: rows.map((r) => `${thousands(r.minutes)} min`),
    textposition: "outside",
    textfont: { family: MONO, size: 11, color: s.ink2 },
    customdata: rows.map((r) => [r.opens, r.min_per_open,
                                 CATEGORY_LABEL[r.category]]),
    hovertemplate: hover.topBars,
  }], {
    title: { text: heading },
    xaxis: { title: { text: unit.minutesMonth }, range: [0, most * 1.24] },
    yaxis: { tickfont: { family: MONO, size: 11, color: s.ink } },
    bargap: 0.28, showlegend: false,
    margin: { t: 48, r: 48, b: 56, l: 110 },
  }, 380);
}

/** Weekly clock: screen minutes by weekday and hour. */
export function hourHeat(s: Surface, cells: HeatCell[], user: UserId): Figure {
  const grid: number[][] = Array.from({ length: 7 },
                                      () => Array.from({ length: 24 }, () => 0));
  for (const cell of cells) {
    const row = grid[cell.dow];
    if (row) row[cell.hour] = (row[cell.hour] ?? 0) + cell.minutes;
  }
  return frame(s, [{
    type: "heatmap", z: grid,
    x: Array.from({ length: 24 }, (_, h) => h), y: [...DOW],
    colorscale: s.heat, xgap: 2, ygap: 2,
    colorbar: {
      title: { text: unit.min,
               font: { family: MONO, size: 10, color: s.ink2 } },
      tickfont: { family: MONO, size: 10, color: s.ink2 },
      outlinewidth: 0, thickness: 9, len: 0.8, x: 1.02,
    },
    hovertemplate: hover.heat,
  }], {
    title: { text: title.hourHeat(user) },
    xaxis: { title: { text: unit.localTime }, dtick: 2, showgrid: false },
    yaxis: { showgrid: false, autorange: "reversed",
             tickfont: { family: MONO, size: 11, color: s.ink } },
    showlegend: false, hovermode: "closest",
  }, 330);
}

// ---------------------------------------------------------------------------
// Blocks
// ---------------------------------------------------------------------------

/** Blocked attempts per day, stacked by category. */
export function blocksDaily(s: Surface, blocks: Blocks,
                            heading: string): Figure {
  const days = [...new Set(blocks.byDay.map((r) => r.day))].sort();
  const order = present(blocks.byDay.map((r) => r.category));
  const byKey = new Map(blocks.byDay.map((r) => [`${r.day}|${r.category}`,
                                                 r.count]));
  const data: Trace[] = order.map((category) => ({
    type: "bar", x: days,
    y: days.map((day) => byKey.get(`${day}|${category}`) ?? 0),
    name: CATEGORY_LABEL[category],
    marker: { color: CATEGORY_COLOR[category],
              line: { color: s.card, width: 1.2 } },
    hovertemplate: hover.blocksCategory(CATEGORY_LABEL[category]),
  }));
  return frame(s, data, {
    title: { text: heading },
    yaxis: { title: { text: unit.blockedAttempts } },
    xaxis: { tickformat: "%d %b" },
    barmode: "stack", bargap: 0.2,
  });
}

const SENSITIVE: Category[] = ["ADULT", "GAMBLING"];

/** What time the wall gets hit; sensitive against the rest. */
export function blocksByHour(s: Surface, blocks: Blocks,
                             heading: string): Figure {
  const hours = Array.from({ length: 24 }, (_, h) => h);
  const tally = (wanted: boolean): number[] => {
    const counts = hours.map(() => 0);
    for (const row of blocks.byHour) {
      if (SENSITIVE.includes(row.category) === wanted) {
        counts[row.hour] = (counts[row.hour] ?? 0) + row.count;
      }
    }
    return counts;
  };
  const data: Trace[] = [
    [series.ordinary, tally(false), "#3987e5"],
    [series.sensitive, tally(true), "#e66767"],
  ].map(([name, counts, color]) => ({
    type: "bar", x: hours, y: counts as number[], name: name as string,
    marker: { color: color as string, line: { color: s.card, width: 1.2 } },
    hovertemplate: hover.blocksHour(name as string),
  }));
  return frame(s, data, {
    title: { text: heading },
    xaxis: { title: { text: unit.localTime }, dtick: 2 },
    yaxis: { title: { text: unit.attemptsMonth } },
    barmode: "stack", bargap: 0.15,
    margin: { t: 48, r: 24, b: 96, l: 56 },
    legend: { y: -0.3 },
  }, 300);
}
