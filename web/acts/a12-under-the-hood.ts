/**
 * Act 12 · under the hood. Everything closed by default; nothing hidden.
 */

import { COMPONENTS } from "../charts/score";
import { explain } from "../copy/explain";
import { unit } from "../copy/units";
import { pct, thousands } from "../format";
import { caption, chart, details, grid, kpis, lede, note, table } from "../html";
import type { Payload, UserId } from "../types/index";
import type { Act, Context } from "./act";

const copy = {
  eyebrow: "Schema and derivations",
  title: "Under the hood",

  lede: "Every number on this page is a pure function of one event log. "
  + "Nothing was estimated, nothing was fetched, and the browser never sees an event — the whole pipeline runs before the page is written. "
  + "Open any of these to see how a given figure was reached.",

  userColumn: (user: UserId) => `User ${user}`,

  pipeline: {
    title: "From the log to this page",
    columns: ["Layer", "What it turns into what"],
    layers: [
      ["Events", "Raw log into screen stretches, unlocks and attributed time"],
      ["Metrics", "Stretches into one row per day, and one per week"],
      ["Index", "A day's row into five component scores and one number"],
      ["Intelligence", "The daily rows into alerts, nudges and reinforcements"],
      ["Render", "All of the above into figures, acts and this page"],
    ],
    note: "The layers only ever point downwards: none of them knows the page exists, and none of them imports a charting library. "
    + "That is why the command line and this dashboard can be two readers of the same numbers rather than two implementations of them.",
  },

  stream: {
    title: "The stream",
    columns: { field: "Field", means: "What it means" },
    means: {
      SCREEN_ON: "May be a glance.",
      SCREEN_OFF: "",
      USER_PRESENT: "A real unlock. This is what makes a pickup.",
      APP_FOREGROUND: "",
      URL_VISIT: "Domain only, never a path.",
      BLOCK: "Nothing opened.",
    } as Record<string, string>,
  },

  fields: {
    title: "The eight fields",
    columns: ["Field", "Type", "On"],
    rows: [
      ["id", "int", "all"],
      ["event_type", "str", "all"],
      ["timestamp_millis", "int", "all"],
      ["package_name", "str|null", "APP_FOREGROUND, BLOCK"],
      ["url_domain", "str|null", "URL_VISIT, BLOCK"],
      ["category", "str|null", "APP_FOREGROUND, URL_VISIT, BLOCK"],
      ["block_type", "str|null", "BLOCK"],
      ["is_keyguard_locked", "bool|null", "SCREEN_ON, USER_PRESENT"],
    ],
  },

  anomalies: {
    title: "Awkward things in the stream",
    columns: ["Stream", "Handled"],
    rows: (screenA: number, dupA: number, dupB: number) => [
      ["A screen-on while the screen is already on.",
       `A depth counter, giving the union: ${screenA.toFixed(1)} h for A.`],
      ["The file ends mid-day.",
       "That day leaves every average, but still counts towards the night before."],
      ["A day opens at 00:20, the tail of the night before.",
       "First unlock means the first from 06:00."],
      ["A screen stretch runs through midnight.", "Split at the boundary."],
      [`One unlock recorded twice, ${dupA} times in A and ${dupB} in B.`,
       "Counted, not dropped in silence."],
    ],
    footnote: "Why a depth counter is in DECISIONS.md.",
  },

  derivations: {
    title: "From event to metric",
    columns: ["Metric", "How it is derived"],
    rows: [
      ["Screen time",
       "Union of on-to-off intervals, split at midnight."],
      ["Real pickup", "A screen-on with an unlock before the next one."],
      ["Glance", "A screen-on with no unlock. It lit; it never opened."],
      ["Night band",
       "23:00 to 06:00 the next morning. Sleep does not cut at midnight."],
      ["Your normal", "Rolling median of this user's last 14 days."],
    ],
    footnote: "The rest are in ARCHITECTURE.md.",
  },

  coverage: {
    title: "Screen time explained",
    reconstructed: (user: UserId) => `${user} · screen reconstructed`,
    attributed: (user: UserId) => `${user} · attributed to app/site`,
    caption: (a: number, b: number) =>
      `The rest is lock screen and notifications. B's ${b.toFixed(0)} % `
      + `against A's ${a.toFixed(0)} % is the checking pattern.`,
  },

  index: {
    title: "The index",
    columns: ["Component", "Value scoring 100", "Value scoring 0", "Weight"],
    note: "Blocks do not score. "
    + "Docking points for an attempt the filter already stopped charges the user for the product working.",
  },
};

const DUPLICATES = "duplicate USER_PRESENT in stretch";

function stream(payload: Payload): string {
  const users = payload.meta.profiles;
  const kinds = [...new Set(users.flatMap((u) =>
    Object.keys(payload.profiles[u]?.eventCounts ?? {})))].sort();
  const rows = kinds.map((kind) => [
    kind,
    ...users.map((u) =>
      thousands(payload.profiles[u]?.eventCounts[kind] ?? 0)),
    copy.stream.means[kind] ?? "",
  ]);
  return table([copy.stream.columns.field, ...users.map(copy.userColumn),
                copy.stream.columns.means], rows);
}

function anomalies(payload: Payload): string {
  const a = payload.profiles.A;
  const b = payload.profiles.B;
  return table(copy.anomalies.columns, copy.anomalies.rows(
    a?.summary.screen_h ?? 0,
    a?.anomalies[DUPLICATES] ?? 0,
    b?.anomalies[DUPLICATES] ?? 0))
    + caption(copy.anomalies.footnote);
}

function coverage(payload: Payload): string {
  const users = payload.meta.profiles;
  const summary = (u: UserId) => payload.profiles[u]?.summary;
  const strip = kpis([
    ...users.map((u) => ({
      label: copy.coverage.reconstructed(u),
      value: `${(summary(u)?.screen_h ?? 0).toFixed(0)} ${unit.hours}`,
    })),
    ...users.map((u) => ({
      label: copy.coverage.attributed(u),
      value: `${(summary(u)?.attributed_pct ?? 0).toFixed(0)} %`,
    })),
  ]);
  return strip + caption(copy.coverage.caption(
    summary("A")?.attributed_pct ?? 0, summary("B")?.attributed_pct ?? 0));
}

function index(payload: Payload): string {
  return table(copy.index.columns,
               COMPONENTS.map((c) => [c.label, c.good, c.bad, pct(c.weight)]))
    + grid(payload.meta.profiles.map((u) =>
      chart(`score_breakdown.${u}`, explain(`score_breakdown.${u}`),
            { scope: "shared" })))
    + note(copy.index.note);
}

/** The five layers, in the order a number passes through them. */
function pipeline(): string {
  return table(copy.pipeline.columns, copy.pipeline.layers)
    + note(copy.pipeline.note);
}

export const act: Act = {
  id: "12",
  part: 3,
  eyebrow: copy.eyebrow,
  title: copy.title,
  build({ payload }: Context): string {
    return lede(copy.lede)
      + details(copy.pipeline.title, pipeline())
      + details(copy.stream.title, stream(payload))
      + details(copy.fields.title,
                table(copy.fields.columns, copy.fields.rows))
      + details(copy.anomalies.title, anomalies(payload))
      + details(copy.derivations.title,
                table(copy.derivations.columns, copy.derivations.rows)
                + caption(copy.derivations.footnote))
      + details(copy.coverage.title, coverage(payload))
      + details(copy.index.title, index(payload));
  },
};
