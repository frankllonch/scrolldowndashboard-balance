/**
 * Where the reader is, and what the page does about it.
 *
 * The surface travels with them: whichever act holds the middle of the
 * viewport owns the page's tokens.
 */

import { plotly } from "../charts/plotly";
import { act, all, one, root } from "../interaction/dom";
import { drawn } from "../interaction/plots";
import { PART_TWO } from "../page";

let painted: string | null = null;

/**
 * Point the page's tokens at one act's surface.
 *
 * Every figure was built for its own surface, grid included. The night is the
 * exception: it borrows figures drawn for the dark ground and dims them, so
 * act 06 is the only one that needs re-pointing, in or out.
 */
function paintSurface(id: string, force = false): void {
  if (id === painted && !force) return;
  painted = id;
  root.dataset.surface = `a${id}`;
  const colour = getComputedStyle(root).getPropertyValue("--grid").trim();
  const grid = { "xaxis.gridcolor": colour, "yaxis.gridcolor": colour };
  const night = act("06");
  if (!night) return;
  for (const mount of all(".chart", night)) {
    if (drawn(mount)) void plotly().relayout(mount, grid);
  }
}

/** Repaint whatever surface is current, after part two changed height. */
export function repaint(): void {
  if (painted) paintSurface(painted, true);
}

/** How far down the page the reader is, as the bar across the top. */
export function progressBar(): void {
  const bar = one("#progress-bar");
  if (!bar) return;
  const scrollable = root.scrollHeight - window.innerHeight;
  const share = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  bar.style.width = `${share}%`;
}

/** Which act owns the middle of the viewport: the surface, the rail's current
 *  item, and whether the profile switch means anything here. */
/**
 * The act holding the middle of the viewport, or nothing between two.
 *
 * Measured rather than remembered. The observer below is a good trigger and a
 * bad judge: on a jump it reports several acts at once, in an order that is
 * not the order they sit on the page, and taking the last one left the ground
 * painted for a section the reader had already scrolled past.
 */
function owner(sections: HTMLElement[]): HTMLElement | undefined {
  const middle = window.innerHeight / 2;
  return sections.find((section) => {
    const box = section.getBoundingClientRect();
    return box.top <= middle && box.bottom >= middle;
  });
}

function holdsMiddle(section: HTMLElement): boolean {
  const middle = window.innerHeight / 2;
  const box = section.getBoundingClientRect();
  return box.top <= middle && box.bottom >= middle;
}

export function watchActs(): void {
  const sections = all<HTMLElement>(".act");
  const links = new Map<string, HTMLElement>();
  for (const link of all("[data-rail]")) {
    if (link.dataset.rail) links.set(link.dataset.rail, link);
  }
  let active: HTMLElement | null = null;
  let held: HTMLElement | null = null;

  const settle = () => {
    const section = owner(sections);
    if (!section) return;          // between two acts: whoever had it keeps it
    held = section;
    const id = section.id.slice(4);
    paintSurface(id);
    // The pill is only true where it does something: part one has the fork,
    // part three reads both profiles at once.
    const pill = document.getElementById("profile-pill");
    if (pill) pill.hidden = !PART_TWO.includes(id);
    const link = links.get(id);
    if (!link || link === active) return;
    active?.removeAttribute("aria-current");
    active = link;
    link.setAttribute("aria-current", "true");
  };

  // Two triggers, because neither is enough on its own. The observer catches
  // a jump that lands somewhere new. It does not fire when the boundary
  // between two acts drifts across its band — both stay intersecting, and the
  // middle changes hands with nothing to say so. That is what the scroll
  // handler is for, and it costs one rectangle while the answer holds.
  const watcher = new IntersectionObserver(settle,
                                           { rootMargin: "-45% 0px -45% 0px" });
  for (const section of sections) watcher.observe(section);

  let queued = false;
  window.addEventListener("scroll", () => {
    if (queued || (held && holdsMiddle(held))) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      settle();
    });
  }, { passive: true });
}

/**
 * Resizing, on width only.
 *
 * iOS fires resize every time the URL bar slides, which is most of a scroll.
 * Plotly's own responsive handler would re-lay out twenty-six plots on each
 * one, so it is off and this takes its place.
 */
export function watchResize(): void {
  let width = window.innerWidth;
  let settling: number | undefined;
  window.addEventListener("resize", () => {
    if (window.innerWidth === width) return;
    width = window.innerWidth;
    window.clearTimeout(settling);
    settling = window.setTimeout(() => {
      // Not `Plots.resize`: it drops the authored height and switches the plot
      // to autosize, making every act taller. Only width changes on a
      // rotation, and it is the card's content box.
      for (const el of all(".js-plotly-plot")) {
        const box = getComputedStyle(el);
        void plotly().relayout(el, {
          width: el.clientWidth - parseFloat(box.paddingLeft)
                 - parseFloat(box.paddingRight),
        });
      }
    }, 160);
  }, { passive: true });
}

/** Where the reader is, as an act plus how far into it, so the switch can put
 *  them back after part two changes height. */
interface Anchor {
  section: HTMLElement;
  into: number;
}

export function anchor(): Anchor | null {
  const above = all(".act").filter((a) => a.offsetTop <= window.scrollY + 1);
  const section = above[above.length - 1] ?? one<HTMLElement>(".act");
  return section ? { section, into: window.scrollY - section.offsetTop } : null;
}

export function restore(mark: Anchor | null): void {
  if (!mark) return;
  window.scrollTo({ top: mark.section.offsetTop + mark.into,
                    behavior: "instant" });
}
