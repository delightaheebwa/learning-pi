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
  "viz-audit": "viz_audit",
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
// The review close is delegated to review-clerk once per flow. Re-dispatching it
// re-writes the same Review notes / rows and re-commits.
export const MAX_REVIEW_CLERK_DISPATCHES = 2;
export const MATCH_THRESHOLD = 0.95;
// The emitted text may differ from the verified draft only by tag-strip,
// punctuation, or reordering (all handled by `coverage`). At most this many
// emitted tokens may be absent from the draft, so a large unverified tail can
// never ride on a passed receipt (the old 1.4x ratio allowed an unbounded tail).
export const LENGTH_SLACK_TOKENS = 12;
// A verdict-only grade turn is short (answers + confirmation framing). These
// bound how long it may be before it counts as teaching prose needing a
// fact-check: at least `VERDICT_ONLY_MIN_TOKENS` tokens, and no more than
// `VERDICT_ONLY_MAX_RATIO` of the graded question text.
export const VERDICT_ONLY_MIN_TOKENS = 12;
export const VERDICT_ONLY_MAX_RATIO = 0.5;
export const TURN_TAG_RE = /^\s*\[\[TURN:(claims|quiz|grade|viz|none)\]\]\s*/i;
export const FLOW_TAG_RE = /\[\[FLOW:(teach|resume|review|ingest|solo)\]\]/i;
export const STATE_AUDIT_RE = /(\d+)\s+errors?\b[^\d]*(\d+)\s+warnings?/i;
export const WRITE_TOOLS = new Set(["write", "edit"]);

// Provider-level failure signatures. Two consecutive failures for the same
// verifier/scout surface a one-shot directive to re-dispatch on the alternate
// model (availability fallback, not a model-purity rule).
export const PROVIDER_FAILURE_RE = /(service_overloaded|upstream request failed|rate.?limit|too many requests|overloaded|\b(429|502|503)\b)/i;
export const VERIFIER_FALLBACK_MODEL = "opencode-go/deepseek-v4.1-flash";
export const SCOUT_FALLBACK_MODEL = "opencode-go/muse-spark-1.3-contributor";
export const FALLBACK_AFTER_FAILURES = 2;

export type Flow = "teach" | "resume" | "review" | "ingest" | "solo" | "other";

export interface Receipt {
  gate: string;
  valid: boolean;
  issues: boolean;
  flags?: boolean;
  agrees?: boolean;
  correctVerdict?: string;
  // Per-item grade corrections from a batched `grade-audit` response. Lets the
  // gate surface exactly which answers the verifier disputed on a mismatch.
  gradeItems?: GradeCorrection[];
  renderedContent?: string;
  // The load-bearing claims the generator submitted for a `fact_check` envelope,
  // joined. Lets the gate check that every hard fact in the draft was actually
  // placed before the verifier (see `missingHardFacts`).
  claimsText?: string;
  // Canonical JSON of the verified visualization spec (viz_audit). A viz turn
  // binds only when its emitted fenced spec canonicalizes to this value.
  vizSpec?: string;
  // Content binding so an old PASS can't satisfy a new turn.
  questionsText?: string;
  gradeText?: string;
  // The learner answers the grade-audit graded (one per item). A verdict-only
  // grade turn binds by restating these even when it does not repeat the full
  // question text. See `verdictOnlyGradeBinds`.
  gradeAnswers?: string[];
  auditFiles?: string[];
  envelopeGate?: string;
  // Whether a dispatch envelope was present when this receipt was minted. A
  // present-but-wrong-shape envelope (missing the gate's binding field) must
  // not bind any emission; only an envelope-less async notification may fall
  // back to unbound. See `receiptBinds`.
  hasEnvelope?: boolean;
  // How a `review` receipt was produced: an actual review-gate dispatch, or a
  // verdict marker relayed inside the Clerk's own output (self-attested).
  provenance?: "dispatch" | "clerk";
  // Review-family verdicts must carry an `evidence` list (what was read/checked).
  evidenceMissing?: boolean;
  // Highest issue severity the verifier reported (high/medium/low). Used by the
  // retry-cap rule: while a high/medium issue remains, the gate keeps blocking
  // and never dumps the turn as UNVERIFIED.
  severity?: "high" | "medium" | "low";
  raw: string;
}

