/**
 * Act 10 · the finding. This is what act 02 refused to explain.
 */

import { explain } from "../copy/explain";
import { chart, grid, lede, note } from "../html";
import type { Act, Context } from "./act";

const copy = {
  eyebrow: "The reveal",
  title: "The finding",

  lede: "B's index fell as their night-time use rose.",
  heroValue: (multiple: number) => `×${multiple.toFixed(0)}`,
  heroLabel: "late-night screen, week 1 against week 4",
  sleepValue: (minutes: number) => `${minutes.toFixed(0)} min`,
  sleepLabel: "less rest available per night",

  body: (shift: number, first: number, last: number, pickFirst: number,
         pickLast: number) =>
    `The last screen moves ${shift.toFixed(0)} minutes later, the first unlock stays put, and the window closes from ${first.toFixed(1)} h to ${last.toFixed(1)} h. `
    + `Unlocks after midnight go ${pickFirst.toFixed(1)} to ${pickLast.toFixed(1)}. `
    + "A records zero night minutes over the same thirty days.",

  next: "One obvious objection: surely a plain screen-time rule would have caught this too?",
};

function hero(value: string, label: string): string {
  return '<div class="hero-card"><p class="hero-number huge">'
    + `${value}</p><p class="hero-sub">${label}</p></div>`;
}

export const act: Act = {
  id: "10",
  part: 3,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build({ payload }: Context): string {
    const { finding } = payload;
    const b = payload.profiles.B?.summary;
    if (!b) return "";
    const shift = b.last_screen_first_week_h === null
      || b.last_screen_last_week_h === null
      ? 0 : (b.last_screen_last_week_h - b.last_screen_first_week_h) * 60;
    return lede(copy.lede)
      + grid([
        hero(copy.heroValue(finding.night_multiple), copy.heroLabel),
        hero(copy.sleepValue(finding.sleep_loss_min), copy.sleepLabel),
      ])
      + chart("night_drift", explain("night_drift"), { scope: "shared" })
      + note(copy.body(shift, b.sleep_first_week_h ?? 0,
                       b.sleep_last_week_h ?? 0,
                       b.night_pickups_first_week,
                       b.night_pickups_last_week), "serious");
  },
};
