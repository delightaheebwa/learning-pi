# Spec: `critique` — bring your own model or interrogation, get it diagnosed

Status: implemented 2026-11-25.

Mode: standalone. It sits alongside `/teach` and `/read` and shares none of
their per-turn machinery.

## Objective

Add one lightweight flow for the two things the learner already does in a plain
chat:

1. **Explain-back.** The learner talks through their mental model of a topic in
   their own words, as if teaching it. Pi diagnoses the model: what is right,
   what is wrong, what is vague, what is missing, and what is overgeneralised.
   Pi does not write the corrected model.
2. **Text interrogation.** The learner brings a paragraph from a book or source
   plus their own interrogation of it. Pi diagnoses the interrogation: what is
   read correctly, what is misread, what overreaches the text, what the
   interrogation ignores, and which tests are too weak. Pi does not write the
   corrected interpretation.

Both modes share one contract: **the learner produces the artifact, pi
diagnoses it, and the learner produces the next version.** The reference
conversations are the two shared ChatGPT chats of 2026-11-24/25: the opencode
internals explain-back and the Housel paragraph interrogation.

This is not the interrogation flow. There is no entry gate, no triage table, no
dependency tree, no attack battery, no repair ladder, no graduation clone, no
curriculum position, and no quiz batch. The reading mode's `model-diagnose`
module is the closest existing behavior and the source of the diagnosis shape.

## Capability map

| Module | Responsibility | Depends on |
|---|---|---|
| `critique-session` | Artifact intake, quoted diagnosis, revision loop, close and capture | — |

One module. The mode is small enough that a second module would be inventing
structure.

## Behavior

### Entry

The learner opens with the artifact, not a request for a lecture. If they open
with only a topic or a request to be taught, ask for the artifact in a
`[[TURN:none]]` transition and stop: either their own-words model, or the source
excerpt plus their interrogation. This is the only precondition, and it is not
the teach flow's entry gate. It is the inverse of "never teach cold": pi never
critiques an empty page.

One `[[TURN:claims]]` turn with `turn_kind:"plan"` is legal only to confirm the
mode and the anchor after the artifact exists, then stop. It carries no lesson
plan and no preview. Asking for the artifact is a `[[TURN:none]]` transition,
not a claims turn.

### Diagnosis

One presentation yields exactly one `[[TURN:claims]]` turn with
`turn_kind:"answer"`. The diagnosis has five buckets in explain mode:

- **right** — load-bearing mechanisms the learner stated correctly. Confirm
  briefly; no praise, no polished restatement, no re-teaching.
- **wrong** — a claim that is false. Quote the learner's verbatim words and,
  when an anchor exists, the passage or case that contradicts it. Say what is
  wrong. Supply no corrected version.
- **vague** — a claim with no mechanism. Quote it and ask the mechanism
  question: what moves, which way, and why. Do not answer it.
- **missing** — a load-bearing condition, regime, or failure mode the model
  omits. Name it and point at the anchor passage; never explain it into place.
- **overgeneralised** — a rule stated wider than it holds. Give one concrete
  case that satisfies the learner's words as written and breaks the rule. Do
  not state the patched rule.

Interrogate mode uses the same turn and a parallel set:

- **right** — what the interrogation extracts correctly.
- **wrong** — a misreading. Quote the learner and the paragraph.
- **overreach** — a claim the paragraph does not support. Quote the paragraph
  and name the limit; do not supply the intended reading.
- **missing** — a load-bearing aspect of the paragraph the interrogation
  ignores. Quote it; do not interpret it for the learner.
- **weak test** — a question or counterexample that does not test the claim it
  names. Say why it misses; do not replace it.
- **process** — optional, one line on how the learner interrogated, not on the
  content: what they did and one adjustment. No praise, no answer.

Either mode ends with **next**: at most two sharper questions or one thought
experiment. No answers.

Every verdict quotes the learner's verbatim words. When an anchor is attached,
every wrong, missing, overreach, overgeneralised, and weak-test verdict also
quotes the anchor. An invented or paraphrased "you said..." is
`PRIOR_UNGROUNDED`, the same standard as every other flow.

### Verification

Every substantive turn is dispatched to `fact-check` before the learner sees
it. The gate binds the receipt to the exact full draft in `rendered_content`
and to the critique payload: the learner's artifact in `critique_artifact`,
the anchor in `critique_anchor`, and the mode in `critique_mode`. A missing or
mismatched receipt withholds the turn. A diagnosis that returns an unquoted
verdict, or that writes the corrected model or reading, is withheld with the
same codes the reading flow uses: `UNQUOTED_DIAGNOSIS` and
`DIAGNOSIS_REWRITE`. A diagnosis before the learner presents an artifact is
withheld with `CRITIQUE_BEFORE_ARTIFACT`.

