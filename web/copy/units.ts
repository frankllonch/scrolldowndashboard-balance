/**
 * Words that are not about any one section: units, and the handful of phrases
 * that stand in for a value the data does not have.
 */

export const unit = {
  min: "min",
  minutes: "minutes",
  hours: "h",
  unlocks: "unlocks",
  blocks: "blocks",
  percent: "%",
} as const;

export const value = {
  noUse: "no use",
  noChange: "no change",
  notAvailable: "n/a",
  noStretch: "no stretch",
  doesNotFire: "does not fire",
} as const;

export const chrome = {
  pageTitle: "Balance · Device event explorer",
  pillLabel: "Reading",
} as const;

/** The three parts the twelve acts group into. */
export const PARTS = ["Setup", "One person's month", "The analysis"] as const;
