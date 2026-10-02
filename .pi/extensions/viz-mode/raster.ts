/**
 * raster — turn a viz spec into a PNG raster for the terminal image protocols.
 *
 * Primary path is `@resvg/resvg-js` (fast, in-process, ~15-30 ms), resolved from
 * the extension's own node_modules or from pi-math's hoisted copy. If that is
 * unavailable we shell out to `rsvg-convert`. Rendering is best-effort: any
 * failure returns undefined and the caller falls back to the Unicode renderer.
 * Results are cached by (svg, pixel size) so a streaming transcript or a
 * slider drag does not re-rasterise the same figure.
 */
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";
import { join } from "node:path";
import { getCellDimensions } from "@earendil-works/pi-tui";
import { type SvgOptions, renderSvg } from "./render-svg.ts";
import type { VizSpec } from "./spec.ts";

export interface Raster {
  base64Data: string;
  widthPx: number;
  heightPx: number;
  columns: number;
  rows: number;
}

const DEVICE_SCALE = 1.5;
const MAX_CACHE = 32;
const cache = new Map<string, Raster | null>();

const FONT_FILES = [
  "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
  "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
  "/usr/share/fonts/liberation/LiberationMono-Regular.ttf",
  "/usr/share/fonts/liberation/LiberationMono-Bold.ttf",
].filter((f) => existsSync(f));

let resvgCtor: any;
let resvgTried = false;
let svgFallbackBroken = false;

function loadResvg(): any {
  if (resvgTried) return resvgCtor;
  resvgTried = true;
  let req: NodeRequire;
  try {
    req = createRequire(import.meta.url);
  } catch {
    return undefined;
  }
  const candidates = ["@resvg/resvg-js", join(homedir(), ".pi/agent/npm/node_modules/@resvg/resvg-js")];
  for (const candidate of candidates) {
    try {
      const mod = req(candidate);
      if (mod?.Resvg) {
        resvgCtor = mod.Resvg;
        return resvgCtor;
      }
    } catch {
      /* try the next candidate */
    }
  }
  return undefined;
}

function cellsFor(widthPx: number, heightPx: number): { columns: number; rows: number } {
  const cells = getCellDimensions();
  const cw = cells?.widthPx || 9;
  const ch = cells?.heightPx || 18;
  return {
    columns: Math.max(1, Math.round(widthPx / cw)),
    rows: Math.max(1, Math.round(heightPx / ch)),
  };
}

function rasterizeSvg(svg: string, cssW: number, cssH: number): Raster | undefined {
  const targetW = Math.max(2, Math.round(cssW * DEVICE_SCALE));
  const targetH = Math.max(2, Math.round(cssH * DEVICE_SCALE));
  const key = `${targetW}x${targetH}\u0000${svg}`;
  const hit = cache.get(key);
  if (hit !== undefined) return hit || undefined;

  let png: Uint8Array | undefined;
  let widthPx = targetW;
  let heightPx = targetH;

  const Resvg = loadResvg();
  if (Resvg) {
    try {
      const resvg = new Resvg(svg, {
        fitTo: { mode: "width", value: targetW },
        font: FONT_FILES.length
          ? { loadSystemFonts: false, defaultFontFamily: "Liberation Sans", fontFiles: FONT_FILES }
          : { loadSystemFonts: true },
      });
      const image = resvg.render();
      png = image.asPng();
      widthPx = image.width;
      heightPx = image.height;
    } catch {
      png = undefined;
    }
  }

  if (!png && !svgFallbackBroken) {
    try {
      png = execFileSync("rsvg-convert", ["-w", String(targetW), "-h", String(targetH)], {
        input: svg,
        maxBuffer: 64 * 1024 * 1024,
      });
    } catch {
      svgFallbackBroken = true;
      png = undefined;
    }
  }

  let raster: Raster | undefined;
  if (png) {
    const { columns, rows } = cellsFor(widthPx, heightPx);
    raster = { base64Data: Buffer.from(png).toString("base64"), widthPx, heightPx, columns, rows };
  }
  if (cache.size >= MAX_CACHE) cache.clear();
  cache.set(key, raster ?? null);
  return raster;
}

/** Rasterise a spec to PNG. `width`/`height` are the SVG's intrinsic pixels. */
export function rasterizeSpec(spec: VizSpec, opts: SvgOptions = {}): Raster | undefined {
  const width = opts.width ?? 960;
  const height = opts.height ?? 520;
  let svg: string;
  try {
    svg = renderSvg(spec, { ...opts, width, height });
  } catch {
    return undefined;
  }
  return rasterizeSvg(svg, width, height);
}

/** True when every raster backend has failed (for a one-shot user notice). */
export function rasterUnavailable(): boolean {
  return !loadResvg() && svgFallbackBroken;
}
