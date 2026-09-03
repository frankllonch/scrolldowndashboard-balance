/**
 * The month on one axis, with the event rail under it.
 */

import { annotation, axis as unit, hover } from "../copy/figures";
import { MONO, type Surface } from "../theme";
import type { DailyRow, Day, ReplayDay } from "../types/index";
import { frame } from "./frame";
import type { Figure, Trace } from "./plotly";

/**
 * Every variable the alert rules read.
 *
 * Divided by its own maximum rather than rescaled min-max, because zero has
 * to stay zero: for user A, "no late-night minutes" is the finding, and
 * min-max would paint it halfway up the axis.
 *
 * The dash pattern is a second encoding, not decoration. The worst adjacent
 * pair in this palette sits at ΔE 10.3 on this surface, inside the floor band
 * for protan colour blindness.
 */
const TRACKED = [
  { key: "night_min", label: "Late-night screen", unit: "min", slot: 0,
    dash: "solid", symbol: "circle", rules: "night_drift · night_streak" },
  { key: "night_end_min", label: "Last screen (from 23:00)", unit: "min",
    slot: 1, dash: "dash", symbol: "square", rules: "night_drift" },
  { key: "screen_min", label: "Screen per day", unit: "min", slot: 2,
    dash: "solid", symbol: "diamond", rules: "screen_jump" },
  { key: "longest_offline_h", label: "Longest break", unit: "h", slot: 3,
    dash: "dot", symbol: "cross", rules: "offline_record" },
  { key: "blocks", label: "Blocks per day", unit: "", slot: 4,
    dash: "dashdot", symbol: "x", rules: "calm_week" },
  { key: "blocks_sensitive", label: "Sensitive attempts", unit: "", slot: 5,
    dash: "dash", symbol: "triangle-up", rules: "sensitive_spike · filter_calm" },
  { key: "distract_pct", label: "Distraction share", unit: "%", slot: 6,
    dash: "dot", symbol: "pentagon", rules: "focus_week" },
] as const;

/** Visible on open. Seven lines at once do not read, and starting with all of
 *  them on forces the reader to switch things off rather than on. */
const DEFAULT_ON = new Set(["night_min", "night_end_min", "screen_min"]);

/** Height of the event rail, below the data zero. */
const RAIL = -9;

/** The columns that exist only for this chart. */
function derived(row: DailyRow): Record<string, number | null> {
  return {
    // The last screen is minutes past 23:00, so zero means "went dark on
    // time" rather than "midnight".
    night_end_min: row.night_end_h === null ? null : (row.night_end_h - 23) * 60,
    longest_offline_h: row.longest_offline_h,
    distract_pct: row.distract_share * 100,
    night_min: row.night_min,
    screen_min: row.screen_min,
    blocks: row.blocks,
    blocks_sensitive: row.blocks_sensitive,
  };
}

/** Which days carried which emission. */
function rails(replay: ReplayDay[]) {
  const nudges: Day[] = [];
  const alerts: Day[] = [];
  const digests: Day[] = [];
  const positives: Day[] = [];
  for (const day of replay) {
    if (day.nudge?.fired) nudges.push(day.day);
    if (day.alert) alerts.push(day.day);
    else if (day.digest_entry) digests.push(day.day);
    if (day.positives.length) positives.push(day.day);
  }
  return { nudges, alerts, digests, positives };
}

export function trackedSeries(s: Surface, rows: DailyRow[],
                              replay: ReplayDay[], cursor: Day): Figure {
  const days = rows.map((r) => r.day);
  const values = rows.map(derived);
  const data: Trace[] = [];

  TRACKED.forEach((track, i) => {
    const raw = values.map((v) => v[track.key] ?? null);
    const top = Math.max(...raw.map((v) => v ?? 0));
    // A series flat at zero is drawn anyway, hugging the axis, so it is
    // visible that the data exists and is zero.
    const flat = !Number.isFinite(top) || top <= 0;
    const colour = s.categorical[track.slot] ?? s.ink;
    data.push({
      type: "scatter", mode: "lines+markers", x: days,
      y: flat ? raw.map(() => 0) : raw.map((v) => (v === null ? null : v / top * 100)),
      name: `${track.label}${flat ? " · no activity" : ""}`,
      // The group only titles the legend; `groupclick: "toggleitem"` keeps a
      // click on one entry from switching off the whole group.
      legendgroup: "tracked",
      ...(i === 0 ? { legendgrouptitle: { text: "Watched variables" } } : {}),
      visible: DEFAULT_ON.has(track.key) ? true : "legendonly",
      line: { color: colour, width: 2, dash: track.dash },
      marker: { size: 5, color: colour, symbol: track.symbol },
      customdata: raw,
      hovertemplate: hover.tracked(track.label, track.unit, track.rules),
    });
  });

  const { nudges, alerts, digests, positives } = rails(replay);
  const events = [
    { name: "Night with a nudge", days: nudges, symbol: "circle",
      color: s.warn, detail: "Night nudge on the device" },
    { name: "Alert", days: alerts, symbol: "triangle-up", color: s.serious,
      detail: "Notification shown on the phone" },
    { name: "Summary entry", days: digests, symbol: "diamond", color: s.ink2,
      detail: "Signal held for the weekly summary" },
    { name: "Reinforcement", days: positives, symbol: "star", color: s.good,
      detail: "Reinforcement sent" },
  ];
  events.forEach((event, i) => {
    data.push({
      type: "scatter", mode: "markers", x: event.days,
      y: event.days.map(() => RAIL), name: event.name,
      legendgroup: "events",
      ...(i === 0 ? { legendgrouptitle: { text: "Emissions" } } : {}),
      marker: { symbol: event.symbol, size: 11, color: event.color,
                line: { color: s.card, width: 1 } },
      hovertemplate: hover.event(event.detail),
      showlegend: true,
    });
  });

  return frame(s, data, {
    hovermode: "x unified",
    yaxis: { title: { text: unit.pctOfMax }, range: [RAIL - 5, 108],
             dtick: 25, tickvals: [0, 25, 50, 75, 100],
             ticktext: ["0", "25", "50", "75", "100 %"] },
    xaxis: { tickformat: "%d %b" },
    margin: { t: 44, r: 24, b: 120, l: 64 },
    legend: { orientation: "h", y: -0.24, x: 0, xanchor: "left",
              yanchor: "top", groupclick: "toggleitem",
              font: { family: MONO, size: 11, color: s.ink2 },
              grouptitlefont: { family: MONO, size: 11, color: s.muted } },
    shapes: [
      { type: "line", xref: "paper", x0: 0, x1: 1, y0: 0, y1: 0,
        line: { color: s.rule, width: 1 } },
      { type: "line", yref: "paper", y0: 0, y1: 1, x0: cursor, x1: cursor,
        line: { color: s.ink, width: 2 } },
    ],
    annotations: [{ xref: "paper", x: 0, y: RAIL, yanchor: "middle",
                    xanchor: "right", xshift: -8, text: annotation.events,
                    showarrow: false,
                    font: { family: MONO, size: 10, color: s.muted } }],
  }, 560);
}

/** The cursor is the only thing that moves when the day slider does. */
export function cursorUpdate(day: Day): Record<string, unknown> {
  return { "shapes[1].x0": day, "shapes[1].x1": day };
}
