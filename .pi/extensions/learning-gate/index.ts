import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

/**
 * learning-gate — verification gate for the pi learning system.
 *
 * Tracks foreground verification subagent calls per agent run and blocks
 * teaching / quiz / grade assistant messages that lack the matching receipt.
 * Fails open on internal error so a bug never bricks a learning session.
 */

const VERIFIER_AGENTS: Record<string, string> = {
  "fact-check": "fact_check",
  "quiz-audit": "quiz_audit",
  "grade-audit": "grade_audit",
  "review-gate": "review",
};

const MAX_RETRIES = 2;

type Flow = "teach" | "resume" | "review" | "ingest" | "other";

interface RunState {
  flow: Flow;
  receipts: Set<string>;
  scoutCalled: boolean;
  retries: number;
}

function textOf(message: any): string {
  const c = message?.content;
  if (typeof c === "string") return c;
  if (Array.isArray(c)) {
    return c
      .filter((p: any) => p && p.type === "text")
      .map((p: any) => p.text || "")
      .join("\n");
  }
  return "";
}

function hasToolCall(message: any): boolean {
  const c = message?.content;
  if (!Array.isArray(c)) return false;
  return c.some((p: any) => p && typeof p.type === "string" && p.type.toLowerCase().includes("tool"));
}

function replaceText(message: any, text: string): any {
  if (typeof message.content === "string") return { ...message, content: text };
  return { ...message, content: [{ type: "text", text }] };
}

function detectFlow(prompt: string): Flow {
  const p = (prompt || "").toLowerCase();
  if (p.includes("learning-teach") || p.includes("probe -> plan -> teach") || p.includes("teach me about") || /^\/teach\b/.test(p)) {
    return "teach";
  }
  if (p.includes("learning-system") && p.includes("review flow")) return "review";
  if (p.includes("run a review session") || p.includes("review the active track")) return "review";
  if (p.includes("ingest the following") || p.includes("learning-system") && p.includes("ingest flow")) return "ingest";
  if (p.includes("next curriculum lesson")) return "teach";
  if (p.includes("continue the current lesson")) return "resume";
  if (p.includes("pause the current lesson")) return "resume";
  return "other";
}

/** Extract {agent -> gate} pairs from a subagent tool input. */
function subagentCalls(input: any): Array<{ agent: string; gate?: string }> {
  const out: Array<{ agent: string; gate?: string }> = [];
  const push = (agent: any, task: any) => {
    if (typeof agent !== "string") return;
    out.push({ agent, gate: gateFromTask(task) });
  };
  if (!input || typeof input !== "object") return out;
  if (typeof input.agent === "string") push(input.agent, input.task);
  if (Array.isArray(input.tasks)) for (const t of input.tasks) push(t?.agent, t?.task);
  if (Array.isArray(input.chain)) for (const t of input.chain) push(t?.agent, t?.task);
  return out;
}

function gateFromTask(task: any): string | undefined {
  let obj = task;
  if (typeof task === "string") {
    try {
      obj = JSON.parse(task);
    } catch {
      const m = task.match(/\{[^]*\}/);
      if (m) {
        try {
          obj = JSON.parse(m[0]);
        } catch {
          return undefined;
        }
      } else return undefined;
    }
  }
  const g = obj && typeof obj === "object" ? obj.gate : undefined;
  return typeof g === "string" ? g : undefined;
}

function classify(text: string): { quiz: boolean; grade: boolean; teach: boolean } {
  const quiz = /(^|\n)\s*[A-Da-d][).:]\s/.test(text) || ((text.match(/\?/g) || []).length >= 2 && /(choose|option|answer|A[–-]D|select)/i.test(text));
  const grade = /\b(correct|incorrect|right|wrong|pass|fail|✓|✗)\b/i.test(text) && text.length < 500 && /(answer|you said|your |nice|not quite|spot on)/i.test(text);
  const teach = text.length > 180 && (/(^|\n)#{1,4}\s/.test(text) || /```/.test(text) || /\b(because|therefore|means|defined as|in other words)\b/i.test(text));
  return { quiz, grade, teach };
}

