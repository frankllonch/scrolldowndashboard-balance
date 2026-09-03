/**
 * The line under every chart.
 *
 * Keyed by figure, and resolved by walking the key from the most specific name
 * to the least — `week_days.night_min.3` falls back through
 * `week_days.night_min` to `week_days` — so a variant inherits its family's
 * line and a new one cannot ship bare.
 */

const EXPLANATIONS: Record<string, string> = {
  score_line:
    "Both people's wellbeing index, every day of the month. The line is a "
    + "7-day average so it does not jump around; the faint dots behind it are "
    + "the actual daily scores.",

  "week_evolution.screen_min":
    "Your average screen time per day, week by week. The highlighted bar is "
    + "the week you have selected.",
  "week_evolution.night_min":
    "The same weeks, but only the minutes between 23:00 and 06:00. Watch this "
    + "one against the bar chart beside it.",
  "week_evolution.pickups":
    "How many times a day you really unlocked the phone, week by week. A "
    + "screen that lit up without being unlocked is a glance, and is not "
    + "counted here.",
  "week_evolution.blocks":
    "How many attempts the filter stopped per day, week by week. Rising bars "
    + "mean the phone is being asked more often, not that more is getting "
    + "through.",

  week_components:
    "The five parts of the index, scored 0 to 100, week by week. The dotted "
    + "line marks the week you have selected. A part that falls here is a part "
    + "that is pulling your score down.",

  "week_days.screen_min":
    "Screen time for each day of the week you picked, Monday to Sunday. The "
    + "dotted line is your average across every week before this one, so a bar "
    + "above it is a day above your own normal.",
  "week_days.night_min":
    "The same seven days, counting only what happened after 23:00. Most weeks "
    + "this should be a flat row of nothing.",

  "daily_bars.screen_min":
    "Your screen time on every day of the month, against your own rolling "
    + "14-day median — not against the other user, and not against a target. "
    + "The first two weeks have no history to compare with yet.",
  "daily_bars.pickups":
    "The same thirty days, counting unlocks instead of minutes. A day can sit "
    + "under your median for time and over it for unlocks: that is a day you "
    + "checked the phone a lot without settling into it.",

  hour_heat:
    "Your week as a grid: days down, hours across. The darker the cell, the "
    + "more screen time in that hour. It shows the shape of your week at a "
    + "glance — where the phone lives in your day.",

  day_span:
    "One bar per day, running from your first unlock to your last screen. It "
    + "is not how much you used the phone, it is how much of the day the phone "
    + "was part of.",
  "day_span.night":
    "The same day-length bars, with the 23:00 to 06:00 band marked. What you "
    + "are looking for is bars leaking into the band.",

  night_drift:
    "Screen minutes between 23:00 and 06:00, night by night, for both people. "
    + "This is the single chart the whole month turns on.",

  "compare.night_pickups":
    "Unlocks after midnight, both people on the same scale. One of these two "
    + "lines stays on the floor for thirty days.",
  "compare.screen_min":
    "Total screen time per day for both people, week 1 to the last. This is "
    + "the measure a plain screen-time rule would watch — and it barely moves.",
  "compare.night_min":
    "The same weeks, same scale, but only the night band. This is the measure "
    + "that moves, and it is why watching the total would have missed the whole "
    + "month.",

  "top_bars.apps":
    "Your ten biggest apps by minutes. Colour is the content category; hover "
    + "for how many times you opened each one.",
  "top_bars.sites":
    "The same, for websites. Only the domain is ever recorded, never the page "
    + "— so time spent in the browser lands here rather than under Chrome.",

  category_area:
    "What your minutes were made of, day by day, stacked. The order of the "
    + "bands is fixed, so a band that grows really is growing and has not just "
    + "been re-ranked.",

  blocks_daily:
    "How many attempts the filter stopped each day, split by what kind. "
    + "Nothing here opened — a block is an attempt that went nowhere.",
  blocks_by_hour:
    "What time of day you hit the wall. Sensitive attempts are drawn "
    + "separately from ordinary distraction.",

  tracked_series:
    "Every variable the alert rules watch, on one axis. Each is drawn as a "
    + "share of its own maximum, so shapes can be compared even though the "
    + "units cannot. The rail below zero is what the phone actually did that "
    + "day.",

  "score_breakdown.A":
    "Where A's index came from: what each of the five parts contributed on an "
    + "average day, and how many points it let go.",
  "score_breakdown.B":
    "The same breakdown for B. Compare the bars, not the totals — the gap "
    + "between the two people is one component doing most of the work.",
};

/** The line for a figure. Throws rather than shipping a bare chart. */
export function explain(key: string): string {
  const parts = key.split(".");
  while (parts.length) {
    const found = EXPLANATIONS[parts.join(".")];
    if (found) return found;
    parts.pop();
  }
  throw new Error(`no explanation for figure ${key}`);
}
