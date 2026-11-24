# Spec: `free-recall` — closed-book dump, checked against the source

Module of: `docs/specs/CAPABILITY-MAP-reading-mode.md` (approved 2026-11-24)

## Objective

Free recall is the retrieval *activity*, separate from the benchmark questions
(which are the *measurement*). After reading — and again at the start of every
retrieval session — the learner dumps everything they remember, closed book.
Pi checks the dump against the source text and returns feedback only after the
learner has fully generated and rated their confidence. Generate before
feedback; confidence before checking; a high-confidence wrong item is the most
urgent gap (Sung #49, #42).

User story: "I finish the section, come back, and dump what I remember. Pi
doesn't interrupt or correct mid-dump. When I'm done it asks me which items
I'm sure about, and only then tells me what was wrong or missing — with
quotes."

## Behavior

1. **Dump.** The learner writes everything they remember from the scoped
   reading, in any form (prose, list, rough map). Pi does not comment, correct,
   or complete anything during the dump. If the learner asks "is this right?"
   mid-dump, pi declines and asks them to finish first.
2. **Confidence.** After the learner signals the dump is complete, pi asks
   them to mark each item `sure | hunch | no-idea` (the existing three-level
   vocabulary from the teach flow's v1 spine) before any feedback is revealed.
3. **Check.** Pi then returns an itemized check against the attached source:
   - **wrong** — contradicts the source; quote the source passage.
   - **missing** — load-bearing content in the scoped text that the dump
     omitted; name it, quote it.
   - **right** — confirmed briefly, no re-teaching, no polished restatement.
   Every verdict cites the source. An unanchored verdict is withheld by the
   gate.
4. **Priority flag.** `sure`-but-wrong items are marked as the most urgent
   gaps and carried into the session handoff so retrieval prioritizes them.

Hard rules:

- No feedback of any kind before the dump is complete and confidence is
  marked.
- Pi never rewrites the dump or fills gaps proactively — it names what is
  missing; the learner goes back to the source.
- The same procedure runs at the start of every retrieval session
  (+1d/+1w/+1m) over the same scoped material.

## Commands

- Verify: `scripts/learn-check --no-load`

## Project Structure

- `.pi/skills/learning-read/SKILL.md` — free-recall procedure
- Gate verifier rules — generate-before-feedback and source-citation
  enforcement
- Session handoff (`Pending Ingest.json` shape) — `sure`-wrong priority items

## Testing Strategy

- Gate test: feedback emitted before dump-completion + confidence is
  withheld.
- Gate test: a check verdict without a source quote is withheld.
- Gate test: pi completing a gap for the learner (content the dump omitted,
  explained rather than named+quoted) is withheld as model-ghostwriting,
  reusing the existing verdict family.
- Contract: `R-*` invariants bind these rules to the tests.

## Boundaries

- Always: confidence marks before feedback; quotes on every verdict;
  `sure`-wrong flagged.
- Ask first: adding a second confidence round after feedback.
- Never: correct mid-dump; restate the learner's dump in cleaner prose;
  reveal answers while the learner is still generating.

## Success Criteria

1. A completed dump + confidence marks yields an itemized, quoted check.
2. Mid-dump interruptions and premature feedback are withheld by the gate.
3. `sure`-wrong items appear in the session handoff as priority gaps.
4. The procedure is reusable verbatim at retrieval sessions
   (`benchmark-retrieval` depends on this module).

## Open Questions

- Whether the dump and the mental-model presentation
  (`model-diagnose`) are one message or two — default two (dump first, then
  the model), since Sung treats externalized structure as its own step.