const SEVERITY_RANK: Record<string, number> = { high: 3, medium: 2, low: 1 };

/** Highest severity among a verdict object's `issues[]`, or undefined. */
export function maxSeverity(issues: any[]): "high" | "medium" | "low" | undefined {
  let best: "high" | "medium" | "low" | undefined;
  let rank = 0;
  for (const it of issues) {
    const s = typeof it?.severity === "string" ? it.severity.toLowerCase() : "";
    const r = SEVERITY_RANK[s];
    if (r && r > rank) {
      rank = r;
      best = s as "high" | "medium" | "low";
    }
  }
  return best;
}

export function isHighOrMedium(severity: string | undefined): boolean {
  return severity === "high" || severity === "medium";
}

export interface StateAudit {
  errors: number;
  warnings: number;
}

/** One entry of a batched grade-audit response's `items[]`. */
export interface GradeCorrection {
  id?: string | number;
  agrees?: boolean;
  correctVerdict?: string;
  explanation?: string;
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
  // Review-context: the review flow's `review-scout` run (its `REVIEW_SCOUT_DIGEST:`
  // receipt is parsed so a partial/missing digest surfaces a banner, never a withhold).
  reviewScoutCalled: boolean;
  reviewScoutFinished: boolean;
  reviewScoutReceiptSeen: boolean;
  reviewScoutFailedRefs: unknown[];
  // Review-close writer: `review-clerk` owns the durable writes; a completed run
  // arms the review-session audit gate. Capped to stop a re-ingest loop.
  reviewClerkCalled: boolean;
  reviewClerkDispatches: number;
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
  // Same-issue repeat count per turn, keyed by a fingerprint of (gate + issue
  // text). After three repeats the judge is asked whether the issue still
  // applies (the dispute safeguard); the engine performs the release.
  issueBlocks: Record<string, number>;
  // The newest `grade_audit` receipt, kept even after that receipt is consumed.
  // A corrected (agreeing) re-dispatch must supersede an older disagreement, so
  // a stale `agrees:false` cannot block every later grade turn in the flow.
  lastGradeReceipt?: Receipt;
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
    reviewScoutCalled: false,
    reviewScoutFinished: false,
    reviewScoutReceiptSeen: false,
    reviewScoutFailedRefs: [],
    reviewClerkCalled: false,
    reviewClerkDispatches: 0,
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
    issueBlocks: {},
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

/**
 * Decode a JSON string literal whose value is itself JSON text, tolerating a
 * non-string suffix after the closing quote (a model occasionally leaves the
 * envelope's final `}` outside the quotes). Returns the decoded inner string,
 * or undefined when `s` is not a JSON string literal.
 */
function unwrapJsonStringLiteral(s: string): string | undefined {
  if (s[0] !== '"') return undefined;
  let esc = false;
  for (let i = 1; i < s.length; i++) {
    const ch = s[i];
    if (esc) esc = false;
    else if (ch === "\\") esc = true;
    else if (ch === '"') {
      try {
        const v = JSON.parse(s.slice(0, i + 1));
        return typeof v === "string" ? v : undefined;
      } catch {
        return undefined;
      }
    }
  }
  return undefined;
}

/** Try parsing a JSON envelope out of freeform task text (prose + JSON). */
export function parseTask(task: any): any | undefined {
  if (task && typeof task === "object") return task;
  if (typeof task !== "string") return undefined;
  const trimmed = task.trim();
  try {
    const v = JSON.parse(trimmed);
    if (v && typeof v === "object") return v;
    // A JSON string literal whose value is the envelope: some models
    // double-encode the dispatch (the `task` argument literally begins with a
    // quote and carries escaped inner quotes). Unwrap and retry so the
    // receipt still binds its `rendered_content` / `questions_json` instead of
    // dead-ending with FACT_CHECK_MISSING_DRAFT (2026-10-03 session).
    if (typeof v === "string") {
      const inner = parseTask(v);
      if (inner) return inner;
    }
  } catch {
    const unwrapped = unwrapJsonStringLiteral(trimmed);
    if (typeof unwrapped === "string") {
      const inner = parseTask(unwrapped);
      if (inner) return inner;
    }
  }
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
 * Number of tokens in `hay` not accounted for by `needle` (as a multiset).
 * Reordering or punctuation edits leave this near zero; appended prose raises
 * it. Bounds the unverified tail of an emission.
 */
export function extraTokenCount(needle: string, hay: string): number {
  const need = new Map<string, number>();
  for (const t of tokens(needle)) need.set(t, (need.get(t) || 0) + 1);
  let extra = 0;
  for (const t of tokens(hay)) {
    const c = need.get(t) || 0;
    if (c > 0) need.set(t, c - 1);
    else extra++;
  }
  return extra;
}

/**
 * Guard against unverified tails: the emission must reproduce the verified
 * draft (coverage ≥ `MATCH_THRESHOLD`) AND add no more than
 * `LENGTH_SLACK_TOKENS` tokens of its own. Reordering and punctuation are
 * tolerated; an appended, never-verified sentence is not.
 */
export function contentMatches(renderedContent: string, emittedText: string): boolean {
  const nLen = tokens(renderedContent).length;
  if (nLen === 0) return false;
  if (coverage(renderedContent, emittedText) < MATCH_THRESHOLD) return false;
  return extraTokenCount(renderedContent, emittedText) <= LENGTH_SLACK_TOKENS;
}

const YEAR_RE = /^(19|20)\d{2}$/;

/** Normalise a hard fact for containment comparison. */
export function normHardFact(s: string): string {
  return s.toLowerCase().replace(/\s+/g, " ").trim().replace(/[.,;:]+$/, "");
}

/**
 * Deterministic extraction of the *hard*, objectively-checkable facts in a
 * draft: URLs, LaTeX/math expressions, scientific notation, decimals,
 * percentages, and integers of 3+ digits (calendar years excluded). These are
 * exactly the load-bearing facts a `fact_check` envelope's `claims[]` must
 * place before the verifier — a number or formula nobody listed is a number or
 * formula nobody checked. Prose claims are left to the verifier.
 */
export function extractHardFacts(text: string): string[] {
  if (typeof text !== "string" || text.length === 0) return [];
  const out = new Set<string>();
  const add = (s: string) => {
    const n = normHardFact(s);
    if (n.length > 0) out.add(n);
  };
  for (const m of text.matchAll(/https?:\/\/[^\s)\]}>"']+/g)) add(m[0]);
  for (const m of text.matchAll(/\$\$([\s\S]+?)\$\$/g)) add(m[1]);
  for (const m of text.matchAll(/\$([^$\n]+)\$/g)) add(m[1]);
  for (const m of text.matchAll(/\\\[([\s\S]*?)\\\]/g)) add(m[1]);
  for (const m of text.matchAll(/\\\(([\s\S]*?)\\\)/g)) add(m[1]);
  for (const m of text.matchAll(/\b\d+(?:\.\d+)?[eE][+-]?\d+\b/g)) add(m[0]);
  for (const m of text.matchAll(/\b\d+\.\d+\b/g)) add(m[0]);
  for (const m of text.matchAll(/\b\d+(?:\.\d+)?%/g)) add(m[0]);
  for (const m of text.matchAll(/\b\d{3,}\b/g)) {
    if (!YEAR_RE.test(m[0])) add(m[0]);
  }
  return [...out];
}

/**
 * Hard facts present in `draft` but absent from the submitted claims text. A
 * non-empty result means the draft states a number/formula/URL the verifier was
 * never asked about.
 */
export function missingHardFacts(draft: string, claimsText: string | undefined): string[] {
  const facts = extractHardFacts(draft);
  if (facts.length === 0) return [];
  const hay = normHardFact(claimsText || "");
  return facts.filter((f) => !hay.includes(f));
}

/** Quiz/grade binding: the receipt's audited content must overlap the emission. */
export function bindingMatches(bound: string | undefined, emittedText: string): boolean {
  if (!bound || bound.trim().length === 0) return true; // back-compat
  return coverage(bound, emittedText) >= 0.5;
}

/**
 * Quiz/grade binding for a receipt, distinguishing the two reasons its bound
 * text can be empty:
 *
 *   - the receipt was minted with **no envelope at all** (an async completion
 *     notification whose dispatch could not be correlated). Its verdict cannot
 *     be content-bound, so fall back to unbound (back-compat).
 *   - the receipt was minted from a **present but wrong-shape envelope** — a
 *     quiz-audit sent with `items[]` instead of `questions_json`, or a grade
 *     envelope with none of `question`/`learner_answer`/`claimed_verdict`.
 *     There is no binding to check, and accepting it would let one such receipt
 *     authorize every later quiz/grade turn. Refuse to bind.
 */
export function receiptBinds(r: Receipt, emittedText: string): boolean {
  if (r.gate === "grade_audit") {
    const bound = r.gradeText;
    if (bound && bound.trim().length > 0) {
      if (coverage(bound, emittedText) >= 0.5) return true;
      // A grade turn is a verdict presentation, so it rarely repeats the full
      // question text. Bind it when it restates the graded answers and stays a
      // verdict summary rather than teaching prose (the 2026-10-06 loop).
      return verdictOnlyGradeBinds(r, emittedText);
    }
    return !r.hasEnvelope;
  }
  const bound = r.questionsText;
  if (bound && bound.trim().length > 0) return coverage(bound, emittedText) >= 0.5;
  return !r.hasEnvelope;
}

/**
 * A verdict-only grade turn binds on the graded answers alone. Every audited
 * learner answer must be restated (its final token — the letter/number the
 * learner chose — must appear in the emission), and the turn must stay short
 * relative to the graded content so teaching/repair prose does not slip through
 * on an answer letter alone. The repair prose still needs its own fact-check.
 */
export function verdictOnlyGradeBinds(r: Receipt, emittedText: string): boolean {
  const answers = (r.gradeAnswers || []).map((a) => tokens(a)).filter((t) => t.length > 0);
  if (answers.length === 0) return false;
  const hay = new Set(tokens(emittedText));
  for (const a of answers) {
    if (!hay.has(a[a.length - 1])) return false;
  }
  const emittedLen = tokens(emittedText).length;
  const boundLen = tokens(r.gradeText || "").length;
  return emittedLen <= Math.max(VERDICT_ONLY_MIN_TOKENS, boundLen * VERDICT_ONLY_MAX_RATIO);
}

/**
 * Fenced ` ```viz ` blocks in a message; returns the raw inner JSON strings.
 * The viz-mode extension renders these at display time; the gate uses them to
 * bind a `viz_audit` receipt to the exact spec that was audited.
 */
export function extractVizFences(text: string): string[] {
  const out: string[] = [];
  if (typeof text !== "string") return out;
  const re = /```viz[^\n]*\n([\s\S]*?)```/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    const body = m[1].trim();
    if (body.length > 0) out.push(body);
  }
  return out;
}

/** Canonical JSON (recursively sorted keys, insignificant whitespace dropped). */
export function canonicalJson(value: unknown): string {
  const norm = (v: unknown): unknown => {
    if (Array.isArray(v)) return v.map(norm);
    if (v && typeof v === "object") {
      const obj = v as Record<string, unknown>;
      const out: Record<string, unknown> = {};
      for (const key of Object.keys(obj).sort()) {
        if (obj[key] === undefined) continue;
        out[key] = norm(obj[key]);
      }
      return out;
    }
    return v;
  };
  return JSON.stringify(norm(value));
}

/**
 * Viz binding: a `viz_audit` receipt authorizes a `[[TURN:viz]]` only when the
 * emitted fenced spec canonicalizes to the audited spec AND the audit's
 * `rendered_content` covers the emitted text. A present-but-wrong-shape
 * envelope (no spec, or no rendered_content) binds nothing; only an
 * envelope-less async completion falls back to unbound.
 */
export function vizBinds(r: Receipt, emittedText: string): boolean {
  if (!r.hasEnvelope) return true;
  if (!r.vizSpec || !r.renderedContent) return false;
  const fences = extractVizFences(emittedText);
  if (fences.length === 0) return false;
  let match = false;
  for (const f of fences) {
    try {
      if (canonicalJson(JSON.parse(f)) === r.vizSpec) {
        match = true;
        break;
      }
    } catch {
      /* unparseable fence cannot bind */
    }
  }
  if (!match) return false;
  return contentMatches(r.renderedContent, emittedText);
}

/**
 * Whether a receipt names the artifacts it audited.
 *
 * The write gates (tutor-audit, review-session, review-gate) verify files, not
 * emitted text. A receipt whose dispatch envelope was present but omitted its
 * artifact list (`files` / `written_files` / `target_files`) audited nothing
 * identifiable and must not satisfy the gate — otherwise one wrong-shape
 * envelope releases every later handoff/close/ingest summary. An envelope-less
 * async notification has no list to bind against, so it falls back.
 */
export function receiptAuditsArtifacts(r: Receipt): boolean {
  if (!r.hasEnvelope) return true;
  return !!r.auditFiles && r.auditFiles.length > 0;
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
        if (v && typeof v === "object") {
          // Quiz items carry their choices in `options`; include them so the
          // bound text covers the emitted batch (the judge requires 100%
          // coverage of the emitted quiz text, options included).
          const parts = [v.question, v.text, v.claim, v.q, v.prompt].filter((x) => typeof x === "string");
          if (Array.isArray(v.options)) parts.push(...v.options.filter((x: any) => typeof x === "string"));
          return parts.join(" ");
        }
        return "";
      })
      .join("\n");
  }
  return "";
}

