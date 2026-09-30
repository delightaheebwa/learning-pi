/**
 * render-svg — deterministic SVG generation for a viz spec.
 *
 * Used for side artifacts under `Learning System/.tmp/viz/` (and as the future
 * source for inline terminal images once an image backend is wired). PURE.
 * Supports line/scatter/bar; table/diagram fall back to a text <g>.
 */
import { type VizSpec, sampleSpec } from "./spec.ts";

export interface SvgOptions {
  width?: number;
  height?: number;
  frame?: number;
  background?: string;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

const COLORS = ["#4c9be8", "#e8884c", "#5fc27e", "#d76bd7", "#d9c04a"];

export function renderSvg(spec: VizSpec, opts: SvgOptions = {}): string {
  const W = opts.width ?? 640;
  const H = opts.height ?? 360;
  const pad = 48;
  const inner = `x="${pad}" y="${pad}" width="${W - pad * 2}" height="${H - pad * 2}"`;
  const parts: string[] = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`);
  if (opts.background) parts.push(`<rect width="${W}" height="${H}" fill="${esc(opts.background)}"/>`);
  parts.push(`<g font-family="DejaVu Sans, Helvetica, Arial, sans-serif" font-size="14">`);
  if (spec.title) parts.push(`<text x="${W / 2}" y="28" text-anchor="middle" font-size="17" font-weight="600">${esc(spec.title)}</text>`);

  const frameSpec = spec.frames && spec.frames.length ? spec.frames[Math.min(opts.frame ?? 0, spec.frames.length - 1)].spec : spec;

  if (frameSpec.kind === "line" || frameSpec.kind === "scatter") {
    const series = sampleSpec(frameSpec);
    const pts = series.flatMap((s) => s.points);
    const xMin = Math.min(...pts.map((p) => p.x));
    const xMax = Math.max(...pts.map((p) => p.x));
    const yMin = Math.min(...pts.map((p) => p.y));
    const yMax = Math.max(...pts.map((p) => p.y));
    const sx = (x: number) => pad + ((x - xMin) / (xMax - xMin || 1)) * (W - pad * 2);
    const sy = (y: number) => H - pad - ((y - yMin) / (yMax - yMin || 1)) * (H - pad * 2);
    // Axes
    parts.push(`<line x1="${pad}" y1="${H - pad}" x2="${W - pad}" y2="${H - pad}" stroke="#888"/>`);
    parts.push(`<line x1="${pad}" y1="${pad}" x2="${pad}" y2="${H - pad}" stroke="#888"/>`);
    series.forEach((s, i) => {
      const color = COLORS[i % COLORS.length];
      const d = s.points.map((p, j) => `${j === 0 ? "M" : "L"}${sx(p.x).toFixed(1)},${sy(p.y).toFixed(1)}`).join(" ");
      if (frameSpec.kind === "line") parts.push(`<path d="${d}" fill="none" stroke="${color}" stroke-width="2"/>`);
      else for (const p of s.points) parts.push(`<circle cx="${sx(p.x).toFixed(1)}" cy="${sy(p.y).toFixed(1)}" r="3" fill="${color}"/>`);
    });
    if (frameSpec.xLabel) parts.push(`<text x="${W / 2}" y="${H - 12}" text-anchor="middle">${esc(frameSpec.xLabel)}</text>`);
    if (frameSpec.yLabel)
      parts.push(`<text x="16" y="${H / 2}" text-anchor="middle" transform="rotate(-90 16 ${H / 2})">${esc(frameSpec.yLabel)}</text>`);
  } else if (frameSpec.kind === "bar") {
    const bars = frameSpec.bars || [];
    const max = Math.max(...bars.map((b) => Math.abs(b.value)), 1);
    const bw = (W - pad * 2) / Math.max(1, bars.length);
    bars.forEach((b, i) => {
      const h = (Math.abs(b.value) / max) * (H - pad * 2);
      const x = pad + i * bw + bw * 0.15;
      parts.push(`<rect x="${x.toFixed(1)}" y="${(H - pad - h).toFixed(1)}" width="${(bw * 0.7).toFixed(1)}" height="${h.toFixed(1)}" fill="${COLORS[i % COLORS.length]}"/>`);
      parts.push(`<text x="${(x + bw * 0.35).toFixed(1)}" y="${H - 12}" text-anchor="middle" font-size="12">${esc(b.label)}</text>`);
    });
  } else {
    const rows = (frameSpec.columns || []).length > 0
      ? [ (frameSpec.columns || []).join(" | "), ...((frameSpec.rows || []).map((r) => r.join(" | "))) ]
      : (frameSpec.nodes || []).map((n) => `${n.id}${n.label ? `: ${n.label}` : ""}`);
    rows.slice(0, 20).forEach((r, i) => parts.push(`<text x="${pad}" y="${pad + 20 + i * 18}" font-size="13">${esc(r)}</text>`));
  }

  parts.push(`</g></svg>`);
  return parts.join("\n");
}
