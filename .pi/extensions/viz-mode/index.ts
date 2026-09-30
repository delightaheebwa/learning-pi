/**
 * viz-mode — render learning visualizations inline and open the explorer.
 *
 * A learning message may carry a ` ```viz ` fenced JSON spec authored by the
 * `viz` subagent and verified by `viz-audit`. This extension:
 *   - replaces each viz fence with ASCII/Unicode art at DISPLAY time via Pi's
 *     markdown transformer (the stored message keeps the JSON, exactly like
 *     pi-math keeps LaTeX), and
 *   - when the spec is interactive (`params`/`formula` or `frames`), draws a
 *     focused explorer panel OVER the chat in the same terminal — not a
 *     separate window or process — already running, so the learner can poke at
 *     it. The read-only transcript cannot host a live control, so the overlay
 *     is where interactivity lives.
 *
 * It is display + interaction only: no gating (the learning-gate owns receipts)
 * and no state writes. `/viz` reopens the last figure, toggles auto-open, shows
 * status, or exports the spec's SVG.
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { openVizExplorer } from "./explorer.ts";
import { renderSvg } from "./render-svg.ts";
import { type VizSpec } from "./spec.ts";
import { firstVizSpec, replaceVizFences } from "./wire.ts";

function textOfMessage(message: any): string {
  const c = message?.content;
  if (typeof c === "string") return c;
  if (Array.isArray(c)) return c.filter((p: any) => p && p.type === "text").map((p: any) => p.text || "").join("\n");
  return "";
}

function isInteractive(spec: VizSpec): boolean {
  // Params only do something when a formula consumes them.
  const paramDriven = !!spec.formula && !!spec.params && spec.params.length > 0;
  return paramDriven || (!!spec.frames && spec.frames.length > 0);
}

export default function vizMode(pi: ExtensionAPI): void {
  let autoOpen = true;
  let lastSpec: VizSpec | undefined;
  let lastOpened = "";

  // --- display transform: viz fence -> ASCII art ---------------------------
  // Pi applies this to assistant Markdown before rendering it in the
  // transcript; the stored message keeps the JSON spec. Unlike a
  // Markdown.prototype.render wrapper, this uses the supported API, so it
  // composes cleanly with other render-patching extensions (e.g. pi-math)
  // and can never recurse into them.
  const renderCache = new Map<string, string>();
  pi.registerMarkdownTransformer((markdown, context) => {
    if (context.messageType !== "assistant" || !markdown.includes("```viz")) return markdown;
    const width = Math.max(24, Math.floor(context.availableWidth) - 2);
    const key = `${width}\u0000${markdown}`;
    const cached = renderCache.get(key);
    if (cached !== undefined) return cached;
    const replaced = replaceVizFences(markdown, width);
    if (renderCache.size >= 128) renderCache.clear();
    renderCache.set(key, replaced);
    return replaced;
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
      const key = JSON.stringify(spec).slice(0, 400);
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
      description: "Visualizations: open the last explorer, toggle auto-open, show status, or export SVG",
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
          ctx.ui.notify(`viz auto-open ${autoOpen ? "on" : "off"}; last spec ${lastSpec ? lastSpec.kind : "none"}`, "info");
          return;
        }
        if (action === "svg" || action === "export") {
          if (!lastSpec) {
            ctx.ui.notify("viz: no figure to export yet", "warning");
            return;
          }
          try {
            const path = join(tmpdir(), `viz-${Date.now()}.svg`);
            writeFileSync(path, renderSvg(lastSpec), "utf8");
            ctx.ui.notify(`viz SVG written: ${path}`, "info");
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