/**
 * Paths named by a verifier envelope's artifact list. Different gates name the
 * same idea differently: `files` (tutor-audit, array of strings),
 * `written_files` (review-session, array of {path}), `target_files`
 * (review-gate, array of {path}). Returns the first list found, or undefined
 * when the envelope names none.
 */
export function artifactPaths(envelope: any): string[] | undefined {
  if (!envelope || typeof envelope !== "object") return undefined;
  for (const value of [envelope.files, envelope.written_files, envelope.target_files]) {
    if (!Array.isArray(value)) continue;
    return value
      .map((v: any) => (typeof v === "string" ? v : v && typeof v === "object" && typeof v.path === "string" ? v.path : ""))
      .filter((p: string) => p.length > 0);
  }
  return undefined;
}

/**
 * Bound text for a grade-audit receipt. The flat single-answer shape is
 * `{question, learner_answer, claimed_verdict}`; a batched envelope carries
 * `items:[{question, learner_answer, claimed_verdict}, …]` (one entry per
 * learner answer) and binds the same way.
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

/** The learner answers a grade-audit envelope graded, one entry per item. */
export function gradeAnswersOf(envelope: any): string[] | undefined {
  if (!envelope || typeof envelope !== "object") return undefined;
  if (typeof envelope.learner_answer === "string" && envelope.learner_answer.trim().length > 0) {
    return [envelope.learner_answer];
  }
  if (Array.isArray(envelope.items)) {
    const out = envelope.items
      .map((it: any) => (it && typeof it.learner_answer === "string" ? it.learner_answer : ""))
      .filter((s: string) => s.trim().length > 0);
    if (out.length > 0) return out;
  }
  return undefined;
}

