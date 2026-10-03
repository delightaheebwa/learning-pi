/**
 * gate-core/judge/router — budget, cache, escalation, and fallback around a Judge.
 *
 * The router is the only place that knows about cost and availability. It:
 *   - caches by content hash so the same package never costs two calls,
 *   - counts calls per day and refuses past the budget (the engine then falls
 *     back to the legacy path, surfaced as `JUDGE DEGRADED`),
 *   - escalates a HARD case from the primary model to the escalation model
 *     (separately budget-capped), and
 *   - if the primary model errors, tries the escalation model before giving up.
 *
 * It performs no action itself: it only decides whether a judge call happens.
 */
import type {
  DisputePackage,
  DisputeVerdict,
  GateOptions,
  Judge,
  TurnAssessment,
  TurnPackage,
} from "./types.ts";

export interface RouterOptions {
  maxCallsPerDay?: number;
  /** The escalation judge (e.g. gemini-3.5-flash). Optional. */
  escalate?: Judge;
  /** Decide whether an assessment is hard enough to escalate. Defaults to isHardCase. */
  shouldEscalate?: (assessment: TurnAssessment, pkg: TurnPackage) => boolean;
  /** Escalation calls allowed per day (the escalation model's free tier is smaller). */
  maxEscalationsPerDay?: number;
  onCall?: (info: {
    kind: "assessTurn" | "assessDispute";
    cached: boolean;
    escalated: boolean;
    dayCalls: number;
    dayEscalations: number;
  }) => void;
  /** Injected clock for tests. */
  now?: () => number;
}

function hash(input: unknown): string {
  const s = JSON.stringify(input);
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(36);
}

/**
 * A "hard" case is one where the primary model's answer is consequential or
 * uncertain: a valid receipt that does not fully cover (a possible false
 * block), a receipt set with no best match, or thin substantiveness.
 */
export function isHardCase(a: TurnAssessment, pkg: TurnPackage): boolean {
  if (a.bestReceipt === -1 && pkg.receipts.length > 0) return true;
  if (a.substantiveness.some((s) => s === "thin")) return true;
  return pkg.receipts.some((r, i) => {
    const valid = r.verdict === "PASS" || r.verdict === "PASS_WITH_FLAGS";
    const b = a.bindings[i];
    return valid && !!b && !b.covers;
  });
}

export function createRouterJudge(inner: Judge, opts: RouterOptions = {}): Judge {
  const cache = new Map<string, any>();
  const now = opts.now ?? (() => Date.now());
  const maxPerDay = opts.maxCallsPerDay ?? 450;
  const maxEscalations = opts.maxEscalationsPerDay ?? 20;
  const escalate = opts.escalate;
  const shouldEscalate = opts.shouldEscalate ?? isHardCase;
  let day = new Date(now()).toISOString().slice(0, 10);
  let dayCalls = 0;
  let dayEscalations = 0;

  const rollDay = () => {
    const d = new Date(now()).toISOString().slice(0, 10);
    if (d !== day) {
      day = d;
      dayCalls = 0;
      dayEscalations = 0;
      cache.clear();
    }
  };

  const canEscalate = () => !!escalate && dayEscalations < maxEscalations;

  const runEscalation = async (pkg: TurnPackage): Promise<TurnAssessment> => {
    dayEscalations += 1;
    const res = await escalate!.assessTurn(pkg);
    return { ...res, escalated: true };
  };

  return {
    kind: inner.kind === "heuristic" ? "heuristic" : inner.kind,
    async assessTurn(pkg: TurnPackage): Promise<TurnAssessment> {
      rollDay();
      const key = "t:" + hash(pkg);
      if (cache.has(key)) {
        opts.onCall?.({ kind: "assessTurn", cached: true, escalated: false, dayCalls, dayEscalations });
        return cache.get(key);
      }
      if (dayCalls >= maxPerDay) {
        throw new Error(`judge daily budget reached (${maxPerDay})`);
      }
      dayCalls += 1;
      opts.onCall?.({ kind: "assessTurn", cached: false, escalated: false, dayCalls, dayEscalations });

      let primary: TurnAssessment | undefined;
      try {
        primary = await inner.assessTurn(pkg);
      } catch (err) {
        // The primary failed (rate limit, outage). Try the escalation model
        // before letting the engine fall back to the legacy path.
        if (canEscalate()) {
          const res = await runEscalation(pkg);
          cache.set(key, res);
          return res;
        }
        throw err;
      }

      if (canEscalate() && shouldEscalate(primary, pkg)) {
        try {
          const res = await runEscalation(pkg);
          cache.set(key, res);
          return res;
        } catch {
          // Escalation failed; keep the primary result.
        }
      }
      cache.set(key, primary);
      return primary;
    },
    async assessDispute(pkg: DisputePackage): Promise<DisputeVerdict> {
      rollDay();
      const key = "d:" + hash(pkg);
      if (cache.has(key)) return cache.get(key);
      if (dayCalls >= maxPerDay) {
        throw new Error(`judge daily budget reached (${maxPerDay})`);
      }
      dayCalls += 1;
      opts.onCall?.({ kind: "assessDispute", cached: false, escalated: false, dayCalls, dayEscalations });
      const res = await inner.assessDispute(pkg);
      cache.set(key, res);
      return res;
    },
  };
}

/** Convenience: extract a judge from GateOptions, if any. */
export function judgeOf(options: GateOptions | undefined): Judge | undefined {
  return options?.judge;
}
