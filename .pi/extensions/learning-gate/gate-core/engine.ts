/**
 * gate-core/engine — the learning gate's decision state machine.
 *
 * Pure over normalized inputs: it never imports pi and never knows an event
 * name or a pi/pi-subagents wire shape. The adapter (../../pi-adapter) extracts
 * normalized fields and calls these methods; all version-specific knowledge
 * lives there.
 *
 * Behavior is a line-for-line port of the original monolithic extension. Do not
 * change gate semantics here without going through the revise door (CONTRACT.md).
 */
import * as P from "./primitives.ts";

export interface ToolCallInput {
  tool: string;
  input: any;
  calls: P.CallRef[];
  agentless: boolean;
  toolCallId?: string;
}

export interface ToolResultInput {
  tool: string;
  toolCallId?: string;
  isError: boolean;
  text: string;
  asyncId?: string;
  dispatchCalls: P.CallRef[];
  mintCalls: P.CallRef[];
}

export interface NotificationInput {
  text: string;
  agent?: string;
  failedAgent?: string;
  runId?: string;
}

export interface BlockResult {
  block: true;
  reason: string;
}

export interface MessageEndInput {
  message: any;
}

export interface MessageEndResult {
  message?: any;
  notify?: string;
}

export interface GateEngine {
  onBeforeAgentStart(prompt: any): void;
  onToolCall(input: ToolCallInput): BlockResult | undefined;
  onToolResult(input: ToolResultInput): void;
  onCustomMessage(input: NotificationInput): void;
  onMessageEnd(input: MessageEndInput): MessageEndResult | undefined;
  getRun(): P.RunState;
}

