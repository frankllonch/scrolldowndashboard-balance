/**
 * Switching profile without losing the reader's place.
 *
 * Both profiles run the same five weeks and thirty days, so the switch keeps
 * them on the one they were reading: that is the comparison.
 */

import type { Selection } from "../charts/index";
import { act, all, one, root } from "../interaction/dom";
import { PART_TWO, bodies } from "../page";
import { drawWithin } from "../interaction/plots";
import { anchor, repaint, restore } from "../interaction/reader";
import { bindSliders, held, restoreSliders } from "../interaction/sliders";
import type { Payload } from "../types/index";

/**
 * Show a different person's month.
 *
 * Part two is rebuilt from scratch and redrawn. `keepPlace` is the pill: both
 * profiles run the same five weeks and thirty days, so it holds the reader on
 * the one they were reading and puts them back at the same point once the new
 * plots have settled and the section has stopped changing height.
 */
export async function applyProfile(payload: Payload, selection: Selection,
                                   user: string,
                                   keepPlace: boolean): Promise<void> {
  if (!payload.profiles[user]) return;
  const mark = keepPlace ? anchor() : null;
  const positions = keepPlace ? held() : {};

  selection.user = user;
  root.dataset.profile = user;

  const built = bodies(payload, user);
  for (const id of PART_TWO) {
    const body = one(".act-body", act(id) ?? document);
    if (body) body.innerHTML = built[id] ?? "";
  }

  const who = one("#profile-pill .who");
  if (who) who.textContent = user;

  const drawing = Promise.all(PART_TWO.map((id) => {
    const section = act(id);
    return section ? drawWithin(section, payload, selection) : Promise.resolve([]);
  }));

  bindSliders(payload, selection);
  restoreSliders(positions);

  await drawing;
  restore(mark);
  repaint();
}

/** The fork's two buttons, and the pill. */
export function bindSwitches(payload: Payload, selection: Selection): void {
  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    const button = target.closest<HTMLElement>("[data-choose]");
    const chosen = button?.dataset.choose;
    if (!chosen) return;
    void applyProfile(payload, selection, chosen, false)
      .then(() => act("04")?.scrollIntoView());
  });

  const pill = document.getElementById("profile-pill");
  pill?.addEventListener("click", () => {
    const others = payload.meta.profiles.filter((u) => u !== selection.user);
    const next = others[0];
    if (next) void applyProfile(payload, selection, next, true);
  });
}

/** `?profile=B` opens that month directly, with no fork to answer. */
export function requested(payload: Payload): string | null {
  const asked = new URLSearchParams(location.search).get("profile");
  return asked && payload.profiles[asked] ? asked : null;
}

/** Hide act 03 and its rail entry. A reader who arrived with `?profile=`
 *  has already answered the question the fork asks. */
export function skipTheFork(): void {
  const fork = act("03");
  if (fork) fork.hidden = true;
  for (const link of all('[data-rail="03"]')) {
    const item = link.parentElement;
    if (item) item.hidden = true;
  }
}
