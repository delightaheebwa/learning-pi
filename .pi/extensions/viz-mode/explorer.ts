/**
 * explorer — the interactive, centered viz overlay.
 *
 * Given a spec with `params` (sliders over a formula) and/or `frames` (discrete
 * steps), this opens a focused overlay the learner drives with the keyboard AND
 * the mouse: drag a slider, click the frame arrows, or click the figure to read
 * a data point. On an image-capable terminal the figure is a real image; on
 * foot/tmux it is the Unicode renderer. No separate window or process.
 */
import type { Theme } from "@earendil-works/pi-coding-agent";
import { type Component, type TuiMouseEvent, getCapabilities, matchesKey, renderImage } from "@earendil-works/pi-tui";
import { rasterizeSpec } from "./raster.ts";
import { renderAscii } from "./render-ascii.ts";
import { type PlotFrame, plotFrame } from "./render-svg.ts";
import { type VizSpec, sampleSpec } from "./spec.ts";

interface TuiLike {
  requestRender?: () => void;
}

const FIG_PX_W = 960;
const FIG_PX_H = 520;
const FIG_ROWS = 26;
const GUTTER = "  ";

function roundTo(v: number, step: number): number {
  if (step <= 0) return v;
  const n = Math.round(v / step) * step;
  return Math.round(n * 1e6) / 1e6;
}

function clamp(v: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, v));
}

function fmt(n: number): string {
  if (!Number.isFinite(n)) return "?";
  return String(Math.round(n * 1000) / 1000);
}

type Action = { kind: "prev" } | { kind: "next" } | { kind: "slider"; index: number } | { kind: "figure" };

interface Region {
  row: number;
  x0: number;
  x1: number;
  action: Action;
}

interface FigureBlock {
  lines: string[];
  geom?: { ox: number; cols: number; rows: number };
}

export class VizExplorerComponent implements Component {
  private tui: TuiLike;
  private theme: Theme;
  private spec: VizSpec;
  private done: () => void;
  private values: Record<string, number>;
  private selected = 0;
  private frame = 0;
  private readout: string | undefined;
  private regions: Region[] = [];
  private drag: number | undefined;
  private figGeom: { ox: number; oy: number; cols: number; rows: number } | undefined;

  constructor(tui: TuiLike, theme: Theme, spec: VizSpec, done: () => void) {
    this.tui = tui;
    this.theme = theme;
    this.spec = spec;
    this.done = done;
    this.values = {};
    for (const p of spec.params || []) this.values[p.name] = p.value;
  }

  invalidate(): void {}

  private activeSpec(): VizSpec {
    if (this.spec.frames && this.spec.frames.length > 0) {
      return this.spec.frames[clamp(this.frame, 0, this.spec.frames.length - 1)].spec;
    }
    if (!this.spec.params || this.spec.params.length === 0) return this.spec;
    return {
      ...this.spec,
      params: this.spec.params.map((p) => ({ ...p, value: this.values[p.name] ?? p.value })),
    };
  }

  private repaint(): void {
    this.tui.requestRender?.();
  }

