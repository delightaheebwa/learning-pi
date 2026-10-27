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
  "scout-audit": "scout_audit",
  "graph-audit": "graph_audit",
  "ui-audit": "ui_audit",
};

export const MAX_RETRIES = 2;
// Verifier re-checks are NOT capped: review-gate, review-session-audit, and
// scout-audit may be re-dispatched as many times as needed until the verifier
// returns zero issues (any severity). A repeated identical issue is still
// bounded by the dispute safeguard (three identical blocks escalate to the judge).
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
export const TURN_TAG_RE = /^\s*\[\[TURN:(claims|quiz|grade|ui|none)\]\]\s*/i;
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
  // The kind this teach/resume claims turn declared (`plan`, `triage`,
  // `attack`, `hint`, `autopsy`, `answer`, `repair`, `grade_feedback`, `idea`).
  // A triage/attack turn must carry its shape fields, an `autopsy` must carry
  // one reasoning `step`, an `idea` must carry a `foundation` block; other
  // kinds need neither.
  turnKind?: string;
  // Triage rows supplied on a `turn_kind:"triage"` turn.
  triage?: TriageRow[];
  // The single attack subtype supplied on a `turn_kind:"attack"` turn.
  attack?: string;
  // The four-beat theoretical foundation a new idea must ship with (see
  // `foundationGaps`). Each beat is an excerpt of prose actually present in the
  // verified draft.
  foundation?: FoundationBlock;
  // The single reasoning step an `autopsy` patch ships (see `stepGaps`): one
  // new fact resting on something the learner already holds, plus its check.
  step?: StepBlock;
  // Repair mode (see `repairGaps`): the gap being repaired, its diagnosed miss
  // class and repair tactic, and — once the learner has passed a fresh-surface
  // check — the receipt that closes the repair before the attack battery resumes.
  repair?: RepairBlock;
  // Per-item grade envelopes (question / claimed verdict / qtype), used to bind
  // a repair's fresh-surface check to a graded pass without trusting prose.
  gradeClaims?: GradeClaim[];
  // Canonical JSON of the verified OpenUI Lang payload (ui_audit). A `[[TURN:ui]]`
  // turn binds only when its emitted ```openui fence canonicalizes to this value.
  uiPayload?: string;
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
  // The graph record ids a `graph_audit` envelope names. The ingest close
  // requires the audit to cover every id the Clerk wrote, so an audit of one
  // node cannot release a merge of six.
  graphIds?: string[];
  // Highest issue severity the verifier reported (high/medium/low). Retained for
  // the ledger only: severity no longer gates — ANY issue (any severity) keeps
  // blocking and never dumps the turn as UNVERIFIED.
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
  // Graph record ids the Clerk's `CLERK_WRITES.graph` receipt says it wrote
  // (created + linked nodes/chains). Non-empty arms the ingest close's graph
  // audit gate: the summary needs an independent `graph-audit` over these ids.
  clerkGraphIds: string[];
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
  // The learner's latest message text, captured at agent start. The script-drift
  // guard uses it to tell the learner's language from a drift-prone model's, so
  // a learner who writes in CJK keeps getting CJK.
  learnerText?: string;
  // Repair mode (G-repair-complete): an open teaching pass, set when a
  // `turn_kind:"repair"` turn with status `teaching` reaches the learner.
  // An attack turn is withheld (NO_REPAIR_RECEIPT) until a valid `done` turn
  // closes it, so the battery never resumes on an unrepaired gap.
  openRepair?: { gap: string };
  // Fresh-surface repair checks the learner passed (from agreeing grade-audit
  // receipts whose claimed verdict was `pass`). A repair `done` turn must name
  // one of these questions verbatim, so "repaired" is a graded fact, not the
  // Tutor's assertion.
  repairCheckPasses: { question: string }[];
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
    clerkGraphIds: [],
    reviewScoutCalled: false,
    reviewScoutFinished: false,
    reviewScoutReceiptSeen: false,
    reviewScoutFailedRefs: [],
    reviewClerkCalled: false,
    reviewClerkDispatches: 0,
    retries: 0,
    agentFailures: {},
    agentFallbackUsed: {},
    tutorWrote: false,
    writtenPaths: [],
    reviewSessionWrote: false,
    reviewSessionPaths: [],
    agentlessDispatch: false,
    issueBlocks: {},
    repairCheckPasses: [],
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

