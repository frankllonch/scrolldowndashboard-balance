/**
 * The two sliders.
 *
 * The weeks and the days are discrete, the thumb is not: it slides freely and
 * the reading follows the nearest real one. The label is what the eye tracks,
 * so it moves every frame; rebuilding the panel underneath costs far more than
 * a frame allows, so that waits for the drag to settle. On release the thumb
 * lands on a whole step, and so do the arrow keys.
 */

import { plotly } from "../charts/plotly";
import { dayPanel, weekPanel } from "../acts/index";
import { act, all, fill, fillAll, one, slider } from "../interaction/dom";
import { draw, drawn } from "../interaction/plots";
import { profile as profileOf } from "../document";
import { weekLabel } from "../copy/figures";
import { userColor, surface } from "../theme";
import type { Payload } from "../types/index";
import type { Selection } from "../charts/index";

const SETTLE_MS = 90;

/**
 * Pending panel updates, by slider.
 *
 * Held at module scope so re-binding after a profile switch can cancel one,
 * instead of letting it land afterwards and move the reader who had just been
 * put back in place.
 */
const settling: Record<string, number | undefined> = {};

function weekEvolutionColours(payload: Payload, selection: Selection): string[] {
  const s = surface("light");
  const colour = userColor(s, selection.user);
  return profileOf(payload, selection.user).weekly
    .map((w) => (w.week === selection.week ? colour : s.dim));
}

/** The week panel, and the three figures that only need re-pointing. */
function applyWeek(payload: Payload, selection: Selection): void {
  const profile = profileOf(payload, selection.user);
  fillAll(weekPanel(profile, selection.week));

  const week = act("04");
  if (!week) return;
  for (const mount of all("[data-figure-week]", week)) {
    mount.dataset.figure = `${mount.dataset.figureWeek}.${selection.week}`;
    void draw(mount, payload, selection);
  }
  const colours = weekEvolutionColours(payload, selection);
  for (const mount of all('[data-figure^="week_evolution."]', week)) {
    if (drawn(mount)) {
      void plotly().restyle(mount, { "marker.color": [colours] }, [0]);
    }
  }
  const components = one('[data-figure="week_components"]', week);
  if (components && drawn(components)) {
    const at = weekLabel(selection.week);
    void plotly().relayout(components,
                           { "shapes[0].x0": at, "shapes[0].x1": at });
  }
}

/** The day panel, and the cursor on the walkthrough. */
function applyDay(payload: Payload, selection: Selection): void {
  const profile = profileOf(payload, selection.user);
  fillAll(dayPanel(profile, selection.day));
  const tracked = one('[data-figure="tracked_series"]');
  if (tracked && drawn(tracked)) {
    void plotly().relayout(tracked, { "shapes[1].x0": selection.day,
                                      "shapes[1].x1": selection.day });
  }
}

/** What the readout beside a slider says at a given step. */
function readout(payload: Payload, selection: Selection, kind: "week" | "day",
                 index: number): string {
  const profile = profileOf(payload, selection.user);
  if (kind === "week") {
    const row = profile.weekly.find((w) => w.week === index);
    return row ? (row.is_partial ? `Week ${row.week} (short)`
                                 : `Week ${row.week}`) : "";
  }
  const day = profile.replay[index];
  if (!day) return "";
  const [, month, dayOfMonth] = day.day.split("-");
  const names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${Number(dayOfMonth)} ${names[Number(month) - 1] ?? month}`;
}

/**
 * Bind both sliders to the live selection.
 *
 * `selection` is the object the rest of the page reads, so moving a slider
 * updates it in place rather than passing a new one around.
 */
export function bindSliders(payload: Payload, selection: Selection): void {
  for (const kind of ["week", "day"] as const) {
    const input = slider(kind);
    if (!input) continue;
    let shown = Math.round(Number(input.value));
    window.clearTimeout(settling[kind]);

    const apply = (index: number) => {
      if (kind === "week") {
        selection.week = index;
        applyWeek(payload, selection);
      } else {
        const day = profileOf(payload, selection.user).replay[index];
        if (!day) return;
        selection.day = day.day;
        applyDay(payload, selection);
      }
    };

    input.oninput = () => {
      const index = Math.round(Number(input.value));
      if (index === shown) return;
      shown = index;
      fill(`${kind}.label`, readout(payload, selection, kind, index));
      window.clearTimeout(settling[kind]);
      settling[kind] = window.setTimeout(() => apply(index), SETTLE_MS);
    };
    input.onchange = () => {
      input.value = String(Math.round(Number(input.value)));
      window.clearTimeout(settling[kind]);
      apply(Math.round(Number(input.value)));
    };
    input.onkeydown = (event: KeyboardEvent) => {
      const by = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1,
                   ArrowUp: 1 }[event.key];
      if (!by) return;
      event.preventDefault();
      input.value = String(Math.round(Number(input.value)) + by);
      input.dispatchEvent(new Event("input"));
    };
  }
}

/** The two slider positions, so a profile switch can put them back. */
export function held(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const kind of ["week", "day"] as const) {
    const input = slider(kind);
    if (input) out[kind] = input.value;
  }
  return out;
}

/**
 * Put both sliders back where they were.
 *
 * Through the events, not around them: `input` so the handler updates the
 * index it remembers drawing, `change` so it draws now rather than after the
 * debounce, which would land after the reader had been put back.
 */
export function restoreSliders(positions: Record<string, string>): void {
  for (const [kind, value] of Object.entries(positions)) {
    const input = slider(kind as "week" | "day");
    if (!input) continue;
    input.value = value;
    input.dispatchEvent(new Event("input"));
    input.dispatchEvent(new Event("change"));
  }
}
