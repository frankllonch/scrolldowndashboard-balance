/**
 * Act 04 · the week. First interaction of the page: five weeks on a slider.
 *
 * The panels are built when the slider moves, not five times up front. Python
 * precomputed all of them into the payload because the browser held no copy
 * and could not word a KPI; that whole module is gone.
 */

import { explain } from "../copy/explain";
import { unit, value } from "../copy/units";
import { hm, shortDate, thousands } from "../format";
import { median } from "../stats";
import {
  caption, chart, grid, kpis, lede, note, pairs, slot, sub, table,
  type Kpi,
} from "../html";
import type { Emission, Profile, Signal, WeeklyRow } from "../types/index";
import type { Act, Context } from "./act";

const copy = {
  eyebrow: "Week by week",
  title: "The week's summary",

  lede: "Slide through each week to see your usage across those seven days.",
  sliderLabel: "Week",
  option: (week: number, partial: boolean) =>
    partial ? `Week ${week} (short)` : `Week ${week}`,
  range: (start: string, end: string, days: number) =>
    `${start} to ${end} · ${days} days`,
  rangePartial:
    "  ·  short week: the averages are per day, but comparing it against "
    + "seven-day weeks is less reliable.",
  partialFootnote: "Weeks marked with * are shorter than seven days.",
  daysTitle: (week: number) => `The days of week ${week}`,
  emittedTitle: (week: number) => `What the phone emitted in week ${week}`,
  emittedNone: "Nothing this week.",
  recordedTitle: "Also recorded this week, not notified",

  kpi: {
    screen: "Screen / day",
    pickups: "Unlocks / day",
    night: "Late night / night",
    offline: "Longest break, average day",
    bestOffline: "Longest break, best day",
    blocks: "Blocks / day",
    score: "Index",
  },

  tableColumns: (week: number) => [
    "Metric", `Week ${week}`, "Previous week", "Period median", "Change",
  ],
  emissionColumns: ["Date", "Destination", "Type", "Detail"],

  readingA: (blocks: number) =>
    "Nothing here really moves. Your screen time, your unlocks and your "
    + "nights sit in the same place in week 4 as they did in week 1, and the "
    + `filter barely has to step in — ${thousands(blocks)} attempts in the `
    + "whole month, all of them ordinary distraction.",
  readingB: (first: number, last: number) =>
    "Your night usage varies noticeably from week to week, but your general "
    + "usage stays high every week. And as the month goes along the blocks get "
    + `more recurrent — ${first.toFixed(0)} a day in week 1, `
    + `${last.toFixed(0)} by week 4 — every time you try harder to find where `
    + "the blocking fails.",

  next: "Now zoom in. A week is thirty days seen from a distance — here is a "
    + "single day.",
};

/** The nine measures the against-the-period table walks. */
const ROWS: Array<{
  label: string; key: keyof WeeklyRow; unit: string; decimals: number;
  share?: boolean;
}> = [
  { label: "Screen per day", key: "screen_min", unit: unit.min, decimals: 0 },
  { label: "Unlocks per day", key: "pickups", unit: "", decimals: 0 },
  { label: "Late night per night", key: "night_min", unit: unit.min,
    decimals: 0 },
  { label: "Longest break", key: "longest_offline_h", unit: unit.hours,
    decimals: 1 },
  { label: "Distinct apps per day", key: "distinct_apps", unit: "",
    decimals: 1 },
  { label: "App switches per hour", key: "switches_per_screen_hour", unit: "",
    decimals: 0 },
  { label: "Distraction share", key: "distract_share", unit: unit.percent,
    decimals: 0, share: true },
  { label: "Blocks per day", key: "blocks", unit: "", decimals: 1 },
  { label: "Index", key: "score", unit: "", decimals: 0 },
];

function num(row: WeeklyRow, key: keyof WeeklyRow): number | null {
  const found = row[key];
  return typeof found === "number" ? found : null;
}

