/**
 * The four summaries the acts keep asking for.
 *
 * Here rather than in each act that needs one, so the page has a single
 * answer to "what is the average" instead of several that could disagree at
 * the edges.
 */

/** Zero for an empty list: an act that averages nothing is showing a metric
 *  the profile does not have, and the copy beside it says so. */
export function mean(values: number[]): number {
  return values.reduce((total, v) => total + v, 0) / (values.length || 1);
}

export function median(values: number[]): number {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2
    ? (sorted[middle] ?? 0)
    : ((sorted[middle - 1] ?? 0) + (sorted[middle] ?? 0)) / 2;
}

/** Sample standard deviation. Zero below two values, where spread has no
 *  meaning rather than being nothing. */
export function deviation(values: number[]): number {
  if (values.length < 2) return 0;
  const average = mean(values);
  const spread = values.reduce((total, v) => total + (v - average) ** 2, 0);
  return Math.sqrt(spread / (values.length - 1));
}

/**
 * The most common value, and the smallest of them on a tie.
 *
 * A "usual" first unlock is a mode, and every value being unique is a tie
 * between all of them — picking whichever came first in the frame would make
 * the answer depend on row order.
 */
export function mode(values: string[]): string {
  const counts = new Map<string, number>();
  for (const value of values) counts.set(value, (counts.get(value) ?? 0) + 1);
  let best = "";
  let most = -1;
  for (const [value, n] of [...counts].sort((a, b) => a[0].localeCompare(b[0]))) {
    if (n > most) [best, most] = [value, n];
  }
  return best;
}
