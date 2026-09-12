import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

/**
 * learning-gate — verification gate for the pi learning system.
 *
 * Enforcement (v2), beyond "a verifier ran":
 *   - fact-check: the emitted teaching text must match the draft that was actually
 *     verified (`rendered_content` containment), and the verdict must not contain ISSUES.
 *   - quiz-audit: must return PASS (no high/medium issues).
 *   - grade-audit: must not disagree (`agrees`) and must return PASS; the tutor's
 *     claimed verdict is rejected when it conflicts with `correct_verdict`.
 *   - ingest: the clerk result must carry a PASS `REVIEW_GATE_VERDICT` marker.
 *   - new lessons require a scout run.
 *
 * Receipts are consumed per emitted message (per-generation binding). Fails open only
 * on internal error, so a bug never bricks a learning session.
 */

const VERIFIER_AGENTS: Record<string, string> = {
  "fact-check": "fact_check",
  "quiz-audit": "quiz_audit",
  "grade-audit": "grade_audit",
  "review-gate": "review",
};

const MAX_RETRIES = 2;
const MATCH_THRESHOLD = 0.85;

type Flow = "teach" | "resume" | "review" | "ingest" | "other";

interface Receipt {
  gate: string;
  valid: boolean;
  issues: boolean;
  agrees?: boolean;
  correctVerdict?: string;
  renderedContent?: string;
  raw: string;
}

interface RunState {
  flow: Flow;
  receipts: Receipt[];
  scoutCalled: boolean;
  clerkCalled: boolean;
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
  if (p.includes("ingest the following") || (p.includes("learning-system") && p.includes("ingest flow"))) return "ingest";
  if (p.includes("next curriculum lesson")) return "teach";
  if (p.includes("continue the current lesson")) return "resume";
  if (p.includes("pause the current lesson")) return "resume";
  return "other";
}

function parseTask(task: any): any | undefined {
  if (task && typeof task === "object") return task;
  if (typeof task !== "string") return undefined;
  try {
    return JSON.parse(task);
  } catch {
    const m = task.match(/\{[\s\S]*\}/);
    if (m) {
      try {
        return JSON.parse(m[0]);
      } catch {
        return undefined;
      }
    }
    return undefined;
  }
}

interface CallRef {
  agent: string;
  gate?: string;
  envelope?: any;
}

function subagentCalls(input: any): CallRef[] {
  const out: CallRef[] = [];
  const push = (agent: any, task: any) => {
    if (typeof agent !== "string") return;
    const env = parseTask(task);
    out.push({ agent, envelope: env, gate: env && typeof env.gate === "string" ? env.gate : undefined });
  };
  if (!input || typeof input !== "object") return out;
  if (typeof input.agent === "string") push(input.agent, input.task);
  if (Array.isArray(input.tasks)) for (const t of input.tasks) push(t?.agent, t?.task);
  if (Array.isArray(input.chain)) for (const t of input.chain) push(t?.agent, t?.task);
  return out;
}

function resultText(ev: any): string {
  const c = ev?.content;
  if (typeof c === "string") return c;
  if (Array.isArray(c)) {
    return c
      .map((p: any) => (typeof p === "string" ? p : p && typeof p.text === "string" ? p.text : ""))
      .join("\n");
  }
  if (ev?.details) {
    try {
      return JSON.stringify(ev.details);
    } catch {
      return "";
    }
  }
  return "";
}

function classify(text: string): { quiz: boolean; grade: boolean; teach: boolean } {
  const quiz =
    /(^|\n)\s*[A-Da-d][).:]\s/.test(text) ||
    ((text.match(/\?/g) || []).length >= 2 && /(choose|option|answer|A[–-]D|select)/i.test(text));
  const verdictWord = /\b(correct|incorrect|right|wrong|pass|fail|✓|✗|✅|❌)\b/i.test(text);
  const grade =
    verdictWord &&
    (/(you said|you wrote|you answered|your answer|your response|learner answer|the learner)/i.test(text) ||
      (text.length < 120 && /^\s*(✅|❌|✓|✗|correct|incorrect|right|wrong|pass|fail)\b/i.test(text)));
  const teach =
    text.length > 180 &&
    (/(^|\n)#{1,4}\s/.test(text) || /```/.test(text) || /\b(because|therefore|means|defined as|in other words)\b/i.test(text));
  return { quiz, grade, teach };
}

