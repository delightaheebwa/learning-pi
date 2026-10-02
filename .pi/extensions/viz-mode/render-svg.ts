/**
 * render-svg — deterministic SVG generation for a viz spec.
 *
 * This is the source for the inline terminal image (rasterised by raster.ts)
 * and for `/viz svg|png` exports. It draws multi-series overlays, gridlines and
 * ticks, placed annotations, vectors (arrows), legends, bars, tables, and
 * diagrams. PURE: no pi imports, no I/O, unit-testable.
 */
import { type VizArrow, type VizSpec, sampleSpec } from "./spec.ts";

export interface SvgOptions {
  width?: number;
  height?: number;
  frame?: number;
  background?: string;
}

const W_DEFAULT = 720;
const H_DEFAULT = 400;
const PAD = { top: 58, right: 28, bottom: 66, left: 72 };

const COLORS = ["#5aa9ff", "#ff9f43", "#4ade80", "#e879f9", "#facc15", "#f87171", "#22d3ee", "#a78bfa"];
const BG = "#14161c";
const FG = "#e6e8ee";
const MUTED = "#9aa3b2";
const GRID = "#262b36";
const AXIS = "#5b6373";
const FONT = "Liberation Sans, Helvetica, Arial, sans-serif";
const MONO = "Liberation Mono, Menlo, monospace";

function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function fmt(n: number): string {
  if (!Number.isFinite(n)) return "?";
  const a = Math.abs(n);
  if (a !== 0 && (a < 0.01 || a >= 100000)) {
    const e = n.toExponential(1);
    return e.replace("e+", "e").replace("e-0", "e-").replace("e+0", "e");
  }
  const r = Math.round(n * 1000) / 1000;
  return String(r);
}

interface Scale {
  x: (v: number) => number;
  y: (v: number) => number;
}

function niceTicks(min: number, max: number, count = 5): number[] {
  if (!Number.isFinite(min) || !Number.isFinite(max) || min === max) return [min];
  const span = max - min;
  const rawStep = span / Math.max(1, count);
  const mag = Math.pow(10, Math.floor(Math.log10(rawStep)));
  const norm = rawStep / mag;
  const step = (norm >= 5 ? 5 : norm >= 2 ? 2 : 1) * mag;
  const start = Math.ceil(min / step) * step;
  const out: number[] = [];
  for (let v = start; v <= max + step * 1e-6; v += step) out.push(Math.round(v / step) * step);
  if (out.length === 0) out.push(min, max);
  return out;
}

function padRange(min: number, max: number, frac = 0.06): [number, number] {
  if (!Number.isFinite(min) || !Number.isFinite(max)) return [0, 1];
  if (min === max) return [min - 0.5, max + 0.5];
  const pad = (max - min) * frac;
  return [min - pad, max + pad];
}

function arrowHead(x1: number, y1: number, x2: number, y2: number, size: number): string {
  const ang = Math.atan2(y2 - y1, x2 - x1);
  const a = ang + Math.PI - 0.4;
  const b = ang + Math.PI + 0.4;
  return `${x2},${y2} ${x2 + size * Math.cos(a)},${y2 + size * Math.sin(a)} ${x2 + size * Math.cos(b)},${y2 + size * Math.sin(b)}`;
}

function collectBounds(
  series: { points: { x: number; y: number }[] }[],
  arrows: VizArrow[] | undefined,
  annotations: { x?: number; y?: number }[] | undefined,
): { xMin: number; xMax: number; yMin: number; yMax: number } {
  let xMin = Infinity;
  let xMax = -Infinity;
  let yMin = Infinity;
  let yMax = -Infinity;
  const add = (x: number, y: number) => {
    if (!Number.isFinite(x) || !Number.isFinite(y)) return;
    if (x < xMin) xMin = x;
    if (x > xMax) xMax = x;
    if (y < yMin) yMin = y;
    if (y > yMax) yMax = y;
  };
  for (const s of series) for (const p of s.points) add(p.x, p.y);
  for (const a of arrows || []) {
    add(a.x1, a.y1);
    add(a.x2, a.y2);
  }
  for (const a of annotations || []) if (a.x !== undefined && a.y !== undefined) add(a.x, a.y);
  if (!Number.isFinite(xMin)) {
    xMin = 0;
    xMax = 1;
    yMin = 0;
    yMax = 1;
  }
  return { xMin, xMax, yMin, yMax };
}