/**
 * Bookkeeping paths a review-gate pass explicitly excludes (state files,
 * session/review/lesson notes, log/index bookkeeping, git/commit metadata).
 * Used only to decide whether a finding that CITES such a location is
 * out-of-scope for the reviewed content.
 */
const BOOKKEEPING_PATH_RE =
  /(mission\.md|curriculum\.md|learning profile|learner history|mistakes\.md|attempts\.json|pending ingest\.json|\bsessions\/|\breviews\/|\blessons\/|log\.md|index\.md|git history|commit message|provenance|staged files|worktree)/i;

/**
 * Out-of-scope review findings: a review that reports ONLY findings whose
 * `location` is an explicit bookkeeping path must not read as blocking issues
 * on the reviewed content (otherwise the tutor re-reviews the same clean page
 * forever). A finding that cites a content location, or gives no location, is
 * NEVER demoted — a content defect that merely mentions a bookkeeping word in
 * its `issue` text still blocks. (The old code fell back to the issue text and
 * blanket-demoted every `low` finding, which could swallow exactly that.)
 */
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
          const loc = typeof it?.location === "string" ? it.location.trim() : "";
          // A finding with no location cannot be proven out-of-scope, and the
          // issue prose is deliberately NOT consulted — only the cited path.
          return loc.length > 0 && BOOKKEEPING_PATH_RE.test(loc);
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
  // Quiz binding: prefer the exact full batch text (`rendered_content`, mirroring
  // the fact-check/viz full-draft rule) so the intro/instructions and options the
  // learner sees are covered too. Fall back to the structured `questions_json`
  // for envelopes that omit it.
  const quizRendered =
    envelope && typeof envelope.rendered_content === "string" && envelope.rendered_content.trim().length > 0
      ? envelope.rendered_content
      : undefined;
  const questionsText = quizRendered || (envelope ? envelopeText(envelope.questions_json || envelope.questions) : undefined);
  // Grade envelope: flat single-answer object, or the batched `items:[{…}]`
  // shape. Both bind so a dropped tag is still recovered from the receipt.
  const gradeText = gradeTextOf(envelope);
  const gradeAnswers = gradeAnswersOf(envelope);
  const auditFiles = artifactPaths(envelope);
  // Review-family verdicts: a PASS without an evidence list is unsubstantiated.
  let evidenceMissing = false;
  if (gate === "review" || gate === "review_session") {
    const obj = parseVerdictObject(text);
    const ev = obj?.evidence;
    const hasEvidence =
      (Array.isArray(ev) && ev.length > 0) || (typeof ev === "string" && ev.trim().length > 0);
    evidenceMissing = !hasEvidence;
  }
  // Batched grade-audit responses carry a per-item `items[]`; keep the disputed
  // entries so a mismatch can name exactly which answers were corrected.
  let gradeItems: GradeCorrection[] | undefined;
  if (gate === "grade_audit") {
    const obj = parseVerdictObject(text);
    if (obj && Array.isArray(obj.items)) {
      gradeItems = obj.items
        .filter((it: any) => it && typeof it === "object")
        .map((it: any): GradeCorrection => ({
          id: typeof it.id === "string" || typeof it.id === "number" ? it.id : undefined,
          agrees: typeof it.agrees === "boolean" ? it.agrees : undefined,
          correctVerdict: typeof it.correct_verdict === "string" ? it.correct_verdict.toLowerCase() : undefined,
          explanation: typeof it.explanation === "string" ? it.explanation : undefined,
        }));
      if (gradeItems && gradeItems.length === 0) gradeItems = undefined;
    }
  }
  const r: Receipt = {
    gate,
    valid: false,
    issues,
    flags: passWithFlags,
    agrees: am ? am[1].toLowerCase() === "true" : undefined,
    correctVerdict: cm ? cm[1].toLowerCase() : undefined,
    gradeItems,
    renderedContent: envelope && typeof envelope.rendered_content === "string" ? envelope.rendered_content : undefined,
    claimsText:
      envelope && Array.isArray(envelope.claims)
        ? envelope.claims
            .map((c: any) => (c && typeof c.claim === "string" ? c.claim : ""))
            .filter(Boolean)
            .join("\n")
        : undefined,
    vizSpec:
      gate === "viz_audit" && envelope && envelope.spec && typeof envelope.spec === "object"
        ? canonicalJson(envelope.spec)
        : undefined,
    questionsText: questionsText || undefined,
    gradeText: gradeText || undefined,
    gradeAnswers,
    auditFiles,
    envelopeGate: envelope && typeof envelope.gate === "string" ? envelope.gate : undefined,
    hasEnvelope: !!envelope && typeof envelope === "object",
    provenance: "dispatch",
    evidenceMissing,
    severity: (() => {
      const vo = parseVerdictObject(text);
      return vo && Array.isArray(vo.issues) ? maxSeverity(vo.issues) : undefined;
    })(),
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

/**
 * Review-scout receipt: the machine-readable `REVIEW_SCOUT_DIGEST: {...}` line a
 * finished review-scout emits. Mirrors `parseScoutReceipt`: a partial/missing
 * digest surfaces a banner on the first review turn, never a withhold.
 */
export function parseReviewScoutReceipt(text: string): { digest?: string; queue: unknown[]; failedRefs: unknown[] } | undefined {
  const idx = text.search(/REVIEW_SCOUT_DIGEST\s*:\s*/i);
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
      queue: Array.isArray(j.queue) ? j.queue : [],
      failedRefs: Array.isArray(j.failed_refs) ? j.failed_refs : [],
    };
  } catch {
    return undefined;
  }
}

