/**
 * render-ascii — deterministic Unicode rendering of a viz spec.
 *
 * This is the always-available inline representation (no image protocol
 * required, works in every terminal including tmux/foot). Line/scatter data is
 * drawn on a braille canvas; bars, tables, and diagrams use box/text glyphs.
 * PURE: safe to unit-test and to call from the interactive overlay on every
 * keystroke.
 */
import { type VizAnnotation, type VizArrow, type VizSeries, type VizSpec, sampleSpec } from "./spec.ts";

export interface RenderOptions {
  width?: number;
  height?: number;
  /** Which frame to render when `spec.frames` is present (undefined = all frames). */
  frame?: number;
  /** Ignore a hand-tuned `spec.ascii` override (interactive/explorer renders). */
  ignoreAscii?: boolean;
}

const DEFAULT_WIDTH = 72;
const DEFAULT_HEIGHT = 12;

function fmt(n: number): string {
  if (!Number.isFinite(n)) return "?";
  if (Number.isInteger(n)) return String(n);
  const r = Math.round(n * 1000) / 1000;
  return String(r);
}

function pad(s: string, width: number): string {
  return s.length >= width ? s.slice(0, width) : s + " ".repeat(width - s.length);
}

function padLeft(s: string, width: number): string {
  return s.length >= width ? s.slice(0, width) : " ".repeat(width - s.length) + s;
}

function center(s: string, width: number): string {
  if (s.length >= width) return s.slice(0, width);
  const left = Math.floor((width - s.length) / 2);
  return " ".repeat(left) + s;
}

// Braille cell: 2 columns x 4 rows of dots. Bit for [row][col].
const BRAILLE = [
  [0x01, 0x08],
  [0x02, 0x10],
  [0x04, 0x20],
  [0x40, 0x80],
];

interface Bounds {
  xMin: number;
  xMax: number;
  yMin: number;
  yMax: number;
}

function boundsOf(series: VizSeries[]): Bounds {
  let xMin = Infinity;
  let xMax = -Infinity;
  let yMin = Infinity;
  let yMax = -Infinity;
  for (const s of series) {
    for (const p of s.points) {
      if (p.x < xMin) xMin = p.x;
      if (p.x > xMax) xMax = p.x;
      if (p.y < yMin) yMin = p.y;
      if (p.y > yMax) yMax = p.y;
    }
  }
  if (!Number.isFinite(xMin)) {
    xMin = 0;
    xMax = 1;
    yMin = 0;
    yMax = 1;
  }
  if (xMin === xMax) {
    xMin -= 0.5;
    xMax += 0.5;
  }
  if (yMin === yMax) {
    yMin -= 0.5;
    yMax += 0.5;
  }
  return { xMin, xMax, yMin, yMax };
}

/** Plot one or more series on a braille canvas. Multiple series become stacked panels. */
function plotPanels(series: VizSeries[], width: number, height: number, xLabel?: string, yLabel?: string): string[] {
  const panels = series.length > 1 ? series : [series[0]];
  const out: string[] = [];
  for (const s of panels) {
    if (panels.length > 1) out.push(s.name ? `● ${s.name}` : "● series");
    out.push(...braillePanel(s.points, width, height, xLabel, yLabel));
    if (panels.length > 1) out.push("");
  }
  while (out.length && out[out.length - 1] === "") out.pop();
  return out;
}

function braillePanel(
  points: { x: number; y: number }[],
  width: number,
  height: number,
  xLabel?: string,
  yLabel?: string
): string[] {
  const b = boundsOf([{ points }]);
  const cols = Math.max(8, width - 8);
  const rows = Math.max(4, height);
  const dotCols = cols * 2;
  const dotRows = rows * 4;
  const grid = new Uint8Array(cols * rows);

  const mapX = (x: number) => Math.round(((x - b.xMin) / (b.xMax - b.xMin)) * (dotCols - 1));
  const mapY = (y: number) => dotRows - 1 - Math.round(((y - b.yMin) / (b.yMax - b.yMin)) * (dotRows - 1));
  const setDot = (dx: number, dy: number) => {
    if (dx < 0 || dy < 0 || dx >= dotCols || dy >= dotRows) return;
    const cell = Math.floor(dy / 4) * cols + Math.floor(dx / 2);
    grid[cell] |= BRAILLE[dy % 4][dx % 2];
  };

  const sorted = [...points].sort((p, q) => p.x - q.x);
  for (let i = 0; i < sorted.length; i++) {
    const dx = mapX(sorted[i].x);
    const dy = mapY(sorted[i].y);
    setDot(dx, dy);
    if (i > 0) {
      // Connect to the previous point so a "line" reads as a line.
      const px = mapX(sorted[i - 1].x);
      const py = mapY(sorted[i - 1].y);
      const steps = Math.max(Math.abs(dx - px), Math.abs(dy - py));
      for (let t = 1; t < steps; t++) {
        setDot(Math.round(px + ((dx - px) * t) / steps), Math.round(py + ((dy - py) * t) / steps));
      }
    }
  }

  const lines: string[] = [];
  const ymax = fmt(b.yMax);
  const ymin = fmt(b.yMin);
  const gutter = Math.max(ymax.length, ymin.length);
  if (yLabel) lines.push(" ".repeat(gutter + 2) + yLabel);
  for (let r = 0; r < rows; r++) {
    let row = "";
    for (let c = 0; c < cols; c++) {
      const bits = grid[r * cols + c];
      row += bits ? String.fromCodePoint(0x2800 | bits) : " ";
    }
    const tick = r === 0 ? padLeft(ymax, gutter) : r === rows - 1 ? padLeft(ymin, gutter) : " ".repeat(gutter);
    lines.push(`${tick} │${row}`);
  }
  lines.push(" ".repeat(gutter) + " └" + "─".repeat(cols));
  const xmin = fmt(b.xMin);
  const xmax = fmt(b.xMax);
  const axis = padLeft(xmin, 1) + " ".repeat(Math.max(1, cols - xmin.length - xmax.length)) + xmax;
  lines.push(" ".repeat(gutter + 2) + axis + (xLabel ? `  ${xLabel}` : ""));
  return lines;
}

