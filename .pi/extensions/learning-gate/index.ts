import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

/**
 * learning-gate — verification gate for the pi learning system.
 *
 * Turn type is explicit, not guessed:
 *   - Prompt templates carry a flow marker (`[[FLOW:teach|resume|review|ingest]]`).
 *   - Every assistant message in a learning flow must start with a turn tag
 *     `[[TURN:claims|quiz|grade|none]]`. The gate strips the tag before the learner sees it.
 *   - claims -> a fact-check receipt whose `rendered_content` matches the emitted text
 *     (>=85% token coverage, with a length-ratio guard against unverified tails) with no ISSUES.
 *   - quiz  -> a quiz-audit receipt returning PASS, or PASS_WITH_FLAGS (lows only)
 *     which is accepted silently (flags are not surfaced to the learner).
 *   - grade -> a grade-audit receipt that agrees (a conflicting correct_verdict is surfaced).
 *   - none  -> allowed, unless an unused verification receipt matches the text
 *     (tag mismatch / would-be evasion).
 *   - A dropped tag on a grade/quiz turn is inferred from a bound verifier
 *     receipt, or from the single pending valid receipt when a bound draft is
 *     unavailable (async notify mints) — in teach/resume/review alike — so a
 *     forgotten tag never dead-ends the turn. claims/none are never inferred.
 *   - teach/resume writes -> a passing tutor-audit receipt over the files written.
 *   - ingest -> Clerk's result must carry a review verdict marker. A missing marker is
 *     retried once; a PASS renders clean; ISSUES/PASS_WITH_FLAGS render with a visible
 *     `⚠️ REVIEW FLAGS SURFACED` banner (never an endless re-run loop).
 *
 * Receipts are consumed per emitted message. Fails open only on internal error.
 */

const VERIFIER_AGENTS: Record<string, string> = {
  "fact-check": "fact_check",
  "quiz-audit": "quiz_audit",
  "grade-audit": "grade_audit",
  "review-gate": "review",
  "tutor-audit": "tutor_audit",
  "review-session-audit": "review_session",
};

const MAX_RETRIES = 2;
// A review-gate pass may legitimately run twice (fix cycle). A third pass is
// the runaway loop we observed: repeated re-reviews of out-of-scope state
// bookkeeping. Cap dispatches per flow so it cannot spiral.
const MAX_REVIEW_GATES = 2;
// Review-session close audit: at most 2 passes per flow (initial + one fix
// cycle). A third is the runaway loop we must avoid.
const MAX_REVIEW_SESSION_AUDITS = 2;
// The ingest is delegated to clerk once per flow. Re-dispatching it re-ingests
// the same handoff and re-runs the whole review-gate chain.
const MAX_CLERK_DISPATCHES = 2;
const MATCH_THRESHOLD = 0.85;
// Emitted text may be slightly longer than the verified draft (tag strip,
// minor edits) but must not carry a large unverified tail.
const MAX_LENGTH_RATIO = 1.4;
const LENGTH_SLACK_TOKENS = 30;
const TURN_TAG_RE = /^\s*\[\[TURN:(claims|quiz|grade|none)\]\]\s*/i;
const FLOW_TAG_RE = /\[\[FLOW:(teach|resume|review|ingest)\]\]/i;
const STATE_AUDIT_RE = /(\d+)\s+errors?\b[^\d]*(\d+)\s+warnings?/i;
const WRITE_TOOLS = new Set(["write", "edit"]);

type Flow = "teach" | "resume" | "review" | "ingest" | "other";

interface Receipt {
  gate: string;
  valid: boolean;
  issues: boolean;
  flags?: boolean;
  agrees?: boolean;
  correctVerdict?: string;
  renderedContent?: string;
  // Content binding so an old PASS can't satisfy a new turn.
  questionsText?: string;
  gradeText?: string;
  auditFiles?: string[];
  envelopeGate?: string;
  raw: string;
}

interface StateAudit {
  errors: number;
  warnings: number;
}

