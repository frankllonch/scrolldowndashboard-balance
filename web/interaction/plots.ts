/**
 * Getting a figure onto the page.
 *
 * A mount names the figure it wants; this builds it and draws it. Nothing is
 * shipped pre-built: 35 figures and a template per surface would be 59 KB of
 * layout in the document, and a second copy of the palette.
 */

import { build, type Selection } from "../charts/index";
import { CONFIG } from "../charts/frame";
import { plotly } from "../charts/plotly";
import { all } from "../interaction/dom";
import { profile as profileOf } from "../document";
import type { Payload } from "../types/index";

/** A mount Plotly has already drawn into carries its own data. */
type Drawn = HTMLElement & { data?: unknown };

export function drawn(mount: HTMLElement): boolean {
  return Boolean((mount as Drawn).data);
}

/** Build the figure a mount asks for and draw it. A mount whose key has no
 *  builder, or whose profile has no data for it, is left empty. */
export function draw(mount: HTMLElement, payload: Payload,
                     selection: Selection): Promise<unknown> {
  const key = mount.dataset.figure;
  if (!key) return Promise.resolve();
  const figure = build(key, payload, profileOf(payload, selection.user),
                       selection);
  if (!figure) return Promise.resolve();
  return plotly().newPlot(mount, figure.data, figure.layout, CONFIG);
}

/**
 * Every plot inside one scope.
 *
 * Plotly settles asynchronously and every figure it draws changes the height
 * of the act holding it, so anything that moves the reader waits on this or
 * aims at geometry about to shift underneath it.
 */
export function drawWithin(scope: ParentNode, payload: Payload,
                           selection: Selection): Promise<unknown[]> {
  return Promise.all(all(".chart", scope).map((m) => draw(m, payload, selection)));
}
