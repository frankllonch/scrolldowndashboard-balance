/**
 * Act 08 · what the filter stopped, and how little of it is named.
 */

import { CATEGORY_LABEL } from "../copy/figures";
import { explain } from "../copy/explain";
import { chart, grid, kpis, note, table, tags } from "../html";
import { thousands } from "../format";
import { CATEGORY_ORDER } from "../theme";
import type { Category, Profile } from "../types/index";
import type { Act, Context } from "./act";

const SENSITIVE: Category[] = ["ADULT", "GAMBLING"];

const copy = {
  eyebrow: "The filter",
  title: "What the phone stopped",

  deviceOnly: "device only",
  aggregateOnly: "only the aggregate is ever named",
  none: "No blocks in the period.",

  kpi: {
    attempts: "Blocked attempts",
    attemptsDelta: (perDay: number) => `${perDay.toFixed(1)} per day`,
    apps: "Apps blocked",
    sites: "Sites blocked",
    nudity: "Nudity detection",
    nudityDelta: "on device",
    sensitive: "Adult + gambling",
    sensitiveDelta: (share: number) =>
      `${share.toFixed(0)} % of the total`,
    opened: "Ever opened",
    openedDelta: "of the sensitive",
  },

  weekColumn: (week: number, days: number) => `Week ${week} (${days} d)`,
  metric: "Metric",

  readingA: (total: number, first: number, last: number) =>
    `${thousands(total)} attempts in thirty days, all social and `
    + "entertainment, no sensitive content. The filter steps in less as the "
    + `month goes on, ${first.toFixed(0)} to ${last.toFixed(0)} a week.`,

  readingB: (ordinary: number, first: number, last: number, adult: number,
             gambling: number, nudity: number, mid: number, sensitive: number,
             weekFour: number) =>
    `${thousands(ordinary)} ordinary attempts, ${first.toFixed(0)} to `
    + `${last.toFixed(0)} a week, plus ${adult} adult and ${gambling} `
    + `gambling and ${nudity} detections. None opened. The sensitive ones `
    + `spike rather than trend: ${mid} of ${sensitive} land in weeks 2 and 3 `
    + `and ${weekFour} in week 4. That is a summary entry, not a phone call.`,

  scope: (sensitive: number) =>
    "This screen stays on the device. The weekly summary carries the filter's "
    + `state and that <b>${sensitive} sensitive attempts were blocked and none `
    + "opened</b>. Nothing named.",

  next: "The phone knew all of this. Here is what it decided to say about it, "
    + "and what it kept to itself.",
};

function sensitiveTotal(profile: Profile): number {
  return profile.blocks.byDay
    .filter((r) => SENSITIVE.includes(r.category))
    .reduce((sum, r) => sum + r.count, 0);
}

function byCategory(profile: Profile, category: Category): number {
  return profile.blocks.byDay.filter((r) => r.category === category)
    .reduce((sum, r) => sum + r.count, 0);
}

function strip(profile: Profile): string {
  const blocks = profile.blocks;
  const days = profile.daily.length || 1;
  const sensitive = sensitiveTotal(profile);
  return kpis([
    { label: copy.kpi.attempts, value: thousands(blocks.total),
      delta: copy.kpi.attemptsDelta(blocks.total / days) },
    { label: copy.kpi.apps, value: thousands(blocks.byType.APP ?? 0) },
    { label: copy.kpi.sites, value: thousands(blocks.byType.URL ?? 0) },
    { label: copy.kpi.nudity, value: thousands(blocks.byType.NUDITY ?? 0),
      delta: copy.kpi.nudityDelta },
    { label: copy.kpi.sensitive, value: thousands(sensitive),
      delta: copy.kpi.sensitiveDelta(
        sensitive / Math.max(blocks.total, 1) * 100) },
    { label: copy.kpi.opened, value: "0", delta: copy.kpi.openedDelta },
  ]);
}

/**
 * Attempts by category and week.
 *
 * The month does not fall into 7-day weeks — the last is a 2-day tail — and
 * the column headers say how long each was, or blocks look like they collapse
 * at the end.
 */
function weekTable(profile: Profile): string {
  const weeks = profile.weekly.map((w) => w.week);
  const found = new Set(profile.blocks.byWeek.map((r) => r.category));
  const order = CATEGORY_ORDER.filter((c) => found.has(c));
  const counts = new Map(profile.blocks.byWeek
    .map((r) => [`${r.week}|${r.category}`, r.count]));
  const columns = [copy.metric, ...profile.weekly
    .map((w) => copy.weekColumn(w.week, w.days))];
  const rows = order.map((category) => [
    CATEGORY_LABEL[category],
    ...weeks.map((week) => String(counts.get(`${week}|${category}`) ?? 0)),
  ]);
  return table(columns, rows);
}

function reading(ctx: Context): string {
  const { profile, user } = ctx;
  const weekBlocks = (n: number) => profile.daily
    .filter((d) => d.week === n)
    .reduce((sum, d) => sum + d.blocks, 0);
  const sensitive = sensitiveTotal(profile);

  if (user === "A") {
    return note(copy.readingA(profile.blocks.total, weekBlocks(1),
                              weekBlocks(4)), "good");
  }
  const sensitiveWeek = (n: number) => profile.blocks.byWeek
    .filter((r) => r.week === n && SENSITIVE.includes(r.category))
    .reduce((sum, r) => sum + r.count, 0);
  return note(copy.readingB(
    profile.blocks.total - sensitive, weekBlocks(1), weekBlocks(4),
    byCategory(profile, "ADULT"), byCategory(profile, "GAMBLING"),
    profile.blocks.byType.NUDITY ?? 0,
    sensitiveWeek(2) + sensitiveWeek(3), sensitive, sensitiveWeek(4)), "warn");
}

export const act: Act = {
  id: "08",
  part: 2,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build(ctx: Context): string {
    const { profile } = ctx;
    if (!profile.blocks.total) return note(copy.none);
    return tags(copy.deviceOnly, copy.aggregateOnly)
      + strip(profile)
      + grid([chart("blocks_daily", explain("blocks_daily")),
              chart("blocks_by_hour", explain("blocks_by_hour"))])
      + weekTable(profile)
      + reading(ctx)
      + note(copy.scope(sensitiveTotal(profile)));
  },
};