// ---------------------------------------------------------------------------
// Script-drift guard (language).
//
// A drift-prone model occasionally emits a learner-facing turn in a language the
// learner is not using — e.g. a fluent Chinese translation of an English quiz,
// which it then explains away as a "rendering glitch" (the 2026-10-12 t-SNE
// exit-ticket incident). Such a turn is not the verified draft, the learner
// cannot read it, and its receipt no longer binds, so the gate withholds it.
//
// Only CJK ideographs / kana / Hangul are counted. Latin, Greek, and Cyrillic
// are deliberately excluded: math notation and proper nouns legitimately mix
// them into English prose. A turn is also exempt when the learner's own latest
// text or a draft already uses the script (a learner writing Chinese must keep
// getting Chinese).
const CJK_RE = /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7a3]/g;
export const CJK_MIN_CHARS = 12;
// A terse CJK learner ("你好", "好的") must exempt the tutor, so the reference
// threshold is deliberately low; the emission threshold stays high enough that a
// stray CJK word in English prose is never flagged.
export const CJK_MIN_REF_CHARS = 2;

/** Number of CJK/kana/Hangul characters in `s`. */
export function cjkCount(s: string): number {
  const m = (s || "").match(CJK_RE);
  return m ? m.length : 0;
}

/** Fraction of `s`'s letters that are CJK/kana/Hangul. */
export function cjkLetterRatio(s: string): number {
  const letters = (s || "").match(/\p{L}/gu);
  if (!letters || letters.length === 0) return 0;
  return cjkCount(s) / letters.length;
}

/**
 * True when `text` is written predominantly in CJK/kana/Hangul while none of
 * `references` (the learner's latest message and the submitted/verified drafts)
 * use that script. The caller withholds the turn rather than let it render.
 */
export function scriptDrift(text: string, references: Array<string | undefined>): boolean {
  if (cjkCount(text) < CJK_MIN_CHARS) return false;
  if (cjkLetterRatio(text) < 0.5) return false;
  for (const r of references) if (r && cjkCount(r) >= CJK_MIN_REF_CHARS) return false;
  return true;
}

