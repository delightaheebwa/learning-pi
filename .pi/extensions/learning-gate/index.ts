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
 *   - new lesson -> a `scout` run; its `SCOUT_DIGEST: {...}` receipt is parsed so a
 *     partial/missing digest surfaces `⚠️ SOURCES INCOMPLETE` / `⚠️ SCOUT DIGEST
 *     UNVERIFIED` (banner, never a withhold).
 *   - ingest -> the parent dispatches an independent `review-gate` after the Clerk
 *     returns `CLERK_WRITES`. A PASS renders clean; ISSUES/PASS_WITH_FLAGS render
 *     with a visible `⚠️ REVIEW FLAGS SURFACED` banner (never an endless re-run
 *     loop). A verdict relayed inside the Clerk's own output surfaces `⚠️ INGEST
 *     GATE`; a review verdict with no `evidence` list surfaces `⚠️ REVIEW GATE`.
 *   - provider failures (503/429/overloaded) are counted per agent; after two in a
 *     row the withheld banner offers a one-shot alternate-model fallback directive.
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

// Provider-level failure signatures. Two consecutive failures for the same
// verifier/scout surface a one-shot directive to re-dispatch on the alternate
// model (availability fallback, not a model-purity rule).
const PROVIDER_FAILURE_RE = /(service_overloaded|upstream request failed|rate.?limit|too many requests|overloaded|\b(429|502|503)\b)/i;
const VERIFIER_FALLBACK_MODEL = "opencode-go/deepseek-v4.1-flash";
const SCOUT_FALLBACK_MODEL = "opencode-go/muse-spark-1.3-contributor";
const FALLBACK_AFTER_FAILURES = 2;

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
  // How a `review` receipt was produced: an actual review-gate dispatch, or a
  // verdict marker relayed inside the Clerk's own output (self-attested).
  provenance?: "dispatch" | "clerk";
  // Review-family verdicts must carry an `evidence` list (what was read/checked).
  evidenceMissing?: boolean;
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
  scoutFinished: boolean;
  scoutReceiptSeen: boolean;
  scoutFailedRefs: unknown[];
  clerkCalled: boolean;
  clerkDispatches: number;
  reviewGates: number;
  retries: number;
  // Consecutive provider-failure count per verifier/scout, and whether the
  // one-shot alternate-model fallback directive was already surfaced.
  agentFailures: Record<string, number>;
  agentFallbackUsed: Record<string, boolean>;
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
 * `details.results` (`agent`, `finalOutput`), but it **compacts completed
 * foreground results before the extension sees them**: `task` is rewritten to
 * `[prompt redacted]` and `messages` are dropped (`compactForegroundResult`).
 * The dispatch envelope (which carries `rendered_content` / `questions_json` /
 * grade text) therefore cannot be parsed back out of `r.task`, and a receipt
 * minted without it can never bind — the 2026-09-22 foreground
 * NO_TURN_TAG -> FACT_CHECK_MISSING_DRAFT -> ⛔ UNVERIFIED dead-end.
 *
 * Recover the envelope from the calls captured at `tool_call` time, matched per
 * agent in dispatch order so a parallel same-agent fan-out stays aligned. Fall
 * back to the calls captured from the request input for legacy single/chain
 * shapes and async fan-out notices (which carry no immediate output; the notify
 * fallback mints those receipts later).
 */
function resultCalls(event: any, text: string, pending: CallRef[]): CallRef[] {
  const results = event?.details?.results;
  if (Array.isArray(results) && results.length > 0) {
    const out: CallRef[] = [];
    const pendingByAgent = new Map<string, CallRef[]>();
    for (const c of pending) {
      const q = pendingByAgent.get(c.agent) || [];
      q.push(c);
      pendingByAgent.set(c.agent, q);
    }
    for (const r of results) {
      if (!r || typeof r.agent !== "string") continue;
      const finalOutput = typeof r.finalOutput === "string" ? r.finalOutput : undefined;
      if (!finalOutput) continue; // async/pending child — the notify fallback mints it
      // Consume the queued call for this agent even when `r.task` parsed, so the
      // per-agent queues stay aligned across a multi-result fan-out.
      const queued = pendingByAgent.get(r.agent)?.shift();
      const env = parseTask(r.task) ?? queued?.envelope;
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

/**
 * Near-identical drafts: used to catch a re-dispatch of already-verified text.
 * Deliberately stricter than `contentMatches` so a materially corrected draft
 * (the legitimate post-ISSUES re-verification) is never treated as a duplicate.
 */
function nearDuplicate(a: string, b: string): boolean {
  const at = tokens(a);
  const bt = tokens(b);
  if (at.length === 0 || bt.length === 0) return false;
  const ratio = bt.length / at.length;
  if (ratio < 0.85 || ratio > 1.15) return false;
  const bs = new Set(bt);
  let hit = 0;
  for (const t of at) if (bs.has(t)) hit++;
  return hit / at.length >= 0.95;
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

// The Clerk's ingest review receipt verifies the ingest summary, not every
// message that follows it. Requiring it on arbitrary follow-ups (e.g. "was
// clerk's work checked?") withheld correctly-tagged answers with
// NO_REVIEW_GATE_PASS and dead-ended the turn (2026-09-18 ingest session).
const INGEST_SUMMARY_RE = /(ingest complete|REVIEW_GATE_VERDICT|STATE_AUDIT_VERDICT|state audit|files written|wiki enrichment|concepts touched)/i;

function looksLikeIngestSummary(text: string): boolean {
  return INGEST_SUMMARY_RE.test(text || "");
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
 * Bound text for a grade-audit receipt. Primary shape is the single
 * `{question, learner_answer, claimed_verdict}` object; the `items:[{…}]`
 * array shape is accepted as a fallback so an off-spec envelope still binds.
 */
function gradeTextOf(envelope: any): string | undefined {
  if (!envelope || typeof envelope !== "object") return undefined;
  const one = [envelope.question, envelope.learner_answer, envelope.claimed_verdict].filter(
    (x) => typeof x === "string"
  );
  if (one.length > 0) return one.join("\n");
  if (Array.isArray(envelope.items)) {
    const joined = envelope.items
      .map((it: any) =>
        [it?.question, it?.learner_answer, it?.claimed_verdict].filter((x) => typeof x === "string").join(" ")
      )
      .filter((s: string) => s.length > 0)
      .join("\n");
    if (joined.length > 0) return joined;
  }
  return undefined;
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
  // Grade envelope is a single object, but tolerate the `items:[{…}]` shape
  // some generations emit so the receipt still binds (the malformed envelope
  // otherwise left `gradeText` undefined and mis-inferred the turn as `quiz`).
  const gradeText = gradeTextOf(envelope);
  const auditFiles = envelope && Array.isArray(envelope.files) ? envelope.files.filter((x: any) => typeof x === "string") : undefined;
  // Review-family verdicts: a PASS without an evidence list is unsubstantiated.
  let evidenceMissing = false;
  if (gate === "review" || gate === "review_session") {
    const obj = parseVerdictObject(text);
    const ev = obj?.evidence;
    const hasEvidence =
      (Array.isArray(ev) && ev.length > 0) || (typeof ev === "string" && ev.trim().length > 0);
    evidenceMissing = !hasEvidence;
  }
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
    provenance: "dispatch",
    evidenceMissing,
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

/**
 * Parse the verdict JSON object out of a verifier's final output. Walks back
 * from the `"verdict"` key through `{` candidates until one parses as an object
 * carrying a verdict/issues. Tolerates surrounding prose.
 */
function parseVerdictObject(text: string): any | undefined {
  const v = text.search(/"verdict"\s*:/i);
  if (v < 0) return undefined;
  let idx = v;
  for (let guard = 0; guard < 20; guard++) {
    const start = text.lastIndexOf("{", idx - 1);
    if (start < 0) return undefined;
    const blob = extractBalancedJson(text, start);
    if (blob) {
      try {
        const parsed = JSON.parse(blob);
        if (parsed && typeof parsed === "object" && (parsed.verdict || Array.isArray(parsed.issues))) {
          return parsed;
        }
      } catch {
        /* keep walking back */
      }
    }
    idx = start;
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
  return { gate: "review", valid: (pass || passWithFlags) && !issues, issues, flags: passWithFlags, provenance: "clerk", raw: blob };
}

/**
 * Scout receipt: the machine-readable `SCOUT_DIGEST: {...}` line a finished Scout
 * emits. Dispatch alone used to satisfy the new-lesson gate, so a Scout that
 * errored or fetched nothing still unlocked teaching. Parsing the receipt lets
 * the gate surface a partial/missing digest (banner, never withhold — a weak
 * digest must not dead-end a lesson).
 */
function parseScoutReceipt(text: string): { digest?: string; rawFiles: string[]; failedRefs: unknown[] } | undefined {
  const idx = text.search(/SCOUT_DIGEST\s*:\s*/i);
  if (idx < 0) return undefined;
  const brace = text.indexOf("{", idx);
  if (brace < 0) return undefined;
  const blob = extractBalancedJson(text, brace);
  if (!blob) return undefined;
  try {
    const j = JSON.parse(blob);
    if (!j || typeof j !== "object") return undefined;
    return {
      digest: typeof j.digest === "string" ? j.digest : undefined,
      rawFiles: Array.isArray(j.raw_files) ? j.raw_files.filter((x: any) => typeof x === "string") : [],
      failedRefs: Array.isArray(j.failed_refs) ? j.failed_refs : [],
    };
  } catch {
    return undefined;
  }
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
    scoutFinished: false,
    scoutReceiptSeen: false,
    scoutFailedRefs: [],
    clerkCalled: false,
    clerkDispatches: 0,
    reviewGates: 0,
    retries: 0,
    agentFailures: {},
    agentFallbackUsed: {},
    tutorWrote: false,
    writtenPaths: [],
    reviewSessionWrote: false,
    reviewSessionPaths: [],
    reviewSessionAudits: 0,
    agentlessDispatch: false,
  };

  const pendingCalls = new Map<string, CallRef[]>();
  // Async subagent runs: runId -> the child calls captured at dispatch. The
  // tool result for an async dispatch is only a fan-out notice (no verdict), so
  // the receipt is minted later from the `subagent-notify` completion. Storing
  // the envelope here lets that later receipt carry `rendered_content` /
  // `questions_json` / `question+answer`, which a notification alone lacks.
  // Without it an async `fact-check` can never bind (its whole purpose), which
  // was the 2026-09-21 NO_FACT_CHECK_MATCH -> re-dispatch loop.
  const pendingAsync = new Map<string, { calls: CallRef[]; at: number }>();
  // A run that neither completes nor fails (aborted process, dropped notify)
  // must not leave `pendingAsync` populated forever — that would make the
  // "verification pending" hint lie. Prune well past the 30-min run timeout.
  const PENDING_TTL_MS = 35 * 60 * 1000;
  const prunePendingAsync = () => {
    const now = Date.now();
    for (const [id, p] of pendingAsync) if (now - p.at > PENDING_TTL_MS) pendingAsync.delete(id);
  };

  const reset = (flow: Flow) => {
    run = { flow, receipts: [], scoutCalled: false, scoutFinished: false, scoutReceiptSeen: false, scoutFailedRefs: [], clerkCalled: false, clerkDispatches: 0, reviewGates: 0, retries: 0, agentFailures: {}, agentFallbackUsed: {}, tutorWrote: false, writtenPaths: [], reviewSessionWrote: false, reviewSessionPaths: [], reviewSessionAudits: 0, agentlessDispatch: false };
    pendingCalls.clear();
    pendingAsync.clear();
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
      // Duplicate fact-check guard: re-dispatching a draft that already has a
      // valid (PASS) receipt is the observed "multiple fact-checks in one turn"
      // loop — the Tutor re-verifies clean text after a tag/binding withhold
      // instead of emitting the verified text. Block it and say what to do.
      // A materially corrected draft (post-ISSUES) is not a near-duplicate, so
      // the legitimate fix cycle is unaffected.
      for (const fc of calls.filter((c) => c.agent === "fact-check")) {
        const draft = fc.envelope && typeof fc.envelope.rendered_content === "string" ? fc.envelope.rendered_content : undefined;
        if (!draft) continue;
        const verified = run.receipts.find(
          (r) => r.gate === "fact_check" && r.valid && r.renderedContent && nearDuplicate(r.renderedContent, draft)
        );
        if (verified) {
          return {
            block: true,
            reason:
              "This draft already has a valid fact-check receipt. Do NOT re-dispatch it. " +
              "Emit the verified text unchanged (or, if the previous message was withheld, add the correct " +
              "`[[TURN:claims]]` tag). Re-verification is only for a draft you materially corrected after an ISSUES verdict.",
          };
        }
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
      const text = resultText(event);
      const tool = typeof event?.toolName === "string" ? event.toolName.toLowerCase() : "";
      if (tool === "subagent") {
        const pending = (event?.toolCallId && pendingCalls.get(event.toolCallId)) || [];
        if (event?.toolCallId) pendingCalls.delete(event.toolCallId);
        // Async/dispatched run id: remember the captured envelope so the
        // later completion notification can mint a *bound* receipt.
        const asyncId = typeof event?.details?.asyncId === "string" ? event.details.asyncId : undefined;
        prunePendingAsync();
        if (asyncId && pending.length > 0) pendingAsync.set(asyncId, { calls: pending, at: Date.now() });
        for (const call of resultCalls(event, text, pending)) {
          const output = call.output || text;
          // Provider failures (503/429/overloaded) count toward the one-shot
          // alternate-model fallback directive. They mint no receipt.
          const providerFail = event?.isError === true || PROVIDER_FAILURE_RE.test(output);
          if (providerFail && (VERIFIER_AGENTS[call.agent] || call.agent === "scout")) {
            run.agentFailures[call.agent] = (run.agentFailures[call.agent] || 0) + 1;
          }
          if (event?.isError === true) continue;
          // An async dispatch's tool result is only a fan-out notice — it
          // carries no verdict. Minting here would add an unusable stub that
          // then mislabels later blockers (e.g. an invalid quiz stub reading as
          // QUIZ_AUDIT_ISSUES). The completion notification mints the real one
          // via `pendingAsync` above.
          if (asyncId) continue;
          const gate = VERIFIER_AGENTS[call.agent];
          if (gate) {
            // Right envelope for the right agent — a fact-check envelope on a
            // quiz-audit call (or vice versa) mints nothing.
            const expected = EXPECTED_ENVELOPE_GATE[call.agent];
            if (call.envelope && call.gate && expected && call.gate !== expected) continue;
            const r = parseResult(output, gate, call.envelope);
            addReceipt(r);
            if (r.valid) run.agentFailures[call.agent] = 0;
          }
          if (call.agent === "clerk") {
            const r = parseClerkReview(output);
            if (r) addReceipt(r);
          }
          if (call.agent === "scout") {
            run.scoutFinished = true;
            const sr = parseScoutReceipt(output);
            if (sr) {
              run.scoutReceiptSeen = true;
              run.scoutFailedRefs = sr.failedRefs;
              run.agentFailures["scout"] = 0;
            }
          }
        }
      }
      if (event?.isError !== true) {
        const audit = parseStateAudit(text);
        if (audit) run.stateAudit = audit;
      }
    } catch {
      /* fail open */
    }
  });

  // Async gates that cannot be minted from a bare completion notification
  // (their receipt needs the dispatch envelope) are still minted — just gated
  // on `pendingAsync` correlation succeeding. A `fact_check` with no
  // correlated envelope yields nothing rather than an un-bindable receipt.

  /** Async run id from a completion notification (`.../async-subagent-runs/<id>`). */
  const extractAsyncRunId = (text: string): string | undefined => {
    const m = text.match(/async-subagent-(?:runs|results)(?:\/output-archives)?\/([0-9a-fA-F-]{36})/);
    return m ? m[1] : undefined;
  };

  /**
   * Mint a receipt from an async/detached subagent completion notification.
   *
   * Async subagent results reach the parent as `subagent-notify` custom
   * messages (the dispatch's tool result is only the fan-out notice), so a
   * completed verifier/clerk run can otherwise be invisible to the gate.
   * pi-subagents emits `Background task completed: **agent**` for async runs
   * and `Detached foreground task completed: **agent**` for a foreground run
   * that was later detached — both carry the child's output preview, so accept
   * either. The run id in the notification is correlated with the envelope
   * captured at dispatch (`pendingAsync`) so the receipt binds the audited
   * text, not just the verdict. Idempotent (skip a gate that already has a
   * valid receipt) and fail-open; non-notification text is a no-op.
   */
  const NOTIFY_HEADER_RE = /(?:Background task|Detached foreground task) completed:\s*\*\*([\w-]+)\*\*/i;
  const NOTIFY_FAIL_RE = /(?:Background task|Detached foreground task) failed:\s*\*\*([\w-]+)\*\*/i;
  const mintFromNotification = (text: string): void => {
    if (!text) return;
    // A failed async run sends "Background task failed: **agent**". Clear its
    // pending envelope (so the "verification pending" hint does not lie) and
    // count provider failures, without minting a receipt.
    const failAgent = text.match(NOTIFY_FAIL_RE)?.[1]?.toLowerCase();
    if (failAgent) {
      const runId = extractAsyncRunId(text);
      if (runId) pendingAsync.delete(runId);
      if (VERIFIER_AGENTS[failAgent] || failAgent === "scout") {
        if (PROVIDER_FAILURE_RE.test(text)) run.agentFailures[failAgent] = (run.agentFailures[failAgent] || 0) + 1;
      }
      return;
    }
    if (!NOTIFY_HEADER_RE.test(text)) return;
    const agent = text.match(NOTIFY_HEADER_RE)?.[1]?.toLowerCase();
    if (!agent) return;
    if (agent === "clerk") {
      if (run.receipts.some((r) => r.gate === "review" && r.valid)) return;
      const r = parseClerkReview(text);
      if (r) addReceipt(r);
      return;
    }
    if (agent === "scout") {
      run.scoutFinished = true;
      const sr = parseScoutReceipt(text);
      if (sr) {
        run.scoutReceiptSeen = true;
        run.scoutFailedRefs = sr.failedRefs;
      }
      return;
    }
    const gate = VERIFIER_AGENTS[agent];
    if (!gate) return;
    const runId = extractAsyncRunId(text);
    const entry = runId ? pendingAsync.get(runId) : undefined;
    const calls = entry?.calls;
    if (runId) pendingAsync.delete(runId);
    if (gate === "fact_check") {
      // A fact-check receipt is only usable when bound to its draft
      // (`rendered_content`); the notification does not carry the envelope, so
      // without the dispatch-correlated envelope we mint nothing rather than a
      // receipt that could only ever produce FACT_CHECK_MISSING_DRAFT.
      if (!calls || calls.length === 0) return;
      if (run.receipts.some((r) => r.gate === "fact_check" && r.valid)) return;
      for (const c of calls) addReceipt(parseResult(text, gate, c.envelope));
      return;
    }
    if (run.receipts.some((r) => r.gate === gate && r.valid)) return;
    // With the correlated envelope the receipt binds the audited question /
    // answer / files; without it (legacy notifications) mint unbound as before.
    addReceipt(parseResult(text, gate, calls && calls.length === 1 ? calls[0].envelope : undefined));
  };

  /**
   * Names of verifier agents with an async run still in flight. Surfaced in a
   * withheld banner so a Tutor that dispatched async does not panic and
   * re-dispatch: it should wait for the completion notification, then re-emit.
   */
  const pendingVerifierNote = (): string => {
    prunePendingAsync();
    const agents = new Set<string>();
    for (const { calls } of pendingAsync.values()) {
      for (const c of calls) if (VERIFIER_AGENTS[c.agent]) agents.add(c.agent);
    }
    if (agents.size === 0) return "";
    return (
      `⏳ Verification still in flight (${[...agents].join(", ")}): wait for its completion notification, ` +
      `then re-emit the verified text. Do NOT dispatch the verifier again.\n`
    );
  };

  /** Does this text match a fact-check draft whose async run has not notified? */
  const pendingAsyncDraftMatches = (text: string): boolean => {
    prunePendingAsync();
    for (const { calls } of pendingAsync.values()) {
      for (const c of calls) {
        if (c.agent !== "fact-check") continue;
        const rc = c.envelope && typeof c.envelope.rendered_content === "string" ? c.envelope.rendered_content : undefined;
        if (rc && contentMatches(rc, text)) return true;
      }
    }
    return false;
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

  /**
   * Infer a dropped `claims` tag from a *bound* fact-check receipt.
   *
   * This is not evasion: the emitted text must cover ≥85% of a draft that a
   * fact-check already verified (the exact `rendered_content` binding the
   * claims branch enforces). A transition/summary that doesn't match any
   * verified draft is not inferred, so an unbound message still withholds.
   * This removes the observed dead-end where a long tool-heavy claims turn
   * dropped its tag and the text was withheld despite a valid receipt.
   */
  const inferClaimsTurn = (text: string): boolean => {
    if (run.flow === "ingest" || run.flow === "other") return false;
    return run.receipts.some(
      (r) => r.gate === "fact_check" && r.valid && r.renderedContent && contentMatches(r.renderedContent, text)
    );
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
        ((run.flow === "ingest" && run.clerkCalled && looksLikeIngestSummary(text)) ||
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
      let inferredTag: "grade" | "quiz" | "claims" | undefined;
      if (!tagMatch && !inferredNone) {
        // A bound fact-check receipt is checked first: it is the strongest
        // signal (the emitted text covers a verified draft), and it prevents a
        // stale quiz/grade receipt from mis-inferring the turn type and
        // yielding a misleading `QUIZ_AUDIT_STALE`/`QUIZ_AUDIT_ISSUES` block.
        if (inferClaimsTurn(text)) inferredTag = "claims";
        else inferredTag = inferTaggedTurn(text);
        if (!inferredTag) blockers.push("NO_TURN_TAG");
      }
      const tag = explicitTag || inferredTag || (inferredNone ? "none" : undefined);
      if (run.flow === "ingest") {
        if (run.clerkCalled && looksLikeIngestSummary(text)) {
          // Prefer a verdict from an actual review-gate dispatch over a Clerk-
          // relayed marker when both are present.
          const reviews = run.receipts.filter((r) => r.gate === "review");
          const any = reviews.find((r) => r.provenance === "dispatch") || reviews[0];
          if (any && any.valid) {
            toConsume.push(any);
            if (any.flags || any.issues) {
              surface = "⚠️ REVIEW FLAGS SURFACED — the reviewer returned flags on the ingest output; the content below is shown with those flags outstanding.\n\n";
            }
            if (any.provenance === "clerk") {
              surface +=
                "⚠️ INGEST GATE — the review verdict was relayed by the Clerk, not produced by an independent " +
                "review-gate run. Dispatch a `review-gate` on the Clerk's wiki writes to verify it independently.\n\n";
            }
            if (any.evidenceMissing) {
              surface +=
                "⚠️ REVIEW GATE — the review verdict carries no `evidence` list (what it read/checked); " +
                "treat the pass as unsubstantiated.\n\n";
            }
          } else if (any) {
            // Reviewer found issues: surface, never hard-block (this is what caused the
            // previous endless pass-3/4/… loop). Defer consumption to the
            // success path so a later blocker doesn't lose the receipt.
            toConsume.push(any);
            surface = "⚠️ REVIEW FLAGS SURFACED — high/medium review issues were reported on the ingest output; the content below is shown with those flags outstanding.\n\n";
            if (any.provenance === "clerk") {
              surface +=
                "⚠️ INGEST GATE — the review verdict was relayed by the Clerk, not produced by an independent " +
                "review-gate run. Dispatch a `review-gate` on the Clerk's wiki writes to verify it independently.\n\n";
            }
            if (any.evidenceMissing) {
              surface +=
                "⚠️ REVIEW GATE — the review verdict carries no `evidence` list (what it read/checked); " +
                "treat the result as unsubstantiated.\n\n";
            }
          } else {
            blockers.push("NO_REVIEW_GATE_PASS");
          }
        }
      } else if (tag === "claims") {
        if (run.flow === "teach" && !run.scoutCalled) scoutNeeded = true;
        // Scout receipt: dispatch alone used to satisfy the new-lesson gate. A
        // finished Scout with a partial/missing digest surfaces here as a banner
        // (never a withhold) so the Tutor teaches around the gaps visibly.
        if (run.flow === "teach" && run.scoutCalled) {
          if (run.scoutReceiptSeen && run.scoutFailedRefs.length > 0) {
            surface += `⚠️ SOURCES INCOMPLETE — Scout could not fetch ${run.scoutFailedRefs.length} source(s); teaching proceeds around the gaps.\n\n`;
            run.scoutFailedRefs = [];
          } else if (run.scoutFinished && !run.scoutReceiptSeen) {
            surface += `⚠️ SCOUT DIGEST UNVERIFIED — Scout finished without a parseable \`SCOUT_DIGEST:\` receipt; teaching from whatever context it produced.\n\n`;
            run.scoutFinished = false;
          }
        }
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
          const issuesReceipt = run.receipts.some((r) => r.gate === "quiz_audit" && r.issues);
          blockers.push(anyBound ? "QUIZ_AUDIT_STALE" : issuesReceipt ? "QUIZ_AUDIT_ISSUES" : "NO_QUIZ_AUDIT_PASS");
        }
      } else if (tag === "grade") {
        const candidates = run.receipts.filter(
          (r) => r.gate === "grade_audit" && r.valid && bindingMatches(r.gradeText, text)
        );
        const g = candidates[0];
        if (g) toConsume.push(g);
        else {
          const bad = run.receipts.find((r) => r.gate === "grade_audit" && r.agrees === false);
          if (bad) {
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
        // Evasion guard for the exact 2026-09-21 loop: teaching content tagged
        // `[[TURN:none]]` while its fact-check is still running (no receipt
        // yet). Without this, `none` renders freely and the claims gate is
        // bypassed. Matching the pending draft is decisive — a genuine
        // transition does not quote the teaching draft.
        else if (pendingAsyncDraftMatches(text)) blockers.push("FACT_CHECK_PENDING");
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
          if (audit.evidenceMissing) {
            surface +=
              "⚠️ REVIEW SESSION GATE — the audit verdict carries no `evidence` list (what it read/checked); " +
              "treat the pass as unsubstantiated.\n\n";
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

      // One-shot availability fallback: after repeated provider failures the
      // alternate model is offered (never forced). Directive fires once per
      // agent per flow.
      const fallbackLines: string[] = [];
      for (const [agent, count] of Object.entries(run.agentFailures)) {
        if (count >= FALLBACK_AFTER_FAILURES && !run.agentFallbackUsed[agent]) {
          const fb = agent === "scout" ? SCOUT_FALLBACK_MODEL : VERIFIER_AGENTS[agent] ? VERIFIER_FALLBACK_MODEL : undefined;
          if (fb) {
            fallbackLines.push(`\`${agent}\` failed ${count}× in a row — re-dispatch it once with \`model: "${fb}"\` before giving up.`);
            run.agentFallbackUsed[agent] = true;
          }
        }
      }
      const fallbackNote = fallbackLines.length ? fallbackLines.join("\n") + "\n" : "";

      if (run.retries > MAX_RETRIES) {
        run.retries = 0;
        const banner = `⛔ UNVERIFIED — gate retries exhausted (${codes.join(", ")}). The content below was not verified.\n${fallbackNote}\n`;
        return { message: prependBanner(replaceText(message, text), banner) };
      }

      const fix = [
        "Start every message with a turn tag: `[[TURN:claims]]`, `[[TURN:quiz]]`, `[[TURN:grade]]`, or `[[TURN:none]]`.",
        "claims: send your exact draft as `rendered_content` with its claims, then emit the verified text unchanged. A `[[TURN:claims]]` tag is also inferred automatically when your text matches an already-verified `rendered_content`, so if a message is withheld here, just re-emit the verified draft with its tag.",
        "quiz: send the exact batch; fix high/medium issues (max 2 cycles), then accept PASS_WITH_FLAGS instead of looping.",
        "grade: send question + raw learner answer + claimed verdict as ONE object; use the verifier's `correct_verdict`.",
        "do not re-verify: if a fact-check receipt already covers your draft, emit that draft unchanged — re-dispatching the same claims is blocked and only for a materially corrected draft after an ISSUES verdict.",
        "in flight: if a verifier is still running, wait for its completion notification, then re-emit — do NOT re-dispatch and do NOT downgrade the tag.",
        "do not tag teaching content `[[TURN:none]]` to bypass the gate: a `none` message matching a verified or in-flight `fact-check` draft is withheld (TURN_TAG_MISMATCH / FACT_CHECK_PENDING).",
        "write: write lesson/session/record/Pending Ingest files only at a pause or lesson-end handoff, then dispatch a `tutor-audit` on that batch and fold its verdict before the summary.",
        "ingest: after Clerk returns its `CLERK_WRITES` receipt, dispatch ONE independent `review-gate` on the wiki pages it wrote (the Clerk does not gate itself); fold its verdict into the summary.",
        "grade/quiz: a dropped tag is accepted when a verifier receipt for that turn is pending; if you see NO_TURN_TAG here, no `grade-audit`/`quiz-audit` receipt is available for this text — dispatch the verifier first, or tag the turn.",
        "review close: after writing the Review notes / session note / touched rows, dispatch ONE foreground `review-session-audit` on the exact writes (concepts/transcript/grade_verdicts/written_files/state_rows), then summarize; a PASS/PASS_WITH_FLAGS renders clean and an ISSUES verdict renders with a flags banner (no re-run, cap 2 passes).",
        "verifier failed on provider errors (503/429/timeout): retry once, then re-dispatch the SAME verifier with an explicit `model:` from the alternate set (verifiers → deepseek-v4.1-flash, scout → muse-spark-1.3-contributor); if it still fails, proceed and surface what is unverified.",
      ].join("\n");
      const scoutNote = scoutNeeded ? "Run the `scout` subagent first for a new lesson.\n" : "";
      const agentNote = run.agentlessDispatch
        ? "A `subagent` call omitted the `agent` field, so it minted no receipt. Always pass `agent: \"<name>\"` (e.g. `tutor-audit`).\n"
        : "";
      run.agentlessDispatch = false;
      const note = verdictNote ? verdictNote + "\n" : "";
      const pendingNote = pendingVerifierNote();
      const banner = `⛔ WITHHELD (${codes.join(", ")})\n${scoutNote}${agentNote}${pendingNote}${fallbackNote}${note}${fix}\n`;
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
