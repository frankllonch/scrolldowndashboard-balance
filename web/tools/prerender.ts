/**
 * Writing the page.
 *
 * Every section is rendered here, at build time, so the document that ships is
 * complete and readable before a single line of script runs. This is the last
 * thing the Python side did that TypeScript had not taken over.
 */

/** The two node globals this tool needs. Declaring them beats a dependency on
 *  the whole of `@types/node` for a file that never ships. */
declare const process: {
  argv: string[];
  stdout: { write(text: string): void };
};
declare function require(id: "node:fs"): {
  readFileSync(path: string, encoding: string): string;
};

import raw from "../../docs/data.json";
import { bodies, rail, section } from "../page";
import { ACTS } from "../acts/index";
import { chrome } from "../copy/units";
import type { Payload } from "../types/index";

/** The standfirst doubles as the page description. */
const DESCRIPTION =
  "Balance makes a phone that helps people build a healthier relationship "
  + "with their device — it blocks distraction, understands how someone "
  + "actually uses their phone, and helps keep younger users safer online. "
  + "Not a dumbphone, not anti-tech: technology that serves your life instead "
  + "of hijacking it.";

export function render(shell: string, payload: Payload): string {
  const user = payload.meta.defaultProfile;
  const built = bodies(payload, user);
  let html = shell;
  for (const act of ACTS) {
    html = html.replace(`<!--act:${act.id}-->`,
                        section(act, built[act.id] ?? ""));
  }
  return html
    .replace("<!--title-->", chrome.pageTitle)
    .replace("<!--description-->", DESCRIPTION)
    .replace("<!--rail-->", rail())
    .replace("<!--pill-->",
             `${chrome.pillLabel} <span class="who">${user}</span>`)
    .replace(' data-profile="A"', ` data-profile="${user}"`);
}

const shellPath = process.argv[2];
if (!shellPath) throw new Error("usage: prerender <shell.html>");
process.stdout.write(render(
  require("node:fs").readFileSync(shellPath, "utf8"),
  raw as unknown as Payload));
