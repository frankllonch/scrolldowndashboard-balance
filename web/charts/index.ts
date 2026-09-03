/**
 * Every figure on the page, by the key its mount point names.
 *
 * This replaces two Python modules at once: the half of `payload.py` that
 * built figures, and `profiles.py`, which held the surface each was drawn for.
 * They are together here because they are one decision — what a figure is and
 * what ground it sits on — and splitting them meant reading two files to
 * answer one question.
 */

import { axis as unit, title } from "../copy/figures";
import { surface, type SurfaceName } from "../theme";
import type { Payload, Profile, UserId } from "../types/index";
import {
  blocksByHour, blocksDaily, categoryArea, hourHeat, topBars,
} from "./composition";
import type { Figure } from "./plotly";
import {
  scoreBreakdown, scoreLine, weekComponents, weekDays, weekEvolution,
} from "./score";
import { compareLine, dailyBarsVsBaseline, daySpan, nightDrift,
         type Frames } from "./series";
import { trackedSeries } from "./walkthrough";

/**
 * Which ground a figure is drawn on.
 *
 * Acts 01 to 04 sit on paper, act 05 on the warm olive between paper and
 * night, the rest on near-black.
 */
const LIGHT = new Set(["score_line", "week_components"]);
const LIGHT_PREFIXES = ["week_evolution.", "week_days."];
const DUSK = new Set(["hour_heat", "day_span", "daily_bars.screen_min",
                      "daily_bars.pickups"]);

/** Which of the three grounds a figure is drawn for. A figure carries its
 *  surface's colours from the moment it is built, so this decides them. */
export function surfaceFor(key: string): SurfaceName {
  if (LIGHT.has(key) || LIGHT_PREFIXES.some((p) => key.startsWith(p))) {
    return "light";
  }
  return DUSK.has(key) ? "dusk" : "dark";
}

/** What the sliders are pointing at when a figure is built. */
export interface Selection {
  user: UserId;
  week: number;
  day: string;
}

/** The four measures the week bars step through. */
const WEEK_MEASURES = {
  screen_min: { heading: title.weekScreen, unit: unit.min },
  night_min: { heading: title.weekNight, unit: unit.min },
  pickups: { heading: title.weekPickups, unit: "" },
  blocks: { heading: title.weekBlocks, unit: "" },
} as const;

/** The five measures both profiles are compared on. */
const COMPARE_MEASURES = {
  screen_min: { heading: title.screenPerDay, unit: unit.minutes },
  pickups: { heading: title.pickupsPerDay, unit: unit.unlocks },
  night_min: { heading: title.nightPerDay, unit: unit.minutes },
  blocks: { heading: title.blocksPerDay, unit: unit.blocks },
  night_pickups: { heading: title.nightPickups, unit: unit.unlocks },
} as const;

function frames(payload: Payload): Frames {
  const out: Frames = {};
  for (const [user, profile] of Object.entries(payload.profiles)) {
    out[user] = profile.daily;
  }
  return out;
}

/**
 * Build the figure a mount point asks for.
 *
 * Returns null for a key with nothing behind it — a blocks chart on a profile
 * the filter never acted for — so the caller can leave the mount empty rather
 * than draw an empty axis.
 */
export function build(key: string, payload: Payload, profile: Profile,
                      selection: Selection): Figure | null {
  const s = surface(surfaceFor(key));
  const { user } = selection;
  const [head, ...rest] = key.split(".");

  switch (head) {
    case "score_line":
      return scoreLine(s, frames(payload));
    case "night_drift":
      return nightDrift(s, frames(payload));
    case "score_breakdown": {
      const who = rest[0] ?? user;
      const target = payload.profiles[who];
      return target ? scoreBreakdown(s, target.daily, who) : null;
    }
    case "compare": {
      const measure = rest[0] as keyof typeof COMPARE_MEASURES | undefined;
      if (!measure || !(measure in COMPARE_MEASURES)) return null;
      const { heading, unit: label } = COMPARE_MEASURES[measure];
      return compareLine(s, frames(payload), measure, heading, label);
    }
    case "week_components":
      return weekComponents(s, profile.weekly, selection.week);
    case "week_evolution": {
      const measure = rest[0] as keyof typeof WEEK_MEASURES | undefined;
      if (!measure || !(measure in WEEK_MEASURES)) return null;
      const { heading, unit: label } = WEEK_MEASURES[measure];
      return weekEvolution(s, profile.weekly, measure, heading, label, user,
                           selection.week);
    }
    case "week_days": {
      // `week_days.night_min.3` names its own week, so one mount can be
      // re-pointed as the slider moves without rebuilding the page.
      const measure = rest[0];
      const week = rest[1] ? Number(rest[1]) : selection.week;
      if (measure !== "screen_min" && measure !== "night_min") return null;
      const heading = measure === "screen_min"
        ? title.weekDaysScreen(week) : title.weekDaysNight(week);
      return weekDays(s, profile.daily, week, measure, heading, unit.min, user);
    }
    case "daily_bars": {
      const measure = rest[0];
      if (measure === "screen_min") {
        return dailyBarsVsBaseline(s, profile.daily, "screen_min",
                                   "screen_min_baseline",
                                   title.dayScreen(user), unit.minutes, user);
      }
      if (measure === "pickups") {
        return dailyBarsVsBaseline(s, profile.daily, "pickups",
                                   "pickups_baseline",
                                   title.dayPickups(user), unit.unlocks, user);
      }
      return null;
    }
    case "hour_heat":
      return hourHeat(s, profile.hourHeat, user);
    case "day_span":
      // The same figure appears twice: once in the day, once in the night,
      // where it belongs to that act and is drawn for its ground.
      return daySpan(s, profile.daily, user);
    case "top_bars": {
      const which = rest[0];
      if (which === "apps") {
        return topBars(s, profile.apps, title.apps(user));
      }
      if (which === "sites") {
        return topBars(s, profile.sites, title.domains(user));
      }
      return null;
    }
    case "category_area":
      return categoryArea(s, profile.categoryDaily, title.categories(user));
    case "blocks_daily":
      return profile.blocks.total
        ? blocksDaily(s, profile.blocks, title.blocksDaily(user)) : null;
    case "blocks_by_hour":
      return profile.blocks.total
        ? blocksByHour(s, profile.blocks, title.blocksHour(user)) : null;
    case "tracked_series":
      return trackedSeries(s, profile.daily, profile.replay, selection.day);
    default:
      return null;
  }
}