function tokens(s: string): string[] {
  return s
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
}

/** Fraction of `needle`'s word tokens present in `hay`. */
function coverage(needle: string, hay: string): number {
  const n = tokens(needle);
  if (n.length === 0) return 1;
  const hs = new Set(tokens(hay));
  let hit = 0;
  for (const t of n) if (hs.has(t)) hit++;
  return hit / n.length;
}

function parseResult(text: string, gate: string, envelope: any): Receipt {
  const issues =
    /"verdict"\s*:\s*"ISSUES"/i.test(text) ||
    (gate === "fact_check" && /"verdicts"\s*:\s*\[[\s\S]*?"ISSUES"/i.test(text));
  const pass =
    /"verdict"\s*:\s*"PASS"/i.test(text) ||
    (gate === "fact_check" && /"verdicts"\s*:\s*\[[\s\S]*?"PASS"/i.test(text));
  const unverified =
    /"verdict"\s*:\s*"UNVERIFIED"/i.test(text) ||
    (gate === "fact_check" && /"verdicts"\s*:\s*\[[\s\S]*?"UNVERIFIED"/i.test(text));
  const cm = text.match(/"correct_verdict"\s*:\s*"(pass|fail)"/i);
  const am = text.match(/"agrees"\s*:\s*(true|false)/i);
  const r: Receipt = {
    gate,
    valid: false,
    issues,
    agrees: am ? am[1] === "true" : undefined,
    correctVerdict: cm ? cm[1].toLowerCase() : undefined,
    renderedContent: envelope && typeof envelope.rendered_content === "string" ? envelope.rendered_content : undefined,
    raw: text,
  };
  if (gate === "fact_check") r.valid = (pass || unverified) && !issues;
  else if (gate === "grade_audit") r.valid = !issues && r.agrees !== false;
  else r.valid = pass && !issues; // quiz_audit, review
  return r;
}

function parseClerkReview(text: string): Receipt | undefined {
  const m = text.match(/REVIEW_GATE_VERDICT\s*:\s*(\{[\s\S]*?\})/);
  if (!m) return undefined;
  const blob = m[1];
  const issues = /"verdict"\s*:\s*"ISSUES"/i.test(blob);
  const pass = /"verdict"\s*:\s*"PASS"/i.test(blob);
  return { gate: "review", valid: pass && !issues, issues, raw: blob };
}

export default function (pi: ExtensionAPI) {
  let run: RunState = { flow: "other", receipts: [], scoutCalled: false, clerkCalled: false, retries: 0 };
  const pendingCalls = new Map<string, CallRef[]>();

  const reset = (flow: Flow) => {
    run = { flow, receipts: [], scoutCalled: false, clerkCalled: false, retries: 0 };
    pendingCalls.clear();
  };

  const addReceipt = (r: Receipt) => {
    run.receipts.push(r);
  };
  const findValid = (gate: string) => run.receipts.find((r) => r.gate === gate && r.valid);
  const findAny = (gate: string) => run.receipts.find((r) => r.gate === gate);
  const consume = (r: Receipt) => {
    const i = run.receipts.indexOf(r);
    if (i >= 0) run.receipts.splice(i, 1);
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
      pendingCalls.set(event.toolCallId, calls);
      if (calls.some((c) => c.agent === "scout")) run.scoutCalled = true;
      if (calls.some((c) => c.agent === "clerk")) run.clerkCalled = true;
    } catch {
      /* fail open */
    }
  });

  pi.on("tool_result", async (event: any, _ctx) => {
    try {
      if (event?.toolName !== "subagent") return;
      const calls = pendingCalls.get(event.toolCallId) || [];
      pendingCalls.delete(event.toolCallId);
      if (event.isError === true) return;
      const text = resultText(event);
      for (const call of calls) {
        const gate = VERIFIER_AGENTS[call.agent];
        if (gate) addReceipt(parseResult(text, gate, call.envelope));
        if (call.agent === "clerk") {
          const r = parseClerkReview(text);
          if (r) addReceipt(r);
        }
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

      const blockers: string[] = [];
      let verdictNote = "";
      let scoutNeeded = false;
      const toConsume: Receipt[] = [];

      if (run.flow === "ingest") {
        if (run.clerkCalled) {
          const r = findValid("review");
          if (r) toConsume.push(r);
          else {
            const any = findAny("review");
            blockers.push(any ? "REVIEW_GATE_ISSUES" : "NO_REVIEW_GATE_PASS");
          }
        }
      } else if (run.flow === "review") {
        if (grade) {
          const g = findValid("grade_audit");
          if (g) toConsume.push(g);
          else {
            const bad = findAny("grade_audit");
            if (bad && bad.agrees === false) {
              blockers.push("GRADE_MISMATCH");
              verdictNote = bad.correctVerdict ? `The verifier says the correct verdict is "${bad.correctVerdict}". Present that, not your own.` : "";
            } else blockers.push("NO_GRADE_AUDIT_PASS");
          }
        }
      } else {
        // teach | resume
        if (quiz) {
          const q = findValid("quiz_audit");
          if (q) toConsume.push(q);
          else blockers.push(findAny("quiz_audit") ? "QUIZ_AUDIT_ISSUES" : "NO_QUIZ_AUDIT_PASS");
        }
        if (grade) {
          const g = findValid("grade_audit");
          if (g) toConsume.push(g);
          else {
            const bad = findAny("grade_audit");
            if (bad && bad.agrees === false) {
              blockers.push("GRADE_MISMATCH");
              verdictNote = bad.correctVerdict ? `The verifier says the correct verdict is "${bad.correctVerdict}". Present that, not your own.` : "";
            } else blockers.push("NO_GRADE_AUDIT_PASS");
          }
        }
        if (teach) {
          let best: Receipt | undefined;
          let bestScore = 0;
          let failingMatch = false;
          for (const r of run.receipts) {
            if (r.gate !== "fact_check") continue;
            const score = r.renderedContent ? coverage(r.renderedContent, text) : 0;
            if (score >= MATCH_THRESHOLD && score > bestScore) {
              bestScore = score;
              best = r;
            }
          }
          if (!best) {
            const failed = run.receipts.find((r) => r.gate === "fact_check" && r.issues);
            blockers.push(failed ? "FACT_CHECK_ISSUES" : "NO_FACT_CHECK_MATCH");
          } else if (!best.valid) {
            failingMatch = true;
            blockers.push(best.issues ? "FACT_CHECK_ISSUES" : "FACT_CHECK_UNVERIFIED");
          } else {
            toConsume.push(best);
          }
          if (run.flow === "teach" && !run.scoutCalled) scoutNeeded = true;
        }
      }

      if (blockers.length === 0 && !scoutNeeded) {
        for (const r of toConsume) consume(r);
        return;
      }

      run.retries += 1;
      const codes = [...blockers];
      if (scoutNeeded) codes.push("NO_SCOUT_CONTEXT");

      if (run.retries > MAX_RETRIES) {
        const banner = `⛔ UNVERIFIED — gate retries exhausted (${codes.join(", ")}). The content below was not verified.\n\n`;
        return { message: replaceText(message, banner + text) };
      }

      const fix = [
        "fact-check: send your exact draft as `rendered_content` with its claims, then emit the verified text unchanged.",
        "quiz-audit: send the exact batch and resolve high/medium issues before showing it.",
        "grade-audit: send question + raw learner answer + claimed verdict; use the verifier's `correct_verdict`.",
        "ingest: the clerk result must include a PASS `REVIEW_GATE_VERDICT` marker.",
      ].join("\n");
      const scoutNote = scoutNeeded ? "Run the `scout` subagent first for a new lesson.\n" : "";
      const note = verdictNote ? verdictNote + "\n" : "";
      const banner = `⛔ WITHHELD (${codes.join(", ")})\n${scoutNote}${note}${fix}\n`;
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
