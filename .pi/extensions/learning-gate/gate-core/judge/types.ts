/**
 * gate-core/judge/types — the judge port.
 *
 * The judge answers SEMANTIC questions the deterministic gate cannot: what type
 * of turn is this, does a verifier's verified draft cover the emission, is a
 * PASS substantive, and what exact remedy is needed. A judge only SEES and
 * WRITES TEXT. It never acts: it runs no tool, writes no file, changes no state.
 * The engine performs every action (consume, block, stamp, ledger).
 *
 * Two implementations satisfy this port:
 *   - heuristic.ts — wraps the legacy deterministic primitives (the fallback,
 *     and the default when no model is configured, so existing behavior and
 *     tests are unchanged).
 *   - model.ts — a Gemini judge built on the router (cache/budget/fallback).
 *
 * This file MUST NOT import pi or pi-subagents shapes.
 */
import type { Flow } from "../primitives.ts";

export type TurnType = "claims" | "quiz" | "grade" | "viz" | "none";

/** How substantive a verifier's verdict looks: real work / thin / none. */
export type Substantiveness = "strong" | "thin" | "none";

export interface JudgeIssue {
  severity?: string;
  location?: string;
  issue?: string;
  correction?: string;
}

/** A receipt as the judge sees it — the verifier's own structured statement. */
export interface JudgeReceipt {
  /** Index into the package's `receipts` array (stable id for bindings). */
  index: number;
  gate: string;
  verdict: "PASS" | "PASS_WITH_FLAGS" | "ISSUES" | "UNVERIFIED" | "UNKNOWN";
  /** The text the verifier says it checked (rendered_content / batch / files). */
  boundText?: string;
  issues: JudgeIssue[];
  /** Highest issue severity present, normalized (high/medium/low or undefined). */
  severityMax?: string;
  evidence?: string[];
  /** Whether a dispatch envelope was present when the receipt was minted. */
  hasEnvelope?: boolean;
  /** Canonical JSON of the audited viz spec (viz_audit only). */
  vizSpec?: string;
  /** Artifact paths a write gate names (files / written_files / target_files). */
  auditFiles?: string[];
  /** Whether the verdict is out-of-scope bookkeeping only (review gates). */
  outOfScopeOnly?: boolean;
  raw: string;
}

/** A full, self-contained package. The judge never needs to ask for more. */
export interface TurnPackage {
  flow: Flow;
  /** The explicit `[[TURN:...]]` tag if the Tutor included one; a hint only. */
  explicitTag?: TurnType;
  /** The emitted text, turn tag stripped. */
  text: string;
  hasVizFence: boolean;
  receipts: JudgeReceipt[];
  /** Drafts of async verifications still in flight (evasion guard). */
  pendingDrafts: string[];
  hasIngestSummaryHint: boolean;
  hasReviewSummaryHint: boolean;
  tutorWrote: boolean;
  reviewSessionWrote: boolean;
  scoutCalled: boolean;
  reviewScoutCalled: boolean;
  writtenPaths: string[];
}

/** Per-receipt coverage of the emission (the 100% rule when `judge.kind` is model). */
export interface BindingVerdict {
  index: number;
  covers: boolean;
  /** Spans of the emission the verified draft does not cover. */
  uncovered: string[];
}

export interface TurnAssessment {
  /** The turn type the engine acts on. The explicit tag wins when present. */
  turnType: TurnType;
  /** Semantic kind, used for summary detection. */
  summaryKind: "content" | "ingest" | "review" | "transition";
  bindings: BindingVerdict[];
  /** Per receipt, aligned to package.receipts by index. */
  substantiveness: Substantiveness[];
  /** Index of the best-binding receipt for this turn, or -1. */
  bestReceipt: number;
  /** The exact remedy the Tutor must apply, when the engine is about to block. */
  remedy?: string;
  /** Short plain-language reason for the ledger. */
  reason: string;
  /** Whether the judge ran on a model or the legacy fallback. */
  source: "model" | "heuristic" | "replay";
  /** True when the escalation model produced this assessment. */
  escalated?: boolean;
}

export interface DisputePackage {
  text: string;
  issue: JudgeIssue;
  verifierEvidence?: string[];
  /** What changed between the three blocked attempts (text or "(unchanged)"). */
  changes: string[];
}

export interface DisputeVerdict {
  applies: boolean;
  reason: string;
  source: "model" | "heuristic" | "replay";
}

export interface Judge {
  readonly kind: "model" | "heuristic" | "replay";
  assessTurn(pkg: TurnPackage): Promise<TurnAssessment>;
  assessDispute(pkg: DisputePackage): Promise<DisputeVerdict>;
}

/**
 * Options accepted by the engine. When `judge` is omitted the engine uses the
 * heuristic judge and preserves the legacy deterministic behavior exactly.
 */
export interface GateOptions {
  judge?: Judge;
  /** Append-only decision + receipt ledger. Best-effort; never blocks a turn. */
  ledger?: Ledger;
}

export interface LedgerReceipt {
  at: string;
  runId?: string;
  agent: string;
  gate: string;
  verdict: string;
  envelopeHash?: string;
  artifact?: string;
  consumedBy?: string;
}

export interface LedgerDecision {
  at: string;
  flow: Flow;
  turnType: TurnType;
  outcome: "pass" | "block" | "unverified" | "dispute-release";
  codes: string[];
  source: "model" | "heuristic" | "replay";
  escalated?: boolean;
  reason?: string;
  remedy?: string;
  disagreements?: string[];
}

export interface Ledger {
  receipt(entry: LedgerReceipt): void;
  decision(entry: LedgerDecision): void;
}
