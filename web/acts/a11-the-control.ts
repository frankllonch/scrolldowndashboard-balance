/**
 * Act 11 · the negative control.
 *
 * `screen_jump` is real, reads the same frames, and fires on nobody. That is
 * the point: the rule that looks obvious would have missed this month.
 */

import { explain } from "../copy/explain";
import { value } from "../copy/units";
import { shortDate } from "../format";
import { chart, grid, lede, note, table } from "../html";
import type { UserId } from "../types/index";
import type { Act, Context } from "./act";

const copy = {
  eyebrow: "The negative control",
  title: "What a screen-time rule would have missed",

  lede: "Screen time against the night band.",
  screenLabel: "screen time, week 1 to week 4",
  nightLabel: "late-night screen, same weeks",
  heroValue: (multiple: number) => `×${multiple.toFixed(0)}`,

  body: (screen: number, night: number) =>
    "<code>screen_jump</code> is implemented, reads the same frames, and "
    + `fires on neither profile. ${screen > 0 ? "+" : ""}${screen.toFixed(0)} `
    + "% is under any threshold worth setting. What happens at night band is "
    + `×${night.toFixed(0)}.`,

  rules: {
    night_drift: "5 nights against the previous 14, plus bedtime",
    sensitive_spike: "Sensitive attempts, 7 days against 7",
    screen_jump: "Screen time, 5 days against the previous 14",
  },
  columns: { rule: "Rule", compares: "What it compares" },
  userColumn: (user: UserId) => `User ${user}`,
  decisionOn: (decision: string, date: string) => `${decision} · ${date}`,

  next: "Everything above comes from eight fields in a log. Here is how.",
};

function hero(value: string, label: string): string {
  return '<div class="hero-card"><p class="hero-number huge">'
    + `${value}</p><p class="hero-sub">${label}</p></div>`;
}

/** Which rule fires on whom. One profile's answer only means something next to
 *  the other's, so both columns are always here. */
function coverage({ payload }: Context): string {
  const users = payload.meta.profiles;
  const rows = (Object.keys(copy.rules) as Array<keyof typeof copy.rules>)
    .map((key) => [
      key, copy.rules[key],
      ...users.map((user) => {
        const found = payload.profiles[user]?.alerts
          .find((a) => a.key === key);
        return found
          ? copy.decisionOn(found.decision, shortDate(found.day))
          : value.doesNotFire;
      }),
    ]);
  return table([copy.columns.rule, copy.columns.compares,
                ...users.map(copy.userColumn)], rows);
}

export const act: Act = {
  id: "11",
  part: 3,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build(ctx: Context): string {
    const { finding } = ctx.payload;
    const change = finding.screen_change_pct;
    return lede(copy.lede)
      + grid([
        hero(`${change > 0 ? "+" : ""}${change.toFixed(0)} %`,
             copy.screenLabel),
        hero(copy.heroValue(finding.night_multiple), copy.nightLabel),
      ])
      + grid([
        chart("compare.screen_min", explain("compare.screen_min"),
              { scope: "shared" }),
        chart("compare.night_min", explain("compare.night_min"),
              { scope: "shared" }),
      ])
      + note(copy.body(change, finding.night_multiple), "warn")
      + coverage(ctx);
  },
};