/** Claim-level verdict extracted from a verifier's raw JSON, for the ledger. */
export interface ClaimVerdict {
  id?: string | number;
  verdict: string;
  explanation?: string;
  correctedClaim?: string;
}

/** Canonical text: Unicode NFC, whitespace collapsed, trimmed. Case preserved. */
export function canonicalText(s: string): string {
  return (s || "").normalize("NFC").replace(/\s+/g, " ").trim();
}

/**
 * A short deterministic hash (FNV-1a 32-bit) of a draft's canonical text, for
 * fingerprinting what a receipt was bound to in the ledger. Not cryptographic:
 * it identifies a draft for audit, it does not authenticate it.
 */
export function draftHash(text: string): string {
  const s = canonicalText(text);
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0).toString(16).padStart(8, "0");
}

/** Parse the first balanced JSON object in a verifier's raw output. */
function parseAnyVerdictObject(raw: string): any | undefined {
  const trimmed = (raw || "").trim();
  const start = trimmed.indexOf("{");
  if (start >= 0) {
    const blob = extractBalancedJson(trimmed, start);
    if (blob) {
      try {
        const j = JSON.parse(blob);
        if (j && typeof j === "object") return j;
      } catch {
        /* fall through to the verdict-keyed walk */
      }
    }
  }
  return parseVerdictObject(raw);
}