/**
 * How a measure moved, in its own unit.
 *
 * Both values are rounded to the precision they are displayed at before being
 * subtracted, so the change always equals the difference between the two
 * numbers on screen. Rounding after would let the table say 2.1, 2.3 and
 * "+0.2" in one row while the strip above it said "+0.3" for the same week.
 *
 * A change that rounds away is worded, not printed: "+0 min" beside an arrow
 * says something improved when nothing moved.
 */
function change(now: number, was: number, label: string,
                decimals: number): string {
  const moved = Number(now.toFixed(decimals)) - Number(was.toFixed(decimals));
  if (Math.abs(moved) < 10 ** -decimals / 2) return value.noChange;
  return `${moved > 0 ? "+" : ""}${moved.toFixed(decimals)} ${label}`.trim();
}

/** The same, against the week before, or nothing where there is no week
 *  before to compare against. */
function delta(row: WeeklyRow, before: WeeklyRow | undefined,
               key: keyof WeeklyRow, label: string,
               decimals = 0): string | undefined {
  const was = before ? num(before, key) : null;
  const now = num(row, key);
  if (was === null || now === null) return undefined;
  return change(now, was, label, decimals);
}

function weekKpis(row: WeeklyRow, before: WeeklyRow | undefined): Kpi[] {
  const items: Array<[string, string, string | undefined]> = [
    [copy.kpi.screen, hm(row.screen_min),
     delta(row, before, "screen_min", unit.min)],
    [copy.kpi.pickups, row.pickups.toFixed(0),
     delta(row, before, "pickups", "")],
    [copy.kpi.night, `${row.night_min.toFixed(0)} ${unit.min}`,
     delta(row, before, "night_min", unit.min)],
    [copy.kpi.offline, `${row.longest_offline_h.toFixed(1)} ${unit.hours}`,
     delta(row, before, "longest_offline_h", unit.hours, 1)],
    [copy.kpi.bestOffline, `${row.best_offline_h.toFixed(1)} ${unit.hours}`,
     row.best_offline_when ?? undefined],
    [copy.kpi.blocks, row.blocks.toFixed(1),
     delta(row, before, "blocks", "", 1)],
    [copy.kpi.score, row.score.toFixed(0), delta(row, before, "score", "")],
  ];
  return items.map(([label, val, d]) =>
    (d === undefined ? { label, value: val } : { label, value: val, delta: d }));
}

function weekTable(weeks: WeeklyRow[], row: WeeklyRow,
                   before: WeeklyRow | undefined): string {
  const rows = ROWS.map((spec) => {
    const scale = spec.share ? 100 : 1;
    const fmt = (v: number) =>
      `${v.toFixed(spec.decimals)} ${spec.unit}`.trim();
    const now = (num(row, spec.key) ?? 0) * scale;
    const was = before ? num(before, spec.key) : null;
    const previous = was === null ? null : was * scale;
    const mid = Number((median(weeks.map((w) => (num(w, spec.key) ?? 0) * scale))
      ).toFixed(spec.decimals));

    return [
      spec.label, fmt(now),
      previous === null ? value.notAvailable : fmt(previous),
      fmt(mid),
      previous === null ? value.notAvailable
                        : change(now, previous, spec.unit, spec.decimals),
    ];
  });
  return table(copy.tableColumns(row.week), rows);
}

function emissions(all: Emission[], days: Set<string>): string {
  const rows = all.filter((e) => days.has(e.day))
    .map((e) => [shortDate(e.day), e.destination, e.type, e.detail]);
  return rows.length
    ? table(copy.emissionColumns, rows) : caption(copy.emittedNone);
}

/** A signal the engine recorded and chose not to send is still a signal. */
function held(positives: Signal[], days: Set<string>): string {
  const rows = positives
    .filter((s) => s.decision === "summary" && days.has(s.day))
    .map((s): [string, string] => [s.headline, s.reason.split(".")[0] ?? ""]);
  return rows.length ? sub(copy.recordedTitle) + pairs(rows) : "";
}

