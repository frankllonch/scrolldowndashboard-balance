/**
 * The acts, in reading order.
 *
 * Parts 1 and 3 are the same for everyone. Part 2 is one person's month: it
 * builds for whichever profile is being read, and the switch rebuilds it.
 */

import { act as a01 } from "./a01-cover";
import { act as a02 } from "./a02-two-people";
import { act as a03 } from "./a03-choose";
import { act as a04 } from "./a04-the-week";
import { act as a05 } from "./a05-a-day";
import { act as a06 } from "./a06-the-night";
import { act as a07 } from "./a07-where-time-goes";
import { act as a08 } from "./a08-what-stopped";
import { act as a09 } from "./a09-what-said";
import { act as a10 } from "./a10-the-finding";
import { act as a11 } from "./a11-the-control";
import { act as a12 } from "./a12-under-the-hood";

export const ACTS = [a01, a02, a03, a04, a05, a06, a07, a08, a09, a10, a11,
                     a12];

// `readout` is what the slider shows while the thumb moves; `panel` is
// everything it lands on. The chart axis's short "W4" is a different thing
// and lives in copy/figures.ts.
export { label as weekReadout, panel as weekPanel } from "./a04-the-week";
export { label as dayReadout, panel as dayPanel } from "./a09-what-said";
export * from "./act";