export interface PlotFrame {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
  xMin: number;
  xMax: number;
  yMin: number;
  yMax: number;
}

/**
 * The plot rectangle and data ranges used for a line/scatter spec, in SVG
 * pixels. The explorer inverts this to turn a click into data coordinates.
 */
export function plotFrame(spec: VizSpec, W: number, H: number): PlotFrame | undefined {
  if (spec.kind !== "line" && spec.kind !== "scatter") return undefined;
  const series = sampleSpec(spec);
  const b = collectBounds(series, spec.arrows, spec.annotations);
  const [xMin, xMax] = padRange(b.xMin, b.xMax);
  const [yMin, yMax] = padRange(b.yMin, b.yMax);
  return { x0: PAD.left, x1: W - PAD.right, y0: H - PAD.bottom, y1: PAD.top, xMin, xMax, yMin, yMax };
}

function buildScale(
  b: { xMin: number; xMax: number; yMin: number; yMax: number },
  W: number,
  H: number,
): Scale {
  const [xMin, xMax] = padRange(b.xMin, b.xMax);
  const [yMin, yMax] = padRange(b.yMin, b.yMax);
  const x0 = PAD.left;
  const x1 = W - PAD.right;
  const y0 = H - PAD.bottom;
  const y1 = PAD.top;
  return {
    x: (v: number) => x0 + ((v - xMin) / (xMax - xMin || 1)) * (x1 - x0),
    y: (v: number) => y0 + ((v - yMin) / (yMax - yMin || 1)) * (y1 - y0),
  };
}

function gridAndAxes(
  scale: Scale,
  bounds: { xMin: number; xMax: number; yMin: number; yMax: number },
  W: number,
  H: number,
  xLabel?: string,
  yLabel?: string,
): string[] {
  const [xMin, xMax] = padRange(bounds.xMin, bounds.xMax);
  const [yMin, yMax] = padRange(bounds.yMin, bounds.yMax);
  const out: string[] = [];
  const xTicks = niceTicks(xMin, xMax, 6);
  const yTicks = niceTicks(yMin, yMax, 5);
  for (const t of yTicks) {
    const y = scale.y(t);
    out.push(`<line x1="${PAD.left}" y1="${y.toFixed(1)}" x2="${W - PAD.right}" y2="${y.toFixed(1)}" stroke="${GRID}" stroke-width="1"/>`);
    out.push(`<text x="${PAD.left - 10}" y="${(y + 4).toFixed(1)}" text-anchor="end" fill="${MUTED}" font-size="12">${esc(fmt(t))}</text>`);
  }
  for (const t of xTicks) {
    const x = scale.x(t);
    if (x < PAD.left - 1 || x > W - PAD.right + 1) continue;
    out.push(`<line x1="${x.toFixed(1)}" y1="${PAD.top}" x2="${x.toFixed(1)}" y2="${H - PAD.bottom}" stroke="${GRID}" stroke-width="1"/>`);
    out.push(`<text x="${x.toFixed(1)}" y="${H - PAD.bottom + 18}" text-anchor="middle" fill="${MUTED}" font-size="12">${esc(fmt(t))}</text>`);
  }
  out.push(`<line x1="${PAD.left}" y1="${PAD.top}" x2="${PAD.left}" y2="${H - PAD.bottom}" stroke="${AXIS}" stroke-width="1.5"/>`);
  out.push(`<line x1="${PAD.left}" y1="${H - PAD.bottom}" x2="${W - PAD.right}" y2="${H - PAD.bottom}" stroke="${AXIS}" stroke-width="1.5"/>`);
  if (xLabel) out.push(`<text x="${(PAD.left + (W - PAD.right)) / 2}" y="${H - 18}" text-anchor="middle" fill="${FG}" font-size="13">${esc(xLabel)}</text>`);
  if (yLabel)
    out.push(
      `<text x="20" y="${(PAD.top + (H - PAD.bottom)) / 2}" text-anchor="middle" fill="${FG}" font-size="13" transform="rotate(-90 20 ${(PAD.top + (H - PAD.bottom)) / 2})">${esc(yLabel)}</text>`,
    );
  return out;
}

