/**
 * Act 02 · both profiles at once, and what the index actually is.
 *
 * The cold open. It plants what is wrong with B and does not say what it is;
 * act 10 answers it.
 */

import { COMPONENTS } from "../charts/score";
import { explain } from "../copy/explain";
import { unit } from "../copy/units";
import { hm, pct, thousands } from "../format";
import { chart, eyebrow, grid, kpis, lede, note, sub, table } from "../html";
import type { Profile, UserId } from "../types/index";
import type { Act, Context } from "./act";

const copy = {
  eyebrow: "Both profiles, thirty days",
  title: "A single wellbeing score",

  lede: "One month, thirty days of raw on-device events, for two different people.",

  cardEyebrow: (user: UserId) => `User ${user} · wellbeing index`,
  scale: " /100",
  weeks: (first: number, last: number) =>
    `week 1 → ${first.toFixed(0)} &nbsp;·&nbsp; last full week → `
    + `${last.toFixed(0)}`,

  person: {
    A: "Likely an adult with a stable relationship with their phone. "
    + "WhatsApp, Spotify and the news fill most of their days, consistent throughout the whole month.",
    B: (blocks: number) =>
      "Also an adult, and on the surface not that different: WhatsApp, Spotify, Maps, the papers, Kindle. "
      + `What sets this month apart is that the filter is switched on, it stops ${thousands(blocks)} attempts, and the nights get later every week.`,
  },

  hook: (drop: number) =>
    `A stays constant throughout the month, whilst B drops ${drop.toFixed(0)} `
    + "points. We will see why below.",

  scoreTitle: "What the wellbeing score is",
  scoreBody:
    "It is a compound index: five components, each scored 0 to 100 against fixed bands, then weighted into one number a day. "
    + "Nothing here is scored against your own past — otherwise a steady six hours a day would score 100 for being steady.",
  scoreNote: (fragGood: number, fragBad: number) =>
    "Two things the names get asked about. "
    + `<b>Fragmentation</b> is not about how many apps you use — it counts how many times a day you pick the phone up: ${fragGood} unlocks scores 100, ${fragBad} scores 0. `
    + "And <b>intent</b> is how distraction is measured: the share of your attributed time that went to social, entertainment or gaming. "
    + "Opening thirty apps for two minutes each is not distraction by this definition; one hour of TikTok is.",
  scoreBlocks:
    "Blocked attempts do not score at all. "
    + "A block means the phone did its job and nothing opened; docking you for it would charge you for the product working, and would reward switching the filter off.",

  columns: ["Component", "Value scoring 100", "Value scoring 0", "Weight"],

  kpi: {
    screen: (user: UserId) => `${user} · screen/day`,
    unlocks: (user: UserId) => `${user} · unlocks/day`,
    night: (user: UserId) => `${user} · late night/day`,
    blocks: (user: UserId) => `${user} · blocks/month`,
    sensitive: (user: UserId) => `${user} · sensitive`,
  },

  next: "Two months, two very different shapes. Pick one and read it from the inside.",
};

/** The index, and one line on who this month belonged to. */
function hero(profile: Profile): string {
  const s = profile.summary;
  const sketch = s.user === "A"
    ? copy.person.A : copy.person.B(s.blocks_total);
  return `<div class="hero-card" data-user="${s.user}">`
    + eyebrow(copy.cardEyebrow(s.user))
    + `<p class="hero-number">${s.score_mean.toFixed(0)}`
    + `<span class="hero-unit">${copy.scale}</span></p>`
    + `<p class="hero-sub">`
    + copy.weeks(s.score_first_week, s.score_last_week) + "</p>"
    + note(sketch)
    + "</div>";
}

function strip(profile: Profile): string {
  const s = profile.summary;
  return kpis([
    { label: copy.kpi.screen(s.user), value: hm(s.screen_mean) },
    { label: copy.kpi.unlocks(s.user), value: s.pickups_mean.toFixed(0) },
    { label: copy.kpi.night(s.user),
      value: `${s.night_mean.toFixed(0)} ${unit.min}` },
    { label: copy.kpi.blocks(s.user), value: thousands(s.blocks_total) },
    { label: copy.kpi.sensitive(s.user), value: s.sensitive_total.toFixed(0) },
  ]);
}

/** What the number on the hero cards is, said where the reader first meets it
 *  rather than in the appendix. */
function scoreExplainer(): string {
  const frag = COMPONENTS.find((c) => c.label === "Fragmentation");
  return sub(copy.scoreTitle)
    + lede(copy.scoreBody)
    + table(copy.columns, COMPONENTS.map((c) =>
      [c.label, c.good, c.bad, pct(c.weight)]))
    + note(copy.scoreNote(frag?.good ?? 15, frag?.bad ?? 60))
    + note(copy.scoreBlocks);
}

export const act: Act = {
  id: "02",
  part: 1,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build({ payload }: Context): string {
    const profiles = payload.meta.profiles
      .map((u) => payload.profiles[u])
      .filter((p): p is Profile => p !== undefined);
    return lede(copy.lede)
      + grid(profiles.map(hero))
      + chart("score_line", explain("score_line"), { scope: "shared" })
      + profiles.map(strip).join("")
      + note(copy.hook(payload.finding.score_drop), "warn")
      + scoreExplainer();
  },
};
