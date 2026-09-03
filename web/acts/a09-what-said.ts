/**
 * Act 09 · the alert and nudge engine.
 *
 * Two destinations and only two: the user's own screen, and the weekly summary
 * a held signal drops into. Nothing leaves the device.
 *
 * The day slider walks all thirty days, and the cards behind it are built here
 * rather than shipped pre-rendered. Python pre-rendered them because the
 * browser held no copy; it holds it now.
 */

import { explain } from "../copy/explain";
import { unit } from "../copy/units";
import { clock, clockOf, ordinal, pct, shortDate } from "../format";
import {
  caption, channel, chart, details, empty, grid, kpis, lede, pairs, phone,
  slot, sub, table, type PhoneCard,
} from "../html";
import type { DailyRow, Profile, ReplayDay } from "../types/index";
import type { Act, Context } from "./act";

/** The nudge arms 30 min after the band opens, matching `NUDGE_AFTER_MIN`. */
const NUDGE_AFTER_MIN = 30;

const copy = {
  eyebrow: "Alerts, nudges, reinforcements",
  title: "The intelligence acting",

  lede: "Slide through each day and see below what was notified to you, and what the phone worked out and kept to itself.",
  caption: "Every variable the rules read, each as a share of its own maximum so the shapes compare. "
  + "The rail below zero is what the phone emitted.",

  sliderLabel: "Day of the period",
  outputs: (date: string) => `Outputs on ${date}`,
  channelUser: "User's screen",
  channelDevice: "On the device",
  noNotifications: "No notifications",

  brand: "BALANCE",
  alertTime: "09:12",
  summaryTime: "09:00",
  eyebrowSummary: "Your summary",
  eyebrowNudge: "Night nudge",
  eyebrowAlert: "Alert",
  ctaWeek: "Your week",
  ctaWeeklySummary: "Weekly summary",
  ctaOff: "Off until tomorrow",
  ctaFiveMore: "5 more minutes",
  nudgeHeadline: (n: string) =>
    `That is the ${n} time you have opened your phone tonight.`,
  nudgeBody: "A month ago you had already put it down by now.",

  device: {
    screen: "Screen", pickups: "Unlocks", night: "Late night",
    nightEnd: "Night ended", offline: "Longest break",
    offlineStart: "· started", distract: "Distraction share",
    sensitive: "Sensitive attempts", blocks: "Total blocks", score: "Index",
    nudges: "Nudges so far", reinforcements: "Reinforcements",
    caption: "Computed and kept on the phone. None of it leaves.",
  },

  emissionsTitle: "Everything the phone emitted this month",
  emissionsNone: "The phone emitted nothing in the period.",
  emissionColumns: ["Date", "Destination", "Type", "Detail"],

  kpi: {
    alerts: "Alerts sent",
    alertsDelta: (budget: number) => `quota ${budget}/month`,
    summary: "Into weekly summary",
    summaryDelta: "not notified",
    reinforcements: "Reinforcements sent",
    reinforcementsDelta: "one a week at most",
    nudgeNights: "Nights with a nudge",
    nudgeNightsValue: (nudged: number, nights: number) => `${nudged}/${nights}`,
    nudgeNightsDelta: (share: number) => `${(share * 100).toFixed(0)} % of nights`,
  },

  nudgeTitle: "On-device nudge",
  nudgeCaption: (from: string) =>
    `Second reopening from ${from}, once a night at most. Replayed over the `
    + "thirty days.",
  nudgeRows: {
    nights: "Nights evaluated",
    nudged: "Nights with a nudge",
    nightMinutes: "Night minutes",
    after: "Minutes after the nudge",
    perNight: "Per night",
  },

  next: "That is the whole month, and everything the phone did with it. Now the finding.",
};

/** The alert, on the phone of the person it is about. Headline and text only:
 *  no app, no domain, no category is ever named in a notification. */
function alertCard(day: ReplayDay): PhoneCard | null {
  if (!day.alert) return null;
  return {
    time: copy.alertTime, brand: copy.brand, eyebrow: copy.eyebrowAlert,
    headline: day.alert.headline, body: day.alert.body,
    ctas: [{ label: copy.ctaWeeklySummary, ghost: true }],
  };
}

/** The reinforcement, or failing that the night nudge. */
function summaryCard(day: ReplayDay): PhoneCard | null {
  const positive = day.positives[0];
  if (positive) {
    return {
      time: copy.summaryTime, brand: copy.brand,
      eyebrow: copy.eyebrowSummary, headline: positive.headline,
      body: positive.body,
      rows: Object.entries(positive.evidence),
      ctas: [{ label: copy.ctaWeek, ghost: true }],
    };
  }
  const nudge = day.nudge;
  if (nudge?.fired && nudge.at_ms !== null) {
    // UTC, not local. The core reads every timestamp as UTC and drops the
    // zone (`analysis/events.py`), so a local reading here would put the nudge
    // two hours away from the night band it belongs to.
    const at = new Date(nudge.at_ms);
    return {
      time: clockOf(at.getUTCHours(), at.getUTCMinutes()),
      brand: copy.brand,
      eyebrow: copy.eyebrowNudge,
      headline: copy.nudgeHeadline(ordinal(nudge.reopens)),
      body: copy.nudgeBody,
      ctas: [{ label: copy.ctaOff, ghost: false },
             { label: copy.ctaFiveMore, ghost: true }],
    };
  }
  return null;
}

/** Everything that would have appeared on the phone that day, in the order it
 *  would have arrived. */
function userCards(day: ReplayDay): PhoneCard[] {
  return [alertCard(day), summaryCard(day)]
    .filter((card): card is PhoneCard => card !== null);
}

