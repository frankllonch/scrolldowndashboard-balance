/**
 * The check that the two halves still agree.
 *
 * `npm run typecheck` compiles this file against the emitted document. If
 * `emit.py` renames a field, drops one, or starts sending a string where the
 * page expects a number, the build fails here rather than at a blank chart.
 */

import raw from "../../docs/data.json";
import type { Payload } from "./index";

/**
 * A JSON import types every string as `string`, so assigning it straight to
 * `Payload` fails on the literal unions — `Category`, `BlockType`, `Decision`
 * — even when the values are right. `Loose` widens exactly those and leaves
 * everything else checked: field names, nullability, and number against
 * string, which is the drift that actually happens.
 *
 * Membership of the unions is asserted in `tests/test_emit.py`, on the side
 * that produces the values.
 */
type Loose<T> =
  T extends string ? string :
  T extends number ? number :
  T extends boolean ? boolean :
  T extends null ? null :
  T extends Array<infer U> ? Array<Loose<U>> :
  T extends object ? { [K in keyof T]: Loose<T[K]> } :
  T;

const checked: Loose<Payload> = raw;

/** The document, typed. Every module reads it through here. */
export const payload = checked as unknown as Payload;
