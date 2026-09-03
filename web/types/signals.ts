/**
 * What the phone worked out, and what it decided to do about it.
 *
 * Everything here runs on the device and is read by the person holding it.
 * A signal's `evidence` never leaves it.
 */

import type { Day, Decision, Tone } from "./primitives";

/** A candidate alert or reinforcement, and what became of it. */
export interface Signal {
  key: string;
  /** First day the rule holds. */
  day: Day;
  /** Last day of the episode, where it runs on. */
  until: Day | null;
  decision: Decision;
  /** Why it was sent, held or dropped. Written for a reader, not a log. */
  reason: string;
  /** magnitude × persistence × actionability, 0 to 1. */
  priority: number;
  tone: Tone;
  headline: string;
  /** The notification text itself. Never names an app or a domain. */
  body: string;
  /** The figures behind it. Stays on the device; never in a notification. */
  evidence: Record<string, string | number>;
}

/** What the on-device night nudge would have done, replayed over one night. */
export interface Nudge {
  day: Day;
  fired: boolean;
  /** Epoch milliseconds it would have appeared. Null when it did not. */
  at_ms: number | null;
  /** Why it stayed quiet, where it did. */
  quiet_reason: string;
  reopens: number;
  /** Night screen time after the trigger: what was at stake. */
  minutes_after: number;
  night_minutes: number;
}

export interface NudgeSummary {
  nights: number;
  nights_with_a_nudge: number;
  appearance_rate: number;
  total_night_minutes: number;
  minutes_at_stake_after_the_nudge: number;
  share_of_night_total: number;
  minutes_at_stake_per_nudged_night: number;
  /** Null where the nudge never fired: the median of nothing is not zero,
   *  and user A genuinely has no night to take a median of. */
  median_nudge_time: number | null;
}

/** The state at the close of one day, knowing only what had happened by then. */
export interface ReplayDay {
  day: Day;
  alert: Signal | null;
  digest_entry: Signal | null;
  positives: Signal[];
  nudge: Nudge | null;
  alerts_so_far: number;
  positives_so_far: number;
  digest_so_far: number;
  nudges_so_far: number;
}

/** One thing the phone actually emitted, in time order. */
export interface Emission {
  day: Day;
  /** "User · screen", "User · alert", "Weekly summary". */
  destination: string;
  type: string;
  detail: string;
}
