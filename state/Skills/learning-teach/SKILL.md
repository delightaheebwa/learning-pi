---
name: learning-teach
description: Teach the user through the probe → plan → teach loop, applying the AIEFS (Rohit) mission — adaptively re-fetching live docs/en.md + Further Reading each new lesson, 80/20 catch-up for P0+P1.01–06 then sequential Phases, per-lesson language (Python/TS/Rust), batched fact-check + quiz-audit subagents. Triggers: 'teach me X', 'lesson', 'continue'.
---

# Learning Teach

> **⚠️ FROZEN / LEGACY — not the canonical teaching behavior.** This Open WebUI copy is kept for
> branch history only and is **no longer maintained**. The canonical teaching skills live in
> **`learning-pi/.pi/skills/`** (`learning-teach`, `learning-system`, `learning-review`,
> `llm-wiki`). Do **not** add teaching-behavior changes here; make them in `learning-pi` and, if a
> change is a behavior contract, update `CONTRACT.md`/`contracts/learning-core.json` in the same
> commit. See `learning-pi/README.md`.

The teaching half of the learning system, running in Open WebUI on the tutor model (the Learning Tutor preset's base model — see `OPENWEBUI.md` for the model-per-task table).
The pipeline is **Scout → Tutor → Clerk** in the same chat (switch presets).

- Scout gathers context and writes `Learning System/.tmp/context-<chat_id>-<slug>.json`.
- Tutor teaches using the session + digest (or the existing lesson file on resume) — it does **not** gather context itself and does **not** write wiki pages/Active Concepts rows. See `OPENWEBUI.md`.
- Clerk ingests the lesson output (Pending Ingest.json) and delegates `GATE:review`.

Teaching verification runs as **foreground** subagent tasks (`delegate_task`, `background:false`) with **envelope schemas** (`gate_schema.py`): `GATE:fact_check` and `GATE:quiz_audit`. Fixed verifier prompts live in the global `subagents.system_prompt` (keyed by `GATE:`) — you send **data only**. The gate Pipe (`gate_pipe.py`) blocks any non-trivial Tutor output without a receipt before it renders. See "Subagent verification protocol" below.

## Subagent verification protocol

> **Which envelope for THIS turn — decide before you dispatch. No substitutions.**
>
> | Your turn does… | Dispatch (ONE foreground `delegate_task` each) |
> | --- | --- |
> | Teach claims (definitions, formulas, mechanisms, code assertions) | `fact_check` with `claims[] + rendered_content` = this turn's draft |
> | Ask questions (probe or end-of-lesson quiz) | `quiz_audit` with `questions_json` = this turn's exact batch |
> | Grade a learner answer (pass/fail) | `grade_audit` — **only** `grade_audit`; `fact_check` does NOT satisfy a grade turn |
> | Teach claims AND ask questions in one turn | **BOTH** `fact_check` **and** `quiz_audit` for this turn |
>
> The gate checks the envelope type against the turn content. A right envelope for the
> wrong turn type is still a block (observed failure: `fact_check` on a grade turn,
> `quiz_audit`-only on a mixed claims+quiz turn). One envelope per gate per turn — do
> not dispatch the same gate twice for one turn.

All gates dispatch as ONE **foreground** `delegate_task` (`background:false`) per gate with a **Pydantic envelope** (`Skills/learning-review/openwebui/gate_schema.py`). The
subagent runs on your own base model (Open WebUI runs verifiers on the calling preset's
model — there is no separate verifier-model setting), so treat its verdict as advisory
evidence, not independence: the deterministic Pipe checks (claim⊆rendered⊆emitted,
quiz option parity, file grounding) are the real enforcement. The gate Pipe validates receipts before render.

Rules:

- **Batch, don't trickle:** collect all claims (or all questions) for the current step and
  send them in a single task. Number every item so verdicts map back unambiguously.
- **Envelope, not freeform prompt:** send `{"gate":"fact_check","claims":[{"id":1,"claim":"..."}],
  "source_url":"https://..." /* or "source_file":"path" */, "context":"..."}`
  (and analogously `{"gate":"quiz_audit", ...}` for quiz-audit). Do not add prose outside the envelope.
- **Fold verdicts in before proceeding:** never present claims or questions to the learner,
  and never finalize a lesson step, while its gate task is still pending.
- **Per-generation (Learning Tutor only):** every Tutor generation that teaches a step must have its own fresh `GATE:fact_check` receipt **for the actual draft text, right before emission**. Draft the step internally, send `claims[] + rendered_content=draft + source_urls + reference_excerpt` in ONE foreground envelope, fold verdicts (apply `corrected_claim`), then emit the corrected final. Do not verify a plan and then generate different text — verifying 5 concepts upfront does not guarantee the per-step generation stays correct. Each assistant message that contains teaching claims needs a `delegate_task` whose `parent_message_id == that message's id`, dispatched for the draft behind that message. The gate Pipe enforces this generation-to-emission binding and will BLOCK any Tutor teaching message whose `rendered_content` does not match the emitted text or whose `claims[]` do not appear in `rendered_content`, or that relies only on a `quiz_audit` receipt for claims content.
- **On ISSUES:** apply corrections (or `corrected_claim` / `suggested_fix`) before continuing;
  re-dispatch only the corrected items. Max 2 cycles per batch; then surface remaining flags
  to the user.
- **If a subagent can't run:** say so explicitly and mark the affected claims/questions as
  UNVERIFIED to the user — never silently skip verification.
- **Gate blocks:** if the Pipe replaces your draft with `⛔ BLOCKED (<code>)`, fix the envelope per the code and retry; cap 2, then withheld banner.

### Fact-check envelope (per claim, batched) — send as delegate_task payload

The subagent's fixed prompt lives in `subagents.system_prompt` (`GATE:fact_check`); you send data only:

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

Generation-to-emission (not plan-to-generation): draft the step internally first, put the draft in `rendered_content`, list its load-bearing claims in `claims[]`, then dispatch. Fold verdicts (apply `corrected_claim`) before emitting the final.

Legacy single-source form (`source_url` OR `source_file: Learning System/RESOURCES.md`) still validates, but prefer `source_urls` (Rohit + at least one external ref) for every Teach step.

The subagent fetches the source itself; Pipe substring-checks the reference. Subagent returns `{"verdicts":[{"id":1,"verdict":"PASS|ISSUES|UNVERIFIED","explanation":"...","corrected_claim":"only when ISSUES else null"}, ...]}`.

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

Subagent returns `{"issues":[{"id":"q1","severity":"high|medium|low","problem":"...","suggested_fix":"..."}],"verdict":"PASS|ISSUES"}`. Mechanical pre-checks (done BEFORE dispatch): each MCQ has 4 options, correct_index in range, correct positions not all in one slot.

## Scope & state (repo root: the checkout — `LEARNING_SYSTEM_ROOT` or auto-detected via `Learning System/Core`)

- Mission: `Learning System/MISSION.md` (AIEFS — Rohit; Mission 0 catch-up done, P1 L07 done — resume P1 L08 Optimization).
- Curriculum: `Learning System/CURRICULUM.md` — the authoritative "what's next" map (Rohit 20 phases + Mission 0 Catch-Up; lessons sequential; full map navigational, not contractual; `📦 Concept Archive.md` strictly out of scope). **Position example frozen 2026-09-08 (P1 L08 paused 2/5 — HISTORICAL). Live position 2026-10-16: P1 L10 DR paused 5/6 — see MISSION.md/CURRICULUM.md.**
- Sources: AI Engineering from Scratch (`phases/<phase>/<lesson>/docs/en.md` + **every URL in its `## Further Reading`**) + `Learning System/RESOURCES.md` (curated primary readings: 3Blue1Brown, Stanford CS229, log-sum-exp, etc.). **Rohit is a source, not the source** — Scout fetches the live docs + 2–4 external refs per lesson, hashes, compares, surfaces drift, and packs per-source `excerpt` + `takeaways` + `adds_vs_rohit` plus top-level `synthesis` into the digest; you teach from the combined digest substance, not from parametric memory, a frozen snapshot, or URLs alone. Adaptive re-fetch covers upstream changes (e.g., after 2–3 lessons, returning for the 4th, Scout re-fetches and compares hash). Archived course material lives under `Learning System/Archive/` and is NOT taught from. **Cache is ignored per decision 2026-09-01** — live fetch each lesson (no `Curriculum/cache/` layer).
- Glossary: `Learning System/GLOSSARY.md` (AIEFS active). Learning records: `Learning System/Learning Records/`. Lessons: `Learning System/Lessons/`.
- Learner state: `Learning System/Core/📚 Active Concepts.md` → grep/range the **relevant (aiefs)** track and concepts only. Never read the whole file per concept during probing (user constraint). **SWE is archived 2026-09-01 — do not grep `📦 Concept Archive.md`.**
- Attempts sidecar: `Learning System/Core/Attempts.json` — record every probe/quiz/review answer via `python3 scripts/ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail]` (updates recency-weighted mastery, interval_index, next_review). **Advisory only** — show mastery 0.00–0.80 + Feynman rubric status alongside prose Held/Advanced for one cycle.
- Mistakes ledger: `Learning System/Core/🧯 Mistakes.md` — on fail, append row with error_type (`structural|deviation|application|metacognitive`) and self-attribution; due mistakes asked first in reviews.
- Feynman rubric for `concept`/`design` types (explain-back must hit 4 checks: what it is in own words, when/why used, distinguish from nearest neighbor, one concrete example). Grade pass/fail and pass to attempt call.
- You teach **from** the combined sources (derive fresh markdown lessons from `docs/en.md` + external refs synthesis), you do not reformat a single HTML into markdown. Rohit sets the agenda (what to cover today — the high-level guide); the external refs enrich every checkpoint with a new angle, counterexample, or depth Rohit glosses over. Cite both `rohit_source` and relevant `external_refs` in `GATE:fact_check` `source_urls` (with `reference_excerpt` quoting the digest excerpts). Each digest entry carries `excerpt` (~500 chars) + `takeaways` + `adds_vs_rohit` plus top-level `synthesis` — teach from those, not from the URLs alone.
- When creating new Active Concepts rows, set the `Type` column (`memory|concept|procedure|design` — see Active Concepts.md header) — ambiguous defaults to `concept`. New concepts get `Attempts.json` entry with interval_index 0 and next_review today+interval (memory 0d etc. per mastery.py). **Language column** follows the lesson's `Languages:` header (Python / TypeScript / Rust; Julia optional, Python-first for Phase 1) — record in Notes or infer from `lang_recommendation` in digest, not hardcoded.

## Multiple-choice integrity (applies to the probe AND the end-of-lesson quiz)

These rules stop the correct answer from being guessable by its presentation or
by the distractors. The user must earn the answer by knowledge, never by noticing
a pattern. The rules are enforced two ways: you follow them while writing items,
and the **quiz-audit subagent independently audits every batch before the learner
sees it** — see "Subagent verification protocol" above.

- **Balance option length and structure.** The correct option must not be the
  longest (or shortest) or the only one with extra detail. Rewrite options so
  all are roughly the same length and shape. This is the single most common leak.
- **Randomize the correct position.** Do not put the correct answer in the same
  slot repeatedly (e.g. not always "D" or always last). Vary it across questions.
- **No "all of the above" / "none of the above"** as a crutch to make one option
  longer.
- **Keep parallel grammar** across options — same part of speech, same verb
  tense, no qualifiers ("usually", "primarily") only on the true one.
- **Do not leak via wording.** The correct option must not be the only one that
  matches the question's phrasing, restates a term verbatim, or contains the
  answer in the question stem.
- **Do not reuse the exact textbook sentence** for the correct option while
  paraphrasing the distractors.
- **Make the correct answer subtle — not a neon sign.** The correct option must
  not be the only defensible one. Build the distractors so a person who knows the
  material still has to think: mix in *almost right* (one term swapped, one step
  off), *right in another context* (true elsewhere but wrong here), *right under
  a narrower/wider condition*, and *right by nuance* (missing a qualifier). An
  expert should recognize the correct answer; a guesser should not. No option may
  be eliminated just because it is worded differently.
- **Never leak the answer key in the instructions.** Do not give the user an
  example answer string that encodes the correct positions (e.g. "reply '1b, 2b,
  3c'"). Ask for answers without revealing which slot is correct, or omit the
  example entirely.
- Before presenting a question, self-check: cover the options and ask "could the
  answer be inferred from length/position/format alone, or is any distractor so
  weak it can be discarded without knowledge?" If yes, rewrite.

### Quiz-audit protocol (mandatory for probe AND end-of-lesson quiz)

1. Write the full batch first: all MCQs plus one free-recall item per strand.
2. Run the mechanical pre-checks yourself — fix before dispatch: each MCQ has 4 options;
   `correct_index` in range; correct positions not all in one slot (batches of 3+);
   correct option not the longest/shortest outlier (compare prose shape; code/math
   options exempt); no "all/none of the above"; no example answer string in the
   instructions that encodes the correct positions.
3. Dispatch ONE quiz-audit subagent task with `questions_json` (each item: id,
   type mcq|free_recall, question, options + correct_index for MCQs,
   target_bloom), `purpose` ("probe" or "end-of-lesson quiz"), `concept`,
   `bloom_levels`, and `source_excerpt`, using the template above.
4. On `ISSUES`: fix every high/medium item per `suggested_fix`, then re-run.
   Max 2 cycles; if it still fails, show remaining flags to the user.
5. Never present a batch that has not passed the audit. The auditor checks
   quality only and never sees learner answers.

## The loop (prior → probe → plan → teach)

### 0. Personalization prior (cheap, capped — hypothesis only, probe wins)
- Read the Scout digest's `prereqs` field first (zero extra calls): `[{concept, keywords, why}]`. The keyword aliases are the search terms — use them verbatim to build ONE alternation regex; do not invent variants. (Fallback for legacy digests without `prereqs`: derive the prerequisite list from the digest outline, then proceed identically.)
- ONE bundle call max with that regex across `Knowledge Wiki/index.md`, the aiefs slice of `📚 Active Concepts.md`, and `🧯 Mistakes.md` (plus `Attempts.json` mastery where rows exist). Then read at most 2–3 matched wiki pages (section reads only, `@^## ` headings first). Total ≤4 reads. Never traverse the wiki in full; never read `📦 Concept Archive.md`.
- Rank hits per prereq: active mistake → stale/failed attempts → `developing` Active row → wiki-exposed-only → no hit. Map to `Known / Unknown / Reframe`: `skip-fast` (solid + recent pass), `expand` (unknown/unstable or source glosses over it), `reframe` (use Learning Profile analogy + prior wiki example). This is a hypothesis — the probe validates it; anything the prior calls solid but probe shows unknown is demoted and expanded before advancing.
- Persist the durable subset into the session note at Plan time: the prereq→evidence map + the hypothesis table. Future chats (`/continue`, new chat) inherit it with one file read instead of re-searching. Log the hypothesis in the session note so future lessons inherit a smarter prior (and record every AIEFS checkpoint outcome via `ops.py attempt` so `Attempts.json` grows beyond the archived SWE history).

### 1. Probe (find the edge — prereq-driven)
- Read only relevant state: the target lesson's dependent concepts (grep `📚 Active Concepts.md` **aiefs** track; do not grep SWE archive), recent learning records, glossary terms. Never the whole file. For **Mission 0 Catch-Up (80/20 P0+P1.01–06)**, probe **broad→narrow across 5 strands** (tooling / vectors-matrices / transforms-eigen / calculus-chain-rule / probability) rather than a single strand — 6–8 MCQs + 2 free-recall total, still `quiz-audit` gated, then map gaps to the 80/20 list (`CURRICULUM.md` Mission 0 `80/20 map`). For regular lessons, 3–8 MCQs per strand as before.
- Ask 3–8 graded multiple-choice questions (always offer "I don't know"), broad → narrow, binary-searching each dependency strand to the boundary. Stop per-strand once the edge is found; hard cap 3–8. Follow **Multiple-choice integrity** and pass the whole strand's batch through the **quiz-audit subagent** before showing any of it. Build distractors against **combined sources** (Rohit + external refs), not just one textbook sentence.
- **Math (paper accommodation):** Never use free-recall "write the full formula / type the LaTeX." For math-heavy strands, use either (a) give inputs → compute final numeric result **on paper** (learner replies with just the number), or (b) MCQ select-correct-formula among 4 balanced options (learner replies with letter A–D). Always prompt explicitly: "Work on paper, reply with final answer only." Correct final answer validates formula recall — do not skip math concepts.
- Include exactly **one free-recall item per strand** ("explain in your own words…") — unguessable by construction; grade it against the combined source excerpt (Rohit `docs/en.md` + Further Reading synthesis). For math strands, this free-recall must be a short insight/conceptual prompt, not verbatim formula transcription.
- **Withheld feedback:** do NOT reveal right/wrong during a strand. Present the full batch, collect answers, only then reveal results. Feedback mid-strand lets the learner adapt-guess and contaminates the measurement.
- **Confidence tagging:** require a tag on every answer: `sure` / `hunch` / `no idea`. Scoring rule: correct+`sure` = knows · correct+`hunch` = **unknown** (lucky guess — run an isomorphic re-probe of that concept with structurally different wording before counting it) · anything else = not known.
- **Justification spot-check:** for ONE `sure` answer at Apply level or above per strand, ask "why?" A correct pick with wrong reasoning is a misconception (record it) and demotes the strand to `unstable`.
- End the probe with a **structured probe verdict** in the session note: per-strand boundary state (`solid` / `unstable` / `unknown`) plus evidence rows (question id, answer, confidence tag, follow-up result). Every judgment must cite its evidence. For catch-up, include a `gaps → 80/20` mapping: which of the 5 80/20 buckets are `solid` vs need teach.
- If the user discloses prior knowledge ("I already know X"), note it and record it (see Learning Records trigger 2). For catch-up, prior exercises are assumed done — probe verifies, never assumes.

### 2. Plan (force the reasoning)
- Reason out the dependency path from current understanding → goal. Collect the load-bearing claims in the plan (definitions, formulas, mechanisms) and verify them in ONE batched foreground `GATE:fact_check` envelope (see above), with `source_urls` listing **both** `rohit_source` and relevant `external_refs` URLs plus `reference_excerpt` (or `source_file: Learning System/RESOURCES.md` when both point there); correct anything before it reaches the user. Label each plan-graph node with the digest source(s) it draws on (`rohit` / `external:<label>` / `synthesis`). Respect the lesson's `lang_recommendation` (Python / TypeScript / Rust) in the plan's Build It block. **This plan-time batch validates the dependency ordering only — it does NOT replace per-step verification during Teach.** Each Teach step must still be fact-checked right before it is generated (see 3. Teach).
- Present the plan as a **Mermaid graph** (renders in Open WebUI) and persist it in the session note. The graph must be a real dependency ordering — it forces reasoning out, not decoration. For catch-up, graph the 5 80/20 buckets as parallel unlock paths converging on "Ready for Phase 1 L07".
- The plan MUST include: (a) the `Known / Unknown / Reframe` table from step 0 (what to skip fast, what to expand beyond the source, which analogy/example to reuse from the wiki), (b) the lesson split into **checkpoints**, each checkpoint = a small ordered cluster of **mini-checkpoints** + one practice, every part independently stoppable (see 3. Teach). List each checkpoint's mini-checkpoints explicitly (`CP2.1`, `CP2.2`, …); each mini-checkpoint is ONE atomic reasoning unit — a single definition, formula, mechanism, or worked micro-step — labeled with its prereq and exit condition. The checkpoint's single practice integrates its mini-checkpoints. Never teach source order as-is — teach dependency order from probe gaps. Keep mini-checkpoints genuinely small: if a mini-checkpoint cannot be stated as one idea plus at most one implication, split it. State explicitly what the source glosses over that this learner needs expanded.

### 3. Teach (checkpoints → mini-checkpoints — one reasoning step at a time, always stoppable)
- Teach each **checkpoint as a sequence of mini-checkpoints**, then one short practice, ending in a clean stoppable state. A **mini-checkpoint** is ONE atomic reasoning unit (a single definition, formula, mechanism, or worked micro-step): deliver it alone and never bundle it with the rest of the checkpoint. The learner digests one small piece at a time, may ask any number of questions or chase tangents, and can stop after any mini-checkpoint. Never stream a whole Rohit lesson — or a whole checkpoint — in one block. A learner interrupt (`/pause`, "let's stop here", "continue tomorrow") always wins over finishing the source outline — stop cleanly, do not push through.
- **Mini-checkpoint pause protocol (mandatory — the learner is never rushed):** deliver one mini-checkpoint at a time and never chain mini-checkpoint → practice → next checkpoint. Run this exact loop for every checkpoint:
  1. **Mini-checkpoint idea** (`GATE:fact_check`-gated teaching turn) — teach ONE atomic reasoning unit. Do **not** fold the checkpoint's other mini-checkpoints into this message. If it is growing past one idea + one implication, split it.
  2. **Pause** — say this mini-checkpoint is done, then explicitly invite questions, clarifications, or tangents ("Anything unclear here before the next piece? Any question?"). STOP and wait. Do **not** present the next mini-checkpoint or the practice yet.
  3. If the learner asks anything, answer it (fact-check-gated when it carries claims; DIVE tangents per Tangent triage), then re-offer the pause. Only when the learner says they have none do you continue.
  4. Repeat steps 1–3 for each remaining mini-checkpoint of the checkpoint. Never fold two mini-checkpoints into one message.
  5. **Practice** — after the last mini-checkpoint, the checkpoint's one practice question (it integrates the mini-checkpoints), `GATE:quiz_audit`-gated.
  6. **Grade** — verdict + one-line why, `GATE:grade_audit`-gated.
  7. **Pause #2** — after grading, explicitly invite further questions before moving on. Wait again.
  8. Only after a "no questions" at Pause #2 do you proceed to the next checkpoint (its first mini-checkpoint). Never fold two checkpoints into one message.
- **Synthesis shape (every checkpoint, spread across its mini-checkpoints):** each checkpoint still teaches in three moves — (a) **Rohit framing** (what Rohit says — the agenda for today, 1–2 lines), (b) **external angle** (what at least one Further Reading ref adds: a new angle, counterexample, intuition, or depth — cite `external_refs[label]` + its `adds_vs_rohit`), (c) **synthesis** (how they combine into the working mental model, including any disagreement between sources). Attach these to the mini-checkpoint they fit (framing usually opens the first, the external angle lands where it adds most); the enrichment must not enlarge any single mini-checkpoint. A checkpoint that only restates Rohit is incomplete — go back to the digest `synthesis`/`adds_vs_rohit` fields and pull the enrichment in. If the digest marks a ref `failed`, say so and teach from the remaining fetched sources — never invent the missing angle.
- **Math formatting (OpenWebUI KaTeX — learner-facing prose only):** inline math as `\(...\)` (never single-`$`); display math with `\[` and `\]` each on their own line (never `$$...$$` inline, never fenced ```math/```latex blocks). GATE envelopes stay raw JSON.
- **Tangent triage (hybrid):** every off-path question gets a 10-second ruling. QUICK (answer inline ≤2 min, log to Open Questions, return to the current mini-checkpoint): curiosity, terminology, "what if" that does not block the current step. DIVE (pause the checkpoint, chase it fully, record the branch in the session note, then explicitly offer "back to Checkpoint N, mini M?"): the tangent blocks understanding of the current mini-checkpoint, or it exposes an active `🧯 Mistakes.md` item / probe-unknown prereq. When in doubt, ask: "quick answer now, or dive properly?"
- Each step: (a) unconditional truth (or "all X are Y"/definition) if the step has one, (b) motivated discovery — "why would anyone try this?", (c) **guided Socratic** question wherever the user has prior knowledge to connect to; tell the minimum hint/accurate analogy the moment they stall (never pure Socratic — matches Learning Profile). **Analogies:** flexible and accuracy-first; **do not use soccer analogies** (removed per Learning Profile). Prefer a direct explanation over a forced or oversimplified analogy.
- **Hook-in:** open with the mission-grounded "why this matters" hook (for catch-up: why 80/20 reactivation unlocks Phase 1 L07+). **Wonder-out:** close with open "what if…?" questions feeding the Open Questions principle.
- **Bloom climb (phase-mapped):** introduction targets Remember/Understand; practice climbs Apply → Analyze → Evaluate; the capstone is Create. Every lesson climbs at least to Apply. Not every lesson reaches every level (short lessons). For catch-up, target Apply on each 80/20 bucket (e.g., implement `softmax` + `cross-entropy` from scratch, reason `W@x+b` shapes).
- **Per-generation fact-check (Learning Tutor ONLY — enforced by Gate Pipe, not optional):** draft each step's teaching content internally first, then dispatch a foreground `GATE:fact_check` envelope carrying the draft as `rendered_content` plus **every load-bearing claim in that draft** (definitions, formulas, mechanisms, code assertions) in `claims[]`, with `source_urls` listing the combined live sources (Rohit + external refs for this lesson from the Scout digest) and `reference_excerpt` quoting the digest excerpts for this step; fold in verdicts before emitting the step — on ISSUES, correct the draft first, then emit. **Do NOT verify a plan and then generate different text** — e.g., for RAG, draft the retrieval step, verify that draft, then emit it; repeat per step. Each assistant message that teaches must have its own receipt (`parent_message_id == this message's id`) whose `rendered_content` matches the emitted text. Routine consistency (prerequisites, self-contradiction, coverage) is your own responsibility — check it yourself rather than delegating. **Language:** code blocks use the lesson's `lang_recommendation` (Rohit header; Python default for Phases 0–12, TypeScript for Tools/Agents, Rust where listed). Single-turn presets (Scout, Clerk) do not use this per-generation rule — they verify per their own single turns as before.

### 4. Pause (student-paced breakpoint — `/pause` or "let's stop here")
- The student decides lesson length, not the tutor. On pause: (a) run a small **exit ticket** for TODAY's mini-checkpoints only (2–3 retrieval items, quiz-audit gated, same integrity rules — never cumulative over un-revisited days); (b) write/extend the partial lesson file `Lessons/Lesson — … — date.md` with `Status: paused at Checkpoint N/M, mini K/L` + a `Resume from:` pointer (next mini-checkpoint `CPN.K`, or the checkpoint practice + one-line context); (c) write partial `Learning System/Core/Pending Ingest.json` with `{partial:true, lesson_file, session_file, checkpoints_done:[...], concepts:[...], source_url|source_file, created_at}` and tell the learner: "Paused — switch to the **Clerk** preset and run `/ingest` to bank today's progress." Clerk ingests today's concepts and KEEPS the Scout digest + lesson `in-progress` (see learning-system skill). Curriculum row becomes `in-progress (paused N/M)`. The `Checkpoint N/M` fraction stays the canonical position (`audit_state.py` reads it); the mini index is extra precision in the pointer, not a replacement.
- **Resume (`/continue`):** the lesson file + last session note are the source of truth (Scout digest optional). Open with a 2-minute recall warm-up on the last completed mini-checkpoint (retrieval, not re-teach), then continue at the next mini-checkpoint (or the checkpoint's practice) — never restart the checkpoint from its first idea. Never re-quiz Day-1 material cold as if memory were fresh.

### 5. Lesson end (final checkpoint only: cumulative + Feynman → handoff to Clerk)
- **Final quiz (cumulative, final checkpoint only):** retrieval items (spaced, storage strength) + higher-order items ("explain why / predict / modify"). For any multiple-choice item, follow **Multiple-choice integrity** and pass the full batch through the **quiz-audit subagent** (foreground envelope) before presenting it. Confidence tagging applies here too: a correct `hunch` does not count as retrieval success — re-check that item with an isomorphic variant. **Math (paper accommodation):** on-paper workflow — prompt "Work on paper, reply with just the final output (number or A–D)". Never require typing full LaTeX. Final answer correctness validates formula recall.
- **Feynman explain-back:** the user explains the idea back in plain terms (one short paragraph). The lesson is not `done` until this passes.
- **Fuzziness inference (no self-rating):** deduce from answers — "I don't know", hedging/vague phrasing, self-corrections, wrong answers on already-reviewed concepts, fluent explain-back but failed retrieval. High fuzziness → drop a rung (analogy, smaller step, re-probe). Low → climb.
- Write a **Learning Record** (trigger 1) with the highest Bloom level demonstrated in **Evidence**; note a corrected misconception (trigger 3) when it happens.
- If the lesson corresponds to an existing curriculum row: advance it only when practice complete + retrieval pass + Feynman pass; write the session note (`Sessions/Session — … — date.md`) and a lesson file (`Lessons/Lesson — … — date.md`).
- **Do not write wiki pages or Active Concepts rows.** Instead, write `Learning System/Core/Pending Ingest.json` with `{lesson_file, session_file, concepts:[...], source_url|source_file, created_at}` for Clerk, then tell the learner: "Lesson complete — switch to the **Clerk** preset and run `/ingest` to finalize." If resuming a lesson (`Lessons/` file exists), the tutor grounds in that file + Sessions/ + CURRICULUM.md and the Scout digest is optional. Lesson files, learning records, and glossary promotions are gated live by `GATE:fact_check` during teach, not by the review gate. See `Skills/learning-review/SKILL.md`.

## Interleaving

Interleaving lives in the **review flow only** (the SRS shuffle + adjacency constraint + question-type alternation in the learning-system skill). Lessons are sequential: one concept, one reasoning step at a time. Do not mix other concepts into probes, practice, or end-of-lesson quizzes.

## SRS integration

- On first introduction of a new concept: add a row to `📚 Active Concepts.md` (status `developing`, `last_reviewed` today, `next_review` +3d, `Last Q Type` `definitional`) — identical to ingest. Record the lesson's build language in Notes when non-Python.
- The `review` trigger (AIEFS) handles subsequent reviews; teaching does not bundle reviews into a single session. SWE reviews are archived — do not schedule.
- Curriculum rows already `done` from prior learning (now Mission 0 catch-up `not-started*` Phase 0 + Phase 1 L01–L06): run a **retrieval check** to verify instead of re-teaching; on failure, demote the row to `in-progress` and correct the concept status. After catch-up passes, **Phase 1 L07** is the next `in-progress` (jump per 2026-09-01).

## Writes & consistency

After a teaching session (lesson file + session note + learning record + Pending Ingest.json):

1. Re-read all touched files and verify:
    - Lesson file exists in `Lessons/` with today's date · session note exists in `Sessions/`
    - Learning record numbered correctly (highest + 1) · glossary terms promoted only with user approval
    - `Pending Ingest.json` written with lesson_file, concepts, and source ref
    - `CURRICULUM.md` statuses match reality
2. Fix any discrepancy immediately.
3. Commit and push per `Learning System/AGENTS.md` (only `Learning System/`, `Knowledge Wiki/`, `Skills/`).
    The Pipe (`gate_pipe.py`) blocks non-trivial Tutor output without a **fresh per-generation** foreground `GATE:fact_check` (claims + rendered_content draft) or `GATE:quiz_audit` (quizzes) receipt — each Tutor teaching message must have its own receipt with `parent_message_id == that message` whose `rendered_content` matches the emitted text; a plan-only batch never satisfies Teach steps, and a `quiz_audit` receipt never satisfies claims content. Scout digest presence for new lessons (7-day TTL, `Learning System/.tmp/context-<chat>-<slug>.json`) still enforced. Resume of an existing lesson grounds in `Lessons/` and bypasses the digest check. Scout and Clerk remain single-turn and are unchanged.