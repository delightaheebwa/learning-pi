/**
 * gate-core/primitives — pure, version-agnostic pieces of the learning gate.
 *
 * THIS FILE MUST NOT IMPORT pi OR PI-SUBAGENTS SHAPES. It operates on plain
 * data (messages, receipts, call refs, tool inputs) and the learning system's
 * own protocol (`[[FLOW:...]]`, `[[TURN:...]]`, verifier envelopes).
 *
 * Everything that knows how pi names an event, how a pi message is shaped, or
 * how pi-subagents reports a subagent result lives in ../pi-adapter. If pi
 * changes a wire shape, this file must not need to change.
 *
 * Invariant IDs referenced in comments are defined in ../../../../../CONTRACT.md.
 */

export const VERIFIER_AGENTS: Record<string, string> = {
  "fact-check": "fact_check",
  "quiz-audit": "quiz_audit",
  "grade-audit": "grade_audit",
  "review-gate": "review",
  "tutor-audit": "tutor_audit",
  "review-session-audit": "review_session",
};

export const MAX_RETRIES = 2;
// A review-gate pass may legitimately run twice (fix cycle). A third pass is
// the runaway loop we observed: repeated re-reviews of out-of-scope state
// bookkeeping. Cap dispatches per flow so it cannot spiral.
export const MAX_REVIEW_GATES = 2;
// Review-session close audit: at most 2 passes per flow (initial + one fix
// cycle). A third is the runaway loop we must avoid.
export const MAX_REVIEW_SESSION_AUDITS = 2;
// The ingest is delegated to clerk once per flow. Re-dispatching it re-ingests
// the same handoff and re-runs the whole review-gate chain.
export const MAX_CLERK_DISPATCHES = 2;
export const MATCH_THRESHOLD = 0.85;
// Emitted text may be slightly longer than the verified draft (tag strip,
// minor edits) but must not carry a large unverified tail.
export const MAX_LENGTH_RATIO = 1.4;
export const LENGTH_SLACK_TOKENS = 30;
export const TURN_TAG_RE = /^\s*\[\[TURN:(claims|quiz|grade|none)\]\]\s*/i;
export const FLOW_TAG_RE = /\[\[FLOW:(teach|resume|review|ingest)\]\]/i;
export const STATE_AUDIT_RE = /(\d+)\s+errors?\b[^\d]*(\d+)\s+warnings?/i;
export const WRITE_TOOLS = new Set(["write", "edit"]);

// Provider-level failure signatures. Two consecutive failures for the same
// verifier/scout surface a one-shot directive to re-dispatch on the alternate
// model (availability fallback, not a model-purity rule).
export const PROVIDER_FAILURE_RE = /(service_overloaded|upstream request failed|rate.?limit|too many requests|overloaded|\b(429|502|503)\b)/i;
export const VERIFIER_FALLBACK_MODEL = "opencode-go/deepseek-v4.1-flash";
export const SCOUT_FALLBACK_MODEL = "opencode-go/muse-spark-1.3-contributor";
export const FALLBACK_AFTER_FAILURES = 2;

export type Flow = "teach" | "resume" | "review" | "ingest" | "other";