function slider(weeks: WeeklyRow[], current: WeeklyRow): string {
  const ticks = weeks.map((w) =>
    `<option value="${w.week}" label="${w.week}"></option>`).join("");
  const numbers = weeks.map((w) => w.week);
  return '<div class="slider" data-slider="week">'
    + `<label for="week-slider">${copy.sliderLabel}</label>`
    + '<output for="week-slider" data-slot="week.label">'
    + `${copy.option(current.week, current.is_partial)}</output>`
    + '<input type="range" id="week-slider" list="week-ticks" '
    + `min="${Math.min(...numbers)}" max="${Math.max(...numbers)}" `
    + `step="any" value="${current.week}">`
    + `<datalist id="week-ticks">${ticks}</datalist></div>`;
}

/** What the slider's readout says at one step. The panel says the same, so
 *  the label the reader sees while dragging is the label they land on. */
export function label(profile: Profile, week: number): string {
  const row = profile.weekly.find((w) => w.week === week);
  return row ? copy.option(row.week, row.is_partial) : "";
}


/** Everything behind the slider, for one week. Exported so the interaction
 *  can rebuild it without going through the whole act. */
export function panel(profile: Profile, week: number): Record<string, string> {
  const weeks = profile.weekly;
  const row = weeks.find((w) => w.week === week) ?? weeks[weeks.length - 1];
  if (!row) return {};
  const before = weeks.find((w) => w.week === row.week - 1);
  const days = new Set(profile.daily.filter((d) => d.week === row.week)
    .map((d) => d.day));
  return {
    "week.label": copy.option(row.week, row.is_partial),
    "week.range": caption(
      copy.range(shortDate(row.start), shortDate(row.end), row.days)
      + (row.is_partial ? copy.rangePartial : "")),
    "week.kpis": kpis(weekKpis(row, before)),
    "week.days_title": sub(copy.daysTitle(row.week)),
    "week.table": weekTable(weeks, row, before),
    "week.emitted_title": sub(copy.emittedTitle(row.week)),
    "week.emissions": emissions(profile.emissions, days),
    "week.held": held(profile.positives, days),
  };
}

const EVOLUTION = ["screen_min", "night_min", "pickups", "blocks"] as const;

function reading(ctx: Context): string {
  const daily = ctx.profile.daily;
  const perWeek = (n: number) => {
    const rows = daily.filter((d) => d.week === n);
    return rows.reduce((sum, d) => sum + d.blocks, 0) / (rows.length || 1);
  };
  if (ctx.user === "A") {
    const total = daily.reduce((sum, d) => sum + d.blocks, 0);
    return note(copy.readingA(total), "good");
  }
  return note(copy.readingB(perWeek(1), perWeek(4)), "warn");
}

export const act: Act = {
  id: "04",
  part: 2,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build(ctx: Context): string {
    const { profile, selection } = ctx;
    const weeks = profile.weekly;
    const current = weeks.find((w) => w.week === selection.week) ?? weeks[0];
    if (!current) return "";
    const built = panel(profile, current.week);
    const days = (measure: "screen_min" | "night_min") =>
      chart(`week_days.${measure}.${current.week}`,
            explain(`week_days.${measure}`),
            { weekly: `week_days.${measure}` });

    return lede(copy.lede)
      + slider(weeks, current)
      + slot("week.range", built["week.range"] ?? "")
      + slot("week.kpis", built["week.kpis"] ?? "")
      + grid(EVOLUTION.map((m) =>
        chart(`week_evolution.${m}`, explain(`week_evolution.${m}`))))
      + caption(copy.partialFootnote)
      + chart("week_components", explain("week_components"))
      + slot("week.days_title", built["week.days_title"] ?? "")
      + grid([days("screen_min"), days("night_min")])
      + slot("week.table", built["week.table"] ?? "")
      + slot("week.emitted_title", built["week.emitted_title"] ?? "")
      + slot("week.emissions", built["week.emissions"] ?? "")
      + slot("week.held", built["week.held"] ?? "")
      + reading(ctx);
  },
};