/**
 * Claim-level verdicts from a verifier's raw JSON, for the ledger. A fact-check
 * carries `verdicts[]`, a grade-audit `items[]` (with `correct_verdict`), and
 * the review/quiz family an `issues[]` list. This is what makes a recorded PASS
 * auditable (which claims passed) instead of a tally.
 */
export function claimVerdictsOf(raw: string, gate: string): ClaimVerdict[] {
  const obj = parseAnyVerdictObject(raw);
  if (!obj) return [];
  const out: ClaimVerdict[] = [];
  if (Array.isArray(obj.verdicts)) {
    for (const v of obj.verdicts) {
      if (!v || typeof v !== "object") continue;
      out.push({
        id: v.id,
        verdict: typeof v.verdict === "string" ? v.verdict : "",
        explanation: typeof v.explanation === "string" ? v.explanation : undefined,
        correctedClaim: typeof v.corrected_claim === "string" ? v.corrected_claim : undefined,
      });
    }
  }
  if (Array.isArray(obj.items)) {
    for (const it of obj.items) {
      if (!it || typeof it !== "object") continue;
      out.push({
        id: it.id,
        verdict:
          typeof it.correct_verdict === "string"
            ? it.correct_verdict
            : typeof it.agrees === "boolean"
            ? it.agrees
              ? "agrees"
              : "disagrees"
            : "",
        explanation: typeof it.explanation === "string" ? it.explanation : undefined,
      });
    }
  }
  if (out.length === 0 && Array.isArray(obj.issues)) {
    for (const it of obj.issues) {
      if (it == null) continue;
      if (typeof it === "string") {
        out.push({ verdict: "ISSUE", explanation: it });
        continue;
      }
      if (typeof it !== "object") continue;
      const sev = typeof it.severity === "string" ? it.severity : "";
      const msg = typeof it.problem === "string" ? it.problem : typeof it.issue === "string" ? it.issue : "";
      out.push({ id: it.id, verdict: sev ? `ISSUE:${sev}` : "ISSUE", explanation: msg || undefined });
    }
  }
  return out.slice(0, 50);
}

/** Expected envelope gate per verifier agent (wrong envelope => no receipt). */
export const EXPECTED_ENVELOPE_GATE: Record<string, string> = {
  "fact-check": "fact_check",
  "quiz-audit": "quiz_audit",
  "grade-audit": "grade_audit",
  "review-gate": "review",
  "tutor-audit": "tutor_audit",
  "review-session-audit": "review_session",
  "viz-audit": "viz_audit",
};
