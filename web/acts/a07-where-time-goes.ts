/**
 * Act 07 · apps, domains and categories. Device-side only.
 */

import { explain } from "../copy/explain";
import { unit } from "../copy/units";
import { pct, shortDate, thousands } from "../format";
import { mean } from "../stats";
import { aside, caption, chart, grid, kpis, note, tags } from "../html";
import type { Profile, UsageTotal } from "../types/index";
import { other, type Act, type Context } from "./act";

const copy = {
  eyebrow: "Apps, domains, categories",
  title: "Where your time goes",

  deviceOnly: "device only",
  neverSent: "never leaves the phone",

  kpi: {
    attributed: "Attributed time",
    attributedDelta: (share: number) => `of ${share.toFixed(0)} % of screen`,
    apps: "Distinct apps",
    domains: "Distinct domains",
    thisMonth: "this month",
    top3: "Top 3 apps",
    top3Delta: "of app time",
    distract: "Distraction share",
    distractDelta: "social + entertainment + games",
  },

  readingA: (apps: number, top3Names: string, top3: number, news: number,
             distract: number, first: number, last: number) =>
    `You used ${apps} apps this month, with ${top3Names} holding `
    + `${top3.toFixed(0)} % of your time. When you browse, ${news.toFixed(0)} `
    + `% of it is news. Distraction averages ${distract.toFixed(0)} % and it `
    + `is going down, not up: ${first.toFixed(0)} % in week 1 to `
    + `${last.toFixed(0)} % in week 4.`,

  readingB: (apps: number, top3Names: string, top3: number, appsA: number,
             messaging: number, messagingApps: number, distract: number,
             distractA: number) =>
    `You used ${apps} apps this month, with ${top3Names} holding `
    + `${top3.toFixed(0)} % of your usage — against A's ${appsA} apps. You `
    + `spent ${thousands(messaging)} min reaching people across `
    + `${messagingApps} apps. Your distraction share is `
    + `${distract.toFixed(0)} %, barely above A's ${distractA.toFixed(0)} %. `
    + "What you spend your time on is completely ordinary. How much of it, and when, is not.",

  chrome: (opens: number, minutes: number) =>
    `Chrome shows ${opens.toFixed(0)} openings and ${minutes.toFixed(0)} min: `
    + "browser time goes to the domain.",

  distractExplain:
    "<b>How is distraction measured?</b> Not by how many apps you open. "
    + "It is the share of your attributed time that landed in social, entertainment or gaming. "
    + "Thirty apps for two minutes each is not distraction by this definition; one hour of one app is.",

  blockedAbsent: (names: string, attempts: string, through: string) =>
    `This chart only shows what actually opened, which is why ${names} are `
    + `barely on it: the filter stopped them ${attempts} times and let through `
    + `${through}.`,

  leakExplain: (days: number, median: number, outage: string, hours: number) =>
    "<b>So why are they here at all? Were they downloaded that day?</b> "
    + `They look to have been on the phone the whole time: the filter blocked them on every one of the ${days} days, a median of ${median.toFixed(0)} times a day, which it could not do to something that was not installed. `
    + `Every minute they ever got comes from one window on ${outage}, when distraction blocking went quiet for about ${hours.toFixed(0)} hours. `
    + "It came back the next morning and they were never opened again.",

  leakScope: (sensitive: number) =>
    "<b>And it was not the whole filter.</b> "
    + `Adult and gambling blocking never stopped — it turned away ${sensitive} attempts inside that same window, while not one distraction block fired. `
    + "Why one list went quiet and the other did not, the log does not say. It records what the phone did, not why it did it.",

  next: "That is what got through. Here is what did not.",
};

/** The three apps the reader is about to see at the top of the chart. */
function top3Names(apps: UsageTotal[]): string {
  const names = apps.slice(0, 3).map((a) => a.label);
  if (names.length < 2) return names.join("");
  return `${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}`;
}

function top3Share(apps: UsageTotal[]): number {
  const total = apps.reduce((sum, a) => sum + a.minutes, 0) || 1;
  return apps.slice(0, 3).reduce((sum, a) => sum + a.minutes, 0) / total * 100;
}