function legend(names: string[], W: number): string[] {
  if (names.length < 2) return [];
  const out: string[] = [];
  let y = PAD.top + 4;
  const x = W - PAD.right - 6;
  for (let i = 0; i < names.length; i++) {
    const name = names[i];
    const w = Math.min(200, 14 + name.length * 7.2);
    const bx = x - w;
    out.push(`<rect x="${bx.toFixed(1)}" y="${(y - 10).toFixed(1)}" width="${w.toFixed(1)}" height="18" rx="3" fill="${BG}" fill-opacity="0.82" stroke="${GRID}"/>`);
    out.push(`<rect x="${bx + 6}" y="${(y - 5).toFixed(1)}" width="10" height="10" rx="2" fill="${COLORS[i % COLORS.length]}"/>`);
    out.push(`<text x="${bx + 22}" y="${y + 4}" fill="${FG}" font-size="12">${esc(name)}</text>`);
    y += 20;
  }
  return out;
}

function annotationMarkers(
  spec: VizSpec,
  scale: Scale,
  W: number,
  H: number,
): string[] {
  const anns = spec.annotations || [];
  if (anns.length === 0) return [];
  const out: string[] = [];
  const placed = anns.filter((a) => a.x !== undefined && a.y !== undefined);
  const unplaced = anns.filter((a) => a.x === undefined || a.y === undefined);
  for (const a of placed) {
    const x = scale.x(a.x as number);
    const y = scale.y(a.y as number);
    out.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.5" fill="${COLORS[1]}" stroke="${BG}" stroke-width="1"/>`);
    const anchor = x > W - PAD.right - 160 ? "end" : "start";
    const tx = anchor === "end" ? x - 8 : x + 8;
    const ty = y - 8;
    out.push(
      `<text x="${tx.toFixed(1)}" y="${ty.toFixed(1)}" text-anchor="${anchor}" fill="${FG}" font-size="12">${esc(a.text)}</text>`,
    );
  }
  // Unplaced annotations become a compact note list along the bottom.
  let ny = H - PAD.bottom + 34;
  for (const a of unplaced.slice(0, 6)) {
    out.push(`<text x="${PAD.left}" y="${ny}" fill="${MUTED}" font-size="12">• ${esc(a.text)}</text>`);
    ny += 16;
  }
  return out;
}

function arrowsLayer(spec: VizSpec, scale: Scale): string[] {
  const out: string[] = [];
  for (const a of spec.arrows || []) {
    const x1 = scale.x(a.x1);
    const y1 = scale.y(a.y1);
    const x2 = scale.x(a.x2);
    const y2 = scale.y(a.y2);
    out.push(`<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="${COLORS[3]}" stroke-width="2.5"/>`);
    out.push(`<polygon points="${arrowHead(x1, y1, x2, y2, 10)}" fill="${COLORS[3]}"/>`);
    if (a.label) {
      const mx = (x1 + x2) / 2;
      const my = (y1 + y2) / 2 - 6;
      out.push(`<text x="${mx.toFixed(1)}" y="${my.toFixed(1)}" text-anchor="middle" fill="${COLORS[3]}" font-size="12" font-weight="600">${esc(a.label)}</text>`);
    }
  }
  return out;
}

