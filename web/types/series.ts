/**
 * The time series: one row per day, per week, per app, per cell.
 *
 * The unit is in the name — `_min`, `_h`, `_s`, `_share` — because nothing
 * arrives pre-formatted and whoever reads the field has to know what it is.
 */

import type { BlockType, Category, Day, Weekday } from "./primitives";

/** One row per day. */
export interface DailyRow {
  day: Day;
  dow: Weekday;
  is_weekend: boolean;
  week: number;
  /** A day the file cuts short. It leaves every average but still counts
   *  towards the night before it. */
  is_partial: boolean;

  screen_min: number;
  sessions: number;
  median_session_s: number;

  /** A screen-on with an unlock behind it. */
  pickups: number;
  /** A screen-on with no unlock: it lit, it never opened. */
  glances: number;
  first_pickup_h: number | null;
  /** Epoch milliseconds. The hour above is what the charts plot; a clock face
   *  is written from this, because truncating a decimal hour to minutes loses
   *  one. */
  first_pickup_ms: number | null;

  last_use_h: number | null;
  last_use_ms: number | null;
  /** Minutes between 23:00 and 06:00 the next morning. */
  night_min: number;
  night_pickups: number;
  night_end_h: number | null;

  longest_offline_h: number;
  /** Where the longest break started, already worded: "Saturday morning". */
  longest_offline_when: string | null;

  distinct_apps: number;
  switches_per_screen_hour: number;
  /** Social + entertainment + gaming over attributed time, 0 to 1. */
  distract_share: number;

  blocks: number;
  blocks_sensitive: number;

  /** This user's own rolling 14-day median. Null over the first two weeks. */
  screen_min_baseline: number | null;
  pickups_baseline: number | null;

  /** Each component scored 0 to 100 before weighting. */
  score_screen_min: number;
  score_pickups: number;
  score_night_min: number;
  score_longest_offline_h: number;
  score_distract_share: number;
  /** The weighted total, 0 to 100. */
  score: number;
  /** 7-day rolling mean of `score`. Null until there are three days. */
  score_7d: number | null;
}

/** One row per week. A week is the Nth block of seven days from the first day
 *  in the log, so week 1 opens on whatever weekday that is. */
export interface WeeklyRow {
  week: number;
  days: number;
  start: Day;
  end: Day;
  /** Shorter than seven days: its averages are per day, but comparing it to a
   *  full week is not fair, and the page marks it. */
  is_partial: boolean;

  screen_min: number;
  pickups: number;
  night_min: number;
  night_pickups: number;
  night_end_h: number | null;
  first_pickup_h: number | null;
  longest_offline_h: number;
  best_offline_h: number;
  best_offline_when: string | null;
  distinct_apps: number;
  switches_per_screen_hour: number;
  distract_share: number;
  blocks: number;
  blocks_total: number;
  blocks_sensitive: number;
  score: number;


  /** Component scores averaged over the week. */
  score_screen_min: number;
  score_pickups: number;
  score_night_min: number;
  score_longest_offline_h: number;
  score_distract_share: number;
}

/** One app or one domain over the whole period. */
export interface UsageTotal {
  /** Package name or bare domain. Never shown; it is the identity. */
  key: string;
  /** What the reader sees: "WhatsApp", "elpais.com". */
  label: string;
  category: Category;
  minutes: number;
  opens: number;
  min_per_open: number;
}

/** Minutes per category and day, for the stacked area. */
export interface CategoryDay {
  day: Day;
  category: Category;
  minutes: number;
}

/** Screen minutes per weekday and hour: the usage clock. */
export interface HeatCell {
  dow: Weekday;
  hour: number;
  minutes: number;
}

/** Blocked attempts, already tallied. Nothing here ever opened, and nothing
 *  displays a single attempt: every view of them is a count. */
export interface Blocks {
  total: number;
  byDay: Array<{ day: Day; category: Category; count: number }>;
  byHour: Array<{ hour: number; category: Category; count: number }>;
  byWeek: Array<{ week: number; category: Category; count: number }>;
  byType: Partial<Record<BlockType, number>>;
  /** The ten targets the filter stopped most. Device-side only: it never
   *  reaches a notification, and only this reader's own page shows it. */
  top: Array<{ target: string; block_type: BlockType; count: number }>;
}
