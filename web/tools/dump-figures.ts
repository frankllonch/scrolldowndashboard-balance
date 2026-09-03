/**
 * Build every figure and print it as JSON.
 *
 * This exists so the port can be checked rather than eyeballed:
 * `tests/test_figures.py` runs it and compares each trace against the one the
 * Python builders produce. It is a tool, not part of the page.
 */

/** The one node global this tool needs. Declaring it beats a dependency on
 *  the whole of `@types/node` for a file that never ships. */
declare const process: { stdout: { write(text: string): void } };

import raw from "../../docs/data.json";
import { build, surfaceFor } from "../charts/index";
import type { Payload } from "../types/index";

const payload = raw as unknown as Payload;

/** Every figure key the page mounts, in the order the acts ask for them. */
function keys(payload: Payload, user: string): string[] {
  const profile = payload.profiles[user];
  if (!profile) throw new Error(`no profile ${user}`);
  const weeks = profile.weekly.map((w) => w.week);
  return [
    "score_line", "night_drift",
    ...payload.meta.profiles.map((u) => `score_breakdown.${u}`),
    ...["screen_min", "pickups", "night_min", "blocks", "night_pickups"]
      .map((m) => `compare.${m}`),
    "week_components",
    ...["screen_min", "night_min", "pickups", "blocks"]
      .map((m) => `week_evolution.${m}`),
    ...weeks.flatMap((w) => [`week_days.screen_min.${w}`,
                             `week_days.night_min.${w}`]),
    "daily_bars.screen_min", "daily_bars.pickups",
    "hour_heat", "day_span", "day_span.night",
    "top_bars.apps", "top_bars.sites", "category_area",
    "tracked_series", "blocks_daily", "blocks_by_hour",
  ];
}

const out: Record<string, unknown> = {};
for (const user of payload.meta.profiles) {
  const profile = payload.profiles[user];
  if (!profile) continue;
  const selection = { user, week: profile.defaultWeek, day: profile.defaultDay };
  for (const key of keys(payload, user)) {
    const figure = build(key, payload, profile, selection);
    if (figure) {
      out[`${user}/${key}`] = { ...figure, surface: surfaceFor(key) };
    }
  }
}
process.stdout.write(JSON.stringify(out));