function plotSvg(spec: VizSpec, W: number, H: number): string[] {
  const series = sampleSpec(spec);
  const bounds = collectBounds(series, spec.arrows, spec.annotations);
  const scale = buildScale(bounds, W, H);
  const out: string[] = [];
  out.push(...gridAndAxes(scale, bounds, W, H, spec.xLabel, spec.yLabel));
  if (spec.kind === "line") {
    series.forEach((s, i) => {
      const color = COLORS[i % COLORS.length];
      const d = s.points
        .map((p, j) => `${j === 0 ? "M" : "L"}${scale.x(p.x).toFixed(1)},${scale.y(p.y).toFixed(1)}`)
        .join(" ");
      if (d) out.push(`<path d="${d}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>`);
    });
  } else {
    series.forEach((s, i) => {
      const color = COLORS[i % COLORS.length];
      for (const p of s.points) {
        out.push(`<circle cx="${scale.x(p.x).toFixed(1)}" cy="${scale.y(p.y).toFixed(1)}" r="3.5" fill="${color}"/>`);
      }
    });
  }
  out.push(...arrowsLayer(spec, scale));
  out.push(...annotationMarkers(spec, scale, W, H));
  if (series.length > 1) out.push(...legend(series.map((s, i) => s.name || `series ${i + 1}`), W));
  return out;
}

function barSvg(spec: VizSpec, W: number, H: number): string[] {
  const bars = spec.bars || [];
  const out: string[] = [];
  const areaX = PAD.left;
  const areaW = W - PAD.left - PAD.right;
  const areaY = PAD.top;
  const areaH = H - PAD.top - PAD.bottom;
  const maxV = Math.max(...bars.map((b) => Math.abs(b.value)), 0);
  const minV = Math.min(...bars.map((b) => Math.min(0, b.value)), 0);
  const [lo, hi] = padRange(minV, Math.max(maxV, 0.0001), 0.08);
  const y = (v: number) => areaY + areaH - ((v - lo) / (hi - lo || 1)) * areaH;
  const bw = areaW / Math.max(1, bars.length);
  // gridlines
  for (const t of niceTicks(lo, hi, 4)) {
    const yy = y(t);
    out.push(`<line x1="${areaX}" y1="${yy.toFixed(1)}" x2="${areaX + areaW}" y2="${yy.toFixed(1)}" stroke="${GRID}"/>`);
    out.push(`<text x="${areaX - 10}" y="${(yy + 4).toFixed(1)}" text-anchor="end" fill="${MUTED}" font-size="12">${esc(fmt(t))}</text>`);
  }
  const zero = y(0);
  out.push(`<line x1="${areaX}" y1="${zero.toFixed(1)}" x2="${areaX + areaW}" y2="${zero.toFixed(1)}" stroke="${AXIS}" stroke-width="1.5"/>`);
  bars.forEach((b, i) => {
    const color = COLORS[i % COLORS.length];
    const top = y(Math.max(0, b.value));
    const bot = y(Math.min(0, b.value));
    const x = areaX + i * bw + bw * 0.18;
    const w = bw * 0.64;
    out.push(`<rect x="${x.toFixed(1)}" y="${top.toFixed(1)}" width="${w.toFixed(1)}" height="${Math.max(1, bot - top).toFixed(1)}" rx="2" fill="${color}"/>`);
    out.push(`<text x="${(x + w / 2).toFixed(1)}" y="${(top - 6).toFixed(1)}" text-anchor="middle" fill="${FG}" font-size="12" font-weight="600">${esc(fmt(b.value))}</text>`);
    out.push(`<text x="${(x + w / 2).toFixed(1)}" y="${H - PAD.bottom + 18}" text-anchor="middle" fill="${MUTED}" font-size="11">${esc(b.label.length > 18 ? b.label.slice(0, 17) + "…" : b.label)}</text>`);
  });
  if (spec.xLabel) out.push(`<text x="${areaX + areaW / 2}" y="${H - 18}" text-anchor="middle" fill="${FG}" font-size="13">${esc(spec.xLabel)}</text>`);
  if (spec.yLabel) out.push(`<text x="20" y="${areaY + areaH / 2}" text-anchor="middle" fill="${FG}" font-size="13" transform="rotate(-90 20 ${areaY + areaH / 2})">${esc(spec.yLabel)}</text>`);
  return out;
}

