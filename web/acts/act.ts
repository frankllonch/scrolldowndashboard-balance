/**
 * What an act is, and what it is handed.
 *
 * An act owns its markup, its copy and which figures it mounts. That is the
 * whole point of the shape: changing what the week section says means opening
 * `a04-the-week.ts` and nothing else.
 */

import type { Payload, Profile, UserId } from "../types/index";

/** What the sliders point at while an act is built. */
export interface Selection {
  user: UserId;
  week: number;
  day: string;
}

export interface Context {
  payload: Payload;
  /** The profile being read. Parts 1 and 3 look at both and ignore this. */
  user: UserId;
  profile: Profile;
  selection: Selection;
}

export interface Act {
  /** Two digits, matching the `#act-NN` the page and the rail use. */
  id: string;
  /** 1 is the setup, 2 is one person's month, 3 is the analysis. */
  part: 1 | 2 | 3;
  eyebrow: string;
  title: string;
  /**
   * The line handing the reader to the next act.
   *
   * A scroll only works if each scene asks for the next one. The last act has
   * nothing to hand to and leaves this out.
   */
  next?: string;
  build(ctx: Context): string;
}

/** Part 2 is lived from inside one profile; the rest is not. */
export function perProfile(act: Act): boolean {
  return act.part === 2;
}

/** The other profile's summary, for an act that compares the two. */
export function other(ctx: Context): Profile | undefined {
  const them = ctx.payload.meta.profiles.find((u) => u !== ctx.user);
  return them ? ctx.payload.profiles[them] : undefined;
}