### Reveal limit

Pi may name a verdict, quote evidence, and pose a test. Pi may not:

- write the corrected model or the corrected interrogation;
- state the missing mechanism or the patched rule;
- state what the paragraph "really means" or return a restructured reading;
- clean up, merge, or polish the learner's words;
- answer its own next question.

"Just tell me" is answered with a source pointer or a narrower question. The
reading mode's no-rewrite rule carries over: correcting a single link is legal
only as a quoted verdict, never as a rebuilt artifact.

### Revision loop

The learner revises and presents again. Each presentation gets one fresh
diagnosis. The loop closes when the learner declares a final version, or when a
presentation draws only `right` verdicts and consciously parked `missing`
items, recorded in the learner's own words. There is no attempt cap and no
forced number of rounds.

### Close and capture

Full capture, in the learner's words, for **both modes**. At close the learner
states the final version. Explain mode closes on the revised model. Interrogate
mode closes on the revised interrogation plus what the learner now thinks.
Neither mode closes on a pi-written summary. If the learner stops mid-loop, the
note preserves v1 and the diagnosis, marks v2 open, and pi invents no v2.

Both modes write the same session artifact:
`Learning System/Sessions/Session — Critique (<topic>) — <date>.md`. The shared
sections are `## Session Info`, `## Diagnosis`, `## Concepts`, `## Mistakes`,
and `## Open questions`. The mode-specific sections preserve the artifacts
verbatim:

| Mode | v1 section | v2 section |
|---|---|---|
| explain | `## Model (v1)` | `## Model (v2)` |
| interrogate | `## Source excerpt` then `## Interrogation (v1)` | `## Revised interrogation (v2)` then `## What I now think` |

Then a `clerk` ingest writes the matching wiki pages and Active Concepts rows.
Each concept page carries the learner's words verbatim under
`## My understanding`, marked `status=learner-note`. Pi never writes that
section. Both modes schedule the concept rows at +3d like any new concept.
When an anchor exists, graded review cites it. When no anchor exists, the row
is marked `anchor: none` and recorded as a self-model retrieval, not a
source-graded one.

No lesson file is written. No curriculum position moves. No
`Pending Ingest.json` lesson handoff is created. The capture is a standalone
ingest, the same shape as the 2026-11-24 Housel ingest, plus the diagnosis and
the v1/v2 trail that ingest could not preserve.

### Anchor policy

- Explain mode: the anchor is optional. A path, a pasted excerpt, a docs page,
  or the learner's own notes all count. With no anchor, pi diagnoses internal
  consistency, mechanism gaps, and concrete counterexamples, and may not claim
  a source contradiction.
- Interrogate mode: the anchor is the paragraph and is required. No paragraph,
  ask for it and stop.

## Hard rules

- Artifact first. A diagnosis before the learner presents one is withheld.
- Diagnose, never rewrite. The corrected model and the corrected interrogation
  are the learner's to write.
- One diagnosis per presentation. No interleaved quizzes, attacks, hints,
  repairs, or widgets.
- Quote the learner on every verdict; quote the anchor on every contradiction,
  omission, overreach, overgeneralisation, or weak test.
- The learner authors v1 and v2. Capture preserves both verbatim.
- No teach-flow entry gate, no triage, no dependency tree, no attack battery,
  no repair ladder, no naive clone, no curriculum position.

## Commands

- Verify (offline): `scripts/learn-check --no-load`
- Verify (full): `scripts/learn-check`
- Doc drift: `python3 scripts/check-docs`
- Diff floor: `node scripts/floor-guard.mjs`

## Project structure

New:

- `.pi/prompts/critique.md` — entry point carrying `[[FLOW:critique]]`
- `.pi/skills/learning-critique/SKILL.md` — the two-mode procedure
- `docs/specs/SPEC-critique.md` — this file

Edited:

- `.pi/APPEND_SYSTEM.md` — router entries and the critique stance paragraph
- `.pi/agents/fact-check.md` — critique diagnosis checks and codes
- `.pi/extensions/learning-gate/gate-core/primitives.ts` — `FLOW_TAG_RE` and
  `FLOW_TURN_KINDS` (`critique` allows `plan` and `answer` only)
- `contracts/learning-core.json` + `CONTRACT.md` — additive `C-critique-*`
  invariants
- `test/contract/check_learning_layer.py` — prompt map (9→10), skill set (6→7),
  resource phrases
- `test/gate_test.mjs` — critique flow and withholding cases
- `test/contract/load_probe.py` — expected prompt
- `README.md`, `FIELD-GUIDE.md`, `docs/README.md`,
  `docs/teaching-methodology.md` — current-flow maps

Untouched:

