# Spec: `benchmark-retrieval` — the 1-day / 1-week / 1-month shots

Module of: `docs/specs/CAPABILITY-MAP-reading-mode.md` (approved 2026-11-24)

## Objective

The benchmark questions generated in `benchmark-session` come back as spaced
retrieval at **+1 day, +1 week, +1 month** — fixed three shots, never reset
(user decision 2026-11-24). Each retrieval session opens with a free-recall
dump (`free-recall` module), then asks the benchmark questions from memory,
scores them against the **90% low / 80% mid / 70% high** targets, and records
the trajectory. Sung's spacing rule of thumb is exactly this ladder, and his
caveat governs the design: "the interval matters far less than what you do in
the session" (#88, #101).

User story: "The day after my reading session, review nudges me. I dump what I
remember, answer my own 15 benchmark questions cold, rate my confidence, then
get the graded check with quotes and my running score per level. Same at one
week, same at one month. If I miss one, it comes back next session — the
clock doesn't restart."

## Behavior

1. **Persistence.** At reading-session close, the 15 benchmark questions are
   ingested as retrieval items with level labels (`low|mid|high`), the
   scoped-source reference, and due dates at session date +1d, +1w, +1m. They
   enter the existing review queue machinery (`ops.py queue`) alongside —
   never displacing — due mistakes and concept reviews.
2. **Fixed schedule.** Each question is asked at all three shots regardless
   of outcomes. A miss at any shot marks the question to re-appear at the
   learner's next retrieval session, but **never resets, shortens, or extends
   the 1d/1w/1m ladder**. After the +1m shot the question graduates out of
   the queue. (The existing interval ladders in `ops.py`
   —`memory [0,1,3,7,14,30,60]` etc. — remain untouched for concept/memory
   items; benchmark items are a separate track.)
3. **Session shape.** Each due retrieval session:
   a. free-recall dump over the scoped material, confidence marks, quoted
      check (`free-recall` module, verbatim);
   b. benchmark questions answered from memory, one generate-before-feedback
      batch — no answers shown until the learner has attempted every
      question and rated confidence;
   c. graded check: per-question pass/fail with source quotes; `sure`-wrong
      flagged as priority gaps;
   d. running score report: hit rate per level vs the 90/80/70 targets after
      this shot, plus trajectory across shots so far.
4. **Recording.** Per-question, per-shot results and per-level hit rates are
   written through the existing review-close machinery (`review-clerk` →
   `ops.py apply` → `Attempts.json`/concept tables or a benchmark ledger —
   decided in the plan phase), committed at review close like all state
   writes, and auditable.

Hard rules:

- Free-recall format only; recognition/MCQ is contract-banned already.
- The 1d/1w/1m dates are fixed; nothing the learner does moves them.
- Benchmark items never alter the scheduling of concept/memory/procedure
  items and vice versa.
- Feedback always quotes the source; scores are recorded, not just displayed.

## Commands

- Verify: `scripts/learn-check --no-load`; state tools: `python3 state/scripts/ops_test.py`

## Project Structure

- `state/scripts/ops.py` — benchmark track: fixed `[1, 7, 30]` schedule,
  queue inclusion, graduation after the third shot
- `state/Learning System/` — persistence of benchmark items + scores
- `.pi/skills/learning-review/SKILL.md` (or `learning-read` — plan decision)
  — retrieval-session shape
- Gate/review invariants + tagged tests

## Testing Strategy

- `ops_test.py`: benchmark items queue at +1/+7/+30; a miss re-queues for
  the next session without touching the ladder; third shot graduates the
  item; concept/memory scheduling unaffected.
- Gate test: answers or feedback revealed before the learner attempts all
  questions + confidence are withheld.
- Gate test: a score report that doesn't match the recorded attempts is
  withheld.
- Contract: `R-*` invariants bind fixed-schedule, generate-before-feedback,
  and score recording to these tests.

## Boundaries

- Always: three fixed shots; misses re-appear without resetting; scores
  recorded per level per shot.
- Ask first: changing [1,7,30]; adaptive resets; asking questions outside
  due dates.
- Never: let benchmark results alter concept/memory/procedure scheduling;
  reveal answers before generation; delete the score history at graduation.

## Success Criteria

1. A reading session's 15 questions appear due at +1d, +1w, +1m in the
   existing review queue.
2. Misses re-appear next session; the ladder dates never move.
3. Each session runs dump → questions → graded check → score report, with
   feedback withheld until generation completes.
4. Per-level hit rates vs 90/80/70 are recorded across all three shots and
   visible in the trajectory report.
5. `ops_test.py` and `learn-check --no-load` pass with the new track.

## Open Questions

- Exact persistence shape (extend `Attempts.json` + Active Concepts vs. a
  dedicated benchmark ledger) — plan phase.
- Whether the existing review-session-audit/review-gate close machinery
  covers benchmark sessions as-is or needs a scoped extension — plan phase.
