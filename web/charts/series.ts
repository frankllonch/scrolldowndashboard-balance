/**
 * Time series: one line or one bar per day.
 */

import { axis as unit, annotation, hover, series, title } from "../copy/figures";
import { clock, rollingMean } from "../format";
import { MONO, userColor, type Surface } from "../theme";
import type { DailyRow, UserId } from "../types/index";
import { directLabel, frame } from "./frame";
import type { Figure, Trace } from "./plotly";

/** The frames both profiles are drawn from, keyed by user. */
export type Frames = Record<UserId, DailyRow[]>;

const SMOOTH = 7;

function column(rows: DailyRow[], key: keyof DailyRow): Array<number | null> {
  return rows.map((row) => {
    const value = row[key];
    return typeof value === "number" ? value : null;
  });
}

/** One smoothed line per user, with the raw daily point behind it. */
export function compareLine(s: Surface, frames: Frames, key: keyof DailyRow,
                            heading: string, unitLabel = ""): Figure {
  const data: Trace[] = [];
  const labels = [];
  for (const [user, rows] of Object.entries(frames)) {
    const colour = userColor(s, user);
    const days = rows.map((r) => r.day);
    const values = column(rows, key);
    data.push({
      type: "scatter", mode: "markers", x: days, y: values,
      marker: { size: 4, color: colour, opacity: 0.28 },
      name: series.daily(user), legendgroup: user, showlegend: false,
      hovertemplate: hover.compareDaily(user, unitLabel),
    });
    const smoothed = rollingMean(values, SMOOTH);
    data.push({
      type: "scatter", mode: "lines", x: days, y: smoothed,
      line: { color: colour, width: 2.4 },
      name: series.user(user), legendgroup: user,
      hovertemplate: hover.compareSmoothed(user, unitLabel, SMOOTH),
    });
    const lastDay = days[days.length - 1];
    const lastValue = smoothed[smoothed.length - 1];
    if (lastDay !== undefined && lastValue !== null && lastValue !== undefined) {
      labels.push(directLabel(lastDay, lastValue, user, colour));
    }
  }
  return frame(s, data, {
    title: { text: heading },
    yaxis: { title: { text: unitLabel } },
    xaxis: { tickformat: "%d %b" },
    annotations: labels,
  });
}

/** A daily bar against this user's own 14-day rolling median. */
export function dailyBarsVsBaseline(s: Surface, rows: DailyRow[],
                                    key: keyof DailyRow,
                                    baselineKey: keyof DailyRow,
                                    heading: string, unitLabel: string,
                                    user: UserId): Figure {
  const colour = userColor(s, user);
  const values = column(rows, key);
  const baseline = column(rows, baselineKey);
  const over = values.map((v, i) => {
    const b = baseline[i];
    return v !== null && b !== null && b !== undefined && v > b;
  });

  // Two traces rather than one with mixed colours: this way the amber enters
  // the legend and explains itself, with no caption to read.
  const split = (wanted: boolean, name: string, color: string): Trace => ({
    type: "bar", name,
    x: rows.filter((_, i) => over[i] === wanted).map((r) => r.day),
    y: values.filter((_, i) => over[i] === wanted),
    marker: { color, line: { color: s.card, width: 1.5 } },
    hovertemplate: hover.dayValue(unitLabel),
  });

  return frame(s, [
    split(false, series.atOrBelow, colour),
    split(true, series.above, s.warn),
    {
      type: "scatter", mode: "lines",
      x: rows.map((r) => r.day), y: baseline,
      line: { color: s.ink, width: 1.6, dash: "dot" },
      name: series.baseline,
      hovertemplate: hover.baseline(unitLabel),
    },
  ], {
    title: { text: heading },
    yaxis: { title: { text: unitLabel } },
    xaxis: { tickformat: "%d %b" },
    bargap: 0.25, barmode: "overlay",
    margin: { t: 48, r: 24, b: 86, l: 56 },
    legend: { y: -0.22 },
  }, 340);
}

/**
 * From the first unlock to the last screen-off, day by day.
 *
 * The axis runs past 24 so the small hours sit at the top rather than dropping
 * to the floor: what spills over the top is eating into the night.
 */
export function daySpan(s: Surface, rows: DailyRow[], user: UserId): Figure {
  const colour = userColor(s, user);
  const starts = rows.map((r) => r.first_pickup_h);
  const ends = rows.map((r) => r.last_use_h);
  const present = (xs: Array<number | null>) =>
    xs.filter((x): x is number => x !== null && Number.isFinite(x));

  const low = Math.max(5, Math.floor(Math.min(...present(starts))) - 1);
  const high = Math.min(29, Math.floor(Math.max(...present(ends))) + 2);
  const ticks: number[] = [];
  for (let h = low + (low % 2); h <= high; h += 2) ticks.push(h);

  const data: Trace[] = [
    {
      type: "bar", x: rows.map((r) => r.day),
      y: rows.map((_, i) => {
        const end = ends[i];
        const start = starts[i];
        return end != null && start != null ? end - start : null;
      }),
      // A day with no unlock has no bar to place, and 0 would draw one from
      // midnight.
      base: starts.map((v) => v ?? 0),
      marker: { color: colour, opacity: 0.55,
                line: { color: s.card, width: 1.2 } },
      name: series.dayWithPhone,
      customdata: rows.map((r) => [clock(r.first_pickup_h), clock(r.last_use_h)]),
      hovertemplate: hover.daySpan,
    },
    {
      type: "scatter", mode: "lines", x: rows.map((r) => r.day),
      y: rollingMean(ends, 7),
      line: { color: s.ink, width: 2 },
      name: series.lastScreenMean, hoverinfo: "skip",
    },
  ];

  return frame(s, data, {
    title: { text: title.daySpan(user) },
    yaxis: { title: { text: unit.localTime }, range: [low, high],
             tickvals: ticks, ticktext: ticks.map((h) => clock(h % 24)) },
    xaxis: { tickformat: "%d %b" },
    // Inside the plotting area, not beside it: to the right of the axis the
    // card's own edge cuts the label off.
    shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, y0: 23, y1: 23,
               line: { color: s.warn, width: 1.2, dash: "dot" } }],
    annotations: [{ xref: "paper", x: 1, y: 23, text: annotation.nightStart,
                    showarrow: false, xanchor: "right", yanchor: "bottom",
                    yshift: 3, font: { family: MONO, size: 10, color: s.warn } }],
  });
}

/** Screen minutes between 23:00 and 06:00, per night, for both profiles. */
export function nightDrift(s: Surface, frames: Frames): Figure {
  const data: Trace[] = [];
  for (const [user, rows] of Object.entries(frames)) {
    const values = rows.map((r) => r.night_min);
    // A series flat at zero reads as "data missing" unless you say so, and the
    // note goes in the legend rather than an annotation: over the bars it
    // covered what has to be read, and over the title it collided with it.
    const flat = Math.max(...values) < 0.5;
    data.push({
      type: "bar", x: rows.map((r) => r.day), y: values,
      name: flat ? series.nightFlat(user, rows.length) : series.user(user),
      marker: { color: userColor(s, user),
                line: { color: s.card, width: 1.2 } },
      hovertemplate: hover.nightDrift(user),
    });
  }
  return frame(s, data, {
    title: { text: title.nightDrift },
    yaxis: { title: { text: unit.minutes } },
    xaxis: { tickformat: "%d %b" },
    barmode: "group", bargap: 0.2,
  });
}
