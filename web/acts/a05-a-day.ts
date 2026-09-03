/**
 * Act 05 · the daily rhythm. Passive: one month of days, on one screen.
 */

import { explain } from "../copy/explain";
import { unit } from "../copy/units";
import { clockAt, hm } from "../format";
import { caption, chart, grid, kpis, note } from "../html";
import type { DailyRow } from "../types/index";
import { other, type Act, type Context } from "./act";

const copy = {
  eyebrow: "Hour by hour",
  title: "A day in the life",

  kpi: {
    screen: "Screen / day",
    screenDelta: (sd: number) => `±${sd.toFixed(0)} min`,
    sessions: "Sessions / day",
    sessionsDelta: (median: number) => `median ${median.toFixed(1)} min`,
    pickups: "Real unlocks",
    pickupsDelta: (glances: number) => `${glances.toFixed(0)} glances`,
    firstPickup: "First unlock",
    firstPickupDelta: (median: number) => `median ${median.toFixed(1)} h`,
    offline: "Longest break",
    offlineDelta: (best: number, when: string) =>
      `best ${best.toFixed(1)} h, ${when}`,
    switches: "App switches / h",
    switchesDelta: (apps: number) => `${apps.toFixed(0)} distinct apps`,
  },

  baseline: "Against this user's own 14-day median. The first two weeks have "
    + "no history.",

  readingA: (weekday: number, weekend: number, lastUse: string) =>
    `A working week with a weekend in it: ${weekday.toFixed(0)} min on `
    + `weekdays, ${weekend.toFixed(0)} at weekends, last screen around `
    + `${lastUse}, nothing after 23:00 on any day.`,

  readingB: (weekend: number, weekday: number, switches: number,
             session: number, ratio: number) =>
    `Your weekend looks like your Tuesday. ${weekend.toFixed(0)} min at `
    + `weekends against ${weekday.toFixed(0)} on weekdays, and you are on the `
    + "phone from 08:00 to midnight all seven days. You pick it up "
    + `${switches.toFixed(0)} times an hour and stay about `
    + `${session.toFixed(1)} minutes each time — you are checking the phone, `
    + `not sitting down with it (${ratio.toFixed(1)} times more than A's rate `
    + "of usage).",

  next: "The daytime looks ordinary enough. But what happens when we turn "
    + "the lights off?",
};

function mean(values: number[]): number {
  return values.reduce((a, b) => a + b, 0) / (values.length || 1);
}

function sd(values: number[]): number {
  if (values.length < 2) return 0;
  const m = mean(values);
  const variance = values.reduce((a, v) => a + (v - m) ** 2, 0)
    / (values.length - 1);
  return Math.sqrt(variance);
}

/**
 * The most common value, which is what a "usual" first unlock means.
 *
 * A tie goes to the smallest, which for a clock face is the earliest. Every
 * value being unique is a tie between all of them, and picking whichever came
 * first in the frame would make the answer depend on row order.
 */
function mode(values: string[]): string {
  const counts = new Map<string, number>();
  for (const v of values) counts.set(v, (counts.get(v) ?? 0) + 1);
  let best = "";
  let most = -1;
  for (const [v, n] of [...counts.entries()].sort((a, b) =>
    a[0].localeCompare(b[0]))) {
    if (n > most) { best = v; most = n; }
  }
  return best;
}

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  if (!sorted.length) return 0;
  return sorted.length % 2 ? (sorted[mid] ?? 0)
    : ((sorted[mid - 1] ?? 0) + (sorted[mid] ?? 0)) / 2;
}

function present(rows: DailyRow[], key: "first_pickup_h" | "last_use_h"): number[] {
  return rows.map((r) => r[key]).filter((v): v is number => v !== null);
}

function strip(rows: DailyRow[]): string {
  const bestDay = rows.reduce((best, r) =>
    (r.longest_offline_h > best.longest_offline_h ? r : best), rows[0]!);
  return kpis([
    { label: copy.kpi.screen, value: hm(mean(rows.map((r) => r.screen_min))),
      delta: copy.kpi.screenDelta(sd(rows.map((r) => r.screen_min))) },
    { label: copy.kpi.sessions,
      value: mean(rows.map((r) => r.sessions)).toFixed(0),
      delta: copy.kpi.sessionsDelta(
        mean(rows.map((r) => r.median_session_s)) / 60) },
    { label: copy.kpi.pickups,
      value: mean(rows.map((r) => r.pickups)).toFixed(0),
      delta: copy.kpi.pickupsDelta(mean(rows.map((r) => r.glances))) },
    { label: copy.kpi.firstPickup,
      value: mode(rows.map((r) => clockAt(r.first_pickup_ms))),
      delta: copy.kpi.firstPickupDelta(
        median(present(rows, "first_pickup_h"))) },
    { label: copy.kpi.offline,
      value: `${mean(rows.map((r) => r.longest_offline_h)).toFixed(1)} `
        + unit.hours,
      delta: copy.kpi.offlineDelta(bestDay.longest_offline_h,
                                   bestDay.longest_offline_when ?? "") },
    { label: copy.kpi.switches,
      value: mean(rows.map((r) => r.switches_per_screen_hour)).toFixed(0),
      delta: copy.kpi.switchesDelta(
        mean(rows.map((r) => r.distinct_apps))) },
  ]);
}

function reading(ctx: Context): string {
  const rows = ctx.profile.daily;
  const weekend = mean(rows.filter((r) => r.is_weekend).map((r) => r.screen_min));
  const weekday = mean(rows.filter((r) => !r.is_weekend).map((r) => r.screen_min));
  const switches = mean(rows.map((r) => r.switches_per_screen_hour));
  const session = mean(rows.map((r) => r.median_session_s)) / 60;

  if (ctx.user === "A") {
    return note(copy.readingA(weekday, weekend,
                              mode(rows.map((r) => clockAt(r.last_use_ms)))),
                "good");
  }
  const them = other(ctx);
  const reference = them
    ? mean(them.daily.map((r) => r.switches_per_screen_hour)) : switches;
  return note(copy.readingB(weekend, weekday, switches, session,
                            switches / (reference || 1)), "warn");
}

export const act: Act = {
  id: "05",
  part: 2,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build(ctx: Context): string {
    return strip(ctx.profile.daily)
      + grid([chart("daily_bars.screen_min", explain("daily_bars.screen_min")),
              chart("daily_bars.pickups", explain("daily_bars.pickups"))])
      + caption(copy.baseline)
      + grid([chart("hour_heat", explain("hour_heat")),
              chart("day_span", explain("day_span"))])
      + reading(ctx);
  },
};