- `.pi/skills/learning-teach/`, `.pi/skills/learning-read/`, every existing
  invariant and its tests, `.opencode/`, `state/Skills/`.

## Contract additions

Six hard invariants and one policy invariant, all additive:

| Id | Rule |
|---|---|
| `C-critique-flow` | `[[FLOW:critique]]` routes `/critique` and the natural-language triggers; only `plan` and `answer` claims turns are legal. |
| `C-critique-verified` | Every diagnosis turn carries a passing `fact-check` bound to the full draft and the critique payload; a missing or mismatched receipt withholds the turn. |
| `C-critique-artifact-first` | No diagnosis until the learner presents a model or an interrogation. |
| `C-critique-grounded` | Every verdict quotes the learner's verbatim words; every contradiction, omission, overreach, overgeneralisation, or weak test also quotes the anchor when one exists. |
| `C-critique-no-rewrite` | Pi never writes the corrected model, the corrected interrogation, the missing mechanism, or a restructured reading. |
| `C-critique-capture` | Close preserves v1, the diagnosis, and v2 verbatim for both modes, or marks v2 open when the learner stops; the learner authors both versions; no lesson file and no curriculum move. |
| `C-critique-no-machinery` (policy) | No triage, attack, repair, clone, quiz, or widget turns inside the flow. |

## Testing strategy

- Gate test: a critique diagnosis with no passing `fact-check` is withheld
  (`NO_FACT_CHECK_MATCH` / `FACT_CHECK_MISSING_DRAFT`).
- Gate test: a critique diagnosis with no passing `fact-check` is withheld
  (`NO_FACT_CHECK_MATCH`).
- Gate test: a verifier ISSUES verdict for an unquoted verdict is withheld
  (`FACT_CHECK_ISSUES`), and the verifier resource check pins
  `UNQUOTED_DIAGNOSIS`.
- Gate test: a verifier ISSUES verdict for a rewritten artifact is withheld
  (`FACT_CHECK_ISSUES`), and the verifier resource check pins
  `DIAGNOSIS_REWRITE`.
- Gate test: a verifier ISSUES verdict for an empty artifact is withheld
  (`FACT_CHECK_ISSUES`), and the verifier resource check pins
  `CRITIQUE_BEFORE_ARTIFACT`.
- Gate test: `triage`, `attack`, `repair`, `autopsy`, or `idea` as a
  `[[FLOW:critique]]` claims kind is `FOUNDATION_INCOMPLETE`; an attack probe or
  quiz interleaved into a claims turn is `CRITIQUE_OUT_OF_SHAPE`.
- Resource test: the skill's explain-mode template carries `## Model (v1)` and
  `## Model (v2)`, its interrogate-mode template carries `## Interrogation
  (v1)`, `## Revised interrogation (v2)`, and `## What I now think`, and both
  preserve the versions verbatim with no lesson file.
- Resource tests: the prompt carries `[[FLOW:critique]]`; the skill names both
  modes, the no-rewrite rule, and the fact-check step; the router maps the
  triggers.
- Existing suites: none removed; existing invariants: none edited.

## Boundaries

- Always: run `scripts/learn-check --no-load` before every commit; keep the
  contract diff additive; land contract edits in one `revise(contract):` commit
  with the user's approval of the diff.
- Ask first: any change to an existing invariant, any new agent file, any change
  to the gate engine's core turn-tagging rule.
- Never: remove or reword an existing invariant; edit vendored `.opencode/` or
  `state/Skills/`; weaken `CONSTRAINTS.md`; write the learner's model.

## Success criteria

1. `/critique` with a model starts explain-back; `/critique` with a paragraph
   and an interrogation starts text interrogation. Neither starts a teach,
   read, review, or solo session.
2. A presented artifact yields one fully quoted diagnosis in one turn, with no
   corrected version.
3. A revised artifact yields one fresh diagnosis; the loop closes on the
   learner's final version.
4. Close captures v1, the diagnosis, and v2 verbatim, creates the wiki pages and
   concept rows, and moves no curriculum position.
5. `scripts/learn-check --no-load` passes with the new prompt, skill, flow, and
   `C-critique-*` invariants.
6. `/teach`, `/lesson`, `/continue`, `/review`, `/solo`, and `/read` behave
   exactly as before.

## Open questions

- Review scheduling for source-less explain-back. The recommendation above is
  to capture and schedule at +3d but mark the row `anchor: none`, so review
  never pretends to grade against a source it does not have.
- Whether `/critique` should also be installable outside `state/` for code
  explain-back. The pi resources load from `state/` only; a path or pasted
  excerpt works today. A user-level install is a separate change.
- Photographed book pages. The anchor is text, so a photo must be transcribed
  verbatim before diagnosis; the verifier grounds on the transcription, not the
  image. A vision-based verifier is out of scope for this change.