/** Whether `s` looks like a verifier/subagent GATE envelope rather than prose. */
export function looksLikeGateEnvelope(s: string): boolean {
  return /GATE:\s*\w+/.test(s) || /"gate"\s*:/.test(s);
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

const YEAR_RE = /^(1[0-9]\d{2}|20\d{2})$/;

/** Normalise a hard fact for containment comparison. */
export function normHardFact(s: string): string {
  return s.toLowerCase().replace(/\s+/g, " ").trim().replace(/[.,;:]+$/, "");
}

/**
 * Normalise a hard fact for *notation-insensitive* containment: the same fact
 * written as LaTeX and as plain prose must compare equal. The generator submits
 * claims in prose ("Per(P_i) = 2^(H(P_i))") while the draft may render the same
 * fact as math ("\mathrm{Per}(P_i) = 2^{H(P_i)}"); a byte comparison withheld
 * such a turn as CLAIMS_INCOMPLETE even though the verifier had checked it (the
 * 2026-10-09 t-SNE perplexity loop). Symbol macros whose prose spelling is not
 * the macro name are translated first ("\propto" vs "proportional to" — the
 * 2026-10-12 t-SNE kernel loop), then LaTeX font/formatting wrappers and
 * delimiters are stripped and whitespace is dropped only around math operators
 * so `1/(1+d_{ij}^2)` equals `1/(1 + d_{ij}^2)`. Inter-word whitespace between
 * ordinary words is preserved so `factPresent`'s token-boundary test still keeps
 * numeric containment exact ("200" does not match inside "2000").
 */
export function normMathFact(s: string): string {
  return (
    normHardFact(s)
      // Symbol macros whose plain-prose spelling is not the macro name. Without
      // this the generic backslash strip below leaves the bare token "propto"
      // and a correctly-claimed formula is withheld as CLAIMS_INCOMPLETE. The
      // Unicode spellings of the same symbols normalise identically.
      .replace(/\\(?:propto|varpropto)(?![a-zA-Z])|∝/g, " proportional to ")
      .replace(/\\(?:approx|sim|simeq|cong)(?![a-zA-Z])|≈/g, " approximately ")
      .replace(/\\(?:times|cross)(?![a-zA-Z])|×/g, " x ")
      .replace(/\\(?:cdot|ast)(?![a-zA-Z])|·/g, " ")
      .replace(/\\(?:to|rightarrow|longrightarrow|Rightarrow|implies)(?![a-zA-Z])|→/g, " to ")
      .replace(/\\(?:le|leq|leqslant)(?![a-zA-Z])|≤/g, " <= ")
      .replace(/\\(?:ge|geq|geqslant)(?![a-zA-Z])|≥/g, " >= ")
      .replace(/\\(?:ne|neq)(?![a-zA-Z])|≠/g, " != ")
      .replace(/\\(?:pm|mp)(?![a-zA-Z])|±/g, " +/- ")
      .replace(/\\(?:infty)(?![a-zA-Z])|∞/g, " infinity ")
      .replace(
        /\\(?:mathrm|mathbf|mathit|mathsf|mathtt|operatorname|boldsymbol|vec|hat|bar|tilde|left|right|big|Big|bigg|Bigg)\b/g,
        " "
      )
      .replace(/\\/g, "")
      .replace(/[{}\[\]()]/g, "")
      .replace(/\s*([+\-=/^_*<>!])\s*/g, "$1")
      .replace(/\s+/g, " ")
      .trim()
  );
}

/**
 * Deterministic extraction of the *hard*, objectively-checkable facts in a
 * draft: URLs, LaTeX/math expressions, scientific notation, decimals,
 * percentages, and integers of 3+ digits (calendar years excluded). These are
 * exactly the load-bearing facts a `fact_check` envelope's `claims[]` must
 * place before the verifier — a number or formula nobody listed is a number or
 * formula nobody checked. Prose claims, and 1–2 digit integers (list markers,
 * small counts), are left to the verifier.
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
    const i = m.index ?? 0;
    const before = text[i - 1];
    const after = text[i + m[0].length];
    // Skip a fragment that is part of a comma-grouped number ("3,000" would
    // otherwise contribute a bogus "000" hard fact).
    if (before === "," && /\d/.test(text[i - 2] || "")) continue;
    if (after === "," && /\d/.test(text[i + m[0].length + 1] || "")) continue;
    if (!YEAR_RE.test(m[0])) add(m[0]);
  }
  return [...out];
}

/**
 * True when `fact` occurs in `hay` on its own token boundaries. A plain
 * `includes` is unsafe: the fact "200" would be considered present inside
 * "2000", letting a wrong number pass as verified.
 */
function factPresent(fact: string, hay: string): boolean {
  // An empty needle has no token boundary to anchor on: `indexOf("")` clamps to
  // `hay.length` forever and the boundary test can never pass when the last
  // character is wordish, so the scan below would spin. A content-free fact
  // (e.g. `\cdot`/`\ast`, which normalise to "") is trivially "present".
  if (fact.length === 0) return true;
  const wordish = (c: string) => /[0-9a-z.]/.test(c);
  let from = 0;
  while (true) {
    const idx = hay.indexOf(fact, from);
    if (idx < 0) return false;
    const before = idx > 0 ? hay[idx - 1] : "";
    const after = idx + fact.length < hay.length ? hay[idx + fact.length] : "";
    if (!wordish(before) && !wordish(after)) return true;
    from = idx + 1;
  }
}

/**
 * Hard facts present in `draft` but absent from the submitted claims text. A
 * non-empty result means the draft states a number/formula/URL the verifier was
 * never asked about.
 */
export function missingHardFacts(draft: string, claimsText: string | undefined): string[] {
  const facts = extractHardFacts(draft);
  if (facts.length === 0) return [];
  const hay = normMathFact(claimsText || "");
  return facts.filter((f) => !factPresent(normMathFact(f), hay));
}

/**
 * The theoretical-foundation beat a new idea must ship with: not just the
 * "what" but `problem` (what it is for), `where_from` (derivation or
 * mechanism), `conditions` (assumptions/boundary cases), and `contrast` (the
 * nearest-neighbour distinction). Mirrors the Feynman rubric — that rubric is
 * used to *grade* the learner; this is the teaching-side twin.
 */
export interface FoundationBlock {
  problem?: string;
  where_from?: string;
  conditions?: string;
  contrast?: string;
}

/**
 * The single reasoning step an `autopsy` patch may install. A step is one new
 * fact attached to something the learner already holds (`rests_on`) plus the
 * check that verifies it landed (`check`). More than one step is a lecture, not
 * a patch; the Tutor must pause for the learner's check before the next step.
 */
export interface StepBlock {
  index?: number;
  total?: number;
  fact?: string;
  rests_on?: string;
  check?: string;
}

/**
 * Repair mode: after a graded miss survives the hint ladder (or at once for a
 * `missing`/structural gap), the Tutor teaches the diagnosed gap one checked
 * step at a time. The receipt closes it: a fresh-surface check the learner
 * passed plus the learner's own-words restatement.
 */
export interface RepairBlock {
  /** The triage row / attacked claim this repair is bound to. */
  gap?: string;
  /** The diagnosed miss class (same taxonomy as grade-audit). */
  miss_class?: string;
  /** The repair tactic chosen for that miss class. */
  tactic?: string;
  /** `teaching` (a step) or `done` (the receipt). */
  status?: string;
  /** Exactly one reasoning step on a `teaching` turn. */
  step?: StepBlock;
  /** The fresh-surface question the learner answered and passed (`done`). */
  fresh_surface_check?: string;
  /** The learner's own-words restatement, verbatim (`done`). */
  learner_restate?: string;
}

/** Miss classes that select a repair tactic (the grade-audit taxonomy). */
export const REPAIR_MISS_CLASSES = new Set([
  "cue",
  "discrimination",
  "execution",
  "careless",
  "structural",
]);

/**
 * Repair tactics, one per diagnosed miss class (plus the full pass for a gap
 * the learner never learned). The Tutor selects the tactic from the diagnosis,
 * never from a free-form catalogue.
 */
export const REPAIR_TACTICS = new Set([
  "source_return",
  "retrieval_cue",
  "contrasting_pair",
  "worked_step",
  "push_down",
  "full_teach",
]);

/** One item of a batched grade envelope, kept for repair-check binding. */
export interface GradeClaim {
  concept?: string;
  question?: string;
  claimedVerdict?: string;
  qtype?: string;
}

export const FOUNDATION_FIELDS = ["problem", "where_from", "conditions", "contrast"] as const;

/**
 * A foundation beat is an excerpt of the emitted turn, so token coverage
 * tolerates markdown/punctuation differences without accepting a beat whose
 * prose is not actually in the draft. (A claim stated in the envelope but never
 * emitted is the "sounds complete" failure in reverse.)
 */
export const FOUNDATION_BIND_THRESHOLD = 0.6;

/** turn_kinds that do NOT introduce a new idea and need no foundation beat. */
const NON_IDEA_TURN_KINDS = new Set([
  "answer",
  "repair",
  "hint",
  "plan",
  "triage",
  "attack",
  "autopsy",
  "grade_feedback",
]);

/** The interrogation turn kinds a teach/resume claims turn may declare. */
export const VALID_TURN_KINDS = new Set([...NON_IDEA_TURN_KINDS, "idea"]);

/** The attack menu. One attack per turn is enforced by the shape check. */
export const ATTACK_KINDS = new Set([
  "mechanism",
  "counterexample",
  "perturbation",
  "source_clash",
  "sabotage",
  "synthesis",
]);

export interface TriageRow {
  item?: string;
  bucket?: string;
  evidence?: string;
  // Dependency ordering for the attack plan: the other triage rows whose
  // load-bearing claim must be solid before this row may be attacked. Optional;
  // a row with no `requires` is a root of the attack tree.
  requires?: string[];
  // True when the row sits on the shortest dependency path to the model's goal.
  // Off-path holes are recorded but not attacked this session.
  on_path?: boolean;
}

/**
 * Shape check for a `turn_kind:"triage"` turn: every row names an item and a
 * valid bucket, and every non-solid row carries grounding (the learner's quote
 * for `suspect`, the source citation for `missing`). The optional dependency
 * ordering (`requires`, `on_path`) must name real rows and be acyclic, so the
 * attack plan is traversable. A row with no grounding is the `UNGROUNDED_HOLE`
 * failure, caught deterministically before the verifier.
 */
function triageGaps(triage: TriageRow[] | undefined): string[] {
  if (!Array.isArray(triage) || triage.length === 0) return ["triage (missing)"];
  const gaps: string[] = [];
  const names = new Set<string>();
  const seen = new Set<string>();
  triage.forEach((row, i) => {
    if (!row || typeof row !== "object") return;
    const item = typeof row.item === "string" ? row.item.trim() : "";
    if (!item) return;
    if (seen.has(item)) {
      gaps.push(`triage row ${i + 1} (duplicate item '${item}')`);
    }
    seen.add(item);
    names.add(item);
  });
  const edges = new Map<string, string[]>();
  triage.forEach((row, i) => {
    const n = i + 1;
    if (!row || typeof row !== "object") {
      gaps.push(`triage row ${n} (not an object)`);
      return;
    }
    const item = typeof row.item === "string" ? row.item.trim() : "";
    const bucket = typeof row.bucket === "string" ? row.bucket.trim().toLowerCase() : "";
    const evidence = typeof row.evidence === "string" ? row.evidence.trim() : "";
    if (!item) gaps.push(`triage row ${n} (no item)`);
    if (!["solid", "missing", "suspect"].includes(bucket)) {
      gaps.push(`triage row ${n} (bucket ${bucket ? `'${bucket}'` : "missing"} is not solid|missing|suspect)`);
    } else if (bucket !== "solid" && !evidence) {
      gaps.push(`triage row ${n} (${bucket} row has no learner quote or source citation)`);
    }
    if (row.on_path !== undefined && typeof row.on_path !== "boolean") {
      gaps.push(`triage row ${n} (on_path must be true or false)`);
    }
    if (row.requires !== undefined) {
      if (!Array.isArray(row.requires)) {
        gaps.push(`triage row ${n} (requires must be an array of row items)`);
      } else {
        const refs: string[] = [];
        for (const raw of row.requires) {
          const ref = typeof raw === "string" ? raw.trim() : "";
          if (!ref) {
            gaps.push(`triage row ${n} (requires has an empty entry)`);
          } else if (ref === item) {
            gaps.push(`triage row ${n} (requires itself)`);
          } else if (!names.has(ref)) {
            gaps.push(`triage row ${n} (requires unknown item '${ref}')`);
          } else {
            refs.push(ref);
          }
        }
        if (item && refs.length > 0) edges.set(item, refs);
      }
    }
  });
  // A cycle makes "attack the prerequisites first" unsatisfiable.
  const state = new Map<string, number>();
  const visit = (name: string): boolean => {
    const s = state.get(name) || 0;
    if (s === 1) return true;
    if (s === 2) return false;
    state.set(name, 1);
    for (const next of edges.get(name) || []) {
      if (visit(next)) return true;
    }
    state.set(name, 2);
    return false;
  };
  for (const name of names) {
    if (visit(name)) {
      gaps.push("triage (dependency cycle in requires)");
      break;
    }
  }
  return gaps;
}

/**
 * Shape check for an `autopsy` patch: exactly one reasoning step, bound into
 * the draft, with the check that verifies it. The step must rest on something
 * the learner already holds; a patch that installs several facts at once is a
 * lecture and is withheld.
 */
function stepGaps(renderedContent: string | undefined, step: StepBlock | undefined): string[] {
  if (!step || typeof step !== "object" || Array.isArray(step)) return ["step (missing)"];
  const gaps: string[] = [];
  const index = typeof step.index === "number" ? step.index : NaN;
  const total = typeof step.total === "number" ? step.total : NaN;
  if (!Number.isInteger(index) || index < 1) gaps.push("step.index (missing or not a positive integer)");
  if (!Number.isInteger(total) || total < 1) gaps.push("step.total (missing or not a positive integer)");
  if (Number.isInteger(index) && Number.isInteger(total) && index > total) {
    gaps.push("step.index (greater than step.total)");
  }
  const draft = renderedContent || "";
  const fact = typeof step.fact === "string" ? step.fact.trim() : "";
  if (!fact) gaps.push("step.fact (missing)");
  else if (coverage(fact, draft) < FOUNDATION_BIND_THRESHOLD) gaps.push("step.fact (not in the draft)");
  const restsOn = typeof step.rests_on === "string" ? step.rests_on.trim() : "";
  if (!restsOn) gaps.push("step.rests_on (missing)");
  const check = typeof step.check === "string" ? step.check.trim() : "";
  if (!check) gaps.push("step.check (missing)");
  else if (coverage(check, draft) < FOUNDATION_BIND_THRESHOLD) gaps.push("step.check (not in the draft)");
  return gaps;
}

/** Shape check for a `turn_kind:"attack"` turn: exactly one known subtype. */
function attackGaps(attack: string | undefined): string[] {
  const kind = typeof attack === "string" ? attack.trim().toLowerCase() : "";
  if (!kind) return ["attack (missing)"];
  if (kind.includes(",") || kind.includes("|")) return [`attack '${kind}' (declare exactly one subtype)`];
  if (!ATTACK_KINDS.has(kind)) return [`attack '${kind}' (unknown subtype)`];
  return [];
}

/**
 * Deterministic shape check for a teach/resume `claims` turn.
 *
 *   - no/invalid `turn_kind`             -> ["turn_kind"]
 *   - `triage`                           -> every row valid, grounded, acyclic
 *   - `attack`                           -> exactly one known subtype
 *   - `autopsy`                          -> exactly one bound reasoning step
 *   - answer/repair/hint/...             -> [] (no shape required)
 *   - `turn_kind: "idea"`                -> every foundation field non-empty AND
 *     its prose bound into the verified draft
 */
export function foundationGaps(
  renderedContent: string | undefined,
  turnKind: string | undefined,
  foundation: FoundationBlock | undefined,
  triage?: TriageRow[],
  attack?: string,
  step?: StepBlock
): string[] {
  const kind = typeof turnKind === "string" ? turnKind.trim().toLowerCase() : "";
  if (!VALID_TURN_KINDS.has(kind)) return ["turn_kind"];
  if (kind === "triage") return triageGaps(triage);
  if (kind === "attack") return attackGaps(attack);
  if (kind === "autopsy") return stepGaps(renderedContent, step);
  if (kind !== "idea") return [];
  const draft = renderedContent || "";
  const gaps: string[] = [];
  for (const field of FOUNDATION_FIELDS) {
    const raw = foundation && typeof foundation[field] === "string" ? foundation[field]!.trim() : "";
    if (raw.length === 0) gaps.push(`${field} (missing)`);
    else if (coverage(raw, draft) < FOUNDATION_BIND_THRESHOLD) gaps.push(`${field} (not in the draft)`);
  }
  return gaps;
}

/**
 * Shape check for a `turn_kind:"repair"` turn (G-repair-method).
 *
 * A repair turn is legal only after a graded miss survives the hint ladder (or
 * at once for a `missing`/structural gap). It is bound to exactly one gap,
 * names the diagnosed miss class and the tactic that diagnosis selects, and
 * ships exactly one reasoning step with its check — or, when `status:"done"`,
 * the fresh-surface check the learner passed plus their own-words restatement.
 * A repair that ships a compressed multi-step lecture is withheld.
 */
export function repairGaps(renderedContent: string | undefined, repair: RepairBlock | undefined): string[] {
  if (!repair || typeof repair !== "object" || Array.isArray(repair)) return ["repair (missing)"];
  const gaps: string[] = [];
  const gap = typeof repair.gap === "string" ? repair.gap.trim() : "";
  if (!gap) gaps.push("repair.gap (missing)");
  const missClass = typeof repair.miss_class === "string" ? repair.miss_class.trim().toLowerCase() : "";
  if (!REPAIR_MISS_CLASSES.has(missClass)) {
    gaps.push(
      `repair.miss_class (${missClass ? `'${missClass}'` : "missing"} is not cue|discrimination|execution|careless|structural)`
    );
  }
  const tactic = typeof repair.tactic === "string" ? repair.tactic.trim().toLowerCase() : "";
  if (!REPAIR_TACTICS.has(tactic)) {
    gaps.push(
      `repair.tactic (${tactic ? `'${tactic}'` : "missing"} is not source_return|retrieval_cue|contrasting_pair|worked_step|push_down|full_teach)`
    );
  }
  const status = typeof repair.status === "string" ? repair.status.trim().toLowerCase() : "";
  if (status !== "teaching" && status !== "done") {
    gaps.push(`repair.status (${status ? `'${status}'` : "missing"} is not teaching|done)`);
  } else if (status === "teaching") {
    gaps.push(...stepGaps(renderedContent, repair.step).map((g) => `repair.${g}`));
  } else {
    const fresh = typeof repair.fresh_surface_check === "string" ? repair.fresh_surface_check.trim() : "";
    if (!fresh) gaps.push("repair.fresh_surface_check (missing)");
    const restate = typeof repair.learner_restate === "string" ? repair.learner_restate.trim() : "";
    if (!restate) gaps.push("repair.learner_restate (missing)");
  }
  return gaps;
}

/**
 * True when a `fact_check` verdict lists a non-empty `omitted_foundations[]` —
 * load-bearing theory present in the sources with no trace in the draft. Such a
 * verdict is an ISSUES verdict even if the verifier labelled it PASS.
 */
export function hasOmittedFoundations(text: string): boolean {
  return /"omitted_foundations"\s*:\s*\[\s*[{"]/.test(text);
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
 * Fenced ` ```openui ` blocks in a message; returns the raw inner OpenUI Lang
 * strings. The bridge renders these as interactive embeds; the gate uses them to
 * bind a `ui_audit` receipt to the exact payload that was audited.
 */
export function extractUiFences(text: string): string[] {
  const out: string[] = [];
  if (typeof text !== "string") return out;
  const re = /```openui[^\n]*\n([\s\S]*?)```/g;
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
 * Canonical OpenUI Lang: normalise line endings and trailing whitespace so a
 * payload the verifier audited binds the emitted fence even when the Tutor
 * reformats blank lines. OpenUI Lang is a statement DSL, not JSON, so equality
 * is on this canonical text; a JSON payload (object/array) canonicalises as JSON.
 */
export function canonicalUiPayload(value: unknown): string {
  if (typeof value !== "string") return canonicalJson(value);
  return value
    .replace(/\r\n?/g, "\n")
    .split("\n")
    .map((line) => line.replace(/[ \t]+$/g, ""))
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

/** A fenced payload: parsed JSON when it is valid JSON, else the OpenUI Lang text. */
export function parseUiPayload(raw: string): unknown {
  const t = raw.trim();
  try {
    return JSON.parse(t);
  } catch {
    return t;
  }
}

/**
 * UI binding: a `ui_audit` receipt authorizes a `[[TURN:ui]]` only when the
 * emitted fenced payload canonicalises to the audited payload AND the audit's
 * `rendered_content` covers the emitted text. A present-but-wrong-shape envelope
 * (no payload, or no rendered_content) binds nothing; only an envelope-less
 * async completion falls back to unbound.
 */
export function uiBinds(r: Receipt, emittedText: string): boolean {
  if (!r.hasEnvelope) return true;
  if (!r.uiPayload || !r.renderedContent) return false;
  const fences = extractUiFences(emittedText);
  // Exactly one payload: a second, unaudited fence must not ride along on the
  // first one's receipt (the bridge would otherwise render both).
  if (fences.length !== 1) return false;
  let match = false;
  for (const f of fences) {
    try {
      if (canonicalUiPayload(parseUiPayload(f)) === r.uiPayload) {
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
 * (review-gate, array of {path}), `digest` + `raw_files` (scout-audit — the
 * `digest` string is mandatory, `raw_files` alone binds nothing). Returns the
 * first list found, or undefined when the envelope names none.
 */
export function artifactPaths(envelope: any): string[] | undefined {
  if (!envelope || typeof envelope !== "object") return undefined;
  for (const value of [envelope.files, envelope.written_files, envelope.target_files]) {
    if (!Array.isArray(value)) continue;
    return value
      .map((v: any) => (typeof v === "string" ? v : v && typeof v === "object" && typeof v.path === "string" ? v.path : ""))
      .filter((p: string) => p.length > 0);
  }
  // Scout-audit names its digest as a single `digest` string plus a `raw_files`
  // string list. The digest is mandatory: `raw_files` alone names context
  // without the digest under audit, so without a digest string there is
  // nothing bound and the receipt must not satisfy the gate.
  if (typeof envelope.digest !== "string" || envelope.digest.length === 0) return undefined;
  const scout: string[] = [envelope.digest];
  if (Array.isArray(envelope.raw_files)) {
    for (const v of envelope.raw_files) if (typeof v === "string" && v.length > 0) scout.push(v);
  }
  return scout;
}

/**
 * One graph record id from a ledger list entry. Accepts the canonical plain id
 * string and the `{"id":"n_…", …}` record shape (a Clerk may copy the merge's
 * record objects), so a non-string entry cannot silently disarm the gate.
 */
export function graphIdOf(value: any): string | undefined {
  if (typeof value === "string" && value.trim().length > 0) return value.trim();
  if (value && typeof value === "object" && typeof value.id === "string" && value.id.trim().length > 0) {
    return value.id.trim();
  }
  return undefined;
}

/**
 * Graph record ids named by a `graph_audit` envelope: `written_nodes[]` plus
 * `written_chains[]`. Returns undefined when the envelope names none, so a
 * present-but-untargeted audit cannot release the ingest close.
 */
export function graphIdsOf(envelope: any): string[] | undefined {
  if (!envelope || typeof envelope !== "object") return undefined;
  const ids: string[] = [];
  for (const value of [envelope.written_nodes, envelope.written_chains]) {
    if (!Array.isArray(value)) continue;
    for (const v of value) {
      const id = graphIdOf(v);
      if (id) ids.push(id);
    }
  }
  return ids.length > 0 ? ids : undefined;
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
 * The claimed verdict / question / qtype of every graded item, kept so a
 * repair's fresh-surface check can bind to a real graded pass instead of the
 * Tutor's prose. A flat single-answer envelope is treated as one item.
 */
export function gradeClaimsOf(envelope: any): GradeClaim[] | undefined {
  if (!envelope || typeof envelope !== "object") return undefined;
  const items = Array.isArray(envelope.items) ? envelope.items : [envelope];
  const out = items
    .filter((it: any) => it && typeof it === "object")
    .map(
      (it: any): GradeClaim => ({
        concept: typeof it.concept === "string" ? it.concept : undefined,
        question: typeof it.question === "string" ? it.question : undefined,
        claimedVerdict: typeof it.claimed_verdict === "string" ? it.claimed_verdict.trim().toLowerCase() : undefined,
        qtype: typeof it.qtype === "string" ? it.qtype.trim().toLowerCase() : undefined,
      })
    )
    .filter((c: GradeClaim) => !!c.question || !!c.claimedVerdict);
  return out.length > 0 ? out : undefined;
}

/**
 * Bookkeeping paths a review-gate pass explicitly excludes (state files,
 * session/review/lesson notes, log/index bookkeeping, git/commit metadata).
 * Used only to decide whether a finding that CITES such a location is
 * out-of-scope for the reviewed content.
 *
 * The patterns are path-shaped on purpose: a bare keyword (`provenance`) must
 * NOT match, or a content finding like "Knowledge Wiki/wiki/Backprop.md
 * provenance marker missing" would be silently demoted. Filenames are anchored
 * with `\b` so "dialog.md" does not match `log.md`.
 */
const BOOKKEEPING_PATH_RE =
  /(mission\.md|curriculum\.md|learning profile|learner history|mistakes\.md|attempts\.json|pending ingest\.json|(^|\/)sessions\/|(^|\/)reviews\/|(^|\/)lessons\/|\blog\.md|\bindex\.md|\bgit history\b|commit message|\bstaged files\b|\bworktree\b)/i;

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
  // Review-gate + scout-audit: if every high/medium finding is out-of-scope bookkeeping, the
  // target content is clean. Surface them as flags, never as blocking issues.
  // This is the ONLY remaining source of a passing `flags` receipt — it is a
  // scope ruling on bookkeeping paths, not a severity tolerance.
  const outOfScopeDemoted = (gate === "review" || gate === "scout_audit") && issues && reviewIssuesAllOutOfScope(text);
  if (outOfScopeDemoted) {
    issues = false;
    passWithFlags = true;
  }
  // Any verifier finding blocks at ANY severity. A verdict object carrying a
  // non-empty `issues[]` is an ISSUES verdict regardless of the stated verdict
  // word, so a `PASS_WITH_FLAGS` that lists residual `low` issues is NOT a pass
  // (lows block exactly like highs). The only exception is the out-of-scope
  // bookkeeping demotion above, whose findings are not content issues.
  const parsedVerdict = parseVerdictObject(text);
  const hasIssueList =
    !!parsedVerdict && Array.isArray(parsedVerdict.issues) && parsedVerdict.issues.length > 0;
  if (hasIssueList && !outOfScopeDemoted) issues = true;
  // A fact_check that names `omitted_foundations[]` (load-bearing theory in the
  // sources with no trace in the draft) is an ISSUES verdict even if it also
  // says PASS: silence about the missing "why" is exactly the failure this
  // closes.
  if (gate === "fact_check" && hasOmittedFoundations(text)) issues = true;
  const unverified =
    /"verdict"\s*:\s*"UNVERIFIED"/i.test(text) ||
    (gate === "fact_check" && /"verdicts"\s*:\s*\[[\s\S]*?"UNVERIFIED"/i.test(text));
  const cm = text.match(/"correct_verdict"\s*:\s*"(pass|fail)"/i);
  const am = text.match(/"agrees"\s*:\s*(true|false)/i);
  // Quiz binding: prefer the exact full batch text (`rendered_content`, mirroring
  // the fact-check full-draft rule) so the intro/instructions and options the
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
  if (gate === "review" || gate === "review_session" || gate === "scout_audit" || gate === "graph_audit") {
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
    turnKind: envelope && typeof envelope.turn_kind === "string" ? envelope.turn_kind : undefined,
    triage:
      envelope && Array.isArray(envelope.triage)
        ? (envelope.triage as TriageRow[])
        : undefined,
    attack:
      envelope && typeof envelope.attack === "string" ? envelope.attack : undefined,
    foundation:
      envelope && envelope.foundation && typeof envelope.foundation === "object" && !Array.isArray(envelope.foundation)
        ? (envelope.foundation as FoundationBlock)
        : undefined,
    step:
      envelope && envelope.step && typeof envelope.step === "object" && !Array.isArray(envelope.step)
        ? (envelope.step as StepBlock)
        : undefined,
    repair:
      envelope && envelope.repair && typeof envelope.repair === "object" && !Array.isArray(envelope.repair)
        ? (envelope.repair as RepairBlock)
        : undefined,
    gradeClaims: gate === "grade_audit" ? gradeClaimsOf(envelope) : undefined,
    uiPayload:
      gate === "ui_audit" && envelope && envelope.payload !== undefined
        ? canonicalUiPayload(envelope.payload)
        : undefined,
    questionsText: questionsText || undefined,
    gradeText: gradeText || undefined,
    gradeAnswers,
    auditFiles,
    graphIds: graphIdsOf(envelope),
    envelopeGate: envelope && typeof envelope.gate === "string" ? envelope.gate : undefined,
    hasEnvelope: !!envelope && typeof envelope === "object",
    provenance: "dispatch",
    evidenceMissing,
    severity:
      parsedVerdict && Array.isArray(parsedVerdict.issues) ? maxSeverity(parsedVerdict.issues) : undefined,
    raw: text,
  };
  // UNVERIFIED never counts as verified — it must block, not pass.
  if (gate === "fact_check") r.valid = pass && !issues && !unverified;
  else if (gate === "grade_audit") r.valid = !issues && r.agrees === true;
  else r.valid = (pass || passWithFlags) && !issues; // quiz_audit, review, tutor_audit, graph_audit
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
 * Graph ids from the Clerk's `CLERK_WRITES:` receipt.
 *
 * `graph` carries the four id lists `graph.py merge` returned. Any non-empty
 * list means the Clerk wrote ledger records, so the ingest close owes an
 * independent `graph-audit` over them. A missing graph object (or one with no
 * ids) wrote nothing and arms nothing.
 */
export function parseClerkGraph(text: string): string[] | undefined {
  const idx = text.search(/CLERK_WRITES\s*:/i);
  if (idx < 0) return undefined;
  const brace = text.indexOf("{", idx);
  if (brace < 0) return undefined;
  const blob = extractBalancedJson(text, brace);
  if (!blob) return undefined;
  let parsed: any;
  try {
    parsed = JSON.parse(blob);
  } catch {
    return undefined;
  }
  const graph = parsed && typeof parsed === "object" ? parsed.graph : undefined;
  if (!graph || typeof graph !== "object" || Array.isArray(graph)) return undefined;
  const ids: string[] = [];
  for (const key of ["created_nodes", "linked_nodes", "created_chains", "linked_chains"]) {
    const value = (graph as any)[key];
    if (!Array.isArray(value)) continue;
    for (const v of value) {
      const id = graphIdOf(v);
      if (id) ids.push(id);
    }
  }
  return ids.length > 0 ? Array.from(new Set(ids)) : undefined;
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
  "scout-audit": "scout_audit",
  "graph-audit": "graph_audit",
  "ui-audit": "ui_audit",
};
