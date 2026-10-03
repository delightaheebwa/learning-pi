/**
 * learning-gate — verification gate for the pi learning system.
 *
 * Entry point. The implementation is split so that all version-specific
 * knowledge (pi event names, message shapes, pi-subagents result shapes) lives
 * in `pi-adapter/` and the decision logic is pure and pi-independent in
 * `gate-core/`. See ../../../CONTRACT.md for the invariants this gate enforces.
 *
 * Turn type is explicit, not guessed:
 *   - Prompt templates carry a flow marker (`[[FLOW:teach|resume|review|ingest]]`).
 *   - Every assistant message in a learning flow must start with a turn tag
 *     `[[TURN:claims|quiz|grade|viz|none]]`. The gate strips the tag before the learner sees it.
 *   - claims -> a fact-check receipt whose `rendered_content` covers the emitted text
 *     (the judge checks 100% span coverage; the legacy path approximates it with
 *     >=85% token coverage and a length-ratio guard) with no ISSUES.
 *   - When a judge model is configured (Gemini, see gate-core/judge/), it answers
 *     the semantic questions: turn type, full coverage, PASS substance, remedy,
 *     and a dispute. The judge only sees and writes text; the engine acts. On a
 *     judge fault the gate runs this legacy deterministic path unchanged.
 *   - quiz  -> a quiz-audit receipt returning PASS, or PASS_WITH_FLAGS (lows only)
 *     which is accepted silently (flags are not surfaced to the learner).
 *   - grade -> a grade-audit receipt that agrees (a conflicting correct_verdict is surfaced).
 *   - viz   -> a [[TURN:viz]] message carrying one ```viz spec needs a passing viz-audit
 *     whose canonical spec matches the emitted block and whose rendered_content covers the turn;
 *     a viz fence in a claims/none turn is withheld (VIZ_REQUIRES_OWN_TURN).
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
 *   - review -> a `review-scout` run before the first claims/quiz turn
 *     (`NO_REVIEW_CONTEXT` until then); its `REVIEW_SCOUT_DIGEST: {...}` receipt
 *     surfaces `⚠️ REVIEW CONTEXT INCOMPLETE` / `⚠️ REVIEW SCOUT DIGEST UNVERIFIED`
 *     (banner, never a withhold). The close writes are delegated to `review-clerk`;
 *     a completed run arms the review-session audit gate, so the summary needs a
 *     passing `review-session-audit` over the writes.
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
export { default } from "./pi-adapter/index.ts";