export interface Receipt {
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

export interface StateAudit {
  errors: number;
  warnings: number;
}

export interface RunState {
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

export interface CallRef {
  agent: string;
  gate?: string;
  envelope?: any;
  output?: string;
}

export function newRun(flow: Flow): RunState {
  return {
    flow,
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
}

export function textOf(message: any): string {
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

export function hasToolCall(message: any): boolean {
  const c = message?.content;
  if (!Array.isArray(c)) return false;
  return c.some((p: any) => p && typeof p.type === "string" && p.type.toLowerCase().includes("tool"));
}

export function replaceText(message: any, text: string): any {
  if (typeof message.content === "string") return { ...message, content: text };
  return { ...message, content: [{ type: "text", text }] };
}

/** Prepend a banner to the message text while keeping role/content shape. */
export function prependBanner(message: any, banner: string): any {
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
export function stripTag(message: any): any {
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

export function promptText(prompt: any): string {
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
export function detectFlow(prompt: any): Flow {
  const raw = promptText(prompt);
  const tag = raw.match(FLOW_TAG_RE);
  if (tag) return tag[1].toLowerCase() as Flow;
  return "other";
}

/** Try parsing a JSON envelope out of freeform task text (prose + JSON). */
export function parseTask(task: any): any | undefined {
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

export function tokens(s: string): string[] {
  return s
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
}

/** Fraction of `needle`'s word tokens present in `hay`. */
export function coverage(needle: string, hay: string): number {
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
export function contentMatches(renderedContent: string, emittedText: string): boolean {
  const score = coverage(renderedContent, emittedText);
  if (score < MATCH_THRESHOLD) return false;
  const nLen = tokens(renderedContent).length;
  const hLen = tokens(emittedText).length;
  if (nLen === 0) return false;
  return hLen <= nLen * MAX_LENGTH_RATIO + LENGTH_SLACK_TOKENS;
}

/** Quiz/grade binding: the receipt's audited content must overlap the emission. */
export function bindingMatches(bound: string | undefined, emittedText: string): boolean {
  if (!bound || bound.trim().length === 0) return true; // back-compat
  return coverage(bound, emittedText) >= 0.5;
}

/**
 * Near-identical drafts: used to catch a re-dispatch of already-verified text.
 * Deliberately stricter than `contentMatches` so a materially corrected draft
 * (the legitimate post-ISSUES re-verification) is never treated as a duplicate.
 */
export function nearDuplicate(a: string, b: string): boolean {
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

export function parseStateAudit(text: string): StateAudit | undefined {
  const marker = text.match(/STATE_AUDIT_VERDICT\s*:\s*\{"errors"\s*:\s*(\d+)\s*,\s*"warnings"\s*:\s*(\d+)/i);
  if (marker) return { errors: Number(marker[1]), warnings: Number(marker[2]) };
  const m = text.match(STATE_AUDIT_RE);
  if (!m) return undefined;
  return { errors: Number(m[1]), warnings: Number(m[2]) };
}

/** Pull a file path out of a write/edit tool input. */
export function writePath(input: any): string | undefined {
  if (!input || typeof input !== "object") return undefined;
  const p = input.filePath || input.path || input.file_path || input.file || input.filename || input.file_name;
  return typeof p === "string" ? p : undefined;
}

export function normPath(path: string): string {
  return path.replace(/\\/g, "/").toLowerCase();
}

export function isLearningStatePath(path: string): boolean {
  const p = normPath(path);
  return /(^|\/)learning system\//.test(p);
}

/** Review-close artifacts whose write arms the review-session audit gate. */
export function isReviewSessionPath(path: string): boolean {
  const p = normPath(path);
  if (!isLearningStatePath(p)) return false;
  if (/(^|\/)learning system\/(reviews|sessions)\//.test(p)) return true;
  return /(active concepts|mistakes)\.md$/.test(p) || /attempts\.json$/.test(p);
}

// A review-close summary lists per-concept results (mastery + next review),
// unlike a mid-session transition. Used so the review-session gate never holds
// a transition hostage after the session note is written.
const REVIEW_SUMMARY_RE = /(mastery\s+\d|next review|last q type|review\s+[—-]|reviews\/|session\s+[—-]|graduated|feynman:)/i;

export function looksLikeReviewSummary(text: string): boolean {
  return REVIEW_SUMMARY_RE.test(text || "");
}

// The Clerk's ingest review receipt verifies the ingest summary, not every
// message that follows it. Requiring it on arbitrary follow-ups (e.g. "was
// clerk's work checked?") withheld correctly-tagged answers with
// NO_REVIEW_GATE_PASS and dead-ended the turn (2026-09-18 ingest session).
const INGEST_SUMMARY_RE = /(ingest complete|REVIEW_GATE_VERDICT|STATE_AUDIT_VERDICT|state audit|files written|wiki enrichment|concepts touched)/i;

export function looksLikeIngestSummary(text: string): boolean {
  return INGEST_SUMMARY_RE.test(text || "");
}

export function envelopeText(value: any): string {
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
export function gradeTextOf(envelope: any): string | undefined {
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

export function reviewIssuesAllOutOfScope(text: string): boolean {
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

export function parseResult(text: string, gate: string, envelope: any): Receipt {
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
export function extractBalancedJson(text: string, start: number): string | undefined {
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
export function parseVerdictObject(text: string): any | undefined {
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

export function parseClerkReview(text: string): Receipt | undefined {
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
export function parseScoutReceipt(text: string): { digest?: string; rawFiles: string[]; failedRefs: unknown[] } | undefined {
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
export const EXPECTED_ENVELOPE_GATE: Record<string, string> = {
  "fact-check": "fact_check",
  "quiz-audit": "quiz_audit",
  "grade-audit": "grade_audit",
  "review-gate": "review",
  "tutor-audit": "tutor_audit",
  "review-session-audit": "review_session",
};
