/**
 * Composing the page from the acts.
 *
 * Every section is written into the document that ships, so the page is
 * complete and readable before a single line of script runs. Part 2 is then
 * rebuilt in place when the reader switches profile.
 */

import { ACTS, perProfile, type Act, type Context } from "./acts/index";
import { PARTS } from "./copy/units";
import type { Payload, Profile, UserId } from "./types/index";
import { profile as profileOf } from "./document";

/**
 * The line handing the reader to the next act.
 *
 * It is appended to the act body, not to the section around it: the profile
 * switch replaces the whole body with what it built, so a bridge added
 * outside would survive the first paint and vanish on the first swap.
 */
function bridge(act: Act): string {
  return act.next ? `<p class="act-next">${act.next}</p>` : "";
}

/** One act's heading and body, as the shell's `<section>` expects them. */
export function section(act: Act, body: string): string {
  return '<header class="act-head">'
    + `<p class="eyebrow">${act.eyebrow}</p>`
    + `<h2 class="act-title">${act.title}</h2></header>`
    + `<div class="act-body">${body}</div>`;
}

/** Twelve acts in uppercase mono, grouped into the three parts. */
export function rail(): string {
  let out = "";
  let part: number | null = null;
  for (const act of ACTS) {
    if (act.part !== part) {
      if (part !== null) out += "</ol>";
      out += `<p class="rail-part">${PARTS[act.part - 1]}</p><ol>`;
      part = act.part;
    }
    out += `<li><a href="#act-${act.id}" data-rail="${act.id}">`
      + `<span class="num">${act.id}</span>${act.title}</a></li>`;
  }
  return `${out}</ol>`;
}

function context(payload: Payload, user: UserId, profile: Profile): Context {
  return {
    payload, user, profile,
    selection: { user, week: profile.defaultWeek, day: profile.defaultDay },
  };
}

/** Every act body for one profile, keyed by act id. */
export function bodies(payload: Payload, user: UserId): Record<string, string> {
  const profile = profileOf(payload, user);
  const ctx = context(payload, user, profile);
  const out: Record<string, string> = {};
  for (const act of ACTS) {
    out[act.id] = act.build(ctx) + bridge(act);
  }
  return out;
}

/** The act bodies the profile switch replaces: part 2 and nothing else. */
export const PART_TWO = ACTS.filter(perProfile).map((a) => a.id);