function tableSvg(spec: VizSpec, W: number, H: number): string[] {
  const cols = spec.columns || [];
  const rows = spec.rows || [];
  const out: string[] = [];
  const charW = 7.4;
  const widths = cols.map((c, i) => Math.max(c.length, ...rows.map((r) => String(r[i] ?? "").length), 1));
  const totalChars = widths.reduce((a, b) => a + b, 0) + (cols.length - 1) * 2;
  const scale = Math.min(1.4, Math.max(0.7, (W - PAD.left - PAD.right) / (totalChars * charW)));
  const rowH = Math.max(18, 22 * scale);
  const fs = Math.round(13 * scale * 10) / 10;
  const colX: number[] = [];
  let x = PAD.left;
  for (let i = 0; i < cols.length; i++) {
    colX.push(x);
    x += (widths[i] + 2) * charW * scale;
  }
  const tableW = x - PAD.left;
  const headerY = PAD.top;
  out.push(`<rect x="${PAD.left - 6}" y="${headerY - rowH + 5}" width="${tableW + 12}" height="${rowH}" rx="3" fill="${COLORS[0]}" fill-opacity="0.16"/>`);
  cols.forEach((c, i) => {
    out.push(`<text x="${colX[i].toFixed(1)}" y="${headerY}" fill="${FG}" font-size="${fs}" font-weight="700" font-family="${MONO}">${esc(c)}</text>`);
  });
  rows.forEach((r, ri) => {
    const ry = headerY + (ri + 1) * rowH;
    if (ri % 2 === 0) out.push(`<rect x="${PAD.left - 6}" y="${(ry - rowH + 5).toFixed(1)}" width="${tableW + 12}" height="${rowH}" fill="${FG}" fill-opacity="0.04"/>`);
    cols.forEach((_, i) => {
      out.push(`<text x="${colX[i].toFixed(1)}" y="${ry.toFixed(1)}" fill="${FG}" font-size="${fs}" font-family="${MONO}">${esc(String(r[i] ?? ""))}</text>`);
    });
  });
  return out;
}

function clipToBox(
  cx: number,
  cy: number,
  tx: number,
  ty: number,
  rect: { w: number; h: number },
): { x: number; y: number } {
  const dx = tx - cx;
  const dy = ty - cy;
  if (dx === 0 && dy === 0) return { x: cx, y: cy };
  const hw = rect.w / 2;
  const hh = rect.h / 2;
  const sx = dx > 0 ? hw / dx : dx < 0 ? -hw / dx : Infinity;
  const sy = dy > 0 ? hh / dy : dy < 0 ? -hh / dy : Infinity;
  const s = Math.min(Math.abs(sx), Math.abs(sy));
  return { x: cx + dx * s, y: cy + dy * s };
}

