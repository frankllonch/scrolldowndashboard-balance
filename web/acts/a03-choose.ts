/**
 * Act 03 · the fork. A real choice, full screen, not a dropdown.
 */

import { hm } from "../format";
import { eyebrow, lede, stat } from "../html";
import type { Profile, UserId } from "../types/index";
import type { Act, Context } from "./act";

const copy = {
  eyebrow: "Pick one",
  title: "Choose a profile",

  lede: "Both months are here. Read one, then the other.",
  cardEyebrow: (user: UserId) => `User ${user}`,

  sketch: {
    A: "Likely an adult with a stable relationship with their phone. "
    + "WhatsApp, Spotify and the news fill most of their days, consistent across the whole month.",
    B: "Also an adult, and also mostly WhatsApp, Spotify, Maps and the papers — but with a more erratic pattern. "
    + "A lot of tries to access blocked sites. The days hold steady. The nights slide and sleep is lost.",
  },

  screen: "screen / day",
  index: "index",
  nights: "nights with a nudge",
  cta: "Read this month",

  next: "Start where the shape is easiest to see: a week at a time.",
};

function card(profile: Profile): string {
  const s = profile.summary;
  const sketch = s.user === "A" ? copy.sketch.A : copy.sketch.B;
  return `<button class="fork-card" data-choose="${s.user}" type="button">`
    + eyebrow(copy.cardEyebrow(s.user))
    + `<p class="fork-sketch">${sketch}</p>`
    + '<div class="fork-stats">'
    + stat(hm(s.screen_mean), copy.screen)
    + stat(s.score_mean.toFixed(0), copy.index)
    + stat(String(s.nudge_nights), copy.nights)
    + "</div>"
    + `<span class="fork-cta">${copy.cta}</span>`
    + "</button>";
}

export const act: Act = {
  id: "03",
  part: 1,
  eyebrow: copy.eyebrow,
  title: copy.title,
  next: copy.next,
  build({ payload }: Context): string {
    const cards = payload.meta.profiles
      .map((u) => payload.profiles[u])
      .filter((p): p is Profile => p !== undefined)
      .map(card).join("");
    return lede(copy.lede) + `<div class="fork">${cards}</div>`;
  },
};
