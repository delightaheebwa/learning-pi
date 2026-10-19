import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { getCapabilities } from "@earendil-works/pi-tui";

/**
 * math-mode — tell the model how to write mathematics for the front-end it is in.
 *
 * pi-math can only draw formulas as terminal images on Kitty/iTerm2-protocol
 * terminals (Ghostty, Kitty, WezTerm/Warp, iTerm2). On foot/Alacritty/tmux it
 * falls back to leaving raw LaTeX visible, so the model must switch to plain
 * Unicode/fenced code there. A browser front-end (pi-bridge → Open WebUI) has no
 * terminal image protocol at all, but renders LaTeX with KaTeX/MathJax; it opts
 * in with PI_MATH_MODE=latex. Detection runs per turn so a `/reload`, a
 * different terminal, or a changed environment is picked up without restarting pi.
 */

const LATEX_MODE = "latex";
const UNICODE_MODE = "unicode";

function forcedMode(): string | undefined {
  const mode = (process.env.PI_MATH_MODE ?? "").trim().toLowerCase();
  return mode === LATEX_MODE || mode === UNICODE_MODE ? mode : undefined;
}

function mathDirective(): string {
  let images: string | undefined;
  try {
    images = getCapabilities().images;
  } catch {
    images = undefined;
  }

  const mode = forcedMode() ?? (images ? LATEX_MODE : UNICODE_MODE);

  if (mode === LATEX_MODE) {
    return [
      "## Math authoring (runtime directive)",
      "",
      images
        ? `Terminal image protocol detected: \`${images}\`. The pi-math extension renders LaTeX as images.`
        : "The chat front-end renders LaTeX with KaTeX/MathJax.",
      "Write mathematics as LaTeX: inline `$...$`, display `\\[...\\]` or `$$...$$`.",
      "Keep inline delimiters balanced and surrounded by whitespace or punctuation (`foo $x$ bar`, not `foo$x$bar`).",
      "Do not hand-render formulas as ASCII art or Unicode when LaTeX is available.",
      "Keep GATE envelopes and fenced code raw (do not wrap those in LaTeX).",
      "In a fact-check `claims[]`, restate each formula in plain prose (the gate matches notation-insensitively); keep the LaTeX in the emitted draft and never downgrade it to prose/Unicode.",
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