  handleInput(data: string): boolean {
    const params = this.spec.params || [];
    const frames = this.spec.frames || [];
    if (matchesKey(data, "escape") || matchesKey(data, "ctrl+c") || data === "q") {
      this.done();
      return true;
    }
    if (data === "r") {
      for (const p of params) this.values[p.name] = p.value;
      this.frame = 0;
      this.readout = undefined;
      this.repaint();
      return true;
    }
    if (params.length > 0) {
      if (data === "\t" || matchesKey(data, "right") || data === "l") {
        this.selected = (this.selected + 1) % params.length;
        this.repaint();
        return true;
      }
      if (matchesKey(data, "left") || data === "h") {
        this.selected = (this.selected - 1 + params.length) % params.length;
        this.repaint();
        return true;
      }
      if (matchesKey(data, "up") || data === "+" || data === "=") {
        const p = params[this.selected];
        this.values[p.name] = clamp(roundTo((this.values[p.name] ?? p.value) + p.step, p.step), p.min, p.max);
        this.readout = undefined;
        this.repaint();
        return true;
      }
      if (matchesKey(data, "down") || data === "-" || data === "_") {
        const p = params[this.selected];
        this.values[p.name] = clamp(roundTo((this.values[p.name] ?? p.value) - p.step, p.step), p.min, p.max);
        this.readout = undefined;
        this.repaint();
        return true;
      }
    }
    if (frames.length > 0) {
      if (data === "n" || matchesKey(data, "space")) {
        this.frame = (this.frame + 1) % frames.length;
        this.readout = undefined;
        this.repaint();
        return true;
      }
      if (data === "p") {
        this.frame = (this.frame - 1 + frames.length) % frames.length;
        this.readout = undefined;
        this.repaint();
        return true;
      }
      if (params.length === 0 && matchesKey(data, "right")) {
        this.frame = (this.frame + 1) % frames.length;
        this.readout = undefined;
        this.repaint();
        return true;
      }
      if (params.length === 0 && matchesKey(data, "left")) {
        this.frame = (this.frame - 1 + frames.length) % frames.length;
        this.readout = undefined;
        this.repaint();
        return true;
      }
    }
    return false;
  }

  handleMouse(event: TuiMouseEvent): { handled?: boolean; capture?: boolean; render?: boolean } | undefined {
    const params = this.spec.params || [];
    if (event.type === "wheel") {
      if (params.length === 0) return undefined;
      const p = params[this.selected];
      const dir = (event.wheelDelta ?? 0) >= 0 ? 1 : -1;
      this.values[p.name] = clamp(roundTo((this.values[p.name] ?? p.value) + dir * p.step, p.step), p.min, p.max);
      this.readout = undefined;
      this.repaint();
      return { handled: true };
    }
    const region = this.regions.find((r) => r.row === event.y && event.x >= r.x0 && event.x <= r.x1);
    if (event.type === "press" || event.type === "click") {
      if (!region) return undefined;
      switch (region.action.kind) {
        case "prev":
          if (this.spec.frames && this.spec.frames.length > 0) {
            this.frame = (this.frame - 1 + this.spec.frames.length) % this.spec.frames.length;
            this.readout = undefined;
            this.repaint();
          }
          return { handled: true };
        case "next":
          if (this.spec.frames && this.spec.frames.length > 0) {
            this.frame = (this.frame + 1) % this.spec.frames.length;
            this.readout = undefined;
            this.repaint();
          }
          return { handled: true };
        case "slider": {
          this.selected = region.action.index;
          this.drag = region.action.index;
          this.setSliderFromX(region.action.index, event.x, region);
          return { handled: true, capture: true, render: true };
        }
        case "figure":
          this.inspect(event.x, event.y);
          this.repaint();
          return { handled: true };
      }
    }
    if (event.type === "drag" && this.drag !== undefined) {
      const reg = this.regions.find((r) => r.action.kind === "slider" && r.action.index === this.drag);
      if (reg) this.setSliderFromX(this.drag, event.x, reg);
      return { handled: true, capture: true, render: true };
    }
    if (event.type === "release") {
      this.drag = undefined;
      return { handled: true };
    }
    return undefined;
  }

  private setSliderFromX(index: number, x: number, region: Region): void {
    const p = (this.spec.params || [])[index];
    if (!p) return;
    const span = region.x1 - region.x0 || 1;
    const frac = clamp((x - region.x0) / span, 0, 1);
    const raw = p.min + frac * (p.max - p.min);
    this.values[p.name] = clamp(roundTo(raw, p.step), p.min, p.max);
    this.readout = undefined;
    this.repaint();
  }

