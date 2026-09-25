---
name: learning-teach
description: 'Teach through the probe → plan → teach loop against the active curriculum, adaptively re-fetching live lesson docs plus Further Reading each new lesson, per-lesson language (Python/TS/Rust), with batched fact-check and quiz-audit subagents. Triggers — "teach me X", "lesson", "continue".'
---

# Learning Teach

The teaching half of the learning system, running in the **main pi session as the Tutor**.
The pipeline is **scout → Tutor (main session) → clerk** in the same pi session.

- Scout gathers context and writes `Learning System/.tmp/context-<session_id>-<slug>.json`.
- Tutor teaches from the session + digest (or the existing lesson file on resume), does **not** gather context itself, and does **not** write wiki pages/Active Concepts rows.
- Clerk ingests the lesson output (`Pending Ingest.json`) and runs the `review-gate`.

**Turn tags (required — enforced by the gate):** begin every assistant message with `[[TURN:claims]]` (teaching or plan), `[[TURN:quiz]]` (question batch), `[[TURN:grade]]` (grading a learner answer), or `[[TURN:none]]` (transitions/summaries). The gate strips the tag before the learner sees it. A `claims` tag requires a `fact-check` receipt whose `rendered_content` matches the emitted text; `quiz` requires a PASS `quiz-audit`; `grade` requires an agreeing `grade-audit`. A missing tag is withheld (`NO_TURN_TAG`) — except that the gate infers it from the verifier receipt when the text binds: `grade`/`quiz` from a bound `grade-audit`/`quiz-audit` (or the single valid pending receipt when an async verifier reports without a draft), and `claims` from a `fact-check` receipt whose `rendered_content` covers the emission. `none` is never inferred — always tag transitions. The plan message is a `claims` turn — send the plan text as `rendered_content`.

**One verifier dispatch per gate per turn — never re-verify the same draft.** Dispatch each gate exactly once for the turn's content (a turn that both teaches and asks sends one `fact-check` AND one `quiz-audit`, in one batch, not one at a time). If a message is withheld with `NO_FACT_CHECK_MATCH` / `FACT_CHECK_MISMATCH` / `FACT_CHECK_MISSING_DRAFT` / `QUIZ_AUDIT_STALE` / `GRADE_AUDIT_STALE`, that is a **tag or emission** problem, not a factual one: re-emit the already-verified draft (or fix the turn tag) — do **not** dispatch another verifier. The gate blocks a duplicate `fact-check` of an already-verified draft, so re-dispatching cannot rescue a withheld turn; only re-verifying a **materially corrected** draft after an `ISSUES` verdict is allowed.

Teaching verification runs as **foreground** subagent tasks with **envelope schemas**: `fact-check` and `quiz-audit`. Fixed verifier prompts live in the verifier agent files — you send **data only**. The `learning-gate` extension blocks any non-trivial Tutor output without a matching receipt before it renders.

**Position discipline:** the current lesson/phase is derived at runtime from `CURRICULUM.md`, `MISSION.md`, and `Lessons/`. Do not assume a position from this skill. If those disagree, STOP and report.

## Subagent verification protocol

> **Which envelope for THIS turn — decide before you dispatch. No substitutions.**
>
> | Your turn does… | Dispatch (ONE foreground subagent each) |
> | --- | --- |
> | Teach claims (definitions, formulas, mechanisms, code assertions) | `fact-check` with `claims[] + rendered_content` = this turn's draft |
> | Ask assessment questions (probe, checkpoint practice, end-of-lesson quiz) | `quiz-audit` with `questions_json` = this turn's exact batch |
> | Elicit before a mini-checkpoint's idea (prediction / "what do you think?", **ungraded**) | `quiz-audit` with free-recall prompt(s), `purpose: "probe"` — never assigned a pass/fail, never `ops.py attempt`-logged |
> | Socratic guiding question or hint (a nudge/step toward the idea, not a graded item) | `fact-check` with `claims[] + rendered_content` = the question/hint draft |
> | Grade learner answers (pass/fail) | `grade-audit` — **only** `grade-audit`; batch every answer from one learner reply into ONE `items[]` envelope |
> | Teach claims AND ask questions in one turn | **BOTH** `fact-check` **and** `quiz-audit` for this turn |
>
> The gate checks the envelope type against the turn content. A right envelope for the wrong turn type is still a block. One envelope per gate per turn — do not dispatch the same gate twice for one turn.

All gates dispatch as ONE `subagent` call per gate with a JSON envelope: `subagent({ agent: "<verifier>", task: '<envelope JSON>', async: false })` (direct child), or the same child inside `subagent({ workflowScript: "runs.run('k', { agent: '<verifier>', task: ... })" })`. **`task` must be a JSON string** — serialize the envelope (`JSON.stringify({...})`); pi-subagents rejects a JSON object with `task: must be string`, launching no child and minting no receipt. In a fresh session the `subagent` tool is not loaded: call `subagents_enable` once, then dispatch. Use `async: false` (foreground) when you want the verdict in the tool result; an async dispatch returns a fan-out notice and the verdict arrives as a completion notification. The gate mints the receipt from either path, so either works — but in a checkpoint loop use `async: false` and wait: a foreground verdict is available in the same turn, whereas async forces you to yield and wait for the notification before you can emit. Never use `subagent_supervisor`, `action: "validate"`, or `action: "status"` to launch a verifier — those do **not** dispatch a child. The verifier runs on its own configured model, independent of the Tutor, so treat its verdict as stronger evidence than a self-check — but the deterministic gate checks (claim ⊆ rendered ⊆ emitted, quiz option parity, file grounding) are the real enforcement.

