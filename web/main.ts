/**
 * The page.
 *
 * Everything visible is already in the document when this runs: the sections
 * were written at build time, so the page reads without script. What this adds
 * is the plots, the two sliders, the profile switch and the travelling
 * surface.
 */

import type { Selection } from "./charts/index";
import { load, profile as profileOf } from "./document";
import { currentProfile, root } from "./interaction/dom";
import { drawWithin } from "./interaction/plots";
import { progressBar, watchActs, watchResize } from "./interaction/reader";
import { bindSliders } from "./interaction/sliders";
import {
  applyProfile, bindSwitches, requested, skipTheFork,
} from "./interaction/switch";

async function start(): Promise<void> {
  const payload = await load();
  const user = currentProfile() || payload.meta.defaultProfile;
  const profile = profileOf(payload, user);

  /** What the sliders point at. One object, updated in place, read by
   *  everything that builds a figure. */
  const selection: Selection = {
    user, week: profile.defaultWeek, day: profile.defaultDay,
  };
  root.dataset.profile = user;

  // Draw first. Every figure changes the height of the act holding it, and
  // the two things below aim at geometry: the observer that decides which act
  // owns the surface, and the fork's scroll into act 04.
  await drawWithin(document, payload, selection);
  bindSliders(payload, selection);
  watchActs();
  bindSwitches(payload, selection);

  const asked = requested(payload);
  if (asked) {
    skipTheFork();
    await applyProfile(payload, selection, asked, false);
  }

  progressBar();
  window.addEventListener("scroll", progressBar, { passive: true });
  watchResize();
}

void start().catch((error: unknown) => {
  console.error("the page could not start", error);
});
