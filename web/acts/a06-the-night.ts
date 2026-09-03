/**
 * Act 06 · the night band. The only act that changes the surface mid-page.
 */

import { explain } from "../copy/explain";
import { unit } from "../copy/units";
import { clock, maybe } from "../format";
import { chart, grid, kpis, note, type Kpi } from "../html";
import type { Summary } from "../types/index";
import type { Act, Context } from "./act";

const copy = {
  eyebrow: "23:00 to 06:00",
  title: "What happens at night",

  kpi: {
    firstWeek: "Late night, wk 1",
    lastWeek: "Late night, wk 4",
    lastScreenFirst: "Last screen, wk 1",
    lastScreenLast: "Last screen, wk 4",
    firstUnlock: "First unlock",
    sleepWindow: "Sleep window",
  },
  times: (n: number) => `×${n.toFixed(0)}`,
  minutes: (n: number) => `${n > 0 ? "+" : ""}${n.toFixed(0)} min`,

  driftNote: (endFirst: string, endLast: string, wakeFirst: string,
              wakeLast: string, pickLast: number, sleepLoss: number) =>
    `<b>You are losing sleep.</b> You started the month going to bed at `
    + `${endFirst} and ended it averaging ${endLast}, whilst always waking up `
    + `at the same time — ${wakeFirst} then ${wakeLast}. You went from hardly `
    + `unlocking your phone after midnight to doing it nearly `
    + `${pickLast.toFixed(0)} times a night. That is `
    + `<b>${sleepLoss.toFixed(0)} minutes less rest, every night</b>.`,

  userANote: (lastUse: string) =>
    `You only see user B's usage here, because A slept remarkably well throughout the whole of May: zero minutes between 23:00 and 06:00 on all thirty days, last screen at ${lastUse} on average.`,

  weightNote: (night: number, screen: number) =>
    "The night-time usage increase is the main reason your wellbeing score has dropped so much. "
    + `Sleep! It is the smallest number on this page — ${night.toFixed(0)} min a day against ${screen.toFixed(0)} of screen — and it carries 20 % of the index, because an hour at 01:00 comes out of your rest and an hour at 17:00 does not.`,

  next: "Now you know when. The next question is what.",
};

/** A shift in minutes, or nothing where there is no pair to compare. */
function shift(minutes: number | null): string | undefined {
  return minutes === null ? undefined : copy.minutes(minutes);
}

function sleepChange(s: Summary): number | null {
  const { sleep_first_week_h: first, sleep_last_week_h: last } = s;
  return first === null || last === null ? null : (last - first) * 60;
}

function hoursShift(first: number | null, last: number | null): number | null {
  return first === null || last === null ? null : (last - first) * 60;
}

function strip(s: Summary): string {
  const items: Array<[string, string, string | undefined]> = [
    [copy.kpi.firstWeek, `${s.night_first_week.toFixed(0)} ${unit.min}`,
     undefined],
    [copy.kpi.lastWeek, `${s.night_last_week.toFixed(0)} ${unit.min}`,
     copy.times(s.night_multiple)],
    [copy.kpi.lastScreenFirst, clock(s.last_screen_first_week_h), undefined],
    [copy.kpi.lastScreenLast, clock(s.last_screen_last_week_h),
     shift(hoursShift(s.last_screen_first_week_h, s.last_screen_last_week_h))],
    [copy.kpi.firstUnlock, clock(s.wake_last_week_h),
     shift(hoursShift(s.wake_first_week_h, s.wake_last_week_h))],
    [copy.kpi.sleepWindow, maybe(s.sleep_last_week_h, 1, unit.hours),
     shift(sleepChange(s))],
  ];
  return kpis(items.map(([label, value, delta]): Kpi =>
    (delta === undefined ? { label, value } : { label, value, delta })));
}

function reading(ctx: Context): string {
  const s = ctx.profile.summary;
  if (ctx.user === "A") {
    return note(copy.userANote(clock(s.last_use_mean_h)), "good");
  }
  const first = s.sleep_first_week_h ?? 0;
  const last = s.sleep_last_week_h ?? 0;
  return note(copy.driftNote(
    clock(s.last_screen_first_week_h), clock(s.last_screen_last_week_h),
    clock(s.wake_first_week_h), clock(s.wake_last_week_h),
    s.night_pickups_last_week, Math.abs(last - first) * 60), "serious");
}

export const act: Act = {
  id: "06",
  part: 2,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build(ctx: Context): string {
    const s = ctx.profile.summary;
    return strip(s)
      + chart("night_drift", explain("night_drift"), { scope: "shared" })
      + reading(ctx)
      + grid([chart("day_span.night", explain("day_span.night")),
              chart("compare.night_pickups", explain("compare.night_pickups"),
                    { scope: "shared" })])
      + note(copy.weightNote(s.night_mean, s.screen_mean));
  },
};
