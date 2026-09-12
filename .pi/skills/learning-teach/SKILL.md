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

**Turn tags (required — enforced by the gate):** begin every assistant message with `[[TURN:claims]]` (teaching or plan), `[[TURN:quiz]]` (question batch), `[[TURN:grade]]` (grading a learner answer), or `[[TURN:none]]` (transitions/summaries). The gate strips the tag before the learner sees it. A `claims` tag requires a `fact-check` receipt whose `rendered_content` matches the emitted text; `quiz` requires a PASS `quiz-audit`; `grade` requires an agreeing `grade-audit`. A missing tag is withheld (`NO_TURN_TAG`). The plan message is a `claims` turn — send the plan text as `rendered_content`.

Teaching verification runs as **foreground** subagent tasks with **envelope schemas**: `fact-check` and `quiz-audit`. Fixed verifier prompts live in the verifier agent files — you send **data only**. The `learning-gate` extension blocks any non-trivial Tutor output without a matching receipt before it renders.

**Position discipline:** the current lesson/phase is derived at runtime from `CURRICULUM.md`, `MISSION.md`, and `Lessons/`. Do not assume a position from this skill. If those disagree, STOP and report.

## Subagent verification protocol

> **Which envelope for THIS turn — decide before you dispatch. No substitutions.**
>
> | Your turn does… | Dispatch (ONE foreground subagent each) |
> | --- | --- |
> | Teach claims (definitions, formulas, mechanisms, code assertions) | `fact-check` with `claims[] + rendered_content` = this turn's draft |
> | Ask questions (probe or end-of-lesson quiz) | `quiz-audit` with `questions_json` = this turn's exact batch |
> | Grade a learner answer (pass/fail) | `grade-audit` — **only** `grade-audit`; `fact-check` does NOT satisfy a grade turn |
> | Teach claims AND ask questions in one turn | **BOTH** `fact-check` **and** `quiz-audit` for this turn |
>
> The gate checks the envelope type against the turn content. A right envelope for the wrong turn type is still a block. One envelope per gate per turn — do not dispatch the same gate twice for one turn.

All gates dispatch as ONE **foreground** `subagent` call per gate with a JSON envelope. The verifier runs on its own configured model, independent of the Tutor, so treat its verdict as stronger evidence than a self-check — but the deterministic gate checks (claim ⊆ rendered ⊆ emitted, quiz option parity, file grounding) are the real enforcement.

Rules:

- **Batch, don't trickle:** collect all claims (or all questions) for the current step and send them in a single task. Number every item so verdicts map back unambiguously.
- **Envelope, not freeform prompt:** send `{"gate":"fact_check","claims":[{"id":1,"claim":"..."}],"rendered_content":"...","source_urls":[...],"reference_excerpt":"...","context":"..."}` (and analogously `{"gate":"quiz_audit", ...}`). Do not add prose outside the envelope.
- **Fold verdicts in before proceeding:** never present claims or questions to the learner while a gate task is still pending.
- **Per-generation (Tutor only):** every Tutor generation that teaches a step must have its own fresh `fact-check` receipt **for the actual draft text, right before emission**. Draft the step internally, send `claims[] + rendered_content=draft + source_urls + reference_excerpt` in ONE foreground call, fold verdicts (apply `corrected_claim`), then emit the corrected final. Do not verify a plan and then generate different text. Each assistant message that contains teaching claims needs its own `fact-check` receipt.
- **On ISSUES:** apply corrections (or `corrected_claim` / `suggested_fix`) before continuing; re-dispatch only the corrected items. Max 2 cycles per batch; then surface remaining flags to the user.
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

The subagent returns `{"issues":[{"id":"q1","severity":"high|medium|low","problem":"...","suggested_fix":"..."}],"verdict":"PASS|ISSUES"}`. Mechanical pre-checks (done BEFORE dispatch): each MCQ has 4 options; `correct_index` in range; correct positions not all in one slot.

## Scope & state

