/**
 * viz-mode — render learning visualizations and open the interactive explorer.
 *
 * A learning message may carry a ` ```viz ` fenced JSON spec authored by the
 * `viz` subagent and verified by `viz-audit`. On an image-capable terminal
 * (Ghostty/Kitty/WezTerm/iTerm2) this extension draws the figure as a real
 * terminal image; otherwise it falls back to Unicode/braille art. When the spec
 * is interactive (`params`/`formula` or `frames`) it draws a focused explorer
 * panel OVER the chat in the same terminal, driven by keyboard and mouse.
 *
 * It is display + interaction only: no gating (the learning-gate owns receipts)
 * and no state writes. `/viz` reopens the last figure, toggles auto-open, shows
 * status, or exports the spec's SVG/PNG.
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { getCapabilities } from "@earendil-works/pi-tui";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { openVizExplorer } from "./explorer.ts";
import { installVizImagePatch, uninstallVizImagePatch, vizImagePatchInstalled } from "./image-patch.ts";
import { rasterizeSpec } from "./raster.ts";
import { renderSvg } from "./render-svg.ts";
import { type VizSpec, canonicalJson } from "./spec.ts";
import { firstVizSpec, replaceVizFences } from "./wire.ts";

function textOfMessage(message: any): string {
  const c = message?.content;
  if (typeof c === "string") return c;
  if (Array.isArray(c)) return c.filter((p: any) => p && p.type === "text").map((p: any) => p.text || "").join("\n");
  return "";
}

function isInteractive(spec: VizSpec): boolean {
  const paramDriven = !!spec.formula && !!spec.params && spec.params.length > 0;
  return paramDriven || (!!spec.frames && spec.frames.length > 0);
}

function exportDir(): string {
  return join(process.cwd(), "Learning System", ".tmp", "viz");
}

function imageProtocol(): string {
  try {
    return getCapabilities().images || "none";
  } catch {
    return "none";
  }
}

export default function vizMode(pi: ExtensionAPI): void {
  let autoOpen = true;
  let lastSpec: VizSpec | undefined;
  let lastOpened = "";

  // --- display fallback: viz fence -> Unicode/braille art -------------------
  // Runs at the markdown text stage. When an image protocol is available the
  // image patch owns the fence instead, so this is a no-op there.
  const renderCache = new Map<string, string>();
  pi.registerMarkdownTransformer((markdown, context) => {
    if (context.messageType !== "assistant" || !markdown.includes("```viz")) return markdown;
    if (getCapabilities().images) return markdown;
    const width = Math.max(24, Math.floor(context.availableWidth) - 2);
    const key = `${width}\u0000${markdown}`;
    const cached = renderCache.get(key);
    if (cached !== undefined) return cached;
    const replaced = replaceVizFences(markdown, width);
    if (renderCache.size >= 128) renderCache.clear();
    renderCache.set(key, replaced);
    return replaced;
  });

  // --- inline images: install the Markdown patch once, after pi-math --------
  pi.on("session_start", (_event: any, ctx: any) => {
    if (ctx?.mode !== "tui") return;
    setImmediate(() => installVizImagePatch());
  });
  pi.on("session_shutdown", () => {
    uninstallVizImagePatch();
  });

  // --- auto-open the explorer for an interactive viz turn -------------------
  pi.on("message_end", async (event: any, ctx: any) => {
    try {
      const message = event?.message;
      if (!message || message.role !== "assistant") return;
      const text = textOfMessage(message);
      if (!text || !text.includes("```viz")) return;
      if (text.trimStart().startsWith("⛔")) return; // withheld by the gate
      const spec = firstVizSpec(text);
      if (!spec) return;
      lastSpec = spec;
      if (!autoOpen || !isInteractive(spec)) return;
      const key = canonicalJson(spec);
      if (key === lastOpened) return; // don't reopen for a streamed duplicate
      lastOpened = key;
      setTimeout(() => openVizExplorer(ctx, spec), 0);
    } catch {
      /* display-only best effort */
    }
    return;
  });

  // --- /viz command ---------------------------------------------------------
  try {
    pi.registerCommand("viz", {
      description: "Visualizations: open the last explorer, toggle auto-open, show status, or export SVG/PNG",
      handler: async (args: string, ctx: any) => {
        const action = (args || "").trim().toLowerCase();
        if (action === "auto on") {
          autoOpen = true;
          ctx.ui.notify("viz auto-open enabled", "info");
          return;
        }
        if (action === "auto off") {
          autoOpen = false;
          ctx.ui.notify("viz auto-open disabled", "info");
          return;
        }
        if (action === "status") {
          ctx.ui.notify(
            `viz auto-open ${autoOpen ? "on" : "off"}; images ${imageProtocol()}` +
              `${vizImagePatchInstalled() ? "" : " (patch idle)"}; last spec ${lastSpec ? lastSpec.kind : "none"}`,
            "info",
          );
          return;
        }
        if (action === "svg" || action === "export" || action === "png" || action === "open") {
          if (!lastSpec) {
            ctx.ui.notify("viz: no figure to export yet", "warning");
            return;
          }
          try {
            mkdirSync(exportDir(), { recursive: true });
            const stamp = Date.now();
            if (action === "svg" || action === "export") {
              const path = join(exportDir(), `viz-${stamp}.svg`);
              writeFileSync(path, renderSvg(lastSpec), "utf8");
              ctx.ui.notify(`viz SVG written: ${path}`, "info");
              return;
            }
            const raster = rasterizeSpec(lastSpec);
            if (!raster) {
              ctx.ui.notify("viz: PNG export needs a working image renderer (rsvg-convert)", "warning");
              return;
            }
            const path = join(exportDir(), `viz-${stamp}.png`);
            writeFileSync(path, Buffer.from(raster.base64Data, "base64"));
            ctx.ui.notify(`viz PNG written: ${path}`, "info");
            if (action === "open") {
              try {
                const { spawn } = await import("node:child_process");
                spawn("xdg-open", [path], { detached: true, stdio: "ignore" }).unref();
              } catch {
                /* opening is optional */
              }
            }
          } catch (e) {
            ctx.ui.notify(`viz export failed: ${e instanceof Error ? e.message : String(e)}`, "error");
          }
          return;
        }
        if (lastSpec) {
          openVizExplorer(ctx, lastSpec);
          return;
        }
        ctx.ui.notify("viz: no figure to open yet", "warning");
      },
    });
  } catch {
    /* command registration is optional */
  }
}