  private inspect(x: number, y: number): void {
    const geom = this.figGeom;
    if (!geom) {
      this.readout = "point lookup needs an image-capable terminal (or /viz png)";
      return;
    }
    const fx = (x - geom.ox) / geom.cols;
    const fy = (y - geom.oy) / geom.rows;
    const spec = this.activeSpec();
    if (spec.kind === "bar") {
      if (fx < 0 || fx > 1) {
        this.readout = undefined;
        return;
      }
      const bars = spec.bars || [];
      if (bars.length === 0) return;
      const idx = clamp(Math.floor(fx * bars.length), 0, bars.length - 1);
      this.readout = `${bars[idx].label} = ${fmt(bars[idx].value)}`;
      return;
    }
    const frame: PlotFrame | undefined = plotFrame(spec, FIG_PX_W, FIG_PX_H);
    if (!frame || fx < 0 || fx > 1 || fy < 0 || fy > 1) {
      this.readout = undefined;
      return;
    }
    const px = fx * FIG_PX_W;
    const py = fy * FIG_PX_H;
    if (px < frame.x0 || px > frame.x1 || py < frame.y1 || py > frame.y0) {
      this.readout = "outside the plot area";
      return;
    }
    const dataX = frame.xMin + ((px - frame.x0) / (frame.x1 - frame.x0 || 1)) * (frame.xMax - frame.xMin);
    const dataY = frame.yMin + ((py - frame.y0) / (frame.y1 - frame.y0 || 1)) * (frame.yMax - frame.yMin);
    const series = sampleSpec(spec);
    const xRange = frame.xMax - frame.xMin || 1;
    const yRange = frame.yMax - frame.yMin || 1;
    let best: { x: number; y: number; name?: string; d: number } | undefined;
    for (const s of series) {
      for (const p of s.points) {
        const dx = (p.x - dataX) / xRange;
        const dy = (p.y - dataY) / yRange;
        const d = dx * dx + dy * dy;
        if (!best || d < best.d) best = { x: p.x, y: p.y, name: s.name, d };
      }
    }
    if (!best) {
      this.readout = undefined;
      return;
    }
    const who = best.name ? `${best.name} ` : "";
    this.readout = best.d < 0.004 ? `${who}(${fmt(best.x)}, ${fmt(best.y)})` : `cursor (${fmt(dataX)}, ${fmt(dataY)})`;
  }

  private figure(innerWidth: number): FigureBlock {
    const spec = this.activeSpec();
    if (getCapabilities().images) {
      const raster = rasterizeSpec(spec, { width: FIG_PX_W, height: FIG_PX_H, frame: 0 });
      if (raster) {
        try {
          const result = renderImage(
            raster.base64Data,
            { widthPx: raster.widthPx, heightPx: raster.heightPx },
            { maxWidthCells: Math.max(20, innerWidth), maxHeightCells: FIG_ROWS, moveCursor: false },
          );
          if (result) {
            const ox = Math.max(0, Math.floor((innerWidth - result.columns) / 2));
            const prefix = " ".repeat(ox);
            if (getCapabilities().images === "kitty") {
              return {
                lines: [`${prefix}${result.sequence}`, ...Array.from({ length: result.rows - 1 }, () => "")],
                geom: { ox, cols: result.columns, rows: result.rows },
              };
            }
            const offset = result.rows - 1;
            const moveUp = offset > 0 ? `\x1b[${offset}A` : "";
            return {
              lines: [...Array.from({ length: offset }, () => ""), `${prefix}${moveUp}${result.sequence}`],
              geom: { ox, cols: result.columns, rows: result.rows },
            };
          }
        } catch {
          /* fall through to ASCII */
        }
      }
    }
    const ascii = renderAscii(spec, { width: Math.max(20, innerWidth - 2), height: 12, frame: 0, ignoreAscii: true });
    return { lines: ascii.map((l) => GUTTER + l) };
  }

