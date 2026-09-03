/**
 * Build every act body and print them as JSON.
 *
 * Paired with `tests/test_acts.py`, which pulls the same bodies out of the
 * page Python still writes and compares them. It is a tool, not part of the
 * page.
 */

declare const process: { stdout: { write(text: string): void } };

import raw from "../../docs/data.json";
import { bodies } from "../page";
import type { Payload } from "../types/index";

const payload = raw as unknown as Payload;
const out: Record<string, Record<string, string>> = {};
for (const user of payload.meta.profiles) {
  out[user] = bodies(payload, user);
}
process.stdout.write(JSON.stringify(out));
