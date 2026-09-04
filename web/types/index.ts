/**
 * The contract between the two halves of this project.
 *
 * Python computes; TypeScript draws. Everything crossing that line is
 * declared here, and both sides are held to it: `npm run typecheck` compiles
 * the emitted document against these declarations, and `tests/test_payload.py`
 * asserts the values sit inside the unions in `primitives.ts`.
 *
 *     primitives.ts  the vocabulary: days, categories, decisions
 *     series.ts      one row per day, per week, per app, per cell
 *     signals.ts     what the phone worked out and what it emitted
 *     index.ts       the summaries, and the document itself
 *
 * Conventions:
 *   · a day is an ISO date string, "2026-05-18"
 *   · minutes and hours are numbers, never pre-formatted strings
 *   · a metric that does not exist is `null`, never NaN and never 0
 *   · nothing here is a label the reader sees; copy lives in `web/copy/`
 */

import type { Day, UserId } from "./primitives";
import type {
  Blocks, CategoryDay, DailyRow, HeatCell, UsageTotal, WeeklyRow,
} from "./series";
import type {
  Emission, Nudge, NudgeSummary, ReplayDay, Signal,
} from "./signals";

export * from "./primitives";
export * from "./series";
export * from "./signals";

/** The headline numbers. Scalars only: whatever a KPI or a sentence needs.
 *
 *  Hours stay hours and minutes stay minutes. The clock face, the "2h 02m"
 *  and the "no use" for a metric user A genuinely does not have are all
 *  wording, and wording is the frontend's. */
export interface Summary {
  user: UserId;
  days: number;
  events: number;
  intervals: number;
  screen_h: number;
  /** Share of screen time that could be attributed to an app or a domain. */
  attributed_pct: number;

  score_mean: number;
  score_min: number;
  score_max: number;
  score_first_week: number;
  score_last_week: number;

  screen_mean: number;
  screen_first_week: number;
  screen_last_week: number;
  pickups_mean: number;
  pickups_first_week: number;
  pickups_last_week: number;
  apps_mean: number;
  blocks_total: number;
  sensitive_total: number;

  night_mean: number;
  night_first_week: number;
  night_last_week: number;
  night_multiple: number;
  night_pickups_first_week: number;
  night_pickups_last_week: number;

  last_use_mean_h: number;
  last_screen_first_week_h: number | null;
  last_screen_last_week_h: number | null;
  wake_first_week_h: number | null;
  wake_last_week_h: number | null;
  sleep_first_week_h: number | null;
  sleep_last_week_h: number | null;

  alerts_sent: number;
  alerts_held: number;
  alert_budget: number;
  positives_sent: number;
  nudge_nights: number;
  nights: number;
  emissions_total: number;

  /** Present only where an app appears in the usage frame despite being
   *  blocked — the filter had an opinion every day and once did not fire. */
  outage?: FilterOutage;
}

/** The stretch where blocking went quiet for the apps that got through. */
export interface FilterOutage {
  /** Days on which the leaked apps were blocked at all. */
  leaked_days: number;
  /** Median blocks a day against them. */
  leaked_median: number;
  /** The day the longest silence began. */
  outage_day: Day;
  /** How long it lasted, measured at hour resolution. */
  outage_hours: number;
  /** Adult and gambling attempts blocked inside that same window, while the
   *  distraction list blocked nothing. The log does not say why. */
  sensitive_during: number;
}

/** What the whole month adds up to: the reveal, and its negative control. */
export interface Finding {
  night_multiple: number;
  screen_change_pct: number;
  pickups_change_pct: number;
  sleep_loss_min: number;
  score_drop: number;
}

export interface Profile {
  summary: Summary;
  daily: DailyRow[];
  weekly: WeeklyRow[];
  apps: UsageTotal[];
  sites: UsageTotal[];
  categoryDaily: CategoryDay[];
  hourHeat: HeatCell[];
  blocks: Blocks;
  alerts: Signal[];
  positives: Signal[];
  nudges: Nudge[];
  nudgeSummary: NudgeSummary;
  replay: ReplayDay[];
  emissions: Emission[];
  /** Things the stream does that the metrics would otherwise get wrong,
   *  counted rather than dropped in silence. */
  anomalies: Record<string, number>;
  /** How many of each event type the log carries. The events themselves never
   *  cross: the page names the types and counts them, nothing more. */
  eventCounts: Record<string, number>;
  /** The day the walkthrough opens on: the first alert, else the last day. */
  defaultDay: Day;
  /** The week the sliders open on: the last full one. */
  defaultWeek: number;
}

export interface Meta {
  profiles: UserId[];
  days: number;
  events: number;
  weeks: number[];
  defaultProfile: UserId;
}

/** Everything the browser is given. No HTML, no figures, no copy. */
export interface Payload {
  meta: Meta;
  finding: Finding;
  profiles: Record<UserId, Profile>;
}