function strip(profile: Profile): string {
  const s = profile.summary;
  return kpis([
    { label: copy.kpi.attributed,
      value: `${(s.screen_h * s.attributed_pct / 100).toFixed(0)} ${unit.hours}`,
      delta: copy.kpi.attributedDelta(s.attributed_pct) },
    { label: copy.kpi.apps, value: String(profile.apps.length),
      delta: copy.kpi.thisMonth },
    { label: copy.kpi.domains, value: String(profile.sites.length),
      delta: copy.kpi.thisMonth },
    { label: copy.kpi.top3, value: `${top3Share(profile.apps).toFixed(0)} %`,
      delta: copy.kpi.top3Delta },
    { label: copy.kpi.distract,
      value: pct(mean(profile.daily.map((d) => d.distract_share))),
      delta: copy.kpi.distractDelta },
  ]);
}

/**
 * The two apps the filter stopped most, and how little got through.
 *
 * An app the filter stopped every time never enters the usage frame, so the
 * package name is the fallback for its label.
 */
function mostBlocked(profile: Profile): { names: string; attempts: string;
                                          through: string } {
  const labels = new Map(profile.apps.map((a) => [a.key, a.label]));
  const opens = new Map(profile.apps.map((a) => [a.key, a.opens]));
  const top = profile.blocks.top.filter((b) => b.block_type === "APP")
    .slice(0, 2);
  const join = (parts: Array<string | number>) => parts.join(" and ");
  return {
    names: join(top.map((b) => labels.get(b.target) ?? b.target)),
    attempts: join(top.map((b) => b.count)),
    through: join(top.map((b) => (opens.get(b.target) ?? 0).toFixed(0))),
  };
}

/** Chrome's own row, which looks wrong until you know browser time was moved
 *  off it and onto the domain. */
function chromeCaption(profile: Profile): string {
  const chrome = profile.apps.find((a) => a.key === "com.android.chrome");
  return chrome ? caption(copy.chrome(chrome.opens, chrome.minutes)) : "";
}

function reading(ctx: Context): string {
  const { profile, user } = ctx;
  const distract = mean(profile.daily.map((d) => d.distract_share)) * 100;
  const week = (n: number) =>
    mean(profile.daily.filter((d) => d.week === n)
      .map((d) => d.distract_share)) * 100;

  if (user === "A") {
    const newsMinutes = profile.sites
      .filter((s) => s.category === "NEWS")
      .reduce((sum, s) => sum + s.minutes, 0);
    const allSites = profile.sites.reduce((sum, s) => sum + s.minutes, 0) || 1;
    return note(copy.readingA(
      profile.apps.length, top3Names(profile.apps), top3Share(profile.apps),
      newsMinutes / allSites * 100, distract, week(1), week(4)), "good")
      + chromeCaption(profile);
  }

  const them = other(ctx);
  const messaging = profile.apps.filter((a) => a.category === "MESSAGING");
  const blocked = mostBlocked(profile);
  const outage = profile.summary.outage;
  return note(copy.readingB(
    profile.apps.length, top3Names(profile.apps), top3Share(profile.apps),
    them?.apps.length ?? 0,
    messaging.reduce((sum, a) => sum + a.minutes, 0), messaging.length,
    distract,
    them ? mean(them.daily.map((d) => d.distract_share)) * 100 : distract),
    "warn")
    + caption(copy.blockedAbsent(blocked.names, blocked.attempts,
                                 blocked.through))
    + (outage
        ? aside([
          copy.leakExplain(outage.leaked_days, outage.leaked_median,
                           shortDate(outage.outage_day), outage.outage_hours),
          copy.leakScope(outage.sensitive_during),
        ])
        : "");
}

export const act: Act = {
  id: "07",
  part: 2,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build(ctx: Context): string {
    return tags(copy.deviceOnly, copy.neverSent)
      + strip(ctx.profile)
      + grid([chart("top_bars.apps", explain("top_bars.apps")),
              chart("top_bars.sites", explain("top_bars.sites"))])
      + chart("category_area", explain("category_area"))
      + reading(ctx)
      + note(copy.distractExplain);
  },
};
