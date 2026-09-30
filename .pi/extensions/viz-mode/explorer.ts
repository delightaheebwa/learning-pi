/**
 * explorer — the interactive, right-anchored viz overlay.
 *
 * Given a spec with `params` (continuous sliders over a formula) and/or
 * `frames` (discrete steps), this opens a focused overlay the learner drives
 * with the keyboard: the figure re-renders live as parameters change. It is the
 * terminal-native answer to "let me poke at it" — no separate window, no slash
 * command for the learner to remember.
 */
import type { Theme } from "@earendil-works/pi-coding-agent";
import { type Component, matchesKey } from "@earendil-works/pi-tui";
import { renderAscii } from "./render-ascii.ts";
import { type VizSpec } from "./spec.ts";

interface TuiLike {
  requestRender?: () => void;
}

function roundTo(v: number, step: number): number {
  if (step <= 0) return v;
  const n = Math.round(v / step) * step;
  return Math.round(n * 1e6) / 1e6;
}

export class VizExplorerComponent implements Component {
  private tui: TuiLike;
  private theme: Theme;
  private spec: VizSpec;
  private done: () => void;
  private values: Record<string, number>;
  private selected = 0;
  private frame = 0;

  constructor(tui: TuiLike, theme: Theme, spec: VizSpec, done: () => void) {
    this.tui = tui;
    this.theme = theme;
    this.spec = spec;
    this.done = done;
    this.values = {};
    for (const p of spec.params || []) this.values[p.name] = p.value;
  }

  private effectiveSpec(): VizSpec {
    if (!this.spec.params || this.spec.params.length === 0) return this.spec;
    return {
      ...this.spec,
      params: this.spec.params.map((p) => ({ ...p, value: this.values[p.name] ?? p.value })),
    };
  }

  invalidate(): void {}

  handleInput(data: string): boolean {
    const params = this.spec.params || [];
    if (matchesKey(data, "escape") || matchesKey(data, "ctrl+c") || data === "q") {
      this.done();
      return true;
    }
    if (data === "r") {
      for (const p of params) this.values[p.name] = p.value;
      this.frame = 0;
      this.tui.requestRender?.();
      return true;
    }
    if (params.length > 0) {
      if (data === "\t" || matchesKey(data, "right") || data === "l") {
        this.selected = (this.selected + 1) % params.length;
        this.tui.requestRender?.();
        return true;
      }
      if (matchesKey(data, "left") || data === "h") {
        this.selected = (this.selected - 1 + params.length) % params.length;
        this.tui.requestRender?.();
        return true;
      }
      if (matchesKey(data, "up") || data === "+" || data === "=") {
        const p = params[this.selected];
        this.values[p.name] = Math.min(p.max, roundTo((this.values[p.name] ?? p.value) + p.step, p.step));
        this.tui.requestRender?.();
        return true;
      }
      if (matchesKey(data, "down") || data === "-" || data === "_") {
        const p = params[this.selected];
        this.values[p.name] = Math.max(p.min, roundTo((this.values[p.name] ?? p.value) - p.step, p.step));
        this.tui.requestRender?.();
        return true;
      }
    }
    const frames = this.spec.frames || [];
    if (frames.length > 0 && (data === "n" || matchesKey(data, "space"))) {
      this.frame = (this.frame + 1) % frames.length;
      this.tui.requestRender?.();
      return true;
    }
    if (frames.length > 0 && data === "p") {
      this.frame = (this.frame - 1 + frames.length) % frames.length;
      this.tui.requestRender?.();
      return true;
    }
    return false;
  }

  private box(lines: string[], width: number): string[] {
    const th = this.theme;
    const inner = Math.max(1, width - 2);
    const title = " Viz explorer ";
    const top = "─".repeat(Math.max(0, inner - title.length));
    const out = [th.fg("border", "╭") + th.fg("accent", title) + th.fg("border", top + "╮")];
    for (const line of lines) {
      const clipped = line.length > inner ? line.slice(0, inner) : line;
      out.push(th.fg("border", "│") + clipped + " ".repeat(Math.max(0, inner - clipped.length)) + th.fg("border", "│"));
    }
    out.push(th.fg("border", "╰" + "─".repeat(inner) + "╯"));
    return out;
  }

  render(width: number): string[] {
    const th = this.theme;
    const body: string[] = [];
    const params = this.spec.params || [];
    const frames = this.spec.frames || [];
    try {
      body.push(...renderAscii(this.effectiveSpec(), { width: Math.max(20, width - 4), height: 10, frame: this.frame }));
    } catch (e) {
      body.push(`(render error: ${e instanceof Error ? e.message : String(e)})`);
    }
    body.push("");
    if (params.length > 0) {
      params.forEach((p, i) => {
        const v = this.values[p.name] ?? p.value;
        const cursor = i === this.selected ? th.fg("accent", ">") : " ";
        const span = p.max - p.min || 1;
        const frac = Math.max(0, Math.min(1, (v - p.min) / span));
        const barW = Math.max(8, Math.min(24, width - 28));
        const filled = Math.round(frac * barW);
        const slider = "█".repeat(filled) + "░".repeat(barW - filled);
        body.push(`${cursor} ${p.name.padEnd(8)} ${slider} ${String(Math.round(v * 1000) / 1000)}`);
      });
    }
    if (frames.length > 0) body.push(`${th.fg("dim", "frame")} ${this.frame + 1}/${frames.length}${frames[this.frame]?.caption ? ` — ${frames[this.frame].caption}` : ""}`);
    const help = [
      params.length > 0 ? "←→ param  ↑↓ adjust" : "",
      frames.length > 0 ? "n/p frame" : "",
      "r reset  Esc close",
    ]
      .filter(Boolean)
      .join("  ");
    body.push(th.fg("dim", help));
    return this.box(body, width);
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
      { overlay: true, overlayOptions: { anchor: "right-center", width: 88, maxHeight: 34, offsetX: -1 } }
    );
    if (p && typeof p.catch === "function") p.catch(() => {});
  } catch {
    /* overlay is best-effort; the inline figure still renders */
  }
}
