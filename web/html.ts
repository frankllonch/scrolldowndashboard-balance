/**
 * The small builders the acts are made of.
 *
 * Strings rather than DOM nodes, for the same reason the Python did: the CSS
 * in `site/css/` is written against exactly this markup, the profile switch
 * replaces whole sections at once, and a template literal reads closer to the
 * result than twenty `createElement` calls.
 *
 * Copy arrives already worded and is trusted — the catalogue carries `<b>` and
 * `<code>` on purpose. Anything that came from the data is escaped.
 */

//: `&#x27;` rather than `&#39;` for the apostrophe: both render the same, and
//: this is the form Python's `html.escape` writes, which keeps the migration
//: diff empty rather than merely equivalent.
const ESCAPES: Record<string, string> = {
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#x27;",
};

/** For a value out of the document. Never for copy. */
function esc(value: string | number): string {
  return String(value).replace(/[&<>"']/g, (c) => ESCAPES[c] ?? c);
}

function attrs(pairs: Record<string, string | number | boolean | undefined>): string {
  let out = "";
  for (const [key, value] of Object.entries(pairs)) {
    if (value === undefined || value === false) continue;
    const name = key.replace(/_/g, "-");
    out += value === true ? ` ${name}` : ` ${name}="${esc(value)}"`;
  }
  return out;
}

export function eyebrow(text: string): string {
  return `<p class="eyebrow">${text}</p>`;
}

export function note(text: string, kind = ""): string {
  return `<p class="${["note", kind].filter(Boolean).join(" ")}">${text}</p>`;
}

export function lede(text: string): string {
  return `<p class="lede">${text}</p>`;
}

export function caption(text: string): string {
  return `<p class="caption">${text}</p>`;
}

export function sub(text: string): string {
  return `<h3 class="sub">${text}</h3>`;
}

export function tags(...labels: string[]): string {
  return labels.map((x) => `<span class="tag">${x}</span>`).join("");
}

export function stat(value: string, label: string): string {
  return `<div class="stat"><span class="stat-value">${esc(value)}</span>`
    + `<span class="stat-label">${label}</span></div>`;
}

export interface Kpi {
  label: string;
  value: string;
  /** Context, never a verdict: it is never colour-coded. */
  delta?: string;
}

/** One continuous strip. */
export function kpis(items: Kpi[]): string {
  const cells = items.map((item) =>
    `<div class="kpi"><span class="kpi-label">${item.label}</span>`
    + `<span class="kpi-value">${esc(item.value)}</span>`
    + (item.delta ? `<span class="kpi-delta">${esc(item.delta)}</span>` : "")
    + "</div>").join("");
  return `<div class="kpis">${cells}</div>`;
}

export function table(columns: string[], rows: Array<Array<string | number>>): string {
  const head = columns.map((c) => `<th>${c}</th>`).join("");
  const body = rows.map((row) =>
    `<tr>${row.map((v) => `<td>${esc(v)}</td>`).join("")}</tr>`).join("");
  return `<div class="scroller"><table><thead><tr>${head}</tr></thead>`
    + `<tbody>${body}</tbody></table></div>`;
}

export function pairs(items: Array<[string, string | number]>): string {
  return items.map(([k, v]) =>
    `<div class="pair"><span>${esc(k)}</span><span>${esc(v)}</span></div>`)
    .join("");
}

export function details(summary: string, body: string): string {
  return `<details><summary>${summary}</summary>${body}</details>`;
}

export function empty(text: string): string {
  return `<div class="empty">${text}</div>`;
}

export function channel(label: string, inner: string): string {
  return `<div class="channel">${eyebrow(label)}${inner}</div>`;
}

export function grid(blocks: string[], cols = 2): string {
  return `<div class="grid cols-${cols}">${blocks.join("")}</div>`;
}

export interface PhoneCard {
  time: string;
  brand: string;
  eyebrow: string;
  headline: string;
  body: string;
  rows?: Array<[string, string | number]>;
  ctas?: Array<{ label: string; ghost: boolean }>;
}

export function phone(card: PhoneCard): string {
  const ctas = (card.ctas ?? []).map((c) =>
    `<div class="phone-cta${c.ghost ? " ghost" : ""}">${c.label}</div>`).join("");
  return '<div class="phone"><div class="phone-bar">'
    + `<span>${esc(card.time)}</span><span>${card.brand}</span></div>`
    + `<div class="phone-body"><p class="phone-eyebrow">${card.eyebrow}</p>`
    + `<p class="phone-h">${card.headline}</p>`
    + `<p class="phone-p">${card.body}</p>`
    + `${pairs(card.rows ?? [])}${ctas}</div></div>`;
}

/** Content the sliders replace. Rendered up front so the section is complete
 *  before any of them is touched. */
export function slot(name: string, inner = ""): string {
  return `<div${attrs({ data_slot: name })}>${inner}</div>`;
}

/**
 * A plot and the line under it.
 *
 * The line lives outside the mount on purpose: Plotly replaces everything
 * inside the element it draws into, so anything kept in there is destroyed on
 * the first redraw.
 */
export function chart(key: string, explanation: string, options: {
  scope?: "profile" | "shared";
  size?: "tall";
  /** A mount whose data changes with the week slider, so it re-points rather
   *  than being rebuilt. */
  weekly?: string;
} = {}): string {
  const css = ["chart", options.size].filter(Boolean).join(" ");
  const mount = `<figure class="${css}"${attrs({
    data_figure: key,
    data_figure_week: options.weekly,
    data_scope: options.scope ?? "profile",
  })}></figure>`;
  return `<div class="chart-block">${mount}`
    + `<p class="chart-explain">${explanation}</p></div>`;
}