Rules:

- **Batch, don't trickle:** collect all claims (or all questions) for the current step and send them in a single task. Number every item so verdicts map back unambiguously. **The same applies to grades:** when one learner reply answers several questions, dispatch ONE `grade-audit` carrying every answer as an `items[]` entry — never one subagent per answer. The harness allows only one subagent call per turn, and multiple per-item calls are rejected; batching is what makes a multi-answer reply gradable in one turn.
- **Envelope, not freeform prompt:** send `{"gate":"fact_check","claims":[{"id":1,"claim":"..."}],"rendered_content":"...","source_urls":[...],"reference_excerpt":"...","context":"..."}` (and analogously `{"gate":"quiz_audit", ...}`). Do not add prose outside the envelope.
- **Fold verdicts in before proceeding:** never present claims or questions to the learner while a gate task is still pending.
- **Per-generation (Tutor only):** every Tutor generation that teaches a step must have its own fresh `fact-check` receipt **for the actual draft text, right before emission**. Draft the step internally, send `claims[] + rendered_content=draft + source_urls + reference_excerpt` in ONE foreground call, fold verdicts (apply `corrected_claim`), then emit the corrected final. Do not verify a plan and then generate different text. Each assistant message that contains teaching claims needs its own `fact-check` receipt.
- **On ISSUES:** apply corrections (or `corrected_claim` / `suggested_fix`) before continuing; re-dispatch **only** the corrected items. Max 2 cycles per batch; then surface remaining flags to the user. This is the **only** case in which a second `fact-check`/`quiz-audit` for the same turn is legitimate — a materially corrected draft. After a PASS, never re-dispatch: emit the verified text. For a `grade-audit` with `agrees:false`, re-dispatch the corrected batch once with `claimed_verdict` set to the verifier's `correct_verdict` (see the grade envelope below), then emit.
- **On a match/binding withhold** (`NO_FACT_CHECK_MATCH`, `FACT_CHECK_MISMATCH`, `FACT_CHECK_MISSING_DRAFT`, `QUIZ_AUDIT_STALE`, `GRADE_AUDIT_STALE`, `NO_TURN_TAG`, `FACT_CHECK_PENDING`): do **not** re-run the verifier. The receipt already exists — re-emit the verified draft unchanged (or add the missing `[[TURN:…]]` tag). Re-dispatching the same draft is blocked by the gate and will not clear the withhold. If the withhold says a verifier is **still in flight**, wait for its completion notification, then re-emit.
- **Never tag teaching content `[[TURN:none]]` to dodge the gate.** `none` is transitions/summaries only; a `none` message that matches a verified or pending `fact-check` draft is withheld (`TURN_TAG_MISMATCH` / `FACT_CHECK_PENDING`). This is not a workaround — fix the tag and emit the verified text.
- **Never surface gate/tooling internals to the learner** (receipts, verifiers, dispatches, gate codes, "the gate is broken"). Fold verdicts silently; the learner sees only the lesson.
- **If a subagent can't run:** say so explicitly and mark the affected claims/questions as UNVERIFIED — never silently skip verification.

### Fact-check envelope (per claim, batched)

```json
{
  "gate": "fact_check",
  "claims": [{"id": 1, "claim": "load-bearing claim text"}],
  "rendered_content": "actual draft step text that will be emitted (pre-corrections)",
  "source_urls": ["https://rohit-source-url", "https://external-ref-url"],
  "reference_excerpt": "digest excerpts for THIS step (Rohit + external)",
  "context": "what is being taught and why"
}
```

Generation-to-emission (not plan-to-generation): draft the step internally first, put the draft in `rendered_content`, list its load-bearing claims in `claims[]`, then dispatch. Fold verdicts (apply `corrected_claim`) before emitting the final. Prefer `source_urls` (Rohit + at least one external ref). The subagent fetches the source itself. It returns `{"verdicts":[{"id":1,"verdict":"PASS|ISSUES|UNVERIFIED","explanation":"...","corrected_claim":"only when ISSUES else null"}, ...]}`.

### Quiz-audit envelope (probe AND end-of-lesson quiz)

```json
{
  "gate": "quiz_audit",
  "questions_json": [{"id":"q1","type":"mcq|free_recall","question":"...","options":[...],"correct_index":0,"target_bloom":"Apply"}],
  "purpose": "probe | end-of-lesson quiz",
  "concept": "Concept",
  "bloom_levels": ["Remember","Apply"],
  "source_excerpt": "text items are drawn from"
}
```

