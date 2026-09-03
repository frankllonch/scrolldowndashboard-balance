/**
 * Reaching into the document.
 *
 * Narrow on purpose: every query the page makes goes through one of these, so
 * the selectors it depends on are all in one file.
 */

export function one<T extends Element = HTMLElement>(
    selector: string, within: ParentNode = document): T | null {
  return within.querySelector<T>(selector);
}

export function all<T extends Element = HTMLElement>(
    selector: string, within: ParentNode = document): T[] {
  return [...within.querySelectorAll<T>(selector)];
}

/** A section, by the two digits in its id. */
export function act(id: string): HTMLElement | null {
  return document.getElementById(`act-${id}`);
}

/** Content a slider replaces. */
export function fill(name: string, html: string): void {
  const target = one(`[data-slot="${name}"]`);
  if (target) target.innerHTML = html;
}

export function fillAll(panel: Record<string, string>): void {
  for (const [name, html] of Object.entries(panel)) fill(name, html);
}

export function slider(kind: "week" | "day"): HTMLInputElement | null {
  return document.getElementById(`${kind}-slider`) as HTMLInputElement | null;
}

export const root = document.documentElement;

export function currentProfile(): string {
  return root.dataset.profile ?? "";
}
