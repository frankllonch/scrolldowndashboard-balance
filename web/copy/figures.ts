/**
 * Every word that appears inside a chart.
 *
 * Typed functions rather than a keyed catalogue, so a missing argument is a
 * compile error rather than a blank in the sentence. A template literal and
 * Plotly's `%{...}` do not fight over braces, so both can sit in one string.
 */

import type { Category, UserId } from "../types/index";

// -- titles -----------------------------------------------------------------

export const title = {
  scoreLine: "Digital wellbeing index (7-day mean)",
  scoreBreakdown: (user: UserId) => `User ${user} · where the index comes from`,
  weekComponents: "Index components by week",
  nightDrift: "Screen in the night band (23:00 to 06:00)",
  daySpan: (user: UserId) => `User ${user} · from what time to what time`,
  hourHeat: (user: UserId) => `User ${user} · weekly screen clock`,
  dayScreen: (user: UserId) => `User ${user} · screen per day`,
  dayPickups: (user: UserId) => `User ${user} · unlocks per day`,
  apps: (user: UserId) => `User ${user} · apps by minutes`,
  domains: (user: UserId) => `User ${user} · domains by minutes`,
  categories: (user: UserId) => `User ${user} · minutes by content category`,
  blocksDaily: (user: UserId) => `User ${user} · blocked attempts per day`,
  blocksHour: (user: UserId) => `User ${user} · blocks by hour of day`,
  weekScreen: "Screen per day, by week",
  weekNight: "Late night per night, by week",
  weekPickups: "Unlocks per day, by week",
  weekBlocks: "Blocks per day, by week",
  weekDaysScreen: (week: number) => `Screen per day · week ${week}`,
  weekDaysNight: (week: number) => `Late night per night · week ${week}`,
  screenPerDay: "Screen time per day",
  pickupsPerDay: "Real unlocks per day",
  nightPerDay: "Late-night screen minutes",
  blocksPerDay: "Blocked attempts per day",
  nightPickups: "Unlocks after midnight",
} as const;

// -- axes -------------------------------------------------------------------

export const axis = {
  localTime: "local time",
  minutesRolling: "minutes (3-day rolling mean)",
  minutesMonth: "minutes this month",
  blockedAttempts: "blocked attempts",
  attemptsMonth: "attempts this month",
  points: "points out of 100",
  pctOfMax: "% of the period maximum",
  score: "0 to 100",
  minutes: "minutes",
  min: "min",
  unlocks: "unlocks",
  blocks: "blocks",
} as const;

// -- series and annotations -------------------------------------------------

export const series = {
  user: (user: UserId) => `User ${user}`,
  daily: (user: UserId) => `${user} · daily`,
  dailyPlain: (user: UserId) => `${user} daily`,
  nightFlat: (user: UserId, nights: number) =>
    `User ${user}: 0 min across ${nights} nights`,
  atOrBelow: "At or below your normal",
  above: "Above your normal",
  baseline: "Your normal (14-day median)",
  dayWithPhone: "Day with the phone",
  lastScreenMean: "Last screen (7-day mean)",
  ordinary: "Ordinary distraction",
  sensitive: "Adult / gambling",
  pointsEarned: "Points earned",
  pointsLost: "Points lost",
  week: (week: number) => `Week ${week}`,
} as const;

export const annotation = {
  nightStart: "23:00",
  events: "events",
  prevMean: (mean: number) =>
    `mean of previous weeks: ${Math.round(mean).toLocaleString("en")}`,
  noActivityWeek: "No activity this week",
} as const;

/** A week's short label. The star marks one shorter than seven days. */
export function weekLabel(week: number, partial = false): string {
  return partial ? `W${week} *` : `W${week}`;
}

// -- content categories -----------------------------------------------------

export const CATEGORY_LABEL: Record<Category, string> = {
  SOCIAL_MEDIA: "Social Media",
  MESSAGING: "Messaging",
  ENTERTAINMENT: "Entertainment",
  SHOPPING: "Shopping",
  GAMING: "Gaming",
  ADULT: "Adult",
  NEWS: "News",
  GAMBLING: "Gambling",
  CALLS: "Calls",
  NAVIGATION: "Navigation",
  PRODUCTIVITY: "Productivity",
  LEARNING: "Learning",
  AI_TOOLS: "AI tools",
  REFERENCE: "Research",
  OTHER: "Other",
};

// -- hover templates --------------------------------------------------------
// `%{...}` is Plotly's own interpolation and is left for it to resolve;
// `${...}` is ours and is resolved here.

export const hover = {
  compareDaily: (user: UserId, unit: string) =>
    `%{y:.0f} ${unit}<extra>User ${user}</extra>`,
  compareSmoothed: (user: UserId, unit: string, smooth: number) =>
    `%{y:.0f} ${unit} (${smooth} d mean)<extra>User ${user}</extra>`,
  dayValue: (unit: string) =>
    `%{x|%a %d %b}<br>%{y:.0f} ${unit}<extra></extra>`,
  baseline: (unit: string) => `normal: %{y:.0f} ${unit}<extra></extra>`,
  daySpan:
    "%{x|%a %d %b}<br>from %{customdata[0]} to %{customdata[1]}<extra></extra>",
  nightDrift: (user: UserId) =>
    `%{x|%a %d %b}<br>%{y:.0f} late-night min<extra>User ${user}</extra>`,
  category: (label: string) => `%{y:.0f} min<extra>${label}</extra>`,
  topBars:
    "<b>%{y}</b><br>%{x:.0f} min in total<br>%{customdata[0]} openings · %{customdata[1]:.1f} min per opening<br>%{customdata[2]}<extra></extra>",
  heat: "%{y} · %{x}:00<br>%{z:.0f} min<extra></extra>",
  blocksCategory: (label: string) => `%{y:.0f}<extra>${label}</extra>`,
  blocksHour: (name: string) => `%{x}:00 → %{y:.0f}<extra>${name}</extra>`,
  score: (user: UserId) => `%{y:.0f}/100<extra>User ${user}</extra>`,
  pointsEarned: "%{x:.1f} of %{customdata:.0f} possible<extra></extra>",
  pointsLost: "%{x:.1f} lost<extra></extra>",
  week: (label: string, unit: string) =>
    `%{x}<br>%{y:.1f} ${unit}<extra>${label}</extra>`,
  weekDay: (unit: string) => `%{x}<br>%{y:.0f} ${unit}<extra></extra>`,
  component: (label: string) => `%{y:.0f}/100<extra>${label}</extra>`,
  tracked: (label: string, unit: string, rules: string) =>
    `<b>${label}</b>: %{customdata:.1f} ${unit}<br>${rules}<extra></extra>`,
  event: (detail: string) => `%{x|%d %b}<br>${detail}<extra></extra>`,
} as const;

/** Monday first, matching the `dow` the frames carry. */
export const DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;