  render(width: number): string[] {
    const th = this.theme;
    const inner = Math.max(20, width - GUTTER.length);
    const params = this.spec.params || [];
    const frames = this.spec.frames || [];
    const out: string[] = [];
    this.regions = [];

    const title = this.spec.title || this.spec.frames?.[this.frame]?.spec?.title || "visualization";
    const frameTag = frames.length > 0 ? `${this.frame + 1}/${frames.length}` : "";
    out.push(GUTTER + th.fg("accent", "Viz") + "  " + th.fg("dim", title) + (frameTag ? "  " + th.fg("dim", frameTag) : ""));

    const fig = this.figure(inner);
    const figStart = out.length;
    this.figGeom = fig.geom ? { ...fig.geom, oy: figStart } : undefined;
    out.push(...fig.lines);

    if (frames.length > 0) {
      const plain = `◀  frame ${this.frame + 1}/${frames.length}  ▶`;
      const caption = frames[this.frame]?.caption || "";
      const rendered =
        GUTTER +
        th.fg("accent", "◀") +
        `  frame ${this.frame + 1}/${frames.length}  ` +
        th.fg("accent", "▶") +
        (caption ? "   " + th.fg("dim", caption) : "");
      const row = out.length;
      out.push(rendered);
      const prevX = GUTTER.length;
      const nextIdx = plain.indexOf("▶");
      this.regions.push({ row, x0: prevX, x1: prevX + 1, action: { kind: "prev" } });
      this.regions.push({ row, x0: GUTTER.length + nextIdx - 1, x1: GUTTER.length + nextIdx + 1, action: { kind: "next" } });
    }

    for (let i = 0; i < params.length; i++) {
      const p = params[i];
      const v = this.values[p.name] ?? p.value;
      const cursor = i === this.selected ? th.fg("accent", ">") : " ";
      const span = p.max - p.min || 1;
      const frac = clamp((v - p.min) / span, 0, 1);
      const barW = Math.max(8, Math.min(30, inner - 30));
      const filled = Math.round(frac * barW);
      const slider = "█".repeat(filled) + "░".repeat(barW - filled);
      const prefix = `${cursor} ${p.name.padEnd(8)} `;
      const row = out.length;
      out.push(GUTTER + prefix + slider + `  ${fmt(v)}`);
      const x0 = GUTTER.length + prefix.length;
      this.regions.push({ row, x0, x1: x0 + barW, action: { kind: "slider", index: i } });
    }

    const status = this.readout || this.spec.caption || "";
    if (status) out.push(GUTTER + (this.readout ? th.fg("accent", this.readout) : th.fg("dim", status)));

    const help = [
      params.length > 0 ? "←→ param  ↑↓ adjust  drag slider" : "",
      frames.length > 0 ? "n/p frame  click ◀ ▶" : "",
      this.figGeom ? "click plot to read a point" : "",
      "r reset  Esc close",
    ]
      .filter(Boolean)
      .join("   ");
    out.push(GUTTER + th.fg("dim", help));
    out.push(th.fg("border", "─".repeat(Math.max(1, width))));

    if (this.figGeom) {
      for (let r = 0; r < this.figGeom.rows; r++) {
        this.regions.push({
          row: this.figGeom.oy + r,
          x0: this.figGeom.ox,
          x1: this.figGeom.ox + Math.max(0, this.figGeom.cols - 1),
          action: { kind: "figure" },
        });
      }
    }

    return out;
  }
}

/** Open the explorer overlay for an interactive spec. Best-effort, never throws. */
export function openVizExplorer(ctx: any, spec: VizSpec): void {
  try {
    const custom = ctx?.ui?.custom;
    if (typeof custom !== "function") return;
    const paramDriven = !!spec.formula && !!spec.params && spec.params.length > 0;
    const interactive = paramDriven || (!!spec.frames && spec.frames.length > 0);
    if (!interactive) return;
    const p = ctx.ui.custom(
      (tui: TuiLike, theme: Theme, _kb: unknown, done: () => void) => new VizExplorerComponent(tui, theme, spec, done),
      { overlay: true, overlayOptions: { anchor: "center", width: "92%", maxHeight: "92%", margin: 1 } },
    );
    if (p && typeof p.catch === "function") p.catch(() => {});
  } catch {
    /* overlay is best-effort; the inline figure still renders */
  }
}