export default function (pi: ExtensionAPI) {
  let run: RunState = { flow: "other", receipts: new Set(), scoutCalled: false, retries: 0 };
  const pendingCalls = new Map<string, { agents: string[]; gates: Set<string> }>();

  const reset = (flow: Flow) => {
    run = { flow, receipts: new Set(), scoutCalled: false, retries: 0 };
    pendingCalls.clear();
  };

  pi.on("before_agent_start", async (event: any, _ctx) => {
    try {
      reset(detectFlow(event?.prompt || ""));
    } catch {
      reset("other");
    }
  });

  pi.on("tool_call", async (event: any, _ctx) => {
    try {
      if (event?.toolName !== "subagent") return;
      const calls = subagentCalls(event.input);
      const agents = calls.map((c) => c.agent);
      const gates = new Set(calls.map((c) => c.gate).filter(Boolean) as string[]);
      pendingCalls.set(event.toolCallId, { agents, gates });
      if (agents.includes("scout")) run.scoutCalled = true;
    } catch {
      /* fail open */
    }
  });

  pi.on("tool_result", async (event: any, _ctx) => {
    try {
      if (event?.toolName !== "subagent") return;
      const rec = pendingCalls.get(event.toolCallId);
      if (!rec) return;
      pendingCalls.delete(event.toolCallId);
      const failed = event.isError === true;
      if (failed) return;
      for (const g of rec.gates) run.receipts.add(g);
      for (const a of rec.agents) {
        const g = VERIFIER_AGENTS[a];
        if (g) run.receipts.add(g);
      }
    } catch {
      /* fail open */
    }
  });

  pi.on("message_end", async (event: any, ctx) => {
    try {
      const message = event?.message;
      if (!message || message.role !== "assistant") return;
      if (hasToolCall(message)) return;
      if (run.flow === "other") return;

      const text = textOf(message);
      if (!text || text.trim().length === 0) return;
      const { quiz, grade, teach } = classify(text);

      const required: string[] = [];
      if (grade) required.push("grade_audit");
      if (quiz) required.push("quiz_audit");
      if (teach && (run.flow === "teach" || run.flow === "resume")) required.push("fact_check");

      const missing = required.filter((g) => !run.receipts.has(g));
      const needsScout = run.flow === "teach" && teach && !run.scoutCalled;

      if (missing.length === 0 && !needsScout) {
        // Consume the receipts so the next teaching/quiz/grade message needs a fresh one
        // (generation-to-emission: one verification per emitted step).
        for (const g of required) run.receipts.delete(g);
        return;
      }

      run.retries += 1;
      const codes: string[] = [];
      if (needsScout) codes.push("NO_SCOUT_CONTEXT");
      for (const m of missing) codes.push(m === "fact_check" ? "NO_FACT_CHECK" : `MISSING_${m.toUpperCase()}`);

      if (run.retries > MAX_RETRIES) {
        const banner = `⛔ UNVERIFIED — gate retries exhausted (${codes.join(", ")}). The content below was not verified.\n\n`;
        return { message: replaceText(message, banner + text) };
      }

      const fix =
        "Before emitting teaching, run a foreground `fact-check` subagent with your draft as `rendered_content`; " +
        "for quizzes run `quiz-audit`; for grades run `grade-audit`. Resolve the issues, then re-emit.";
      const scoutNote = needsScout
        ? "For a new lesson, run the `scout` subagent first and use its digest.\n"
        : "";
      const banner = `⛔ WITHHELD (${codes.join(", ")})\n${scoutNote}${fix}\n`;
      try {
        ctx?.ui?.notify?.(`learning-gate blocked: ${codes.join(", ")}`, "warning");
      } catch {
        /* ignore */
      }
      return { message: replaceText(message, banner) };
    } catch {
      return; // fail open
    }
  });
}
