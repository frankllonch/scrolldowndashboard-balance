/**
 * The layout every figure starts from, and the two things every builder does.
 *
 * A function of the surface rather than a registered global, so a builder's
 * colours are whatever it was handed and nothing depends on the order the
 * figures happen to be made in.
 */

import { MONO, SANS, type Surface } from "../theme";
import type { Annotation, Axis, Config, Layout, Trace } from "./plotly";

/** Nothing on this page is a Plotly toolbar; the page owns its own resizing. */
export const CONFIG: Config = {
  displayModeBar: false,
  responsive: false,
  doubleClick: false,
  showTips: false,
};

function axis(s: Surface): Axis {
  return {
    showline: true, linecolor: s.rule, linewidth: 1.2, mirror: false,
    ticks: "outside", tickcolor: s.rule, ticklen: 4,
    tickfont: { family: MONO, size: 11, color: s.ink2 },
    gridcolor: s.grid, zeroline: false,
    title: { font: { family: MONO, size: 11, color: s.ink2 } },
  };
}

/** The base layout for a figure drawn on `s`. */
export function base(s: Surface): Layout {
  return {
    font: { family: SANS, color: s.ink2, size: 13 },
    title: { font: { family: SANS, color: s.ink, size: 15 }, x: 0.01,
             xanchor: "left" },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    colorway: s.categorical,
    xaxis: axis(s),
    yaxis: axis(s),
    legend: {
      bgcolor: "rgba(0,0,0,0)",
      font: { family: MONO, size: 11, color: s.ink2 },
      orientation: "h", yanchor: "top", y: -0.18, xanchor: "left", x: 0,
    },
    margin: { t: 48, r: 24, b: 68, l: 56 },
    hoverlabel: { bgcolor: s.card, bordercolor: s.rule,
                  font: { family: MONO, size: 12, color: s.ink } },
    hovermode: "x unified",
  };
}

/** A finished figure: the base layout, then whatever the builder overrides. */
export function frame(s: Surface, data: Trace[], layout: Layout,
                      height = 340): { data: Trace[]; layout: Layout } {
  const merged = { ...base(s), ...layout, height };
  // The axes are objects, so a builder setting one axis would otherwise drop
  // the whole styled axis underneath it.
  merged.xaxis = { ...axis(s), ...layout.xaxis };
  merged.yaxis = { ...axis(s), ...layout.yaxis };
  return { data, layout: merged };
}

/** A label at the end of a line, so identity is never colour alone. */
export function directLabel(x: string | number, y: number, text: string,
                            color: string, dx = 6): Annotation {
  return {
    x, y, text: ` ${text}`, showarrow: false,
    xanchor: "left", yanchor: "middle", xshift: dx,
    font: { family: MONO, size: 11, color },
  };
}
