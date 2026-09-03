/**
 * Act 01 · the cover.
 *
 * What Balance is, what this page is for, the dataset in three numbers, and
 * one line saying why to keep reading.
 */

import { thousands } from "../format";
import { grid, lede, note, stat } from "../html";
import type { Act, Context } from "./act";

const copy = {
  eyebrow: "Balance Phone · May 2026",
  title: "Balance board",

  standfirst:
    "Balance makes a phone that helps people build a healthier relationship with their device — it blocks distraction, understands how someone actually uses their phone, and helps keep younger users safer online. "
    + "Not a dumbphone, not anti-tech: technology that serves your life instead of hijacking it.",

  purpose:
    "This dashboard takes in the raw behavioural output of two Balance Phones, with two very different users, across the whole of May 2026. "
    + "The goal is to turn that data into meaning and answer one question: <b>so what?</b>",

  intro:
    "Two adults, thirty days each. "
    + "A holds steady; B loses control as the month goes on — not from using the phone more, but from using it later and later. "
    + "Everything below is why.",

  profiles: "profiles",
  events: "events",
  days: "days each",

  next: "First, one number for each of them.",
};

export const act: Act = {
  id: "01",
  part: 1,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build({ payload }: Context): string {
    const { meta } = payload;
    return lede(copy.standfirst)
      + note(copy.purpose)
      + grid([
        stat(String(meta.profiles.length), copy.profiles),
        stat(thousands(meta.events), copy.events),
        stat(String(meta.days), copy.days),
      ], 3)
      + lede(copy.intro);
  },
};