/** The figures the phone keeps for itself. */
function deviceRows(row: DailyRow, day: ReplayDay): Array<[string, string]> {
  const d = copy.device;
  return [
    [d.screen, `${row.screen_min.toFixed(0)} ${unit.min}`],
    [d.pickups, row.pickups.toFixed(0)],
    [d.night, `${row.night_min.toFixed(0)} ${unit.min}`],
    [d.nightEnd, clock(row.night_end_h)],
    [d.offline, `${row.longest_offline_h.toFixed(1)} ${unit.hours}`],
    [d.offlineStart, row.longest_offline_when ?? "no stretch"],
    [d.distract, pct(row.distract_share)],
    [d.sensitive, row.blocks_sensitive.toFixed(0)],
    [d.blocks, row.blocks.toFixed(0)],
    [d.score, `${row.score.toFixed(0)} / 100`],
    [d.nudges, String(day.nudges_so_far)],
    [d.reinforcements, String(day.positives_so_far)],
  ];
}

/** What the slider's readout says at one step. */
export function label(profile: Profile, index: number): string {
  const day = profile.replay[index];
  return day ? shortDate(day.day) : "";
}


/** Everything behind the day slider, for one day. Exported so the interaction
 *  can rebuild it without going through the whole act. */
export function panel(profile: Profile, iso: string): Record<string, string> {
  const day = profile.replay.find((r) => r.day === iso);
  const row = profile.daily.find((r) => r.day === iso);
  if (!day || !row) return {};
  const cards = userCards(day);
  return {
    "day.label": shortDate(iso),
    "day.title": sub(copy.outputs(shortDate(iso))),
    "day.cards": grid([
      channel(copy.channelUser, cards.length
        ? cards.map(phone).join("") : empty(copy.noNotifications)),
      channel(copy.channelDevice,
              pairs(deviceRows(row, day)) + caption(copy.device.caption)),
    ]),
  };
}

function slider(profile: Profile, current: string): string {
  const days = profile.replay.map((r) => r.day);
  const ticks = days.filter((_, i) => i % 7 === 0)
    .map((_, i) => `<option value="${i * 7}"></option>`).join("");
  const index = Math.max(0, days.indexOf(current));
  return '<div class="slider" data-slider="day">'
    + `<label for="day-slider">${copy.sliderLabel}</label>`
    + '<output for="day-slider" data-slot="day.label">'
    + `${shortDate(current)}</output>`
    + '<input type="range" id="day-slider" list="day-ticks" min="0" '
    + `max="${days.length - 1}" step="any" value="${index}">`
    + `<datalist id="day-ticks">${ticks}</datalist></div>`;
}

function emissions(profile: Profile): string {
  if (!profile.emissions.length) return caption(copy.emissionsNone);
  return table(copy.emissionColumns, profile.emissions
    .map((e) => [shortDate(e.day), e.destination, e.type, e.detail]));
}

function notifications(profile: Profile): string {
  const s = profile.summary;
  return kpis([
    { label: copy.kpi.alerts, value: String(s.alerts_sent),
      delta: copy.kpi.alertsDelta(s.alert_budget) },
    { label: copy.kpi.summary, value: String(s.alerts_held),
      delta: copy.kpi.summaryDelta },
    { label: copy.kpi.reinforcements, value: String(s.positives_sent),
      delta: copy.kpi.reinforcementsDelta },
    { label: copy.kpi.nudgeNights,
      value: copy.kpi.nudgeNightsValue(s.nudge_nights, s.nights),
      delta: copy.kpi.nudgeNightsDelta(s.nudge_nights / (s.nights || 1)) },
  ]);
}

function nudgeDetail(profile: Profile): string {
  const n = profile.nudgeSummary;
  const rows: Array<[string, string]> = [
    [copy.nudgeRows.nights, String(n.nights)],
    [copy.nudgeRows.nudged,
     `${n.nights_with_a_nudge} (${(n.appearance_rate * 100).toFixed(0)} %)`],
    [copy.nudgeRows.nightMinutes, n.total_night_minutes.toFixed(0)],
    [copy.nudgeRows.after,
     `${n.minutes_at_stake_after_the_nudge.toFixed(0)} `
     + `(${(n.share_of_night_total * 100).toFixed(0)} %)`],
    [copy.nudgeRows.perNight,
     `${n.minutes_at_stake_per_nudged_night.toFixed(0)} ${unit.min}`],
  ];
  const quiet = new Map<string, number>();
  for (const nudge of profile.nudges) {
    if (nudge.quiet_reason) {
      quiet.set(nudge.quiet_reason, (quiet.get(nudge.quiet_reason) ?? 0) + 1);
    }
  }
  const reasons = [...quiet.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([reason, n2]): [string, string] => [reason, String(n2)]);
  const from = clock(23 + NUDGE_AFTER_MIN / 60);
  return caption(copy.nudgeCaption(from))
    + grid([pairs(rows), pairs(reasons)]);
}

export const act: Act = {
  id: "09",
  part: 2,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build(ctx: Context): string {
    const { profile, selection } = ctx;
    const built = panel(profile, selection.day);
    return lede(copy.lede)
      + caption(copy.caption)
      + slider(profile, selection.day)
      + chart("tracked_series", explain("tracked_series"), { size: "tall" })
      + slot("day.title", built["day.title"] ?? "")
      + slot("day.cards", built["day.cards"] ?? "")
      + sub(copy.emissionsTitle)
      + emissions(profile)
      + notifications(profile)
      + details(copy.nudgeTitle, nudgeDetail(profile));
  },
};