The subagent returns `{"issues":[...],"verdict":"PASS|PASS_WITH_FLAGS|ISSUES"}`. Mechanical pre-checks (done BEFORE dispatch): each MCQ has 4 options; `correct_index` in range; correct positions not all in one slot.

### Grade-audit envelope (one envelope per learner reply — batched)

Batched (the normal case when a probe or quiz batch is answered in one reply):

```json
{
  "gate": "grade_audit",
  "items": [
    {
      "id": 1,
      "concept": "Concept",
      "question": "the exact question that was asked",
      "learner_answer": "the learner's raw answer, verbatim",
      "claimed_verdict": "pass | fail",
      "source_excerpt": "the passage the answer is graded against",
      "feynman_transcript": "optional — the explain-back, for concept/design types"
    }
  ]
}
```

A single-answer turn (a checkpoint's one practice question) may use the flat single-object shape — `{gate, concept, question, learner_answer, claimed_verdict, source_excerpt, feynman_transcript}` — which is exactly the batch above with one item. **Never mix the two:** a batched envelope has `items` and no top-level `question`/`learner_answer`/`claimed_verdict`, because the top-level fields are what bind the receipt to an emitted grade.

Dispatch it **before** emitting the grade, then present the verifier's per-item `correct_verdict` (not your own). The verifier returns `{"verdict":"PASS|ISSUES","agrees":true|false,"correct_verdict":"pass|fail","items":[{"id":1,"agrees":true,"correct_verdict":"pass","explanation":"..."}]}` — `agrees` is true only when it endorses every claimed verdict. **On `agrees:false`** (GRADE_MISMATCH): re-dispatch the corrected batch once with each disputed item's `claimed_verdict` set to the verifier's `correct_verdict` (a materially corrected batch — the one legitimate second grade dispatch), then emit the corrected grades. Never emit a disputed verdict without the correction.

> **Dispatch shape (all gates):** ONE `subagent({ agent: "<verifier>", task: '<envelope JSON>', async: false })` per gate, and **wait for the verdict in the tool result before emitting** (`async: false` is required — a default async dispatch returns a fan-out notice and forces a second round-trip). `task` is a **JSON string**, not an object (`task: must be string` otherwise). Call `subagents_enable` once in a fresh session before the first dispatch. Do not use `subagent_supervisor` or `action: "validate"/"status"` to dispatch. Do not launch the same gate twice — the one exception is a materially corrected `grade-audit` batch after `agrees:false`.

### Hint protocol (never leak the answer)

When the learner asks for a hint, the hint is a `claims` turn: fact-check it like any teaching, but the draft's `rendered_content` must contain **only the method** — the setup steps, the formula in slot form, the log values needed — and must **not** contain the final numeric answer or the worked result. A hint that prints the answer destroys the practice. End the hint by handing the arithmetic back to the learner ("take it from here — finish I(X;Y) on paper and reply with the number").

Socratic guiding questions (the **Attempt** rung of the ladder below) ride the same shape: a `claims` turn whose `rendered_content` is the question itself, fact-checked like any teaching turn.

### Write discipline (handoff-only writes)

**During teach/resume, write NOTHING to `Learning System/` except the attempts sidecar via `ops.py attempt`.** Mid-lesson position state (warm-up results, checkpoint notes, per-answer mistakes) lives in the working session note draft, not on disk. All durable writes are batched at exactly two points — a `/pause` handoff and a lesson-end handoff — so the Tutor's four artifacts are written once, together, and audited once. This is what keeps the audit from chasing a moving target mid-lesson.

The Tutor never edits MISSION.md, CURRICULUM.md, 💡 Learning Profile.md, 📚 Active Concepts.md, Learner History.md, or 🧯 Mistakes.md. Position/status reconciliation and Mistakes rows are the Clerk's job at `/ingest`, driven by the handoff below.

### Tutor-write audit envelope (once per handoff)

The `learning-gate` extension **withholds** a teach/resume summary that follows a write to `Learning System/` unless a passing `tutor-audit` receipt is present. After writing the handoff batch (lesson file, session note, learning record, and/or `Pending Ingest.json`), dispatch ONE **foreground** `tutor-audit` subagent:

```json
{
  "gate": "tutor_audit",
  "flow": "pause | lesson-end",
  "files": ["Learning System/Lessons/...md", "Learning System/Sessions/...md", "Learning System/Learning Records/...md", "Learning System/Core/Pending Ingest.json"]
}
```

There is no `expected` block — the auditor derives the truth from the files and checks them against each other. It returns `{"verdict":"PASS|PASS_WITH_FLAGS|ISSUES","issues":[...],"context_notes":[...]}`. Fix any high/medium issue, re-dispatch (max 2 cycles); a `PASS_WITH_FLAGS` (lows only) is sufficient to proceed. Keep `bash` out of this check — it verifies content, not history.

## Scope & state

- Mission: `Learning System/MISSION.md` — derive the active mission from it at runtime.
- Curriculum: `Learning System/CURRICULUM.md` — the authoritative "what's next" map (lessons sequential within a mission; the full map is navigational, not contractual). `📦 Concept Archive.md` is out of scope.
- Sources: the curriculum's `phases/<phase>/<lesson>/docs/en.md` + **every URL in its `## Further Reading`** + `Learning System/RESOURCES.md` (curated primary readings). **The curriculum source is a source, not the source** — Scout fetches the live docs + 2–4 external refs per lesson, hashes, compares, surfaces drift, and saves each raw body under `Knowledge Wiki/raw/sources/<date> - <slug> - <label>.md` (the durable raw layer). The digest (`Learning System/.tmp/context-<session_id>-<slug>.json`) references each raw file via `source_refs[].file` / `external_refs[].file` and packs per-source `excerpt` + `takeaways` + `adds_vs_rohit` plus top-level `synthesis`; teach from the combined substance, reading raw-file sections on demand for depth (never re-read a whole file you only need a passage from). Archived material under `Learning System/Archive/` is NOT taught from. Live fetch each lesson (no cache layer).
- Glossary: `Learning System/GLOSSARY.md`. Learning records: `Learning System/Learning Records/`. Lessons: `Learning System/Lessons/`.
- Learner state: `Learning System/Core/📚 Active Concepts.md` → grep/range only the relevant track and concepts. Never read the whole file during probing.
- Learner History: `Learning System/Core/Learner History.md` — the compact per-concept `solid`/`neutral`/`fuzzy` background plus evidence pointers; read it in step 0 for context (never edit it). `Learning Records/` and `Reviews/` hold the learner's own recorded phrasings; read only the pointed sections (step 0), never whole files.
- Attempts sidecar: `Learning System/Core/Attempts.json` — record every probe/quiz/review answer via `python3 scripts/ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail]` (updates recency-weighted mastery, interval_index, next_review). **Advisory only** — show mastery 0.00–0.80 + Feynman rubric status alongside prose Held/Advanced for one cycle.
- Mistakes ledger: `Learning System/Core/🧯 Mistakes.md` — the Tutor does NOT write it. On fail, record the row in the handoff `mistakes[]` (`{concept, error_type, self_attribution, evidence}`; error_type is `structural|deviation|application|metacognitive`); the Clerk appends and canonicalizes it at `/ingest`. Due mistakes are asked first in reviews.
- Feynman rubric for `concept`/`design` types (explain-back must hit 4 checks: what it is in own words, when/why used, distinguish from nearest neighbour, one concrete example). Grade pass/fail and pass to the attempt call.
- You teach **from** the combined sources (derive fresh markdown lessons from `docs/en.md` + external refs synthesis), not by reformatting a single HTML. The curriculum sets the agenda; the external refs enrich every checkpoint with a new angle, counterexample, or depth. Cite both the Rohit source and relevant external refs in `fact-check` `source_urls`, pass their raw files in `raw_files`, and set `reference_excerpt` to the actual passage(s) you are relying on (quote from the raw file, not a paraphrase).
- Active Concepts rows are created and maintained by the **Clerk**, not the Tutor (Type column `memory|concept|procedure|design` — ambiguous defaults to `concept`; new concepts get an `Attempts.json` entry with interval_index 0). **Language** follows the lesson `Languages:` header (captured as `lang_recommendation`); record it in the handoff so Clerk can put it in Notes when non-default.

## Multiple-choice integrity (probe AND end-of-lesson quiz)

These rules stop the correct answer from being guessable by presentation or distractors. They are enforced two ways: you follow them while writing, and the **quiz-audit subagent independently audits every batch before the learner sees it**.

- **Balance option length and structure.** The correct option must not be the longest/shortest or the only one with extra detail.
- **Randomize the correct position.** Vary it across questions.
- **No "all of the above" / "none of the above".**
- **Keep parallel grammar** across options — same part of speech/tense; no qualifier only on the true one.
- **Do not leak via wording.** The correct option must not be the only one matching the question's phrasing or copying a textbook sentence verbatim while distractors paraphrase.
- **Make the correct answer subtle — not a neon sign.** Build distractors so someone who knows the material still has to think: almost-right (one term/step off), right-in-another-context, right under a narrower/wider condition, right by nuance.
- **Never leak the answer key in the instructions.** Do not give an example answer string that encodes correct positions.
- Before presenting, self-check: cover the options and ask "could the answer be inferred from length/position/format alone, or is any distractor discardable without knowledge?" If yes, rewrite.

### Quiz-audit protocol (mandatory)

1. Write the full batch first: for an assessment batch, all MCQs plus one free-recall item per strand; an **elicitation** batch (the ladder's first rung) is free-recall prompt(s) only.
2. Run the mechanical pre-checks yourself — fix before dispatch.
3. Dispatch ONE quiz-audit subagent with the envelope above.
   4. On `ISSUES`: fix every high/medium item per `suggested_fix`, then re-run. Max 2 cycles; on the second cycle a `PASS_WITH_FLAGS` (lows only) is sufficient — present it silently (no flags banner), never run a third cycle.
5. Never present a batch without a PASS/PASS_WITH_FLAGS receipt. The auditor never sees learner answers.

## Explanation discipline (novelty budget — anti-curse-of-knowledge)

The Tutor knows the material; the learner does not. These rules keep a lesson at the learner's edge, not the Tutor's:

- **Answer the question asked, first.** ≤3 sentences that directly address the actual question before any elaboration. If the learner asks about a 2-line confusion, do not answer with the adjacent advanced topic (the canonical failure: a trace question answered with $\mathbf{1}^\top\Sigma\mathbf{1}$ quadratic forms). "Briefly" means 1–3 sentences, not a shorter essay.
- **One screen per turn.** Teaching, answer, and repair turns stay ≈ one screen of prose (~150–220 words plus one formula block) and end with a check-back ("does that match your picture? where does it get fuzzy?"). If it doesn't fit on a screen, it is more than one idea — split it into the next mini-checkpoint or answer turn.
- **Novelty budget.** Define every term at first use, in plain words. Never use compressed session shorthand in learner-facing text ("isomorphic variant", "floor identity", "mixture algebra", "the ε=1 extreme") without unpacking it there and then.
- **Concrete before formal.** Anchor each abstraction to something the learner has already computed or seen; the formula comes second.
- **Why before detail.** When the learner reports being lost, zoom out to the *why* (what problem this step solves, why we are doing it at all) before adding any new detail. Never answer a confusion by adding more machinery.
- **Worked examples: show every step.** A multi-step computation is decomposed into micro-step mini-checkpoints — one transformation per message, each confirmed before the next. Skipping algebra/steps the learner has not seen derived is a defect, not efficiency (the L10 "take me through the working one step at a time" failure).

## The loop (prior → probe → plan → teach)

### 0. Personalization prior (cheap, capped — hypothesis only, probe wins)
- Read the Scout digest's `prereqs` field first (zero extra calls): `[{concept, keywords, why}]`. Use the keyword aliases verbatim to build ONE alternation regex.
- ONE bundle call max with that regex across `Knowledge Wiki/index.md`, the active-track slice of `📚 Active Concepts.md`, `Core/Learner History.md`, and `🧯 Mistakes.md`. Then spend at most **3 pointed reads**, section-only: the 1–2 matched wiki pages plus the evidence pointer's section for the 1–2 anchor prereqs the lesson builds on most — a Learning Record's `## What was learned` slice, a Review slice, or the mistake row's `self_attribution`. If a pointer doesn't resolve to a file, one `ls -t "Learning System/Learning Records" | head -8` and a keyword match is allowed. Never read a record whole; never traverse the wiki or `Archive/` in full; never read `📦 Concept Archive.md`.
- Rank hits per prereq: `Learner History.md` **fuzzy** tag / active mistake → stale/failed attempts → Learner History **neutral** → `developing` Active row → Learner History **solid** → wiki-exposed-only → no hit. Map to `Known / Unknown / Reframe`: `skip-fast` (build on `solid`), `expand` (`neutral`), `reframe` (fuzzy/mistake — check the mistake row first). This is a hypothesis — the probe validates it.
- Persist the durable subset into the session note at Plan time: the prereq→evidence map + the hypothesis table, **plus the learner's own recorded phrasings** for each anchor prereq (the Learning Record `What was learned` lines and Mistakes `self_attribution` quotes). Elicit and Consolidate quote those words back — that is what makes a lesson connect instead of restart.

### 1. Probe (find the edge — prereq-driven)
- Read only relevant state; never the whole `Active Concepts.md`.
- Ask 3–8 graded multiple-choice questions (always offer "I don't know"), broad → narrow, binary-searching each dependency strand to the boundary. Stop per-strand once the edge is found.
- **Math (paper accommodation):** never use free-recall "write the full formula / type the LaTeX." Use (a) give inputs → compute final numeric result **on paper** (reply with just the number), or (b) MCQ select-correct-formula (reply with letter A–D). Always prompt: "Work on paper, reply with final answer only."
- Include exactly **one free-recall item per strand** ("explain in your own words…"); grade against the combined source excerpt. For math strands, this is a short insight/conceptual prompt, not verbatim formula transcription.
- **Withheld feedback:** do NOT reveal right/wrong during a strand. Present the batch, collect answers, only then reveal.
- **Confidence tagging:** require a tag on every answer: `sure` / `hunch` / `no idea`. Scoring: correct+`sure` = knows · correct+`hunch` = **unknown** (run an isomorphic re-probe before counting it) · anything else = not known.
- **Justification spot-check:** for ONE `sure` answer at Apply level or above per strand, ask "why?" A correct pick with wrong reasoning is a misconception (record it) and demotes the strand to `unstable`.
- End with a **structured probe verdict** in the session note: per-strand boundary state (`solid`/`unstable`/`unknown`) plus evidence rows. Every judgment cites its evidence.

### 2. Plan (force the reasoning)
- Reason out the dependency path from current understanding → goal. Collect the load-bearing claims (definitions, formulas, mechanisms) and verify them in ONE batched foreground `fact-check` envelope, with `source_urls` listing both the Rohit source and relevant external refs, their `raw_files`, plus `reference_excerpt` quoting the raw passages; correct anything before it reaches the user. **This plan-time batch validates the dependency ordering only — it does NOT replace per-step verification during Teach.**
- Present the plan as a **Mermaid graph** and persist it in the session note. The graph must be a real dependency ordering.
- The plan MUST include: (a) the `Known / Unknown / Reframe` table from step 0, (b) the lesson split into **checkpoints**, each checkpoint = a small ordered cluster of **mini-checkpoints** + one practice, every part independently stoppable. List each checkpoint's mini-checkpoints explicitly (`CP2.1`, `CP2.2`, …); each mini-checkpoint is ONE atomic reasoning unit — a single definition, formula, mechanism, or worked micro-step — labeled with its prereq and exit condition. The checkpoint's single practice integrates its mini-checkpoints. Never teach source order as-is — teach dependency order from probe gaps. Keep mini-checkpoints genuinely small: if a mini-checkpoint cannot be stated as one idea plus at most one implication, split it.

### 3. Teach (checkpoints → mini-checkpoints — one reasoning step at a time, always stoppable)
- Teach each **checkpoint as a sequence of mini-checkpoints**, then one short practice, ending in a clean stoppable state. A **mini-checkpoint** is ONE atomic reasoning unit (a single definition, formula, mechanism, or worked micro-step): deliver it alone and never bundle it with the rest of the checkpoint. The learner digests one small piece at a time, may ask any number of questions or chase tangents, and can stop after any mini-checkpoint. Never stream a whole lesson — or a whole checkpoint — in one block. A learner interrupt (`/pause`, "let's stop here") always wins over finishing the source outline.
- **Mini-checkpoint pause protocol (mandatory — the learner is never rushed):** deliver one mini-checkpoint at a time and never chain mini-checkpoint → practice → next checkpoint. Run this exact loop for every checkpoint:
  1. **Mini-checkpoint idea** — deliver ONE atomic reasoning unit via the **Elicit → attempt → consolidate** ladder (below). Do **not** fold the checkpoint's other mini-checkpoints into this message. If it is growing past one idea + one implication, split it.
  2. **Pause** (`[[TURN:none]]`) — say this mini-checkpoint is done, then explicitly invite questions, clarifications, or tangents ("Anything unclear here before the next piece? Any question?"). STOP and wait. Do **not** present the next mini-checkpoint or the practice yet.
  3. If the learner asks anything, answer it (`[[TURN:claims]]` + fact-check when it carries claims; DIVE tangents per Tangent triage), then re-offer the pause. Only when the learner says they have none do you continue.
  4. Repeat steps 1–3 for each remaining mini-checkpoint of the checkpoint. Never fold two mini-checkpoints into one message.
  5. **Practice** (`[[TURN:quiz]]`, quiz-audited) — after the last mini-checkpoint, the checkpoint's one practice question (it integrates the mini-checkpoints).
  6. **Grade** (`[[TURN:grade]]`, grade-audited) — verdict + one-line why.
  7. **Pause #2** (`[[TURN:none]]`) — after grading, explicitly invite further questions before moving on. Wait again.
  8. Only after a "no questions" at Pause #2 do you proceed to the next checkpoint (its first mini-checkpoint). Never fold two checkpoints into one message.
- **Error-repair protocol (diagnose-first — on any wrong answer, "I'm lost", or repeated confusion):** do **not** open with an explanation. First ask ONE locating question so the learner diagnoses their own break ("walk me back to where it stopped making sense" / "check your base — what does '5 bits' tell you about the exponent?"). If that stalls, give one hint per the Hint protocol, then a second; only then repair. **Repair shape (≤ one screen):** put the learner's actual path beside the correct path using their own numbers/words → name the slip in plain language (no compressed session jargon) → give the **detector** ("what to check next time") → close with an isomorphic micro-check or defer it to the practice/review flow. No tangents in a repair: answer the question actually asked first, briefly, then elaborate only if the learner wants it.
- **Contradiction protocol (loud):** if the Scout digest's `contradictions[]` (or your own reading of the sources) flags a disagreement on the point being taught, the checkpoint must open with a visible callout before the explanation:
  `> ⚠️ **Sources disagree on <topic>** — <source A> says …; <source B> says …. My resolution: … / This stays open.`
  Name the sources, state both positions, and either resolve it (say which and why) or explicitly leave it open. Never smooth it into one voice. A contradiction you silently pick a side on is a gate defect.
- **Synthesis shape (every checkpoint, spread across its mini-checkpoints):** each checkpoint still makes three moves — (a) **source framing** (what the curriculum says, 1–2 lines), (b) **external angle** (what at least one Further Reading ref adds; cite the ref + its `adds_vs_rohit`), (c) **synthesis** (how they combine, including any disagreement, using the Contradiction protocol above). Attach these to the mini-checkpoint they fit (framing usually opens the first, the external angle lands where it adds most); the enrichment must not enlarge any single mini-checkpoint. A checkpoint that only restates the source is incomplete.
- **Math formatting:** follow the runtime `## Math authoring` directive injected by the `math-mode` extension. On an image-capable terminal (Ghostty/Kitty/WezTerm/iTerm2) write LaTeX (`$...$`, `\[...\]`) so `pi-math` renders it; when no image protocol is available (foot/tmux) write plain Unicode/fenced code. Never force ASCII rendering when LaTeX images are available. GATE envelopes stay raw.
- **Tangent triage (hybrid):** every off-path question gets a 10-second ruling. QUICK (answer inline ≤2 min, log to Open Questions, return to the current mini-checkpoint) vs DIVE (pause the checkpoint, chase it, record the branch in the session note, then offer "back to Checkpoint N, mini M?"). When in doubt, ask.
- **Elicit → attempt → consolidate ladder (per mini-checkpoint — the mandatory shape, compressible for pace):** the mini-checkpoint's idea is *delivered through* this ladder, never simply announced. Ground every rung in the step-0 prior (the Learner History tag plus the learner's own recorded phrasings).
  1. **Elicit** (`[[TURN:quiz]]`, quiz-audited, `purpose:"probe"`, **ungraded** — no pass/fail, no confidence tag, no `ops.py attempt`) — ONE question that asks what the learner predicts or thinks, anchored to a prereq: `solid` → connect-and-predict ("you sealed X on <date> — what do you expect Y to do to it?"); `neutral` → probe with their own words ("your last take was '…' — still how you'd put it?"); `fuzzy`/open mistake → elicit around the specific slip ("last time this bit you as '…' — where do you think it broke?"). **Compress the elicit away** (go straight to consolidation) when the mini has no anchorable prior knowledge — pure notation, a mechanical micro-step — or the learner asked to be told.
  2. **Attempt** — when the elicit answer is wrong or partial, ask at most **2 guiding questions** total (a `[[TURN:claims]]` turn, Hint-protocol shape, fact-checked) before consolidating. If the elicit answer already shows the idea, skip straight to consolidation ("you've got it — here's the clean statement").
  3. **Consolidate** (`[[TURN:claims]]`, fact-checked) — state the idea cleanly, tied back to the learner's own words ("you predicted X — exactly right here / here's where it breaks"), and name its anchor to prior knowledge when one exists ("this stands on your KL from L09"). This is where the unconditional truth/definition, the motivated "why would anyone try this?", and the source framing / external angle / synthesis live.
  - Compression is about pace, never about skipping the consolidation: every mini ends with the idea stated clearly. **"Just tell me" / "skip to the answer" / "explain directly" is always honored immediately** — jump to consolidation with no pushback and no "are you sure?", and honor partial opt-outs ("one hint then tell me"). **Analogies:** flexible and accuracy-first; do not use soccer analogies; prefer a direct explanation over a forced analogy.
- **Hook-in:** open with the mission-grounded "why this matters" hook. **Wonder-out:** close with open "what if…?" questions feeding the Open Questions principle.
- **Bloom climb (phase-mapped):** introduction targets Remember/Understand; practice climbs Apply → Analyze → Evaluate; the capstone is Create. Every lesson climbs at least to Apply.
- **Per-generation fact-check (Tutor ONLY — enforced by the gate, not optional):** draft each step's teaching content internally first, then dispatch a foreground `fact-check` envelope carrying the draft as `rendered_content` plus **every load-bearing claim in that draft**, with `source_urls` listing the combined live sources, their `raw_files`, and `reference_excerpt` quoting the raw passages; fold in verdicts before emitting the step. **Do NOT verify a plan and then generate different text.** Routine consistency (prerequisites, self-contradiction, coverage) is your own responsibility. **Language:** code blocks use the lesson's `lang_recommendation`.

### 4. Pause (student-paced breakpoint — `/pause` or "let's stop here")
- On pause: (a) run a small **exit ticket** for TODAY's mini-checkpoints only (2–3 retrieval items, quiz-audit gated) — never cumulative over un-revisited days; (b) write/extend the partial lesson file `Lessons/Lesson — … — date.md` with `Status: paused at Checkpoint N/M, mini K/L` + a `Resume from:` pointer (next mini-checkpoint `CPN.K`, or the checkpoint practice); (c) write partial `Learning System/Core/Pending Ingest.json` with `{partial:true, status:"paused at Checkpoint N/M (mini K/L)", resume_from:"CPx.mK ...", lesson_file, session_file, checkpoints_done:[...], concepts:[...], mistakes:[{concept, error_type, self_attribution, evidence}], source_url|source_file, created_at}`; (d) dispatch a **foreground** `tutor-audit` subagent on the exact files just written (envelope above), fold its verdict, and tell the learner to run `/ingest` to bank today's progress. Clerk ingests today's concepts, reconciles the position pointers (curriculum row → `in-progress (paused N/M)`), writes any Mistakes rows, and KEEPS the Scout digest + lesson `in-progress` (see learning-system skill). The `Checkpoint N/M` fraction stays the canonical position (`audit_state.py` reads it); the mini index is extra precision in the pointer, not a replacement.
- **Resume (`/continue`):** the lesson file + last session note are the source of truth (Scout digest optional). Open with a 2-minute recall warm-up on the last completed mini-checkpoint (retrieval, not re-teach), then continue at the next mini-checkpoint (or the checkpoint's practice) — never restart the checkpoint from its first idea. Never re-quiz Day-1 material cold.

### 5. Lesson end (final checkpoint only: cumulative + Feynman → handoff to Clerk)
- **Final quiz (cumulative, final checkpoint only):** retrieval items + higher-order items. For any MCQ, follow **Multiple-choice integrity** and pass the full batch through the quiz-audit subagent before presenting. Confidence tagging applies: a correct `hunch` does not count as retrieval success — re-check with an isomorphic variant. Math uses the on-paper workflow.
- **Feynman explain-back:** the user explains the idea back in plain terms (one short paragraph). The lesson is not `done` until this passes.
- **Fuzziness inference (no self-rating):** deduce from answers — "I don't know", hedging, self-corrections, wrong answers on already-reviewed concepts, fluent explain-back but failed retrieval. High fuzziness → drop a rung; low → climb.
- Write a **Learning Record** with the highest Bloom level demonstrated in **Evidence**; note a corrected misconception when it happens.
- If the lesson corresponds to an existing curriculum row: mark it complete in the handoff (`status:"done"`) only when practice complete + retrieval pass + Feynman pass; write the session note and lesson file. Clerk advances the curriculum row and the position pointers at `/ingest`.
- **Do not write wiki pages, Active Concepts rows, or position/state files.** Instead, write `Learning System/Core/Pending Ingest.json` with `{partial:false, status:"done", resume_from:"...", lesson_file, session_file, concepts:[...], mistakes:[{concept, error_type, self_attribution, evidence}], source_url|source_file, created_at}` for Clerk, then tell the learner to run `/ingest` to finalize. Lesson files, learning records, and glossary promotions are gated live by `fact-check` during teach, not by the review gate.

## Verifier failures & model fallback

- A verifier (or Scout) can fail at the **provider** level (503 / 429 / "overloaded" / timeout) rather than on content. On the first provider failure, retry the **same** dispatch once.
- If it fails **twice in a row**, re-dispatch that agent once with an explicit alternate model — verifiers → `opencode-go/deepseek-v4.1-flash`, Scout → `opencode-go/muse-spark-1.3-contributor`:
  `subagent({ agent: "fact-check", model: "opencode-go/deepseek-v4.1-flash", task: '<JSON envelope string>', async: false })`.
  The `learning-gate` extension counts consecutive provider failures and surfaces this exact directive in its withheld banner once it sees two.
- If the fallback also fails, proceed and say plainly what remains unverified (the gate shows an `⛔ UNVERIFIED` banner after retries). Never present a grade/quiz/claims turn as verified when its verifier never returned.
- Model separation between caller and verifier is a **preference, not a guarantee**: a verifier may run on the same model as the Tutor when the pinned model is unavailable, and that is acceptable — the gate does not enforce model identity.

## Interleaving

Interleaving lives in the **review flow only** (SRS shuffle + adjacency constraint + question-type alternation). Lessons are sequential: one concept, one reasoning step at a time. Do not mix other concepts into probes, practice, or end-of-lesson quizzes.

## SRS integration

- On first introduction of a new concept: add a row to `📚 Active Concepts.md` (status `developing`, `last_reviewed` today, `next_review` +3d, `Last Q Type` `definitional`) — identical to ingest. Record the lesson's build language in Notes when non-default.
- The `review` trigger handles subsequent reviews; teaching does not bundle reviews into a single session.
- Curriculum rows already `done`: run a **retrieval check** to verify instead of re-teaching; on failure, demote the row to `in-progress` and correct the concept status.

## Writes & consistency

After a teaching session, the Tutor writes its four handoff artifacts (lesson file + session note + learning record + Pending Ingest.json) in one batch at the pause/lesson-end handoff, then:

1. Dispatch ONE **foreground** `tutor-audit` on the written files (envelope above) and fold its verdict before the summary. The `learning-gate` extension withholds a teach/resume summary that follows a `Learning System/` write until this receipt is present (`NO_TUTOR_AUDIT`) — do not skip it.
2. Re-read the four touched files and verify only their own consistency:
   - Lesson file exists in `Lessons/` with today's date · session note exists in `Sessions/`
   - Learning record numbered correctly (highest + 1) · glossary terms promoted only with user approval
   - `Pending Ingest.json` written with `status`, `resume_from`, `lesson_file`, `session_file`, `concepts`, and a source ref
3. Fix any discrepancy immediately, then re-audit once (max 2 cycles).
4. Do **not** commit and do **not** touch position/state files. Hand off to the Clerk (`/ingest`), which reconciles MISSION/CURRICULUM/Profile/Active Concepts/Mistakes, regenerates Learner History, and commits and pushes state (`Learning System/`, `Knowledge Wiki/`) per `Learning System/AGENTS.md`. For a partial (`/pause`) handoff, Clerk keeps the lesson `in-progress`; only a final handoff lets the curriculum row go `done`.
