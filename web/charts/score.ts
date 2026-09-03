/**
 * The index: the curve, the breakdown, and the weekly panels.
 */

import {
  DOW, annotation, axis as unit, hover, series, title, weekLabel,
} from "../copy/figures";
import { MONO, userColor, type Surface } from "../theme";
import type { DailyRow, UserId, WeeklyRow } from "../types/index";
import { directLabel, frame } from "./frame";
import type { Annotation, Figure, Trace } from "./plotly";
import type { Frames } from "./series";

/** The five index components, their weights, and what each one is called.
 *  Mirrors `COMPONENTS` in `balance/score.py`. */
export const COMPONENTS = [
  { key: "screen_min", label: "Screen time", good: 90, bad: 360, weight: 0.25 },
  { key: "pickups", label: "Fragmentation", good: 15, bad: 60, weight: 0.20 },
  { key: "night_min", label: "Protected night", good: 0, bad: 60, weight: 0.20 },
  { key: "longest_offline_h", label: "Long disconnection", good: 4, bad: 1,
    weight: 0.15 },
  { key: "distract_share", label: "Intent", good: 0.10, bad: 0.50,
    weight: 0.20 },
] as const;

/** Both people's index, every day, with the 7-day mean on top. */
export function scoreLine(s: Surface, frames: Frames): Figure {
  const data: Trace[] = [];
  const labels: Annotation[] = [];
  for (const [user, rows] of Object.entries(frames)) {
    const colour = userColor(s, user);
    const days = rows.map((r) => r.day);
    data.push({
      type: "scatter", mode: "markers", x: days, y: rows.map((r) => r.score),
      marker: { size: 4, color: colour, opacity: 0.3 },
      name: series.dailyPlain(user), showlegend: false, hoverinfo: "skip",
    });
    const smoothed = rows.map((r) => r.score_7d);
    data.push({
      type: "scatter", mode: "lines", x: days, y: smoothed,
      line: { color: colour, width: 2.6 }, name: series.user(user),
      hovertemplate: hover.score(user),
    });
    const lastDay = days[days.length - 1];
    const lastValue = smoothed[smoothed.length - 1];
    if (lastDay !== undefined && lastValue != null) {
      labels.push(directLabel(lastDay, lastValue, user, colour));
    }
  }
  return frame(s, data, {
    title: { text: title.scoreLine },
    yaxis: { title: { text: unit.score }, range: [0, 100], dtick: 20 },
    xaxis: { tickformat: "%d %b" },
    annotations: labels,
  });
}

/** How many points each component contributes on an average day, and how many
 *  it lets go. */
export function scoreBreakdown(s: Surface, rows: DailyRow[],
                               user: UserId): Figure {
  // Plotly draws horizontal bars bottom-up, so the list is reversed to read
  // top-down in the order the components are declared.
  const parts = [...COMPONENTS].reverse().map((c) => {
    const scores = rows.map((r) => r[`score_${c.key}`] as number);
    const mean = scores.reduce((a, b) => a + b, 0) / (scores.length || 1);
    return { ...c, points: mean * c.weight, lost: (100 - mean) * c.weight };
  });
  return frame(s, [
    {
      type: "bar", orientation: "h",
      x: parts.map((p) => p.points), y: parts.map((p) => p.label),
      name: series.pointsEarned,
      marker: { color: userColor(s, user),
                line: { color: s.card, width: 1.5 } },
      customdata: parts.map((p) => p.weight * 100),
      hovertemplate: hover.pointsEarned,
    },
    {
      type: "bar", orientation: "h",
      x: parts.map((p) => p.lost), y: parts.map((p) => p.label),
      name: series.pointsLost,
      marker: { color: s.lost, line: { color: s.card, width: 1.5 } },
      hovertemplate: hover.pointsLost,
    },
  ], {
    title: { text: title.scoreBreakdown(user) },
    xaxis: { title: { text: unit.points } },
    yaxis: { tickfont: { family: MONO, size: 11, color: s.ink } },
    barmode: "stack", bargap: 0.3,
    // "Long disconnection" is the longest tick label on the page and it sits
    // in the left margin, so that margin is sized for it rather than the
    // template's 56, which cut it off on a phone.
    margin: { t: 48, r: 24, b: 68, l: 124 },
  }, 300);
}

// ---------------------------------------------------------------------------
// Month walkthrough
// ---------------------------------------------------------------------------