function renderBar(spec: VizSpec, width: number): string[] {
  const bars = spec.bars || [];
  const barWidth = Math.max(4, Math.min(30, width - 24));
  const max = Math.max(...bars.map((b) => Math.abs(b.value)), 1);
  const labelW = Math.max(...bars.map((b) => b.label.length), 1);
  const out: string[] = [];
  for (const b of bars) {
    const n = Math.max(0, Math.round((Math.abs(b.value) / max) * barWidth));
    const sign = b.value < 0 ? "-" : "";
    out.push(`${pad(b.label, labelW)} │ ${sign}${"█".repeat(n)}${n === 0 ? "" : " "}${fmt(b.value)}`);
  }
  return out;
}

function renderTable(spec: VizSpec): string[] {
  const cols = spec.columns || [];
  const rows = spec.rows || [];
  const widths = cols.map((c, i) => Math.max(c.length, ...rows.map((r) => String(r[i] ?? "").length)));
  const head = cols.map((c, i) => pad(c, widths[i])).join("  ");
  const sep = widths.map((w) => "-".repeat(w)).join("  ");
  const body = rows.map((r) => cols.map((_, i) => pad(String(r[i] ?? ""), widths[i])).join("  "));
  return [head, sep, ...body];
}

function renderDiagram(spec: VizSpec): string[] {
  const nodes = spec.nodes || [];
  const edges = spec.edges || [];
  const label = (id: string) => nodes.find((n) => n.id === id)?.label || id;
  const out: string[] = [];
  for (const n of nodes) {
    out.push(`┌─ ${n.id} ${"─".repeat(Math.max(1, 24 - n.id.length))}┐`);
    out.push(`│  ${pad(n.label || "", 22)}│`);
    out.push(`└${"─".repeat(26)}┘`);
  }
  if (edges.length > 0) {
    if (out.length) out.push("");
    for (const e of edges) {
      const lab = e.label ? `(${e.label})` : "";
      out.push(`${label(e.from)} ──${lab}──▶ ${label(e.to)}`);
    }
  }
  return out;
}

function annotationsBlock(annotations?: VizAnnotation[]): string[] {
  if (!annotations || annotations.length === 0) return [];
  const out: string[] = [""];
  for (const a of annotations) {
    const where = a.x !== undefined || a.y !== undefined ? ` (${a.x !== undefined ? `x=${fmt(a.x)}` : ""}${a.x !== undefined && a.y !== undefined ? ", " : ""}${a.y !== undefined ? `y=${fmt(a.y)}` : ""})` : "";
    out.push(`* ${a.text}${where}`);
  }
  return out;
}

/** Arrows cannot be drawn on the braille canvas; list them as vector notes. */
function arrowsBlock(arrows?: VizArrow[]): string[] {
  if (!arrows || arrows.length === 0) return [];
  const out: string[] = [""];
  for (const a of arrows) {
    const label = a.label ? `${a.label}: ` : "";
    out.push(`→ ${label}(${fmt(a.x1)}, ${fmt(a.y1)}) to (${fmt(a.x2)}, ${fmt(a.y2)})`);
  }
  return out;
}

/** Render a single spec (no frames) to lines. */
function renderOne(spec: VizSpec, width: number, height: number): string[] {
  const lines: string[] = [];
  if (spec.title) lines.push(center(spec.title, width));
  switch (spec.kind) {
    case "line":
    case "scatter": {
      const series = sampleSpec(spec);
      lines.push(...plotPanels(series, width, height, spec.xLabel, spec.yLabel));
      break;
    }
    case "bar":
      lines.push(...renderBar(spec, width));
      break;
    case "table":
      lines.push(...renderTable(spec));
      break;
    case "diagram":
      lines.push(...renderDiagram(spec));
      break;
  }
  lines.push(...annotationsBlock(spec.annotations));
  lines.push(...arrowsBlock(spec.arrows));
  return lines;
}

/**
 * Render a viz spec to terminal lines. When `spec.frames` is present, render the
 * requested frame (or all frames stacked, each with its caption).
 */
export function renderAscii(spec: VizSpec, opts: RenderOptions = {}): string[] {
  if (spec.ascii && !opts.ignoreAscii) {
    return spec.ascii.replace(/\r/g, "").split("\n");
  }
  const width = opts.width ?? DEFAULT_WIDTH;
  const height = opts.height ?? DEFAULT_HEIGHT;
  if (spec.frames && spec.frames.length > 0) {
    const frames = spec.frames;
    const out: string[] = [];
    if (spec.title) out.push(center(spec.title, width));
    const indices = opts.frame === undefined ? frames.map((_, i) => i) : [Math.max(0, Math.min(frames.length - 1, opts.frame))];
    indices.forEach((idx, n) => {
      const fr = frames[idx];
      if (n > 0 || spec.title) out.push("");
      out.push(`[${idx + 1}/${frames.length}]${fr.caption ? ` ${fr.caption}` : ""}`);
      out.push(...renderOne(fr.spec, width, height));
    });
    return out;
  }
  return renderOne(spec, width, height);
}
