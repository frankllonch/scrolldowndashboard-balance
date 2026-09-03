/**
 * The slice of Plotly this project uses, typed.
 *
 * The vendored build is a custom cartesian bundle loaded as a global script,
 * so there is no module to import types from. Declaring the five calls we
 * actually make is narrower and more honest than pulling in the full
 * `@types/plotly.js`, and it fails the build the day someone reaches for
 * something the vendored bundle does not contain.
 */

/** A trace. Plotly's own union is enormous; this is what the builders emit. */
export interface Trace {
  type?: "scatter" | "scattergl" | "bar" | "heatmap";
  mode?: string;
  orientation?: "h" | "v";
  x?: Array<string | number | null>;
  y?: Array<string | number | null>;
  z?: Array<Array<number | null>>;
  name?: string;
  text?: Array<string | number>;
  textposition?: string;
  textfont?: Font;
  customdata?: unknown[];
  hovertemplate?: string;
  hoverinfo?: string;
  hoverlabel?: { bgcolor?: string; bordercolor?: string; font?: Font };
  showlegend?: boolean;
  /** `true`, or "legendonly" for a series the reader can switch on. */
  visible?: boolean | "legendonly";
  legendgroup?: string;
  legendgrouptitle?: { text: string; font?: Font };
  stackgroup?: string;
  fill?: string;
  fillcolor?: string;
  line?: Line;
  marker?: Marker;
  colorscale?: Array<[number, string]>;
  showscale?: boolean;
  colorbar?: Record<string, unknown>;
  zmin?: number;
  zmax?: number;
  xgap?: number;
  ygap?: number;
  base?: Array<number>;
  width?: number | number[];
  offsetgroup?: string;
  cliponaxis?: boolean;
}

interface Font {
  family?: string;
  size?: number;
  color?: string | string[];
}

interface Line {
  color?: string;
  width?: number;
  dash?: string;
  shape?: string;
  smoothing?: number;
}

interface Marker {
  color?: string | string[] | number[];
  size?: number | number[];
  symbol?: string;
  opacity?: number | number[];
  line?: Line;
  colorscale?: Array<[number, string]>;
  showscale?: boolean;
  cmin?: number;
  cmax?: number;
}

export interface Axis {
  title?: { text?: string; font?: Font; standoff?: number };
  range?: Array<number | string | null>;
  autorange?: boolean | "reversed";
  dtick?: number | string;
  tick0?: number | string;
  tickformat?: string;
  tickvals?: Array<number | string>;
  ticktext?: string[];
  tickfont?: Font;
  tickangle?: number;
  showticklabels?: boolean;
  showgrid?: boolean;
  showline?: boolean;
  linecolor?: string;
  linewidth?: number;
  mirror?: boolean;
  ticks?: string;
  tickcolor?: string;
  ticklen?: number;
  gridcolor?: string;
  zeroline?: boolean;
  zerolinecolor?: string;
  zerolinewidth?: number;
  type?: "linear" | "log" | "date" | "category";
  categoryorder?: string;
  categoryarray?: string[];
  fixedrange?: boolean;
  side?: string;
  overlaying?: string;
  domain?: [number, number];
  anchor?: string;
  automargin?: boolean;
}

interface Shape {
  type: "line" | "rect";
  x0?: number | string;
  x1?: number | string;
  y0?: number | string;
  y1?: number | string;
  xref?: string;
  yref?: string;
  line?: Line;
  fillcolor?: string;
  layer?: string;
}

export interface Annotation {
  x?: number | string;
  y?: number | string;
  xref?: string;
  yref?: string;
  text: string;
  showarrow?: boolean;
  xanchor?: string;
  yanchor?: string;
  xshift?: number;
  yshift?: number;
  font?: Font;
  align?: string;
  bgcolor?: string;
  bordercolor?: string;
  borderpad?: number;
  textangle?: number;
}

export interface Layout {
  title?: { text?: string; font?: Font; x?: number; xanchor?: string };
  height?: number;
  width?: number;
  font?: Font;
  paper_bgcolor?: string;
  plot_bgcolor?: string;
  colorway?: string[];
  xaxis?: Axis;
  yaxis?: Axis;
  yaxis2?: Axis;
  legend?: {
    bgcolor?: string; font?: Font; orientation?: string; yanchor?: string;
    y?: number; xanchor?: string; x?: number; traceorder?: string;
    /** "toggleitem" so a legend click switches one series, not the group. */
    groupclick?: string;
    grouptitlefont?: Font;
  };
  showlegend?: boolean;
  margin?: { t?: number; r?: number; b?: number; l?: number; pad?: number };
  hoverlabel?: { bgcolor?: string; bordercolor?: string; font?: Font };
  hovermode?: string | false;
  bargap?: number;
  bargroupgap?: number;
  barmode?: "stack" | "group" | "overlay" | "relative";
  shapes?: Shape[];
  annotations?: Annotation[];
  uirevision?: string | number;
  separators?: string;
}

export interface Figure {
  data: Trace[];
  layout: Layout;
}

export interface Config {
  displayModeBar?: boolean;
  responsive?: boolean;
  staticPlot?: boolean;
  scrollZoom?: boolean;
  doubleClick?: boolean | string;
  showTips?: boolean;
  locale?: string;
}

/** The global the vendored bundle installs. */
export interface PlotlyStatic {
  newPlot(el: HTMLElement, data: Trace[], layout: Layout,
          config?: Config): Promise<HTMLElement>;
  react(el: HTMLElement, data: Trace[], layout: Layout,
        config?: Config): Promise<HTMLElement>;
  relayout(el: HTMLElement, update: Record<string, unknown>): Promise<HTMLElement>;
  restyle(el: HTMLElement, update: Record<string, unknown>,
          traces?: number[]): Promise<HTMLElement>;
  purge(el: HTMLElement): void;
}

declare global {
  // eslint-disable-next-line no-var
  var Plotly: PlotlyStatic;
}

/** The bundle, or a clear failure rather than a blank page. */
export function plotly(): PlotlyStatic {
  if (typeof Plotly === "undefined") {
    throw new Error("the Plotly bundle did not load");
  }
  return Plotly;
}
