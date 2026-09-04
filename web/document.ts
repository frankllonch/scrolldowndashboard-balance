/**
 * The document: everything the backend hands over, fetched at runtime.
 *
 * `types/contract.ts` imports the same file statically so the compiler can
 * check its shape. Nothing imports that module at runtime, so the 164 KB
 * stays out of the bundle and is fetched and cached on its own.
 */

import type { Payload, Profile, UserId } from "./types/index";

const SOURCE = "data.json";

/** Fetch the document. The shape is guaranteed by `npm run typecheck`, so
 *  there is nothing to validate again here. */
export async function load(): Promise<Payload> {
  const response = await fetch(SOURCE);
  if (!response.ok) {
    throw new Error(`${SOURCE}: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as Payload;
}

/** One profile, or a clear failure. Reading `payload.profiles[user]` directly
 *  gives `Profile | undefined` under `noUncheckedIndexedAccess`, and every
 *  caller would have to answer for a case that means the document is broken. */
export function profile(payload: Payload, user: UserId): Profile {
  const found = payload.profiles[user];
  if (!found) {
    throw new Error(`no profile ${user} in the document`);
  }
  return found;
}
