/**
 * Palette and Plotly template, in three surfaces.
 *
 * The page moves from paper to a warm olive to near-black as it scrolls, and
 * a figure is drawn for the ground it will sit on. Hues that identify things
 * — a user, a content category — keep their identity across all three and
 * only move in lightness, so a stack keeps its shape when the ground changes.
 *
 * A surface is a value here, not module state: `surface("light")` returns one
 * and builders take it as an argument. The Python this replaces rebound module
 * globals, which meant reading a builder told you nothing about which palette
 * it would get.
 */

import type { Category, UserId } from "./types/index";

export type SurfaceName = "light" | "dusk" | "dark";

/** A colour stop on a continuous scale: position 0–1, then the colour. */
type ColorStop = [number, string];

export interface Surface {
  name: SurfaceName;
  /** The ground a figure is drawn on. Nothing paints it; it is what shows. */
  card: string;
  ink: string;
  ink2: string;
  muted: string;
  rule: string;
  grid: string;
  /** A bar that is present but not selected. */
  dim: string;
  /** A value the figure draws but does not want read: a lost point. */
  lost: string;
  heat: ColorStop[];
  sequential: ColorStop[];
  /** Fixed order, never cycled, never following the ranking. */
  categorical: string[];
  userColor: Record<UserId, string>;
  good: string;
  warn: string;
  serious: string;
}

export const MONO = "IBM Plex Mono, ui-monospace, SFMono-Regular, monospace";
export const SANS = "Inter, sans-serif";

const SURFACES: Record<SurfaceName, Surface> = {
  dark: {
    name: "dark",
    card: "#121214", ink: "#f1eee8", ink2: "#a3a09a", muted: "#6b6862",
    rule: "#2b2b31", grid: "#1c1c21", dim: "#2f2f36", lost: "#33333a",
    heat: [[0, "#131317"], [0.2, "#17324f"], [0.45, "#1f5ca3"],
           [0.75, "#3d86d8"], [1, "#7fb6f2"]],
    sequential: [[0, "#10243c"], [0.25, "#17406e"], [0.5, "#1f5ca3"],
                 [0.75, "#2f7ad0"], [1, "#5ba1ee"]],
    categorical: ["#3987e5", "#199e70", "#c98500", "#008300",
                  "#9085e9", "#e66767", "#d55181", "#d95926"],
    userColor: { A: "#199e70", B: "#d95926" },
    good: "#0ca30c", warn: "#fab219", serious: "#ec835a",
  },
  // The same eight hues, stepped down for a light ground so they keep 3:1
  // against it. Identity survives; only the lightness moves.
  light: {
    name: "light",
    card: "#e4e0d8", ink: "#17171b", ink2: "#4a4740", muted: "#6f6b62",
    rule: "#b6afa1", grid: "#cfc9bd", dim: "#b3ada1", lost: "#c6c1b6",
    heat: [[0, "#e8e5de"], [0.2, "#b9cbe0"], [0.45, "#6f9ac6"],
           [0.75, "#3a6ea8"], [1, "#1c4a7d"]],
    sequential: [[0, "#e8e5de"], [0.25, "#b9cbe0"], [0.5, "#6f9ac6"],
                 [0.75, "#3a6ea8"], [1, "#1c4a7d"]],
    categorical: ["#1c5fb0", "#0f7150", "#8f5f00", "#005f00",
                  "#6055c0", "#c03b3b", "#a82f5c", "#a63d15"],
    userColor: { A: "#0f7150", B: "#a63d15" },
    good: "#0a7a0a", warn: "#8a6410", serious: "#a8542c",
  },
  // Act 05 sits between the paper and the night, on a warm olive ground. The
  // same hues again, desaturated to belong to it rather than shout across it.
  dusk: {
    name: "dusk",
    card: "#1b1a18", ink: "#ece7dd", ink2: "#a8a29a", muted: "#7d766c",
    rule: "#35322d", grid: "#242220", dim: "#3a3733", lost: "#3d3a35",
    heat: [[0, "#1b1a18"], [0.2, "#2f4038"], [0.45, "#456355"],
           [0.75, "#5f8a73"], [1, "#8db69c"]],
    sequential: [[0, "#1b1a18"], [0.25, "#2f4038"], [0.5, "#456355"],
                 [0.75, "#5f8a73"], [1, "#8db69c"]],
    categorical: ["#5c86a8", "#57947a", "#a8894f", "#4d7d4d",
                  "#8579a8", "#b57a7a", "#a86b85", "#b5714a"],
    userColor: { A: "#57947a", B: "#b5714a" },
    good: "#5c9a5c", warn: "#c9a45c", serious: "#c08a6b",
  },
};

/** One of the three grounds, by name. */
export function surface(name: SurfaceName): Surface {
  return SURFACES[name];
}

/**
 * Colour per content category: follows the entity, not its position.
 *
 * Fixed order, never by rank, so a stack keeps its shape between profiles.
 * Reaching people, then leisure, then getting things done, then the two the
 * filter cares about. Every pair is at least ΔE 19 apart on the card and no
 * colour is under 3.7:1 against it.
 */
export const CATEGORY_COLOR: Record<Category, string> = {
  SOCIAL_MEDIA: "#3987e5",
  MESSAGING: "#199e70",
  CALLS: "#2aa5a5",
  ENTERTAINMENT: "#c98500",
  NEWS: "#d55181",
  SHOPPING: "#008300",
  GAMING: "#9085e9",
  NAVIGATION: "#4f9fd4",
  PRODUCTIVITY: "#7d8fa8",
  LEARNING: "#86b83f",
  AI_TOOLS: "#b06ad0",
  REFERENCE: "#a8894f",
  ADULT: "#e66767",
  GAMBLING: "#d95926",
  OTHER: "#55555c", // deliberately neutral: it is the catch-all
};

/** The order categories stack in. Never the ranking. */
export const CATEGORY_ORDER = Object.keys(CATEGORY_COLOR) as Category[];

/**
 * The colour that belongs to a profile.
 *
 * Indexing `userColor` directly gives `string | undefined`, and every caller
 * would have to answer for a profile the palette does not know. It falls back
 * to the categorical order instead, so an unknown third profile gets a colour
 * rather than a crash — and it is still that profile's own, not a repeat.
 */
export function userColor(s: Surface, user: UserId): string {
  const known = s.userColor[user];
  if (known) return known;
  const order = Object.keys(s.userColor).length;
  return s.categorical[order % s.categorical.length] ?? s.ink;
}
