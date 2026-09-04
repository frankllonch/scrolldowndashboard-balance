/**
 * Every figure on the page, by the key its mount point names.
 *
 * What a figure is and what ground it sits on are one decision, so they live
 * in one file. Splitting them means reading two to answer one question.
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
function surfaceFor(key: string): SurfaceName {
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

/** The two measures the day bars step through, against their own baseline. */
const DAILY_MEASURES = {
  screen_min: { baseline: "screen_min_baseline", title: title.dayScreen,
                unit: unit.minutes },
  pickups: { baseline: "pickups_baseline", title: title.dayPickups,
             unit: unit.unlocks },
} as const;

/** The two rankings, and which list each one ranks. */
const RANKINGS = {
  apps: { series: "apps", title: title.apps },
  sites: { series: "sites", title: title.domains },
} as const;

/** The two week-by-day panels. */
const WEEK_DAYS = {
  screen_min: title.weekDaysScreen,
  night_min: title.weekDaysNight,
} as const;

/** The five measures both profiles are compared on. */
const COMPARE_MEASURES = {
  screen_min: { heading: title.screenPerDay, unit: unit.minutes },
  pickups: { heading: title.pickupsPerDay, unit: unit.unlocks },
  night_min: { heading: title.nightPerDay, unit: unit.minutes },
  blocks: { heading: title.blocksPerDay, unit: unit.blocks },
  night_pickups: { heading: title.nightPickups, unit: unit.unlocks },
} as const;

/** The part of a figure key after the family name, if the family knows it.
 *  A key naming something that is not there returns nothing, and the mount is
 *  left empty rather than drawn wrong. */
function pick<T extends object>(table: T, name: string | undefined):
    keyof T | undefined {
  return name && name in table ? (name as keyof T) : undefined;
}


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
      const measure = pick(COMPARE_MEASURES, rest[0]);
      if (!measure) return null;
      const { heading, unit: label } = COMPARE_MEASURES[measure];
      return compareLine(s, frames(payload), measure, heading, label);
    }
    case "week_components":
      return weekComponents(s, profile.weekly, selection.week);
    case "week_evolution": {
      const measure = pick(WEEK_MEASURES, rest[0]);
      if (!measure) return null;
      const { heading, unit: label } = WEEK_MEASURES[measure];
      return weekEvolution(s, profile.weekly, measure, heading, label, user,
                           selection.week);
    }
    case "week_days": {
      // `week_days.night_min.3` names its own week, so one mount can be
      // re-pointed as the slider moves without rebuilding the page.
      const measure = pick(WEEK_DAYS, rest[0]);
      if (!measure) return null;
      const week = rest[1] ? Number(rest[1]) : selection.week;
      return weekDays(s, profile.daily, week, measure, WEEK_DAYS[measure](week),
                      unit.min, user);
    }
    case "daily_bars": {
      const measure = pick(DAILY_MEASURES, rest[0]);
      if (!measure) return null;
      const spec = DAILY_MEASURES[measure];
      return dailyBarsVsBaseline(s, profile.daily, measure, spec.baseline,
                                 spec.title(user), spec.unit, user);
    }
    case "hour_heat":
      return hourHeat(s, profile.hourHeat, user);
    case "day_span":
      // The same figure appears twice: once in the day, once in the night,
      // where it belongs to that act and is drawn for its ground.
      return daySpan(s, profile.daily, user);
    case "top_bars": {
      const which = pick(RANKINGS, rest[0]);
      if (!which) return null;
      const spec = RANKINGS[which];
      return topBars(s, profile[spec.series], spec.title(user));
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
