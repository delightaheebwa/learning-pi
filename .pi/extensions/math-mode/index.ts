import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { getCapabilities } from "@earendil-works/pi-tui";

/**
 * math-mode — tell the model how to write mathematics for the terminal it is in.
 *
 * pi-math can only draw formulas as terminal images on Kitty/iTerm2-protocol
 * terminals (Ghostty, Kitty, WezTerm/Warp, iTerm2). On foot/Alacritty/tmux it
 * falls back to leaving raw LaTeX visible, so the model must switch to plain
 * Unicode/fenced code there. Detection runs per turn so a `/reload` or a
 * different terminal is picked up without restarting pi.
 */

function mathDirective(): string {
  let images: string | undefined;
  try {
    images = getCapabilities().images;
  } catch {
    images = undefined;
  }

  if (images) {
    return [
      "## Math authoring (runtime directive)",
      "",
      `Terminal image protocol detected: \`${images}\`. The pi-math extension renders LaTeX as images.`,
      "Write mathematics as LaTeX: inline `$...$`, display `\\[...\\]` or `$$...$$`.",
      "Do not hand-render formulas as ASCII art or Unicode when LaTeX is available.",
      "Keep GATE envelopes and fenced code raw (do not wrap those in LaTeX).",
    ].join("\n");
  }

  return [
    "## Math authoring (runtime directive)",
    "",
    "No supported terminal image protocol (foot / Alacritty / tmux / screen). pi-math cannot render LaTeX here.",
    "Write mathematics as plain text, Unicode, and fenced code blocks; do not use LaTeX delimiters.",
    "Keep formulas readable as plain text — the learner may work on paper and reply with a final number or choice.",
  ].join("\n");
}

export default function mathModeExtension(pi: ExtensionAPI): void {
  pi.on("before_agent_start", async (event) => {
    return { systemPrompt: `${event.systemPrompt}\n\n${mathDirective()}` };
  });
}