- Mission: `Learning System/MISSION.md` — derive the active mission from it at runtime.
- Curriculum: `Learning System/CURRICULUM.md` — the authoritative "what's next" map (lessons sequential within a mission; the full map is navigational, not contractual). `📦 Concept Archive.md` is out of scope.
- Sources: the curriculum's `phases/<phase>/<lesson>/docs/en.md` + **every URL in its `## Further Reading`** + `Learning System/RESOURCES.md` (curated primary readings). **The curriculum source is a source, not the source** — Scout fetches the live docs + 2–4 external refs per lesson, hashes, compares, surfaces drift, and packs per-source `excerpt` + `takeaways` + `adds_vs_rohit` plus top-level `synthesis` into the digest; teach from the combined digest substance, not from parametric memory or a frozen snapshot. Archived material under `Learning System/Archive/` is NOT taught from. Live fetch each lesson (no cache layer).
- Glossary: `Learning System/GLOSSARY.md`. Learning records: `Learning System/Learning Records/`. Lessons: `Learning System/Lessons/`.
- Learner state: `Learning System/Core/📚 Active Concepts.md` → grep/range only the relevant track and concepts. Never read the whole file during probing.
- Attempts sidecar: `Learning System/Core/Attempts.json` — record every probe/quiz/review answer via `python3 scripts/ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail]` (updates recency-weighted mastery, interval_index, next_review). **Advisory only** — show mastery 0.00–0.80 + Feynman rubric status alongside prose Held/Advanced for one cycle.
- Mistakes ledger: `Learning System/Core/🧯 Mistakes.md` — on fail, append a row with error_type (`structural|deviation|application|metacognitive`) and self-attribution; due mistakes are asked first in reviews.
- Feynman rubric for `concept`/`design` types (explain-back must hit 4 checks: what it is in own words, when/why used, distinguish from nearest neighbour, one concrete example). Grade pass/fail and pass to the attempt call.
- You teach **from** the combined sources (derive fresh markdown lessons from `docs/en.md` + external refs synthesis), not by reformatting a single HTML. The curriculum sets the agenda; the external refs enrich every checkpoint with a new angle, counterexample, or depth. Cite both the Rohit source and relevant external refs in `fact-check` `source_urls` (with `reference_excerpt` quoting the digest excerpts).
- When creating new Active Concepts rows, set the `Type` column (`memory|concept|procedure|design` — ambiguous defaults to `concept`). New concepts get an `Attempts.json` entry with interval_index 0. **Language** follows the lesson `Languages:` header (captured as `lang_recommendation`); record it in Notes when non-default.

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

1. Write the full batch first: all MCQs plus one free-recall item per strand.
2. Run the mechanical pre-checks yourself — fix before dispatch.
3. Dispatch ONE quiz-audit subagent with the envelope above.
4. On `ISSUES`: fix every high/medium item per `suggested_fix`, then re-run. Max 2 cycles; if it still fails, show remaining flags to the user.
5. Never present a batch that has not passed the audit. The auditor never sees learner answers.

## The loop (prior → probe → plan → teach)

### 0. Personalization prior (cheap, capped — hypothesis only, probe wins)
- Read the Scout digest's `prereqs` field first (zero extra calls): `[{concept, keywords, why}]`. Use the keyword aliases verbatim to build ONE alternation regex.
- ONE bundle call max with that regex across `Knowledge Wiki/index.md`, the active-track slice of `📚 Active Concepts.md`, and `🧯 Mistakes.md`. Then read at most 2–3 matched wiki pages (section reads only). Total ≤4 reads. Never traverse the wiki in full; never read `📦 Concept Archive.md`.
- Rank hits per prereq: active mistake → stale/failed attempts → `developing` Active row → wiki-exposed-only → no hit. Map to `Known / Unknown / Reframe`: `skip-fast`, `expand`, `reframe`. This is a hypothesis — the probe validates it.
- Persist the durable subset into the session note at Plan time: the prereq→evidence map + the hypothesis table.

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
- Reason out the dependency path from current understanding → goal. Collect the load-bearing claims (definitions, formulas, mechanisms) and verify them in ONE batched foreground `fact-check` envelope, with `source_urls` listing both the Rohit source and relevant external refs plus `reference_excerpt`; correct anything before it reaches the user. **This plan-time batch validates the dependency ordering only — it does NOT replace per-step verification during Teach.**
- Present the plan as a **Mermaid graph** and persist it in the session note. The graph must be a real dependency ordering.
- The plan MUST include: (a) the `Known / Unknown / Reframe` table from step 0, (b) the lesson split into **checkpoints** (one idea + one practice each, each independently stoppable), each labeled with its prereqs and exit condition. Never teach source order as-is — teach dependency order from probe gaps.

### 3. Teach (checkpoints — one reasoning step at a time, always stoppable)
- Teach as a sequence of **checkpoints**: each = one idea + one short practice, ending in a clean stoppable state. Never stream a whole lesson in one block. A learner interrupt (`/pause`, "let's stop here") always wins over finishing the source outline.
- **Synthesis shape (every checkpoint):** (a) **source framing** (what the curriculum says, 1–2 lines), (b) **external angle** (what at least one Further Reading ref adds; cite the ref + its `adds_vs_rohit`), (c) **synthesis** (how they combine, including any disagreement). A checkpoint that only restates the source is incomplete.
- **Math formatting (terminal):** pi renders markdown, not KaTeX. Do not rely on LaTeX rendering. Prefer plain text/Unicode and fenced code blocks for equations; keep formulas readable as plain text. GATE envelopes stay raw JSON.
- **Tangent triage (hybrid):** every off-path question gets a 10-second ruling. QUICK (answer inline ≤2 min, log to Open Questions, return to checkpoint) vs DIVE (pause the checkpoint, chase it, record the branch in the session note, then offer "back to Checkpoint N?"). When in doubt, ask.
- Each step: (a) unconditional truth/definition if it has one, (b) motivated discovery — "why would anyone try this?", (c) **guided Socratic** question wherever the user has prior knowledge to connect to; give the minimum hint/accurate analogy the moment they stall (never pure Socratic). **Analogies:** flexible and accuracy-first; do not use soccer analogies. Prefer a direct explanation over a forced analogy.
- **Hook-in:** open with the mission-grounded "why this matters" hook. **Wonder-out:** close with open "what if…?" questions feeding the Open Questions principle.
- **Bloom climb (phase-mapped):** introduction targets Remember/Understand; practice climbs Apply → Analyze → Evaluate; the capstone is Create. Every lesson climbs at least to Apply.
- **Per-generation fact-check (Tutor ONLY — enforced by the gate, not optional):** draft each step's teaching content internally first, then dispatch a foreground `fact-check` envelope carrying the draft as `rendered_content` plus **every load-bearing claim in that draft**, with `source_urls` listing the combined live sources and `reference_excerpt` quoting the digest excerpts; fold in verdicts before emitting the step. **Do NOT verify a plan and then generate different text.** Routine consistency (prerequisites, self-contradiction, coverage) is your own responsibility. **Language:** code blocks use the lesson's `lang_recommendation`.

