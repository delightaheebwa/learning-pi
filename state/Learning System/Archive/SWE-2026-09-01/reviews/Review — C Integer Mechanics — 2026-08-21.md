# REVIEW: C Integer Mechanics (Underflow & Type Promotion) — 2026-08-21

## Review Info
- **Date:** 2026-08-21
- **Concept:** C Integer Mechanics (Underflow & Type Promotion)
- **Last Reviewed:** 2026-08-18
- **Review Interval:** 3d (due)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): `double pct = 100.0 * used / total;` — why does the `100.0` (with the decimal point) matter? What would change if you wrote `(used / total) * 100` instead, and what specific integer-mechanics rule is biting you?

## Your Answer
- **Confidence:** confident
- **Answer:** It needs to be a float. If you multiply it with an integer, because the values in brackets will be floats... you will be losing accuracy. Hence we should multiply a float with a float.

## Assistant's Evaluation
- **Result:** Held (3d)
- **Feedback:** Knew `100.0` matters and that "integers lose accuracy" — right instinct — but INVERTED cause and cure. Correct mechanism: in `(used / total) * 100` both operands of `/` are integers, so C performs **integer division, truncating toward zero** (8M/16M = 0, not 0.5) → 0.0% for any usage <100%. The `100.0` float literal is the *cure* — it promotes `used` to `double`, keeping the whole chain floating-point. Type promotion happens *before* the operation; the result type follows its operands. The "integer mechanic" biting you is **integer-division truncation**; promotion is the fix, not the problem.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-21
- **next_review:** 2026-08-24 (held @3d)
- **Last Q Type:** discriminative
- **notes:** Held — cause/cure inverted; integer division truncates, float literal promotes. Reforge next round.

## Key Takeaway
> `(used / total) * 100` does **integer division** (truncates the fraction → 0.0%); leading with a float literal (`100.0 * used / total`) promotes the chain to floating-point. Result type follows its operands.
