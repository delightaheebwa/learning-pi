# MEMORIZATION FILTER

> **Purpose:** Decide whether a repeatedly failing fact should be memorized or
> understood. Rote memorization is the last resort, not the first move.

Adopted from Justin Sung's memorization filter and recorded in
`docs/adr/ADR-0003-solo-first-operating-mode.md`. This is a manual pilot
protocol. Nothing here is wired into the review flow yet.

## The three questions, in order

Ask these when review shows the same fact failing more than twice.

1. **Do I understand why this fact is important?** If you cannot say what it
   explains or what depends on it, the gap is comprehension, not memory.
2. **Is it related to something I already know?** If it connects to a concept
   you hold, put it beside that concept in the mind-map and re-test it there.
3. **Do I need high-level mastery of it?** If you will need to reason with the
   fact, drill understanding. If it is trivia you need at all, memorize it.

If all three answers are no, rote memorization is acceptable for that fact.
Sung's report: this filter cut his daily flashcard volume by about 80% while
memory improved. The point is to stop drilling facts that understanding would
carry.

## Recording

- Record the outcome in the `Open Question` cell of the fact's row in
  `📚 Active Concepts.md`: which questions passed or failed, and the decision.
- If the fact survives to rote, set its `Type` to `memory` so the existing
  interval ladder applies.
- If any question passes, do not drill. Return the fact to its concept and let
  repair or review handle the gap.
- A filter run is not an attempt. Record verdicts through the normal review
  flow, not as a separate score.

## Promotion

If the pilot shows the filter changing which facts get drilled, wiring it into
the review flow is a follow-up decision. The plan's Task 5 revisits this. If
contracted clerk behavior must change, the revise door applies.