### 4. Pause (student-paced breakpoint — `/pause` or "let's stop here")
- On pause: (a) run a small **exit ticket** for TODAY's checkpoints only (2–3 retrieval items, quiz-audit gated) — never cumulative over un-revisited days; (b) write/extend the partial lesson file `Lessons/Lesson — … — date.md` with `Status: paused at Checkpoint N/M` + a `Resume from:` pointer; (c) write partial `Learning System/Core/Pending Ingest.json` with `{partial:true, lesson_file, session_file, checkpoints_done:[...], concepts:[...], source_url|source_file, created_at}` and tell the learner to run `/ingest` to bank today's progress. Clerk ingests today's concepts and KEEPS the Scout digest + lesson `in-progress` (see learning-system skill). The curriculum row becomes `in-progress (paused N/M)`.
- **Resume (`/continue`):** the lesson file + last session note are the source of truth (Scout digest optional). Open with a 2-minute recall warm-up on the last completed checkpoint (retrieval, not re-teach), then continue at N+1. Never re-quiz Day-1 material cold.

### 5. Lesson end (final checkpoint only: cumulative + Feynman → handoff to Clerk)
- **Final quiz (cumulative, final checkpoint only):** retrieval items + higher-order items. For any MCQ, follow **Multiple-choice integrity** and pass the full batch through the quiz-audit subagent before presenting. Confidence tagging applies: a correct `hunch` does not count as retrieval success — re-check with an isomorphic variant. Math uses the on-paper workflow.
- **Feynman explain-back:** the user explains the idea back in plain terms (one short paragraph). The lesson is not `done` until this passes.
- **Fuzziness inference (no self-rating):** deduce from answers — "I don't know", hedging, self-corrections, wrong answers on already-reviewed concepts, fluent explain-back but failed retrieval. High fuzziness → drop a rung; low → climb.
- Write a **Learning Record** with the highest Bloom level demonstrated in **Evidence**; note a corrected misconception when it happens.
- If the lesson corresponds to an existing curriculum row: advance it only when practice complete + retrieval pass + Feynman pass; write the session note and lesson file.
- **Do not write wiki pages or Active Concepts rows.** Instead, write `Learning System/Core/Pending Ingest.json` with `{lesson_file, session_file, concepts:[...], source_url|source_file, created_at}` for Clerk, then tell the learner to run `/ingest` to finalize. Lesson files, learning records, and glossary promotions are gated live by `fact-check` during teach, not by the review gate.

## Interleaving

Interleaving lives in the **review flow only** (SRS shuffle + adjacency constraint + question-type alternation). Lessons are sequential: one concept, one reasoning step at a time. Do not mix other concepts into probes, practice, or end-of-lesson quizzes.

## SRS integration

- On first introduction of a new concept: add a row to `📚 Active Concepts.md` (status `developing`, `last_reviewed` today, `next_review` +3d, `Last Q Type` `definitional`) — identical to ingest. Record the lesson's build language in Notes when non-default.
- The `review` trigger handles subsequent reviews; teaching does not bundle reviews into a single session.
- Curriculum rows already `done`: run a **retrieval check** to verify instead of re-teaching; on failure, demote the row to `in-progress` and correct the concept status.

## Writes & consistency

After a teaching session (lesson file + session note + learning record + Pending Ingest.json):

1. Re-read all touched files and verify:
   - Lesson file exists in `Lessons/` with today's date · session note exists in `Sessions/`
   - Learning record numbered correctly (highest + 1) · glossary terms promoted only with user approval
   - `Pending Ingest.json` written with lesson_file, concepts, and source ref
   - `CURRICULUM.md` statuses match reality
2. Fix any discrepancy immediately.
3. Commit and push **state only** (`Learning System/`, `Knowledge Wiki/`) per `Learning System/AGENTS.md`. For a partial (`/pause`) handoff, only `/ingest` advances the curriculum row and clears the marker.