interface RunState {
  flow: Flow;
  receipts: Receipt[];
  scoutCalled: boolean;
  clerkCalled: boolean;
  clerkDispatches: number;
  reviewGates: number;
  retries: number;
  tutorWrote: boolean;
  writtenPaths: string[];
  // Review-close: set when the review flow writes Review notes / session note /
  // touched state rows; a summary-like turn then needs a review_session audit.
  reviewSessionWrote: boolean;
  reviewSessionPaths: string[];
  reviewSessionAudits: number;
  stateAudit?: StateAudit;
  agentlessDispatch: boolean;
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

/** Prepend a banner to the message text while keeping role/content shape. */
function prependBanner(message: any, banner: string): any {
  const c = message?.content;
  if (typeof c === "string") return { ...message, content: banner + c };
  if (Array.isArray(c)) {
    let done = false;
    const nc = c.map((p: any) => {
      if (!done && p && p.type === "text" && typeof p.text === "string") {
        done = true;
        return { ...p, text: banner + p.text };
      }
      return p;
    });
    if (!done) nc.unshift({ type: "text", text: banner });
    return { ...message, content: nc };
  }
  return message;
}

/** Remove the leading turn tag from the first non-empty text part that carries it. */
function stripTag(message: any): any {
  const c = message?.content;
  if (typeof c === "string") return { ...message, content: c.replace(TURN_TAG_RE, "") };
  if (Array.isArray(c)) {
    let done = false;
    const nc = c.map((p: any) => {
      if (!done && p && p.type === "text" && typeof p.text === "string" && TURN_TAG_RE.test(p.text)) {
        done = true;
        return { ...p, text: p.text.replace(TURN_TAG_RE, "") };
      }
      return p;
    });
    // Fallback: tag spans parts (whitespace-only first part) — strip from the
    // first non-empty text part.
    if (!done) {
      for (let i = 0; i < nc.length; i++) {
        const p = nc[i];
        if (p && p.type === "text" && typeof p.text === "string" && p.text.trim().length > 0) {
          nc[i] = { ...p, text: p.text.replace(TURN_TAG_RE, "") };
          break;
        }
      }
    }
    return { ...message, content: nc };
  }
  return message;
}

function promptText(prompt: any): string {
  if (typeof prompt === "string") return prompt;
  if (Array.isArray(prompt)) {
    try {
      return prompt.map((p: any) => (typeof p === "string" ? p : p?.text || "")).join("\n");
    } catch {
      return "";
    }
  }
  if (prompt && typeof prompt === "object") {
    try {
      return JSON.stringify(prompt);
    } catch {
      return "";
    }
  }
  return "";
}

/**
 * Flow detection is EXPLICIT-ONLY: a learning flow starts iff the prompt
 * carries a `[[FLOW:teach|resume|review|ingest]]` marker. Every prompt
 * template in `.pi/prompts/` emits one.
 *
 * Do NOT reintroduce keyword matching here. The old fallback ("learn",
 * "ingest ", "continue the current lesson", ...) was the root cause of an
 * hour-long gate deadlock: verifier subagents run as background sessions
 * that load this extension, and their GATE envelopes contain phrases like
 * `"flow":"teach"`, "Information Theory Ingest", and "Pending Ingest.json".
 * The fallback classified those verifier sessions as learning flows, so the
 * gate withheld the verifier's own untagged verdict JSON with NO_TURN_TAG,
 * the parent never received a receipt, and every tutor-audit round collapsed
 * into a resume loop. Subagent tasks never carry a FLOW marker, so
 * explicit-only detection keeps the gate off verifier sessions; a bare user
 * message without a marker simply fails open (no gating).
 */
function detectFlow(prompt: any): Flow {
  const raw = promptText(prompt);
  const tag = raw.match(FLOW_TAG_RE);
  if (tag) return tag[1].toLowerCase() as Flow;
  return "other";
}

/** Try parsing a JSON envelope out of freeform task text (prose + JSON). */
function parseTask(task: any): any | undefined {
  if (task && typeof task === "object") return task;
  if (typeof task !== "string") return undefined;
  const trimmed = task.trim();
  try {
    return JSON.parse(trimmed);
  } catch {
    // Walk candidate `{` positions from last to first; the envelope is
    // usually the trailing JSON block, not the first brace in prose.
    const starts: number[] = [];
    for (let i = 0; i < trimmed.length; i++) if (trimmed[i] === "{") starts.push(i);
    for (let s = starts.length - 1; s >= 0; s--) {
      const candidate = trimmed
        .slice(starts[s])
        .replace(/```+\s*$/g, "")
        .trim();
      // Try progressively shorter tails (handles trailing prose after JSON).
      for (let end = candidate.length; end > 0; end--) {
        const ch = candidate[end - 1];
        if (ch !== "}" && ch !== "]") {
          continue;
        }
        const slice = candidate.slice(0, end);
        try {
          const parsed = JSON.parse(slice);
          if (parsed && typeof parsed === "object") return parsed;
        } catch {
          // keep shrinking
        }
        // Only try plausible JSON ends to bound cost.
        if (end < candidate.length - 2000) break;
      }
    }
    return undefined;
  }
}

interface CallRef {
  agent: string;
  gate?: string;
  envelope?: any;
  output?: string;
}

/** Source inside the balanced `(`…`)` pair whose opening paren sits at `openIdx`. */
function sliceBalanced(text: string, openIdx: number): string | undefined {
  const open = text[openIdx];
  const close = open === "(" ? ")" : open === "[" ? "]" : open === "{" ? "}" : "";
  if (!close) return undefined;
  let depth = 0;
  let quote = "";
  let esc = false;
  for (let i = openIdx; i < text.length; i++) {
    const ch = text[i];
    if (quote) {
      if (esc) esc = false;
      else if (ch === "\\") esc = true;
      else if (ch === quote) quote = "";
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") {
      quote = ch;
      continue;
    }
    if (ch === open) depth++;
    else if (ch === close) {
      depth--;
      if (depth === 0) return text.slice(openIdx + 1, i);
    }
  }
  return undefined;
}

/**
 * Agent names launched by a pi-subagents workflow script (`runs.run(key, …)` /
 * `runs.all([…])`). Only these names are needed at dispatch time — the caps and
 * the scout/clerk flags — because the tool result carries each child's envelope
 * and output structurally in `details.results`. The scan is fenced to the
 * `runs.run`/`runs.all` argument lists so an `agent:` word inside a task string
 * cannot inject a phantom child.
 */
function workflowScriptAgents(script: string): string[] {
  const agents: string[] = [];
  const callRe = /\bruns\s*\.\s*(?:run|all)\s*\(/g;
  let call: RegExpExecArray | null;
  while ((call = callRe.exec(script))) {
    const paren = script.indexOf("(", call.index);
    const body = paren >= 0 ? sliceBalanced(script, paren) : undefined;
    if (!body) continue;
    const agentRe = /\bagent\s*:\s*(["'`])([\w.-]+)\1/g;
    let m: RegExpExecArray | null;
    while ((m = agentRe.exec(body))) agents.push(m[2]);
  }
  return agents;
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
  for (const key of ["tasks", "chain", "calls", "subagents"]) {
    const arr = (input as any)[key];
    if (Array.isArray(arr)) for (const t of arr) push(t?.agent, t?.task);
  }
  // pi-subagents >= 0.68 replaced the legacy top-level `chain`/`tasks` inputs
  // with a workflow script (`runs.run(key, {agent, task})` / `runs.all([...])`).
  // Without this the gate saw no child, minted no receipt, and every workflow
  // verifier dispatch dead-ended (e.g. NO_QUIZ_AUDIT_PASS after a foreground
  // workflow quiz-audit). Management actions (validate/status/list/…) launch
  // nothing and are ignored.
  if (input.action === undefined && typeof input.workflowScript === "string") {
    for (const agent of workflowScriptAgents(input.workflowScript)) out.push({ agent });
  }
  return out;
}

/**
 * Resolve the child calls behind a `subagent` tool result.
 *
 * pi-subagents >= 0.68 reports workflow children structurally in
 * `details.results` (`agent`, `task` JSON, `finalOutput`) — the only reliable
 * place to recover a workflow child's envelope and output. Fall back to the
 * calls captured from the request input for legacy single/chain shapes and
 * async fan-out notices (which carry no immediate output; the notify fallback
 * mints those receipts later).
 */
function resultCalls(event: any, text: string, pending: CallRef[]): CallRef[] {
  const results = event?.details?.results;
  if (Array.isArray(results) && results.length > 0) {
    const out: CallRef[] = [];
    for (const r of results) {
      if (!r || typeof r.agent !== "string") continue;
      const finalOutput = typeof r.finalOutput === "string" ? r.finalOutput : undefined;
      if (!finalOutput) continue; // async/pending child — the notify fallback mints it
      const env = parseTask(r.task);
      out.push({
        agent: r.agent,
        envelope: env,
        gate: env && typeof env.gate === "string" ? env.gate : undefined,
        output: finalOutput,
      });
    }
    if (out.length > 0) return out;
  }
  return pending.map((c) => ({ ...c, output: text }));
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
  if (n.length === 0) return 0;
  const hs = new Set(tokens(hay));
  let hit = 0;
  for (const t of n) if (hs.has(t)) hit++;
  return hit / n.length;
}

/**
 * Guard against unverified tails: the verified draft must cover the emission
 * AND the emission must not be much longer than the draft.
 */
function contentMatches(renderedContent: string, emittedText: string): boolean {
  const score = coverage(renderedContent, emittedText);
  if (score < MATCH_THRESHOLD) return false;
  const nLen = tokens(renderedContent).length;
  const hLen = tokens(emittedText).length;
  if (nLen === 0) return false;
  return hLen <= nLen * MAX_LENGTH_RATIO + LENGTH_SLACK_TOKENS;
}

/** Quiz/grade binding: the receipt's audited content must overlap the emission. */
function bindingMatches(bound: string | undefined, emittedText: string): boolean {
  if (!bound || bound.trim().length === 0) return true; // back-compat
  return coverage(bound, emittedText) >= 0.5;
}

function parseStateAudit(text: string): StateAudit | undefined {
  const marker = text.match(/STATE_AUDIT_VERDICT\s*:\s*\{"errors"\s*:\s*(\d+)\s*,\s*"warnings"\s*:\s*(\d+)/i);
  if (marker) return { errors: Number(marker[1]), warnings: Number(marker[2]) };
  const m = text.match(STATE_AUDIT_RE);
  if (!m) return undefined;
  return { errors: Number(m[1]), warnings: Number(m[2]) };
}

/** Pull a file path out of a write/edit tool input. */
function writePath(input: any): string | undefined {
  if (!input || typeof input !== "object") return undefined;
  const p = input.filePath || input.path || input.file_path || input.file || input.filename || input.file_name;
  return typeof p === "string" ? p : undefined;
}

function normPath(path: string): string {
  return path.replace(/\\/g, "/").toLowerCase();
}

function isLearningStatePath(path: string): boolean {
  const p = normPath(path);
  return /(^|\/)learning system\//.test(p);
}

/** Review-close artifacts whose write arms the review-session audit gate. */
function isReviewSessionPath(path: string): boolean {
  const p = normPath(path);
  if (!isLearningStatePath(p)) return false;
  if (/(^|\/)learning system\/(reviews|sessions)\//.test(p)) return true;
  return /(active concepts|mistakes)\.md$/.test(p) || /attempts\.json$/.test(p);
}

// A review-close summary lists per-concept results (mastery + next review),
// unlike a mid-session transition. Used so the review-session gate never holds
// a transition hostage after the session note is written.
const REVIEW_SUMMARY_RE = /(mastery\s+\d|next review|last q type|review\s+[—-]|reviews\/|session\s+[—-]|graduated|feynman:)/i;

function looksLikeReviewSummary(text: string): boolean {
  return REVIEW_SUMMARY_RE.test(text || "");
}

function envelopeText(value: any): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) {
    return value
      .map((v: any) => {
        if (typeof v === "string") return v;
        if (v && typeof v === "object") return [v.question, v.text, v.claim, v.q, v.prompt].filter((x) => typeof x === "string").join(" ");
        return "";
      })
      .join("\n");
  }
  return "";
}

/**
 * Out-of-scope for a review-gate pass: state bookkeeping / provenance that
 * review-gate.md explicitly excludes (state files, lesson/session/review files,
 * log/index bookkeeping, git/commit metadata). A review that reports only these
 * must not read as blocking issues on the target content — otherwise the tutor
 * re-reviews the same clean page forever.
 */
const REVIEW_OUT_OF_SCOPE_RE =
  /(mission\.md|curriculum\.md|learning profile|learner history|mistakes\.md|attempts\.json|pending ingest\.json|\bsessions\/|\breviews\/|\blessons\/|log\.md|index\.md|git history|commit message|provenance|staged files|worktree)/i;

function reviewIssuesAllOutOfScope(text: string): boolean {
  const v = text.search(/"verdict"\s*:/i);
  if (v < 0) return false;
  // Walk back through `{` candidates until one parses as the verdict object.
  let idx = v;
  for (let guard = 0; guard < 20; guard++) {
    const start = text.lastIndexOf("{", idx - 1);
    if (start < 0) return false;
    const blob = extractBalancedJson(text, start);
    if (blob) {
      let parsed: any;
      try {
        parsed = JSON.parse(blob);
      } catch {
        parsed = undefined;
      }
      if (parsed && typeof parsed === "object" && (parsed.verdict || Array.isArray(parsed.issues))) {
        const issues = Array.isArray(parsed.issues) ? parsed.issues : [];
        if (issues.length === 0) return false;
        return issues.every((it: any) => {
          const sev = typeof it?.severity === "string" ? it.severity.toLowerCase() : "";
          if (sev === "low") return true;
          const loc = typeof it?.location === "string" ? it.location.trim() : "";
          const iss = typeof it?.issue === "string" ? it.issue : "";
          // Prefer the cited location; only fall back to the issue text when no
          // location was given (avoids demoting content findings that merely
          // mention a word like "total" in prose).
          return REVIEW_OUT_OF_SCOPE_RE.test(loc.length > 0 ? loc : iss);
        });
      }
    }
    idx = start;
  }
  return false;
}

function parseResult(text: string, gate: string, envelope: any): Receipt {
  let issues =
    /"verdict"\s*:\s*"ISSUES"/i.test(text) ||
    (gate === "fact_check" && /"verdicts"\s*:\s*\[[\s\S]*?"ISSUES"/i.test(text));
  let pass =
    /"verdict"\s*:\s*"PASS"/i.test(text) ||
    (gate === "fact_check" && /"verdicts"\s*:\s*\[[\s\S]*?"PASS"/i.test(text));
  let passWithFlags = /"verdict"\s*:\s*"PASS_WITH_FLAGS"/i.test(text);
  // Review-gate: if every high/medium finding is out-of-scope bookkeeping, the
  // target content is clean. Surface them as flags, never as blocking issues.
  if (gate === "review" && issues && reviewIssuesAllOutOfScope(text)) {
    issues = false;
    passWithFlags = true;
  }
  const unverified =
    /"verdict"\s*:\s*"UNVERIFIED"/i.test(text) ||
    (gate === "fact_check" && /"verdicts"\s*:\s*\[[\s\S]*?"UNVERIFIED"/i.test(text));
  const cm = text.match(/"correct_verdict"\s*:\s*"(pass|fail)"/i);
  const am = text.match(/"agrees"\s*:\s*(true|false)/i);
  const questionsText = envelope ? envelopeText(envelope.questions_json || envelope.questions) : undefined;
  const gradeText = envelope
    ? [envelope.question, envelope.learner_answer, envelope.claimed_verdict].filter((x) => typeof x === "string").join("\n")
    : undefined;
  const auditFiles = envelope && Array.isArray(envelope.files) ? envelope.files.filter((x: any) => typeof x === "string") : undefined;
  const r: Receipt = {
    gate,
    valid: false,
    issues,
    flags: passWithFlags,
    agrees: am ? am[1].toLowerCase() === "true" : undefined,
    correctVerdict: cm ? cm[1].toLowerCase() : undefined,
    renderedContent: envelope && typeof envelope.rendered_content === "string" ? envelope.rendered_content : undefined,
    questionsText: questionsText || undefined,
    gradeText: gradeText || undefined,
    auditFiles,
    envelopeGate: envelope && typeof envelope.gate === "string" ? envelope.gate : undefined,
    raw: text,
  };
  // UNVERIFIED never counts as verified — it must block, not pass.
  if (gate === "fact_check") r.valid = pass && !issues && !unverified;
  else if (gate === "grade_audit") r.valid = !issues && r.agrees === true;
  else r.valid = (pass || passWithFlags) && !issues; // quiz_audit, review, tutor_audit
  return r;
}

/** Extract balanced `{...}` JSON starting at `start` (handles nested braces/strings). */
function extractBalancedJson(text: string, start: number): string | undefined {
  let depth = 0;
  let inStr = false;
  let esc = false;
  for (let i = start; i < text.length; i++) {
    const ch = text[i];
    if (inStr) {
      if (esc) esc = false;
      else if (ch === "\\") esc = true;
      else if (ch === '"') inStr = false;
      continue;
    }
    if (ch === '"') inStr = true;
    else if (ch === "{") depth++;
    else if (ch === "}") {
      depth--;
      if (depth === 0) return text.slice(start, i + 1);
    }
  }
  return undefined;
}

function parseClerkReview(text: string): Receipt | undefined {
  const idx = text.search(/REVIEW_GATE_VERDICT\s*:/i);
  if (idx < 0) return undefined;
  const brace = text.indexOf("{", idx);
  if (brace < 0) return undefined;
  const blob = extractBalancedJson(text, brace);
  if (!blob) return undefined;
  const issues = /"verdict"\s*:\s*"ISSUES"/i.test(blob);
  const pass = /"verdict"\s*:\s*"PASS"/i.test(blob);
  const passWithFlags = /"verdict"\s*:\s*"PASS_WITH_FLAGS"/i.test(blob);
  return { gate: "review", valid: (pass || passWithFlags) && !issues, issues, flags: passWithFlags, raw: blob };
}

/** Expected envelope gate per verifier agent (wrong envelope => no receipt). */
const EXPECTED_ENVELOPE_GATE: Record<string, string> = {
  "fact-check": "fact_check",
  "quiz-audit": "quiz_audit",
  "grade-audit": "grade_audit",
  "review-gate": "review",
  "tutor-audit": "tutor_audit",
  "review-session-audit": "review_session",
};

export default function (pi: ExtensionAPI) {
  let run: RunState = {
    flow: "other",
    receipts: [],
    scoutCalled: false,
    clerkCalled: false,
    clerkDispatches: 0,
    reviewGates: 0,
    retries: 0,
    tutorWrote: false,
    writtenPaths: [],
    reviewSessionWrote: false,
    reviewSessionPaths: [],
    reviewSessionAudits: 0,
    agentlessDispatch: false,
  };

  const pendingCalls = new Map<string, CallRef[]>();

  const reset = (flow: Flow) => {
    run = { flow, receipts: [], scoutCalled: false, clerkCalled: false, clerkDispatches: 0, reviewGates: 0, retries: 0, tutorWrote: false, writtenPaths: [], reviewSessionWrote: false, reviewSessionPaths: [], reviewSessionAudits: 0, agentlessDispatch: false };
    pendingCalls.clear();
  };

  const addReceipt = (r: Receipt) => run.receipts.push(r);
  const findAny = (gate: string) => run.receipts.find((r) => r.gate === gate);
  const consume = (r: Receipt) => {
    const i = run.receipts.indexOf(r);
    if (i >= 0) run.receipts.splice(i, 1);
  };

  pi.on("before_agent_start", async (event: any, _ctx) => {
    try {
      const flow = detectFlow(event?.prompt);
      // Subagent starts carry no FLOW marker — never wipe the parent run.
      // Only (re)start gating when a real learning flow begins.
      if (flow === "other") return;
      reset(flow);
    } catch {
      /* fail open: keep existing run */
    }
  });

  pi.on("tool_call", async (event: any, _ctx) => {
    try {
      const tool = typeof event?.toolName === "string" ? event.toolName.toLowerCase() : "";
      if (WRITE_TOOLS.has(tool)) {
        const p = writePath(event.input);
        if (p && isLearningStatePath(p)) {
          if (run.flow === "teach" || run.flow === "resume") {
            run.tutorWrote = true;
            run.writtenPaths.push(normPath(p));
          } else if (run.flow === "review" && isReviewSessionPath(p)) {
            run.reviewSessionWrote = true;
            run.reviewSessionPaths.push(normPath(p));
          }
        }
        return;
      }
      if (tool === "bash") {
        const cmd = typeof event.input?.command === "string" ? event.input.command : "";
        if (run.flow === "teach" || run.flow === "resume") {
          // ops.py apply during teach/resume marks a Tutor write.
          if (/ops\.py\s+apply/.test(cmd)) run.tutorWrote = true;
        } else if (run.flow === "review") {
          // The review close writes its Review notes + session note via
          // `ops.py apply <<'SPEC'`; the spec (paths included) is in the command
          // string. Arm the review-session audit only when the session note is
          // in the spec — the once-per-session closing artifact — so per-concept
          // Review-note writes do not gate intermediate transitions.
          if (/ops\.py\s+apply/.test(cmd) && /learning system\/sessions\//i.test(cmd)) {
            run.reviewSessionWrote = true;
          }
        }
        return;
      }
      if (tool !== "subagent") return;
      const calls = subagentCalls(event.input);
      // A subagent dispatch with no (string) `agent` mints no receipt and fails
      // opaquely. Remember it so the next withheld message can say why.
      if (calls.length === 0 && event.input && typeof event.input === "object" && ("task" in event.input || "prompt" in event.input)) {
        run.agentlessDispatch = true;
      }
      const reviewGateCalls = calls.filter((c) => c.agent === "review-gate").length;
      const reviewSessionCalls = calls.filter((c) => c.agent === "review-session-audit").length;
      const clerkCalls = calls.filter((c) => c.agent === "clerk").length;
      if (reviewGateCalls > 0) run.reviewGates += reviewGateCalls;
      if (reviewSessionCalls > 0) run.reviewSessionAudits += reviewSessionCalls;
      if (clerkCalls > 0) run.clerkDispatches += clerkCalls;
      if (reviewSessionCalls > 0 && run.reviewSessionAudits > MAX_REVIEW_SESSION_AUDITS) {
        return {
          block: true,
          reason: `review-session audit cap reached (${MAX_REVIEW_SESSION_AUDITS} passes per flow). Report the existing verdict — fix any high/medium flags next session instead of re-running.`,
        };
      }
      if (reviewGateCalls > 0 && run.reviewGates > MAX_REVIEW_GATES) {
        return {
          block: true,
          reason: `review-gate cap reached (${MAX_REVIEW_GATES} passes per flow). Report the existing verdict — do not re-run. State/bookkeeping drift is audit_state.py's job, not another review pass.`,
        };
      }
      if (clerkCalls > 0 && run.clerkDispatches > MAX_CLERK_DISPATCHES) {
        return {
          block: true,
          reason: `clerk ingest cap reached (${MAX_CLERK_DISPATCHES} per flow). The ingest is already running or done — report its result instead of re-dispatching.`,
        };
      }
      if (event?.toolCallId) pendingCalls.set(event.toolCallId, calls);
      if (calls.some((c) => c.agent === "scout")) run.scoutCalled = true;
      if (calls.some((c) => c.agent === "clerk")) run.clerkCalled = true;
    } catch {
      /* fail open */
    }
  });

  pi.on("tool_result", async (event: any, _ctx) => {
    try {
      if (event?.isError === true) return;
      const text = resultText(event);
      const tool = typeof event?.toolName === "string" ? event.toolName.toLowerCase() : "";
      if (tool === "subagent") {
        const pending = (event?.toolCallId && pendingCalls.get(event.toolCallId)) || [];
        if (event?.toolCallId) pendingCalls.delete(event.toolCallId);
        for (const call of resultCalls(event, text, pending)) {
          const output = call.output || text;
          const gate = VERIFIER_AGENTS[call.agent];
          if (gate) {
            // Right envelope for the right agent — a fact-check envelope on a
            // quiz-audit call (or vice versa) mints nothing.
            const expected = EXPECTED_ENVELOPE_GATE[call.agent];
            if (call.envelope && call.gate && expected && call.gate !== expected) continue;
            addReceipt(parseResult(output, gate, call.envelope));
          }
          if (call.agent === "clerk") {
            const r = parseClerkReview(output);
            if (r) addReceipt(r);
          }
        }
      }
      const audit = parseStateAudit(text);
      if (audit) run.stateAudit = audit;
    } catch {
      /* fail open */
    }
  });

  // Gates eligible for the async-completion fallback below. `fact_check` is
  // excluded on purpose: its receipt binds a claims turn through
  // `rendered_content`, which a completion notification does not carry, so a
  // notify-minted fact-check receipt could never bind (it would only swap
  // NO_FACT_CHECK_MATCH for FACT_CHECK_MISSING_DRAFT).
  const NOTIFY_FALLBACK_SKIP = new Set(["fact_check"]);

  /**
   * Mint a receipt from an async/detached subagent completion notification.
   *
   * Async subagent results reach the parent as `subagent-notify` custom
   * messages (the dispatch's tool result is only the fan-out notice), so a
   * completed verifier/clerk run can otherwise be invisible to the gate.
   * pi-subagents emits `Background task completed: **agent**` for async runs
   * and `Detached foreground task completed: **agent**` for a foreground run
   * that was later detached — both carry the child's output preview, so accept
   * either. Idempotent (skip a gate that already has a valid receipt) and
   * fail-open; non-notification text is a no-op.
   */
  const NOTIFY_HEADER_RE = /(?:Background task|Detached foreground task) completed:\s*\*\*([\w-]+)\*\*/i;
  const mintFromNotification = (text: string): void => {
    if (!text || !NOTIFY_HEADER_RE.test(text)) return;
    const agent = text.match(NOTIFY_HEADER_RE)?.[1]?.toLowerCase();
    if (!agent) return;
    if (agent === "clerk") {
      if (run.receipts.some((r) => r.gate === "review" && r.valid)) return;
      const r = parseClerkReview(text);
      if (r) addReceipt(r);
      return;
    }
    const gate = VERIFIER_AGENTS[agent];
    if (!gate || NOTIFY_FALLBACK_SKIP.has(gate)) return;
    if (run.receipts.some((r) => r.gate === gate && r.valid)) return;
    addReceipt(parseResult(text, gate, undefined));
  };

  /**
   * Infer a `grade`/`quiz` turn from a verifier receipt when the Tutor forgot
   * its `[[TURN:...]]` tag.
   *
   * Only `grade` and `quiz` are eligible: the grade receipt carries the exact
   * question + learner answer and the quiz receipt carries the exact question
   * batch, so `bindingMatches` is a real signal. `claims` is excluded (it needs
   * a `rendered_content` draft binding that only a fresh fact-check carries) and
   * `none` is excluded (a transition is not verifiable content — an unbound
   * message must still withhold).
   *
   * Preference order:
   *  1. A receipt whose bound text covers the emission (strong evidence — the
   *     audit really was for this text). Best-covering wins; ties go to `grade`.
   *  2. Otherwise, exactly ONE gate type (`grade` or `quiz`) has a valid, unused
   *     receipt. Async verifiers mint a valid receipt from the completion
   *     notification, which carries no envelope/bound text; requiring a bound
   *     draft there would dead-end every async grade/quiz turn whose tag was
   *     dropped (the observed resume-session NO_TURN_TAG loop). Trusting the
   *     single pending receipt mirrors the explicit-tag path, where an unbound
   *     valid receipt is already accepted. Two pending gate types stay
   *     ambiguous and withhold.
   *
   * Applies to every interactive flow (teach/resume/review) — the dead-end is
   * identical in all three; ingest has its own clerk-receipt inference.
   */
  const inferTaggedTurn = (text: string): "grade" | "quiz" | undefined => {
    if (run.flow === "ingest" || run.flow === "other") return undefined;
    let best: { tag: "grade" | "quiz"; score: number } | undefined;
    const validGates = new Set<"grade" | "quiz">();
    const consider = (tag: "grade" | "quiz", bound: string | undefined) => {
      if (!bound || bound.trim().length === 0) return;
      if (!bindingMatches(bound, text)) return;
      const score = coverage(bound, text);
      if (!best || score > best.score || (score === best.score && tag === "grade")) best = { tag, score };
    };
    for (const r of run.receipts) {
      if (r.gate === "grade_audit") {
        if (r.valid) validGates.add("grade");
        consider("grade", r.gradeText);
      } else if (r.gate === "quiz_audit") {
        if (r.valid) validGates.add("quiz");
        consider("quiz", r.questionsText);
      }
    }
    if (best) return best.tag;
    // With a handoff write pending in teach/resume, an untagged summary is far
    // more likely the handoff summary (which the tutor-audit gate must check)
    // than a grade/quiz turn — require the strong bound-receipt signal before
    // inferring, so the fallback cannot wave the summary past `NO_TUTOR_AUDIT`.
    if (run.tutorWrote && (run.flow === "teach" || run.flow === "resume")) return undefined;
    if (validGates.size === 1) return [...validGates][0];
    return undefined;
  };

  pi.on("message_end", async (event: any, ctx) => {
    try {
      const message = event?.message;
      // Custom messages are async-subagent completion notifications — mint a
      // receipt from them, then leave the message untouched (never gated).
      if (message?.role === "custom") {
        try {
          mintFromNotification(resultText(message));
        } catch {
          /* fail open */
        }
        return;
      }
      if (!message || message.role !== "assistant") return;
      if (hasToolCall(message)) return;
      if (run.flow === "other") return;

      // A generation that did not finish (`error`, `aborted`, or the token cap
      // `length`) is a partial emission pi will retry or continue. Gating it
      // would consume the verifier receipt that the retried message needs — the
      // observed dead-end where an errored, truncated grade turn consumed the
      // grade-audit receipt and the re-emitted grade turn then withheld with
      // NO_GRADE_AUDIT_PASS. Pass partials through ungated and leave receipts
      // intact for the message that actually completes.
      if (message.stopReason === "error" || message.stopReason === "aborted" || message.stopReason === "length") {
        return { message: stripTag(message) };
      }

      const rawText = textOf(message);
      if (!rawText || rawText.trim().length === 0) return;

      const tagMatch = rawText.match(TURN_TAG_RE);
      const text = (tagMatch ? rawText.replace(TURN_TAG_RE, "") : rawText).trim();
      const explicitTag = tagMatch ? tagMatch[1].toLowerCase() : undefined;
      const blockers: string[] = [];
      let verdictNote = "";
      let scoutNeeded = false;
      let surface = "";
      const toConsume: Receipt[] = [];

      // Ingest terminal summary: the clerk's REVIEW_GATE_VERDICT receipt is the
      // verification for this turn, so an untagged summary after a clerk
      // dispatch is treated as an implicit none-turn. Withholding it on
      // NO_TURN_TAG ends the turn (a withheld final message needs a manual user
      // poke) — the dead-end this guard removes. Scoped to ingest-after-clerk;
      // teach/resume summaries still need an explicit tag or a bound receipt.
      const inferredNone =
        !tagMatch &&
        ((run.flow === "ingest" && run.clerkCalled) ||
          // Review close: after the session note is written, a summary-like
          // untagged message is an implicit none-turn (its verification is the
          // review_session receipt below); a transition without summary markers
          // is not, so it cannot be held hostage by arming the gate.
          (run.flow === "review" && run.reviewSessionWrote && looksLikeReviewSummary(text)));
      // Grade/quiz turns are tightly bound to a verifier receipt, so a
      // forgotten tag can be inferred from it in any interactive flow.
      // The same dead-end guard as the ingest `inferredNone` path: a weak Tutor
      // that drops `[[TURN:...]]` after a (often async) verification would
      // otherwise withhold the message, end the turn, and need a manual poke.
      let inferredTag: "grade" | "quiz" | undefined;
      if (!tagMatch && !inferredNone) {
        inferredTag = inferTaggedTurn(text);
        if (!inferredTag) blockers.push("NO_TURN_TAG");
      }
      const tag = explicitTag || inferredTag || (inferredNone ? "none" : undefined);
      if (run.flow === "ingest") {
        if (run.clerkCalled) {
          const any = findAny("review");
          if (any && any.valid) {
            toConsume.push(any);
            if (any.flags || any.issues) {
              surface = "⚠️ REVIEW FLAGS SURFACED — the reviewer returned flags on the ingest output; the content below is shown with those flags outstanding.\n\n";
            }
          } else if (any) {
            // Reviewer found issues: surface, never hard-block (this is what caused the
            // previous endless pass-3/4/… loop). Defer consumption to the
            // success path so a later blocker doesn't lose the receipt.
            toConsume.push(any);
            surface = "⚠️ REVIEW FLAGS SURFACED — high/medium review issues were reported on the ingest output; the content below is shown with those flags outstanding.\n\n";
          } else {
            blockers.push("NO_REVIEW_GATE_PASS");
          }
        }
      } else if (tag === "claims") {
        if (run.flow === "teach" && !run.scoutCalled) scoutNeeded = true;
        let best: Receipt | undefined;
        let bestScore = 0;
        for (const r of run.receipts) {
          if (r.gate !== "fact_check" || !r.valid) continue;
          if (!r.renderedContent || !contentMatches(r.renderedContent, text)) continue;
          const score = coverage(r.renderedContent, text);
          if (score > bestScore) {
            bestScore = score;
            best = r;
          }
        }
        if (!best) {
          const anyIssues = run.receipts.some((r) => r.gate === "fact_check" && r.issues);
          const anyUnverified = run.receipts.some(
            (r) => r.gate === "fact_check" && !r.valid && !r.issues && /UNVERIFIED/i.test(r.raw)
          );
          // A passing receipt that carries no rendered_content can never bind
          // to an emission — say exactly that instead of a generic "no match"
          // so the model fixes the envelope in one cycle.
          const validNoDraft = run.receipts.find((r) => r.gate === "fact_check" && r.valid && !r.renderedContent);
          const validDraft = run.receipts.find((r) => r.gate === "fact_check" && r.valid && r.renderedContent);
          if (anyIssues) blockers.push("FACT_CHECK_ISSUES");
          else if (anyUnverified) blockers.push("FACT_CHECK_UNVERIFIED");
          else if (validNoDraft) {
            blockers.push("FACT_CHECK_MISSING_DRAFT");
            verdictNote =
              "The fact-check passed but its envelope had no `rendered_content`, so it cannot bind to this message. Re-send the same claims WITH the exact draft text in `rendered_content`, then emit that text unchanged.";
          } else if (validDraft) {
            const score = coverage(validDraft.renderedContent as string, text);
            blockers.push("FACT_CHECK_MISMATCH");
            verdictNote = `The fact-check receipt covers only ${Math.round(score * 100)}% of this message (needs ≥${Math.round(
              MATCH_THRESHOLD * 100
            )}%, no unverified tail). Emit the verified draft unchanged, or fact-check this new text.`;
          } else blockers.push("NO_FACT_CHECK_MATCH");
        } else {
          toConsume.push(best);
        }
      } else if (tag === "quiz") {
        const candidates = run.receipts.filter(
          (r) => r.gate === "quiz_audit" && r.valid && bindingMatches(r.questionsText, text)
        );
        const q = candidates[0];
        if (q) {
          toConsume.push(q);
        } else {
          const anyBound = run.receipts.some((r) => r.gate === "quiz_audit" && r.valid);
          blockers.push(anyBound ? "QUIZ_AUDIT_STALE" : findAny("quiz_audit") ? "QUIZ_AUDIT_ISSUES" : "NO_QUIZ_AUDIT_PASS");
        }
      } else if (tag === "grade") {
        const candidates = run.receipts.filter(
          (r) => r.gate === "grade_audit" && r.valid && bindingMatches(r.gradeText, text)
        );
        const g = candidates[0];
        if (g) toConsume.push(g);
        else {
          const bad = findAny("grade_audit");
          if (bad && bad.agrees === false) {
            blockers.push("GRADE_MISMATCH");
            verdictNote = bad.correctVerdict
              ? `The verifier says the correct verdict is "${bad.correctVerdict}". Present that, not your own.`
              : "";
          } else if (run.receipts.some((r) => r.gate === "grade_audit" && r.valid)) {
            blockers.push("GRADE_AUDIT_STALE");
          } else blockers.push("NO_GRADE_AUDIT_PASS");
        }
      } else {
        // none: allowed unless an unused verification draft matches this text
        const match = run.receipts.find(
          (r) => r.gate === "fact_check" && r.valid && r.renderedContent && contentMatches(r.renderedContent, text)
        );
        if (match) blockers.push("TURN_TAG_MISMATCH");
      }

      // Review-session gate: after the review flow writes its notes/rows, a
      // summary-like turn needs a review_session audit. A PASS/PASS_WITH_FLAGS
      // renders clean; ISSUES renders with a flags banner (never a withhold —
      // a withheld final message dead-ends the session). Quiz/grade turns are
      // never held hostage by it.
      const reviewSessionGateApplies =
        run.reviewSessionWrote &&
        run.flow === "review" &&
        (!tag || tag === "claims" || tag === "none") &&
        looksLikeReviewSummary(text);
      if (reviewSessionGateApplies) {
        const audit = findAny("review_session");
        if (audit) {
          toConsume.push(audit);
          run.reviewSessionWrote = false;
          run.reviewSessionPaths = [];
          if (audit.issues) {
            surface +=
              "⚠️ REVIEW FLAGS SURFACED — the end-of-review audit returned flags on the session writes " +
              "(Review notes / session note / touched state rows). The summary below is shown with those flags " +
              "outstanding; fix them next session — do not re-run the audit (hard cap 2 cycles).\n\n";
          }
        } else {
          blockers.push("NO_REVIEW_SESSION_AUDIT");
        }
      }

      // Tutor-write gate: only summary-like turns (claims/none) after a
      // Learning System/ write need a passing tutor-audit receipt. Quiz/grade
      // turns after a write must not be held hostage by it.
      const tutorGateApplies =
        run.tutorWrote && (run.flow === "teach" || run.flow === "resume") && (!tag || tag === "claims" || tag === "none");
      if (tutorGateApplies) {
        const candidates = run.receipts.filter((r) => {
          if (r.gate !== "tutor_audit" || !r.valid) return false;
          if (!r.auditFiles || r.auditFiles.length === 0) return true;
          if (run.writtenPaths.length === 0) return true;
          return r.auditFiles.some((f) => run.writtenPaths.includes(normPath(f)));
        });
        const audit = candidates[0];
        if (audit) {
          toConsume.push(audit);
          run.tutorWrote = false;
          run.writtenPaths = [];
        } else {
          blockers.push(findAny("tutor_audit") ? "TUTOR_AUDIT_ISSUES" : "NO_TUTOR_AUDIT");
        }
      }

      // State audit: surface (never block) when the deterministic audit found
      // errors or warnings still outstanding. Touched ones are fixed in-flow
      // via the script's STATE_AUDIT_FIXES hints before this verdict is emitted.
      if (run.stateAudit && (run.stateAudit.errors > 0 || run.stateAudit.warnings > 0) && (run.flow === "ingest" || run.flow === "review")) {
        surface += `⚠️ STATE AUDIT — ${run.stateAudit.errors} error(s), ${run.stateAudit.warnings} warning(s). Run /audit for details.\n\n`;
        run.stateAudit = undefined;
      }

      if (blockers.length === 0 && !scoutNeeded) {
        for (const r of toConsume) consume(r);
        run.retries = 0;
        run.agentlessDispatch = false;
        let out = stripTag(message);
        if (surface) out = prependBanner(out, surface);
        return { message: out };
      }

      run.retries += 1;
      const codes = [...blockers];
      if (scoutNeeded) codes.push("NO_SCOUT_CONTEXT");

      if (run.retries > MAX_RETRIES) {
        run.retries = 0;
        const banner = `⛔ UNVERIFIED — gate retries exhausted (${codes.join(", ")}). The content below was not verified.\n\n`;
        return { message: prependBanner(replaceText(message, text), banner) };
      }

      const fix = [
        "Start every message with a turn tag: `[[TURN:claims]]`, `[[TURN:quiz]]`, `[[TURN:grade]]`, or `[[TURN:none]]`.",
        "claims: send your exact draft as `rendered_content` with its claims, then emit the verified text unchanged.",
        "quiz: send the exact batch; fix high/medium issues (max 2 cycles), then accept PASS_WITH_FLAGS instead of looping.",
        "grade: send question + raw learner answer + claimed verdict; use the verifier's `correct_verdict`.",
        "write: write lesson/session/record/Pending Ingest files only at a pause or lesson-end handoff, then dispatch a `tutor-audit` on that batch and fold its verdict before the summary.",
        "ingest: the clerk result must include a `REVIEW_GATE_VERDICT` marker (PASS or PASS_WITH_FLAGS).",
        "grade/quiz: a dropped tag is accepted when a verifier receipt for that turn is pending; if you see NO_TURN_TAG here, no `grade-audit`/`quiz-audit` receipt is available for this text — dispatch the verifier first, or tag the turn.",
        "review close: after writing the Review notes / session note / touched rows, dispatch ONE foreground `review-session-audit` on the exact writes (concepts/transcript/grade_verdicts/written_files/state_rows), then summarize; a PASS/PASS_WITH_FLAGS renders clean and an ISSUES verdict renders with a flags banner (no re-run, cap 2 passes).",
      ].join("\n");
      const scoutNote = scoutNeeded ? "Run the `scout` subagent first for a new lesson.\n" : "";
      const agentNote = run.agentlessDispatch
        ? "A `subagent` call omitted the `agent` field, so it minted no receipt. Always pass `agent: \"<name>\"` (e.g. `tutor-audit`).\n"
        : "";
      run.agentlessDispatch = false;
      const note = verdictNote ? verdictNote + "\n" : "";
      const banner = `⛔ WITHHELD (${codes.join(", ")})\n${scoutNote}${agentNote}${note}${fix}\n`;
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
