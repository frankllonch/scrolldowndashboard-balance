/**
 * The page.
 *
 * Everything the reader sees is built here and under `web/`: Python hands
 * over numbers and this decides what they look like.
 */

import { load, profile } from "./payload";

async function main(): Promise<void> {
  const payload = await load();
  const first = payload.meta.profiles[0];
  if (!first) {
    throw new Error("the document carries no profiles");
  }
  // Phase 3 hangs the figures off here; phase 4, the acts.
  console.info("balance board", {
    profiles: payload.meta.profiles,
    days: payload.meta.days,
    score: profile(payload, first).summary.score_mean,
  });
}

void main();
