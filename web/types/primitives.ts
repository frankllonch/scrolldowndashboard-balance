/**
 * The vocabulary every other type is built from.
 *
 * Each union is asserted against the core in `tests/test_emit.py`: if
 * `CATEGORIES` in `balance/events.py` grows a member, that test fails until
 * this file grows it too.
 */

/** ISO date, `YYYY-MM-DD`. */
export type Day = string;

/** Profile identifier. Two in this dataset; nothing assumes that count. */
export type UserId = string;

/** Monday is 0. The frames carry Python's convention and the page keeps it. */
export type Weekday = 0 | 1 | 2 | 3 | 4 | 5 | 6;

/** The five index components, keyed by the column each one scores. */
export type ComponentKey =
  | "screen_min"
  | "pickups"
  | "night_min"
  | "longest_offline_h"
  | "distract_share";

export type Category =
  | "MESSAGING" | "SOCIAL_MEDIA" | "ENTERTAINMENT" | "GAMING" | "NEWS"
  | "SHOPPING" | "ADULT" | "GAMBLING" | "CALLS" | "NAVIGATION"
  | "PRODUCTIVITY" | "AI_TOOLS" | "REFERENCE" | "LEARNING" | "OTHER";

export type BlockType = "APP" | "URL" | "NUDITY";

/** What the rules decided to do with a signal. */
export type Decision = "sent" | "summary" | "discarded" | "candidate";

export type Tone = "alert" | "reinforcement";
