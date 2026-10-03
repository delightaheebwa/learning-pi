/**
 * gate-core/judge/model — the model-backed judge.
 *
 * It never touches pi directly. The adapter injects a `complete` function
 * (pi's ctx.modelRegistry.complete, or any compatible caller). This keeps the
 * judge pi-independent and testable, and lets a test substitute a recorded
 * completion.
 */
import { DISPUTE_SYSTEM, JUDGE_SYSTEM, disputePackagePrompt, turnPackagePrompt } from "./prompts.ts";
import type {
  DisputePackage,
  DisputeVerdict,
  Judge,
  Substantiveness,
  TurnAssessment,
  TurnPackage,
  TurnType,
} from "./types.ts";

export interface CompleteRequest {
  system: string;
  user: string;
  maxTokens?: number;
  timeoutMs?: number;
}

export type CompleteFn = (req: CompleteRequest) => Promise<string>;

export class JudgeModelError extends Error {}

const TURN_TYPES = new Set<TurnType>(["claims", "quiz", "grade", "viz", "none"]);
const SUBSTANTIVENESS = new Set<Substantiveness>(["strong", "thin", "none"]);

/** Pull the first balanced JSON object out of free text. */
function firstJsonObject(text: string): any | undefined {
  const start = text.indexOf("{");
  if (start < 0) return undefined;
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
      if (depth === 0) {
        try {
          return JSON.parse(text.slice(start, i + 1));
        } catch {
          return undefined;
        }
      }
    }
  }
  return undefined;
}

function coerceAssessment(raw: any, pkg: TurnPackage): TurnAssessment {
  if (!raw || typeof raw !== "object") throw new JudgeModelError("judge returned no JSON object");
  const turnType: TurnType =
    pkg.explicitTag ?? (TURN_TYPES.has(raw.turnType) ? raw.turnType : "none");
  const summaryKind = ["content", "ingest", "review", "transition"].includes(raw.summaryKind)
    ? raw.summaryKind
    : "content";
  const byIndex = new Map<number, any>();
  if (Array.isArray(raw.bindings)) {
    for (const b of raw.bindings) {
      if (b && typeof b.index === "number") byIndex.set(b.index, b);
    }
  }
  const bindings = pkg.receipts.map((r) => {
    const b = byIndex.get(r.index);
    return {
      index: r.index,
      covers: !!(b && b.covers === true),
      uncovered: b && Array.isArray(b.uncovered) ? b.uncovered.filter((s: any) => typeof s === "string") : [],
    };
  });
  const substantiveness: Substantiveness[] = pkg.receipts.map((_, i) => {
    const s = Array.isArray(raw.substantiveness) ? raw.substantiveness[i] : undefined;
    return SUBSTANTIVENESS.has(s) ? s : "none";
  });
  const bestReceipt = typeof raw.bestReceipt === "number" ? raw.bestReceipt : -1;
  return {
    turnType,
    summaryKind,
    bindings,
    substantiveness,
    bestReceipt,
    remedy: typeof raw.remedy === "string" ? raw.remedy : undefined,
    reason: typeof raw.reason === "string" ? raw.reason : "",
    source: "model",
  };
}

export function createModelJudge(complete: CompleteFn, opts: { maxTokens?: number } = {}): Judge {
  return {
    kind: "model",
    async assessTurn(pkg: TurnPackage): Promise<TurnAssessment> {
      const text = await complete({
        system: JUDGE_SYSTEM,
        user: turnPackagePrompt(pkg),
        maxTokens: opts.maxTokens ?? 2000,
      });
      const raw = firstJsonObject(text);
      return coerceAssessment(raw, pkg);
    },
    async assessDispute(pkg: DisputePackage): Promise<DisputeVerdict> {
      const text = await complete({
        system: DISPUTE_SYSTEM,
        user: disputePackagePrompt(pkg),
        maxTokens: 400,
      });
      const raw = firstJsonObject(text);
      if (!raw || typeof raw !== "object" || typeof raw.applies !== "boolean") {
        throw new JudgeModelError("judge dispute returned no valid JSON");
      }
      return {
        applies: raw.applies,
        reason: typeof raw.reason === "string" ? raw.reason : "",
        source: "model",
      };
    },
  };
}
