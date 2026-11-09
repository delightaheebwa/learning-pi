---
name: learning-review
description: Quality-gate learning system output before it is finalized — wherever it originates. Runs after every standalone ingest session, at the end of any teaching lesson that produced wiki pages or Active Concepts rows (review-gate on wiki/rows), AND at the close of a standalone /review session (review-session gate on the end-of-review writes). A review-gate subagent task (running on the calling preset's own base model) flags accuracy, correctness, clarity, and completeness issues with severity; the implementer fixes them; max 2 cycles, then remaining flags surface to the user.
---

# Learning System Review Gate

> **⚠️ FROZEN / LEGACY — not the canonical teaching behavior.** This Open WebUI copy is kept for
> branch history only and is **no longer maintained**. The canonical teaching skills live in
> **`learning-pi/.pi/skills/`** (`learning-teach`, `learning-system`, `learning-review`,
> `llm-wiki`). Do **not** add teaching-behavior changes here; make them in `learning-pi` and, if a
> change is a behavior contract, update `CONTRACT.md`/`contracts/learning-core.json` in the same
> commit. See `learning-pi/README.md`.

Verification gate for the learning system's ingest output. Runs automatically:

1. At the end of every standalone **ingest** session (delegated from the learning-system skill).
2. At the end of any **teaching lesson** that wrote wiki pages and/or Active Concepts rows (delegated from the learning-teach skill — see its "Lesson-end ingest gate" step), or on demand.

Scope: **ingest output wherever it originates** — wiki pages, Active Concepts insight rows, question seeds, from both standalone ingests and lesson-end ingests. Review-session **grades** are gated via `GATE:grade_audit` on the Tutor (see `learning-system` Review flow); mechanical date updates alone are NOT gated.

Lesson files under `Learning System/Lessons/`, learning records, and glossary entries promoted by lessons are verified live by the `learning-teach` skill using batched fact-check subagent tasks during plan/teach, before they reach the user. They do **not** go through this gate. See `Skills/learning-teach/SKILL.md`. The two verification paths are deliberately separate.

## Config

- Reviewer model: the **calling preset's own base model** (Open WebUI runs verifiers on the model that dispatched `delegate_task` — there is no separate verifier-model setting). Enforcement rests on the deterministic Pipe checks + fixed `GATE:` prompts, not model independence. To change models, edit the preset's base model in the Open WebUI UI — see the model-per-task table in `OPENWEBUI.md`.
- Fixed verifier prompts now live in the global `subagents.system_prompt` (keyed by `GATE:`), not in this file. The envelope schemas are in `Skills/learning-review/openwebui/gate_schema.py`; the gate Pipe (`gate_pipe.py`) blocks Clerk output without a receipt. Do not bypass by editing the sysprompt.
- This file's template below is the canonical reference for `GATE:review`; the live prompt is the `GATE:review` section of `subagents.system_prompt`.

### Review prompt template (canonical — lives in subagents.system_prompt as GATE:review)

```
# GATE:review — same as below; subagent fetches SOURCE itself and Pipe checks substring
# See gate_schema.GATEReviewEnvelope: {gate:"review", concepts[], wiki_content, source_url|source_file, lesson_ref, pass_number}
# Verdict: {"verdict":"PASS|ISSUES","issues":[{"severity":"high|medium|low","location":"...","issue":"..."}]}

You are an independent, critical reviewer for a spaced-repetition learning system.
Your job is to catch problems in ingest output. You are a critic, not a rewrite bot:
never rewrite content, only flag issues with severity.

## Inputs

- SOURCE URL: <stable source URL>  OR  SOURCE FILE: <repo path>
- SOURCE CONTENT: <fetched; if empty, review for internal consistency>
- CONCEPTS: <comma-separated concept names>
- WIKI CONTENT: <full text>
- PASS (cycle): <1 or 2>
- LESSON REF: <Lessons/...md when from Tutor handoff>

## Scope / What to check / Rules — as before:
Review ONLY wiki content + Active Concepts rows; check accuracy/correctness, clarity, completeness;
high/medium only; output ONLY valid JSON {"verdict":"PASS|ISSUES","issues":[...]}, PASS only when no high/medium.
```

## Steps

### 1. Determine ingest type

From the session note and Active Concepts changes:

- **New concept** (no overlap existed) → run BOTH gates (quality + factual).
- **Enrichment** (existing concept updated) → quality gate only.

### 2. Quality gate — foreground GATE:review envelope (Pipe-enforced)

Dispatch ONE **foreground** `GATE:review` envelope via `delegate_task` (`background:false`) validated by `gate_pipe.py`:

```json
{"gate":"review","concepts":["Concept"],"wiki_content":"exact written wiki text (must match the files on disk — generation-to-emission, never a summary)","source_url":"https://...","lesson_ref":"Lessons/...md","pass_number":1}
```

Grounding (`source_url`, `source_file`, or `lesson_ref`) is required — the Pipe rejects ungrounded envelopes. Every concept must appear in `wiki_content`, and the written files must match the reviewed content (the Pipe checks both). Use `source_file` instead of `source_url` when the source is a repo file. The Pipe verifies the child chat receipt (foreground, schema, verdict coverage) before the Clerk's final message renders; blocked drafts show `⛔ BLOCKED (<code>)` with fix instructions. Save the returned verdict JSON to `Learning System/Reviews/Quality Gates/<concepts>-pass<N>-<date>.json` and show the result to the user.

### 3. Factual gate (new concepts only, same session)

For each NEW concept, spot-check key factual claims with web search. This is a same-session self-audit — the point is "did you check your claims", not a second opinion.

- For each concept insight, identify 1–2 load-bearing factual claims (mechanisms, formulas, definitions).
- Search each against authoritative sources (web search / known references).
- Flag any claim that doesn't match. If search is inconclusive, do NOT flag — note it as unverified for the user instead.

### 4. Fix loop (max 2 cycles)

- If the quality gate returns issues (or factual gate flags claims): fix the wiki/insight/question seeds, then re-run the quality gate with `PASS (cycle) = 2`, the SAME source and concepts, and the UPDATED wiki content (post-fix text — generation-to-emission: the reviewer re-checks what was actually written, not the pre-fix draft).
- Cap: **2 cycles total.** After cycle 2, anything still flagged gets surfaced to the user — no third LLM pass.
- The reviewer never rewrites content. You own final wording.

### 5. Report

Tell the user concisely:

- Gate result per concept (passed after N cycles / flags remaining), with the verdict file path(s)
- What was fixed
- Anything unverified or still flagged (with the specifics)

## Rules

- Only flag issues worth fixing. High/medium severity only; low-severity nits get one combined note.
- Reviewer is a critic, not a rewrite bot.
- Hard stop after 2 cycles. Remaining flags go to the user, always.
- Factual gate runs on new concepts only — enrichments have survived at least one human review.
- Never skip the gates silently. If a gate can't run (e.g. the subagent task fails), say so and surface what was unverified — the Pipe's `⛔ BLOCKED` is the enforcement, not a silent skip.
- The Pipe caps retries at 2 per user turn; after cap the Clerk's output shows `⛔ Withheld` and requires a manual fix.
- Never run this gate on lesson files, learning records, or glossary promotions. Those use foreground `GATE:fact_check` envelopes via `learning-teach`, not this gate; the two verification paths are deliberately separate.

## Review-session gate (standalone `/review` close)

A standalone review session writes durable artifacts that no other gate covers: one `Reviews/Review — [Concept] — [Date].md` per graded concept, the `Sessions/Session — …md` note, touched `📚 Active Concepts.md` rows (status/`last_reviewed`/`next_review`/`Last Q Type`), `🧯 Mistakes.md` rows, and `Attempts.json` transitions. Per-grade `GATE:grade_audit` validates each verdict as it is presented; this gate validates the **writes that the session persists** against the transcript and those verdicts.

Dispatch ONE **foreground** `GATE:review_session` envelope via `delegate_task` (`background:false`) at the close of the review, on the exact content written (generation-to-emission — write the notes/rows first, audit what was written, never a summary):

```json
{"gate":"review_session","concepts":["Concept A","Concept B"],"transcript":"exact Q/A + learner answers + claimed verdicts","grade_verdicts":[{"concept":"Concept A","correct_verdict":"pass"},{"concept":"Concept B","correct_verdict":"fail"}],"written_files":[{"path":"Learning System/Reviews/Review — Concept A — YYYY-MM-DD.md","content":"exact written text"},{"path":"Learning System/Sessions/Session — … — YYYY-MM-DD.md","content":"exact written text"}],"state_rows":"exact touched Active Concepts / Mistakes / Attempts text","pass_number":1}
```

The Pipe (`gate_pipe.py`) checks the envelope, that every `written_files[].path` exists on disk and matches its `content`, and that the verdict parses as `PASS|PASS_WITH_FLAGS|ISSUES`. Scope is fenced: state drift the review did **not** write (MISSION/CURRICULUM/Learning Profile/Learner History/wiki/index/log/git) is `context_notes`, never an `issue` — the state audit owns it. Save the verdict to `Learning System/Reviews/Session Audits/<concepts>-pass<N>-<date>.json`.

Fix loop: on high/medium issues fix and re-dispatch with `pass_number: 2` and the updated content; **hard cap 2 cycles**. If high/medium issues remain after cycle 2, the Pipe **renders the summary with a `⚠️ REVIEW FLAGS SURFACED` banner** (never a third pass, never a withhold — this is deliberate: a withheld final message dead-ends the session and forces a manual poke, which is the pi failure this design avoids). Surface the remaining flags to the user.

## Manual trigger

Run on demand for an existing ingest: dispatch the same review-gate subagent task with `SOURCE URL`, `CONCEPTS`, and `WIKI CONTENT` pointing at the relevant files, same as step 2.