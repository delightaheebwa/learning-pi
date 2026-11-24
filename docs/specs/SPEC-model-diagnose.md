# Spec: `model-diagnose` — present the mental model, get a diagnosis

Module of: `docs/specs/CAPABILITY-MAP-reading-mode.md` (approved 2026-11-24)

## Objective

The learner presents their mental model of what they read (text, ASCII/mermaid
diagram, or the existing photo-ingestion path). Pi **assesses and corrects
simply** — not the teach flow's attack battery, repair ladder, or graduation
clones. The user called that machinery overhead; this module is the
replacement inside the reading mode, faithful to their reference ChatGPT
conversation and to Sung's loop: guess a model knowing it is wrong, revise,
repeat ("make it wrong, make it shorter, make it again", #96).

User story: "I paste my mermaid mind map. Pi tells me which links are wrong,
which nodes are missing, and what's misplaced — quoting me and the book — and
I go fix it myself. No six-attack battery, no hint ladder."

## Behavior

1. **Presentation.** The learner presents the model in any form. Pi does not
   restate it in cleaner prose and does not redraw it — ever.
2. **Diagnosis.** Pi returns one structured verdict:
   - **right** — relations that match the source; confirmed briefly.
   - **wrong** — links/claims that contradict the source; quote the
     learner's words, quote the source, say what's wrong. No corrected
     version supplied.
   - **missing** — load-bearing concepts from the scoped text absent from
     the model; named and quoted, not explained into place.
   - **misplaced** — relations present but with wrong direction/level
     (e.g. A-drives-B where the source says B-modulates-A); both the
     learner's version and the source version quoted.
   Every verdict is grounded in the learner's verbatim words *and* the source
   text. An invented or paraphrased "you said…" is withheld (the existing
   `PRIOR_UNGROUNDED` standard carries over).
3. **Revision loop.** The learner revises and re-presents. Pi re-diagnoses.
   The loop closes when a re-presented model produces only `right` verdicts
   (or `missing` items the learner consciously parks, recorded as such).
   Each iteration is one diagnosis turn — no interleaved quizzes, no
   per-gap repair receipts, no naive-student clone.
4. **Session close.** The final model version (verbatim) plus the diagnosis
   history enters the session handoff.

Hard rules:

- Diagnose, never rewrite. The single forbidden move is producing the
  corrected model for the learner.
- One diagnosis per presentation; the learner always authors the next
  version.
- Direct corrections are allowed *about individual links* (that's the point)
  but only as verdicts with quotes, never as a restructured model.

## Commands

- Verify: `scripts/learn-check --no-load`

## Project Structure

- `.pi/skills/learning-read/SKILL.md` — diagnosis procedure
- Gate verifier rules — grounding + anti-ghostwriting enforcement
- Session handoff — model versions + verdicts

## Testing Strategy

- Gate test: a diagnosis verdict lacking a learner quote or source quote is
  withheld.
- Gate test: a turn that redraws, restructures, or "cleans up" the learner's
  model is withheld as model-ghostwriting.
- Gate test: a diagnosis turn interleaving quizzes/attacks is out of shape.
- Contract: `R-*` invariants bind diagnosis shape + grounding + no-rewrite to
  these tests.

## Boundaries

- Always: quote learner + source on every verdict; one diagnosis turn per
  presentation.
- Ask first: allowing the learner to request the corrected model explicitly
  (opt-in escape hatch) — default no.
- Never: rewrite the model; run the attack battery inside the reading flow;
  graduate with naive-student clones here.

## Success Criteria

1. A presented model yields a structured, fully quoted diagnosis in one turn.
2. Ungrounded or ghostwritten responses are withheld by the gate.
3. The revision loop closes on a clean (or consciously parked) model recorded
   verbatim in the handoff.
4. Zero turns of the teach flow's attack/repair machinery occur inside a
   reading session.

## Open Questions

- None blocking; the photo → excalidraw ingestion path from the solo-first
  ADR is reused as-is if the learner photographs a drawn map.