function diagramSvg(spec: VizSpec, W: number, H: number): string[] {
  const nodes = spec.nodes || [];
  const edges = spec.edges || [];
  const out: string[] = [];
  const n = Math.max(1, nodes.length);
  const cols = Math.ceil(Math.sqrt(n));
  const rows = Math.ceil(n / cols);
  const cellW = (W - PAD.left - PAD.right) / cols;
  const cellH = (H - PAD.top - PAD.bottom) / rows;
  const boxW = Math.min(190, cellW - 26);
  const boxH = Math.min(56, cellH - 22);
  const pos = new Map<string, { x: number; y: number; w: number; h: number }>();
  nodes.forEach((node, i) => {
    const c = i % cols;
    const r = Math.floor(i / cols);
    const cx = PAD.left + c * cellW + cellW / 2;
    const cy = PAD.top + r * cellH + cellH / 2;
    pos.set(node.id, { x: cx - boxW / 2, y: cy - boxH / 2, w: boxW, h: boxH });
  });
  for (const e of edges) {
    const a = pos.get(e.from);
    const b = pos.get(e.to);
    if (!a || !b) continue;
    const acx = a.x + a.w / 2;
    const acy = a.y + a.h / 2;
    const bcx = b.x + b.w / 2;
    const bcy = b.y + b.h / 2;
    const start = clipToBox(acx, acy, bcx, bcy, a);
    const end = clipToBox(bcx, bcy, acx, acy, b);
    out.push(`<line x1="${start.x.toFixed(1)}" y1="${start.y.toFixed(1)}" x2="${end.x.toFixed(1)}" y2="${end.y.toFixed(1)}" stroke="${AXIS}" stroke-width="2"/>`);
    out.push(`<polygon points="${arrowHead(start.x, start.y, end.x, end.y, 10)}" fill="${AXIS}"/>`);
    if (e.label) {
      out.push(`<text x="${((start.x + end.x) / 2).toFixed(1)}" y="${((start.y + end.y) / 2 - 5).toFixed(1)}" text-anchor="middle" fill="${MUTED}" font-size="12">${esc(e.label)}</text>`);
    }
  }
  for (const node of nodes) {
    const p = pos.get(node.id)!;
    out.push(`<rect x="${p.x.toFixed(1)}" y="${p.y.toFixed(1)}" width="${p.w.toFixed(1)}" height="${p.h.toFixed(1)}" rx="8" fill="${COLORS[0]}" fill-opacity="0.14" stroke="${COLORS[0]}" stroke-width="1.5"/>`);
    out.push(`<text x="${(p.x + p.w / 2).toFixed(1)}" y="${(p.y + p.h / 2 + 5).toFixed(1)}" text-anchor="middle" fill="${FG}" font-size="13" font-weight="600">${esc(node.label || node.id)}</text>`);
  }
  return out;
}

export function renderSvg(spec: VizSpec, opts: SvgOptions = {}): string {
  const W = opts.width ?? W_DEFAULT;
  const H = opts.height ?? H_DEFAULT;
  const frameCount = spec.frames?.length ?? 0;
  const frame = Math.max(0, Math.min(frameCount > 0 ? frameCount - 1 : 0, opts.frame ?? 0));
  const frameSpec: VizSpec = frameCount > 0 ? spec.frames![frame].spec : spec;
  const frameCaption = frameCount > 0 ? spec.frames![frame].caption : undefined;
  const title = spec.title ?? frameSpec.title;

  const body: string[] = [];
  switch (frameSpec.kind) {
    case "line":
    case "scatter":
      body.push(...plotSvg(frameSpec, W, H));
      break;
    case "bar":
      body.push(...barSvg(frameSpec, W, H));
      break;
    case "table":
      body.push(...tableSvg(frameSpec, W, H));
      break;
    case "diagram":
      body.push(...diagramSvg(frameSpec, W, H));
      break;
  }

  const caption = frameCaption || spec.caption || frameSpec.caption;
  const parts: string[] = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`);
  parts.push(`<rect width="${W}" height="${H}" fill="${esc(opts.background || BG)}"/>`);
  parts.push(`<g font-family="${FONT}">`);
  if (title) parts.push(`<text x="${W / 2}" y="30" text-anchor="middle" fill="${FG}" font-size="18" font-weight="700">${esc(title)}</text>`);
  if (frameCount > 1) {
    const dots = Array.from({ length: frameCount }, (_, i) => {
      const cx = W / 2 + (i - (frameCount - 1) / 2) * 16;
      return `<circle cx="${cx.toFixed(1)}" cy="44" r="4" fill="${i === frame ? COLORS[0] : GRID}"/>`;
    }).join("");
    parts.push(dots);
  }
  parts.push(...body);
  if (caption) {
    const clipped = caption.length > 120 ? caption.slice(0, 119) + "…" : caption;
    parts.push(`<text x="${W / 2}" y="${H - 6}" text-anchor="middle" fill="${MUTED}" font-size="11">${esc(clipped)}</text>`);
  }
  parts.push(`</g></svg>`);
  return parts.join("\n");
}
