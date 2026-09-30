/**
 * wire — display-time transformation of ` ```viz ` fences into rendered art,
 * and extraction of the first valid spec from a message. PURE: no pi imports,
 * so it is unit-testable and shared by the extension's Markdown patch.
 */
import { renderAscii } from "./render-ascii.ts";
import { type VizSpec, validateSpec } from "./spec.ts";

const VIZ_FENCE_RE = /```viz[^\n]*\n([\s\S]*?)```/g;

function safeParse(body: string): unknown {
  try {
    return JSON.parse(body.trim());
  } catch {
    return undefined;
  }
}

/**
 * Replace each valid viz fence with a ```text block of rendered ASCII art. An
 * invalid fence is left untouched (so the raw spec stays visible for
 * debugging rather than vanishing silently).
 */
export function replaceVizFences(source: string, width = 72): string {
  return source.replace(VIZ_FENCE_RE, (full, body: string) => {
    const res = validateSpec(safeParse(body));
    if (!res.ok) return full;
    try {
      return "```text\n" + renderAscii(res.spec, { width }).join("\n") + "\n```";
    } catch {
      return full;
    }
  });
}

/** The first valid viz spec in a message, if any. */
export function firstVizSpec(text: string): VizSpec | undefined {
  VIZ_FENCE_RE.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = VIZ_FENCE_RE.exec(text)) !== null) {
    const res = validateSpec(safeParse(m[1]));
    if (res.ok) return res.spec;
  }
  return undefined;
}