/** One magnitude week by week, with the selected week highlighted. */
export function weekEvolution(s: Surface, weeks: WeeklyRow[],
                              key: keyof WeeklyRow, heading: string,
                              unitLabel: string, user: UserId,
                              selected: number): Figure {
  const colour = userColor(s, user);
  const values = weeks.map((w) => (w[key] as number | null) ?? 0);
  const most = Math.max(...values, 0);
  return frame(s, [{
    type: "bar",
    x: weeks.map((w) => weekLabel(w.week, w.is_partial)), y: values,
    marker: {
      color: weeks.map((w) => (w.week === selected ? colour : s.dim)),
      line: { color: s.card, width: 1.5 },
    },
    text: values.map((v) => (Math.abs(v) >= 10 ? v.toFixed(0) : v.toFixed(1))),
    textposition: "outside",
    textfont: { family: MONO, size: 11, color: s.ink2 },
    hovertemplate: hover.week(heading, unitLabel),
  }], {
    title: { text: heading },
    yaxis: { title: { text: unitLabel }, range: [0, Math.max(most * 1.25, 0.1)] },
    bargap: 0.35, showlegend: false,
    margin: { t: 44, r: 20, b: 36, l: 54 },
  }, 260);
}

/**
 * The days of the selected week against the mean of the weeks before it.
 *
 * A week is the Nth block of seven days, so week 1 opens on whatever weekday
 * the log does. The bars are still read Monday to Sunday: each block holds one
 * of every weekday, so sorting on it loses nothing.
 */
export function weekDays(s: Surface, rows: DailyRow[], week: number,
                         key: keyof DailyRow, heading: string,
                         unitLabel: string, user: UserId): Figure {
  const current = rows.filter((r) => r.week === week)
                      .sort((a, b) => a.dow - b.dow);
  const earlier = rows.filter((r) => r.week < week);
  const values = current.map((r) => (r[key] as number | null) ?? 0);

  const shapes = [];
  const annotations: Annotation[] = [];
  if (earlier.length) {
    const mean = earlier.reduce((sum, r) => sum + ((r[key] as number) ?? 0), 0)
                 / earlier.length;
    shapes.push({ type: "line" as const, xref: "paper", x0: 0, x1: 1,
                  y0: mean, y1: mean,
                  line: { color: s.ink, width: 1.6, dash: "dot" } });
    annotations.push({ xref: "paper", x: 0, y: mean,
                       text: annotation.prevMean(mean), showarrow: false,
                       xanchor: "left", yanchor: "bottom", yshift: 3,
                       font: { family: MONO, size: 10, color: s.ink2 } });
  }
  if (Math.max(...values.map(Math.abs), 0) === 0) {
    annotations.push({ xref: "paper", yref: "paper", x: 0.5, y: 0.5,
                       text: annotation.noActivityWeek, showarrow: false,
                       font: { family: MONO, size: 11, color: s.muted } });
  }

  return frame(s, [{
    type: "bar",
    x: current.map((r) => DOW[r.dow] ?? String(r.dow)), y: values,
    marker: { color: userColor(s, user),
              line: { color: s.card, width: 1.5 } },
    name: series.week(week),
    hovertemplate: hover.weekDay(unitLabel),
  }], {
    title: { text: heading },
    yaxis: { title: { text: unitLabel } },
    xaxis: { categoryorder: "array", categoryarray: [...DOW] },
    bargap: 0.3, showlegend: false,
    margin: { t: 52, r: 20, b: 40, l: 54 },
    shapes, annotations,
  }, 300);
}

/** The five index components, scored 0 to 100, week by week. */
export function weekComponents(s: Surface, weeks: WeeklyRow[],
                               selected: number): Figure {
  const labels = weeks.map((w) => weekLabel(w.week));
  const data: Trace[] = COMPONENTS.map((component, i) => {
    const colour = s.categorical[i % s.categorical.length] ?? s.ink;
    return {
      type: "scatter", mode: "lines+markers", x: labels,
      y: weeks.map((w) => w[`score_${component.key}`] as number),
      name: component.label,
      line: { color: colour, width: 2.2 },
      marker: { size: 8, color: colour },
      hovertemplate: hover.component(component.label),
    };
  });
  return frame(s, data, {
    title: { text: title.weekComponents },
    yaxis: { title: { text: unit.score }, range: [0, 105], dtick: 25 },
    shapes: [{ type: "line", yref: "paper", y0: 0, y1: 1,
               x0: weekLabel(selected), x1: weekLabel(selected),
               line: { color: s.ink, width: 1.6, dash: "dot" } }],
    margin: { t: 44, r: 20, b: 76, l: 54 },
  }, 320);
}
