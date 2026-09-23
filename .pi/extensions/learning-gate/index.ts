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
export { default } from "./pi-adapter/index.ts";