export function createGate(): GateEngine {
  let run: P.RunState = P.newRun("other");

  // Async subagent runs: runId -> the child calls captured at dispatch. The
  // tool result for an async dispatch is only a fan-out notice (no verdict), so
  // the receipt is minted later from the `subagent-notify` completion. Storing
  // the envelope here lets that later receipt carry `rendered_content` /
  // `questions_json` / `question+answer`, which a notification alone lacks.
  const pendingAsync = new Map<string, { calls: P.CallRef[]; at: number }>();
  const PENDING_TTL_MS = 35 * 60 * 1000;
  const prunePendingAsync = () => {
    const now = Date.now();
    for (const [id, p] of pendingAsync) if (now - p.at > PENDING_TTL_MS) pendingAsync.delete(id);
  };

  const reset = (flow: P.Flow) => {
    run = P.newRun(flow);
    pendingAsync.clear();
  };

  const addReceipt = (r: P.Receipt) => run.receipts.push(r);
  const findAny = (gate: string) => run.receipts.find((r) => r.gate === gate);
  const consume = (r: P.Receipt) => {
    const i = run.receipts.indexOf(r);
    if (i >= 0) run.receipts.splice(i, 1);
  };

  const onBeforeAgentStart = (prompt: any): void => {
    try {
      const flow = P.detectFlow(prompt);
      // Subagent starts carry no FLOW marker — never wipe the parent run.
      // Only (re)start gating when a real learning flow begins.
      if (flow === "other") return;
      reset(flow);
    } catch {
      /* fail open: keep existing run */
    }
  };

  const onToolCall = (input: ToolCallInput): BlockResult | undefined => {
    try {
      const tool = typeof input?.tool === "string" ? input.tool.toLowerCase() : "";
      if (P.WRITE_TOOLS.has(tool)) {
        const p = P.writePath(input.input);
        if (p && P.isLearningStatePath(p)) {
          if (run.flow === "teach" || run.flow === "resume") {
            run.tutorWrote = true;
            run.writtenPaths.push(P.normPath(p));
          } else if (run.flow === "review" && P.isReviewSessionPath(p)) {
            run.reviewSessionWrote = true;
            run.reviewSessionPaths.push(P.normPath(p));
          }
        }
        return;
      }
      if (tool === "bash") {
        const cmd = typeof input.input?.command === "string" ? input.input.command : "";
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
      const calls = input.calls;
      // A subagent dispatch with no (string) `agent` mints no receipt and fails
      // opaquely. Remember it so the next withheld message can say why.
      if (calls.length === 0 && input.agentless) {
        run.agentlessDispatch = true;
      }
      const reviewGateCalls = calls.filter((c) => c.agent === "review-gate").length;
      const reviewSessionCalls = calls.filter((c) => c.agent === "review-session-audit").length;
      const clerkCalls = calls.filter((c) => c.agent === "clerk").length;
      if (reviewGateCalls > 0) run.reviewGates += reviewGateCalls;
      if (reviewSessionCalls > 0) run.reviewSessionAudits += reviewSessionCalls;
      if (clerkCalls > 0) run.clerkDispatches += clerkCalls;
      if (reviewSessionCalls > 0 && run.reviewSessionAudits > P.MAX_REVIEW_SESSION_AUDITS) {
        return {
          block: true,
          reason: `review-session audit cap reached (${P.MAX_REVIEW_SESSION_AUDITS} passes per flow). Report the existing verdict — fix any high/medium flags next session instead of re-running.`,
        };
      }
      if (reviewGateCalls > 0 && run.reviewGates > P.MAX_REVIEW_GATES) {
        return {
          block: true,
          reason: `review-gate cap reached (${P.MAX_REVIEW_GATES} passes per flow). Report the existing verdict — do not re-run. State/bookkeeping drift is audit_state.py's job, not another review pass.`,
        };
      }
      if (clerkCalls > 0 && run.clerkDispatches > P.MAX_CLERK_DISPATCHES) {
        return {
          block: true,
          reason: `clerk ingest cap reached (${P.MAX_CLERK_DISPATCHES} per flow). The ingest is already running or done — report its result instead of re-dispatching.`,
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
          (r) => r.gate === "fact_check" && r.valid && r.renderedContent && P.nearDuplicate(r.renderedContent, draft)
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
      if (calls.some((c) => c.agent === "scout")) run.scoutCalled = true;
      if (calls.some((c) => c.agent === "clerk")) run.clerkCalled = true;
    } catch {
      /* fail open */
    }
  };

  const onToolResult = (input: ToolResultInput): void => {
    try {
      const text = input.text;
      const tool = typeof input?.tool === "string" ? input.tool.toLowerCase() : "";
      if (tool === "subagent") {
        const dispatchCalls = input.dispatchCalls;
        prunePendingAsync();
        if (input.asyncId && dispatchCalls.length > 0) pendingAsync.set(input.asyncId, { calls: dispatchCalls, at: Date.now() });
        for (const call of input.mintCalls) {
          const output = call.output || text;
          // Provider failures (503/429/overloaded) count toward the one-shot
          // alternate-model fallback directive. They mint no receipt.
          const providerFail = input.isError === true || P.PROVIDER_FAILURE_RE.test(output);
          if (providerFail && (P.VERIFIER_AGENTS[call.agent] || call.agent === "scout")) {
            run.agentFailures[call.agent] = (run.agentFailures[call.agent] || 0) + 1;
          }
          if (input.isError === true) continue;
          // An async dispatch's tool result is only a fan-out notice — it
          // carries no verdict. Minting here would add an unusable stub that
          // then mislabels later blockers. The completion notification mints the
          // real one via `pendingAsync` above.
          if (input.asyncId) continue;
          const gate = P.VERIFIER_AGENTS[call.agent];
          if (gate) {
            // Right envelope for the right agent — a fact-check envelope on a
            // quiz-audit call (or vice versa) mints nothing.
            const expected = P.EXPECTED_ENVELOPE_GATE[call.agent];
            if (call.envelope && call.gate && expected && call.gate !== expected) continue;
            const r = P.parseResult(output, gate, call.envelope);
            addReceipt(r);
            if (r.valid) run.agentFailures[call.agent] = 0;
          }
          if (call.agent === "clerk") {
            const r = P.parseClerkReview(output);
            if (r) addReceipt(r);
          }
          if (call.agent === "scout") {
            run.scoutFinished = true;
            const sr = P.parseScoutReceipt(output);
            if (sr) {
              run.scoutReceiptSeen = true;
              run.scoutFailedRefs = sr.failedRefs;
              run.agentFailures["scout"] = 0;
            }
          }
        }
      }
      if (input.isError !== true) {
        const audit = P.parseStateAudit(text);
        if (audit) run.stateAudit = audit;
      }
    } catch {
      /* fail open */
    }
  };

  // Async gates that cannot be minted from a bare completion notification
  // (their receipt needs the dispatch envelope) are still minted — just gated
  // on `pendingAsync` correlation succeeding.
  const onCustomMessage = (input: NotificationInput): void => {
    const text = input.text;
    if (!text) return;
    // A failed async run clears its pending envelope (so the "verification
    // pending" hint does not lie) and counts provider failures, without minting.
    if (input.failedAgent) {
      if (input.runId) pendingAsync.delete(input.runId);
      if (P.VERIFIER_AGENTS[input.failedAgent] || input.failedAgent === "scout") {
        if (P.PROVIDER_FAILURE_RE.test(text)) run.agentFailures[input.failedAgent] = (run.agentFailures[input.failedAgent] || 0) + 1;
      }
      return;
    }
    const agent = input.agent;
    if (!agent) return;
    if (agent === "clerk") {
      if (run.receipts.some((r) => r.gate === "review" && r.valid)) return;
      const r = P.parseClerkReview(text);
      if (r) addReceipt(r);
      return;
    }
    if (agent === "scout") {
      run.scoutFinished = true;
      const sr = P.parseScoutReceipt(text);
      if (sr) {
        run.scoutReceiptSeen = true;
        run.scoutFailedRefs = sr.failedRefs;
      }
      return;
    }
    const gate = P.VERIFIER_AGENTS[agent];
    if (!gate) return;
    const entry = input.runId ? pendingAsync.get(input.runId) : undefined;
    const calls = entry?.calls;
    if (input.runId) pendingAsync.delete(input.runId);
    if (gate === "fact_check") {
      // A fact-check receipt is only usable when bound to its draft
      // (`rendered_content`); the notification does not carry the envelope, so
      // without the dispatch-correlated envelope we mint nothing rather than a
      // receipt that could only ever produce FACT_CHECK_MISSING_DRAFT.
      if (!calls || calls.length === 0) return;
      if (run.receipts.some((r) => r.gate === "fact_check" && r.valid)) return;
      for (const c of calls) addReceipt(P.parseResult(text, gate, c.envelope));
      return;
    }
    if (run.receipts.some((r) => r.gate === gate && r.valid)) return;
    // With the correlated envelope the receipt binds the audited question /
    // answer / files; without it (legacy notifications) mint unbound as before.
    addReceipt(P.parseResult(text, gate, calls && calls.length === 1 ? calls[0].envelope : undefined));
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
      for (const c of calls) if (P.VERIFIER_AGENTS[c.agent]) agents.add(c.agent);
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
        if (rc && P.contentMatches(rc, text)) return true;
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
   *     dropped. Trusting the single pending receipt mirrors the explicit-tag
   *     path, where an unbound valid receipt is already accepted. Two pending
   *     gate types stay ambiguous and withhold.
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
      if (!P.bindingMatches(bound, text)) return;
      const score = P.coverage(bound, text);
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
   */
  const inferClaimsTurn = (text: string): boolean => {
    if (run.flow === "ingest" || run.flow === "other") return false;
    return run.receipts.some(
      (r) => r.gate === "fact_check" && r.valid && r.renderedContent && P.contentMatches(r.renderedContent, text)
    );
  };

  const onMessageEnd = (input: MessageEndInput): MessageEndResult | undefined => {
    try {
      const message = input.message;
      if (!message || message.role !== "assistant") return;
      if (P.hasToolCall(message)) return;
      if (run.flow === "other") return;

      // A generation that did not finish (`error`, `aborted`, or the token cap
      // `length`) is a partial emission pi will retry or continue. Gating it
      // would consume the verifier receipt that the retried message needs.
      if (message.stopReason === "error" || message.stopReason === "aborted" || message.stopReason === "length") {
        return { message: P.stripTag(message) };
      }

      const rawText = P.textOf(message);
      if (!rawText || rawText.trim().length === 0) return;

      const tagMatch = rawText.match(P.TURN_TAG_RE);
      const text = (tagMatch ? rawText.replace(P.TURN_TAG_RE, "") : rawText).trim();
      const explicitTag = tagMatch ? tagMatch[1].toLowerCase() : undefined;
      const blockers: string[] = [];
      let verdictNote = "";
      let scoutNeeded = false;
      let surface = "";
      const toConsume: P.Receipt[] = [];

      // Ingest terminal summary: the clerk's REVIEW_GATE_VERDICT receipt is the
      // verification for this turn, so an untagged summary after a clerk
      // dispatch is treated as an implicit none-turn.
      const inferredNone =
        !tagMatch &&
        ((run.flow === "ingest" && run.clerkCalled && P.looksLikeIngestSummary(text)) ||
          (run.flow === "review" && run.reviewSessionWrote && P.looksLikeReviewSummary(text)));
      // Grade/quiz turns are tightly bound to a verifier receipt, so a
      // forgotten tag can be inferred from it in any interactive flow.
      let inferredTag: "grade" | "quiz" | "claims" | undefined;
      if (!tagMatch && !inferredNone) {
        if (inferClaimsTurn(text)) inferredTag = "claims";
        else inferredTag = inferTaggedTurn(text);
        if (!inferredTag) blockers.push("NO_TURN_TAG");
      }
      const tag = explicitTag || inferredTag || (inferredNone ? "none" : undefined);
      if (run.flow === "ingest") {
        if (run.clerkCalled && P.looksLikeIngestSummary(text)) {
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
        let best: P.Receipt | undefined;
        let bestScore = 0;
        for (const r of run.receipts) {
          if (r.gate !== "fact_check" || !r.valid) continue;
          if (!r.renderedContent || !P.contentMatches(r.renderedContent, text)) continue;
          const score = P.coverage(r.renderedContent, text);
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
            const score = P.coverage(validDraft.renderedContent as string, text);
            blockers.push("FACT_CHECK_MISMATCH");
            verdictNote = `The fact-check receipt covers only ${Math.round(score * 100)}% of this message (needs ≥${Math.round(
              P.MATCH_THRESHOLD * 100
            )}%, no unverified tail). Emit the verified draft unchanged, or fact-check this new text.`;
          } else blockers.push("NO_FACT_CHECK_MATCH");
        } else {
          toConsume.push(best);
        }
      } else if (tag === "quiz") {
        const candidates = run.receipts.filter(
          (r) => r.gate === "quiz_audit" && r.valid && P.bindingMatches(r.questionsText, text)
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
          (r) => r.gate === "grade_audit" && r.valid && P.bindingMatches(r.gradeText, text)
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
          (r) => r.gate === "fact_check" && r.valid && r.renderedContent && P.contentMatches(r.renderedContent, text)
        );
        if (match) blockers.push("TURN_TAG_MISMATCH");
        // Evasion guard for the exact 2026-09-21 loop: teaching content tagged
        // `[[TURN:none]]` while its fact-check is still running (no receipt
        // yet). Matching the pending draft is decisive — a genuine transition
        // does not quote the teaching draft.
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
        P.looksLikeReviewSummary(text);
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
          return r.auditFiles.some((f) => run.writtenPaths.includes(P.normPath(f)));
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
      // errors or warnings still outstanding.
      if (run.stateAudit && (run.stateAudit.errors > 0 || run.stateAudit.warnings > 0) && (run.flow === "ingest" || run.flow === "review")) {
        surface += `⚠️ STATE AUDIT — ${run.stateAudit.errors} error(s), ${run.stateAudit.warnings} warning(s). Run /audit for details.\n\n`;
        run.stateAudit = undefined;
      }

      if (blockers.length === 0 && !scoutNeeded) {
        for (const r of toConsume) consume(r);
        run.retries = 0;
        run.agentlessDispatch = false;
        let out = P.stripTag(message);
        if (surface) out = P.prependBanner(out, surface);
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
        if (count >= P.FALLBACK_AFTER_FAILURES && !run.agentFallbackUsed[agent]) {
          const fb = agent === "scout" ? P.SCOUT_FALLBACK_MODEL : P.VERIFIER_AGENTS[agent] ? P.VERIFIER_FALLBACK_MODEL : undefined;
          if (fb) {
            fallbackLines.push(`\`${agent}\` failed ${count}× in a row — re-dispatch it once with \`model: "${fb}"\` before giving up.`);
            run.agentFallbackUsed[agent] = true;
          }
        }
      }
      const fallbackNote = fallbackLines.length ? fallbackLines.join("\n") + "\n" : "";

      if (run.retries > P.MAX_RETRIES) {
        run.retries = 0;
        const banner = `⛔ UNVERIFIED — gate retries exhausted (${codes.join(", ")}). The content below was not verified.\n${fallbackNote}\n`;
        return { message: P.prependBanner(P.replaceText(message, text), banner) };
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
      return { message: P.replaceText(message, banner), notify: `learning-gate blocked: ${codes.join(", ")}` };
    } catch {
      return; // fail open
    }
  };

  return { onBeforeAgentStart, onToolCall, onToolResult, onCustomMessage, onMessageEnd, getRun: () => run };
}
