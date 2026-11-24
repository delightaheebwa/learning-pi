# Solo-first implementation todo

Plan: `docs/plans/solo-first-implementation.md`
Decision record: `docs/adr/ADR-0003-solo-first-operating-mode.md`

Checkboxes tick as slices land. Every task is an ordinary commit: no `.pi/`, `test/`,
`contracts/`, or `CONTRACT.md` files may appear in any task's diff.

## Task 1: Excalidraw parser and tests

**Description:** `state/scripts/parse_excalidraw.py` reads a `.excalidraw` file and emits a
`GRAPH_CANDIDATES`-shaped JSON on stdout. Nodes come from labeled shapes and standalone text.
Chain candidates come from fully bound arrows. Geometrically inferred edges go to `notes[]`
only. The parser is stdlib-only, uses argparse, and follows the house script pattern.

**Acceptance criteria:**
- [x] Nodes: a shape's label comes from the bound text element, preferring `originalText` over
      `text` via `containerId`; a standalone text element is a node; elements with `isDeleted`
      are skipped
- [x] Edges: an arrow becomes a chain candidate only when both `startBinding.elementId` and
      `endBinding.elementId` resolve; the parser reads `elementId` and treats other binding
      fields as optional
- [x] Inferred edges: an unbound or half-bound arrow gets a geometric fallback (nearest
      container within a threshold), lands in `notes[]` marked as inferred, and is never proposed
      as a chain
- [x] Provenance: every node and chain references the `--source` path (the source note) with a
      non-empty `file` value
- [x] Exits: 0 on a valid file with at least one node; non-zero on invalid JSON, an empty
      element array, or zero parseable nodes
- [x] No unknown fields in output records: the emitted JSON passes `pi/graph.py merge`
      validation shape (fields from the merge spec only)

**Verification:**
- [x] `python3 -m unittest discover -s scripts -p '*_test.py'` passes from `state/`, including
      the new `parse_excalidraw_test.py` with synthetic in-test fixtures
- [x] `scripts/learn-check --no-load` green
- [x] `git diff --stat` shows only the two new files

**Dependencies:** None
**Files likely touched:** `state/scripts/parse_excalidraw.py`,
`state/scripts/parse_excalidraw_test.py`
**Estimated scope:** M

## Checkpoint 1

- [x] State unit tests pass from `state/`
- [x] `scripts/learn-check --no-load` green
- [x] `python3 scripts/check-docs` green

## Task 2: Pilot artifacts

**Description:** Two new files in `state/Learning System/Core/` following the existing template
naming and style. `📓 Learning Log.md` records the pilot: what was tried, prediction, result,
next experiment, one or two changes at a time. `🧭 Memorization Filter.md` records the three
questions (why is this important, how does it relate, is high-level mastery needed) and where
the outcome lands: the `Open Question` cell of the concept's row, with a `Type memory` change
for facts that survive the filter.

**Acceptance criteria:**
- [x] Learning log exists with a header matching the existing template style and a worked first
      row for the pilot start
- [x] Memorization-filter doc lists the three questions and the recording convention, and cites
      ADR-0003 as its decision record
- [x] `audit_state.py` stays silent about both files (new files are audit-invisible)

**Verification:**
- [x] `python3 scripts/audit_state.py --root .` or a `/audit` run shows no new errors or
      warnings caused by these files
- [x] State commit includes only `state/Learning System`

**Dependencies:** None (parallel-safe with Task 1)
**Files likely touched:** `state/Learning System/Core/📓 Learning Log.md`,
`state/Learning System/Core/🧭 Memorization Filter.md`
**Estimated scope:** S

## Task 3: Transcription conventions

**Description:** A new section in `state/Knowledge Wiki/AGENTS.md` defining the mindmap
transcription flow: photo naming and sizing (`raw/assets/mindmap-<slug>-<date>.jpg`, under about
1 MB), transcription location and naming (`raw/mindmaps/<date>-<slug>.excalidraw`, immutable once
confirmed), the confirm-before-ingest rule, the source-note requirement (photo embedded, file
linked), and the parser invocation.

**Acceptance criteria:**
- [x] The section names every file location and the naming patterns from the plan's flow diagram
- [x] The confirm step is stated as a rule: transcription is a faithful copy, and the photo is
      the source of truth
- [x] No banned tokens; `scripts/check-docs` stays green

**Verification:**
- [x] `python3 scripts/check-docs` green
- [x] `scripts/learn-check --no-load` green

**Dependencies:** Task 1 (the parser invocation it documents exists)
**Files likely touched:** `state/Knowledge Wiki/AGENTS.md`
**Estimated scope:** S

## Task 4: First live ingest, end to end

**Description:** One real photographed mind-map goes through the whole flow: archive, transcribe,
confirm, source note, parse, standalone ingest, `log.md` row. Graph candidates are opt-in: the
learner and the agent curate which box statements qualify as subject propositions, then any
merge runs through the unchanged `graph-extract` → `merge` → `graph-audit` path with the
`CLERK_WRITES.graph` receipt.

**Acceptance criteria:**
- [ ] Photo in `raw/assets/`, transcription in `raw/mindmaps/`, source note in `raw/sources/`,
      all named per the Task 3 conventions
- [ ] The learner confirmed the transcription before ingest
- [ ] Parser output reviewed: binding-derived candidates separated from inferred `notes[]`
- [ ] `log.md` has the ingest row; the state audit is clean; the state commit follows the
      two-path commit rule (`state/Learning System` and `state/Knowledge Wiki` only)

**Verification:**
- [ ] `git status` clean afterwards, with `Pending Ingest.json` and `.tmp/` untracked as before
- [ ] State audit shows no new errors or warnings

**Dependencies:** Tasks 1-3
**Files likely touched:** state wiki files only (raw assets, mindmaps, sources, `log.md`)
**Estimated scope:** M

## Checkpoint 2

- [ ] The flow worked on a real map, start to commit
- [ ] The learner confirms the confirm step is tolerable before the pilot continues

## Task 5: Pilot runbook and start

**Description:** The runbook lands in the learning log's header: run for four to six weeks, one
or two changes at a time, memorization filter applied whenever a fact fails repeatedly, and a
scheduled first look at the log. That first look decides among the ADR-0003 revisit triggers:
nothing, an ordinary-commit adjustment, or a small revise-door change.

**Acceptance criteria:**
- [ ] The runbook names the pilot window, the change budget, and the first review date
- [ ] The learning log carries its first real entry from the first solo cycle under the new mode

**Verification:**
- [ ] Log entry exists and names what was tried, the prediction, the result, and the next
      experiment

**Dependencies:** Task 4 (the first cycle exists to log)
**Files likely touched:** `state/Learning System/Core/📓 Learning Log.md`
**Estimated scope:** S

---

# Reading mode implementation todo

Plan: `tasks/plan.md`
Specs: `docs/specs/CAPABILITY-MAP-reading-mode.md` + `docs/specs/SPEC-*.md` (approved 2026-11-24)

The solo-first tasks above are untouched and stay open. Phases 1–3 here are
ordinary commits touching only `.pi/` and `state/`; only V1/V2 touch
`contracts/`, `CONTRACT.md`, or `test/`, in one `revise(contract):` commit the
user approves first.

## Task R1: Register the `read` flow in the gate engine

**Description:** `[[FLOW:read]]` today silently fails open as flow `"other"`
(no gating). Add `read` to `FLOW_TAG_RE` and the `Flow` union in
`.pi/extensions/learning-gate/gate-core/primitives.ts`, then audit every
flow comparison in `gate-core/engine.ts` (the teach/resume vs review/solo
branches around lines 326–876) before extending `foundationApplies` at
`engine.ts:138` so reading-flow claims turns must declare a valid
`turn_kind`. Repair sequencing, the attack menu, and triage/attack/autopsy
shape checks must NOT arm in the reading flow. Update the stale flow lists in
the doc comments (`index.ts:10`, `primitives.ts:362`).

**Acceptance criteria:**
- [x] `detectFlow` returns `"read"` for a `[[FLOW:read]]` message; `"other"`
      still fails open for unmarked messages
- [x] A reading-flow claims turn with no `turn_kind` is withheld; one with a
      valid kind passes; `triage|attack|autopsy|repair` shapes are not enforced
      in the reading flow
- [x] Every existing gate suite passes unchanged (teach/review/solo behavior
      is byte-identical)

**Verification:**
- [x] Deno gate suites + `scripts/learn-check --no-load` green
- [x] No file under `contracts/`, `CONTRACT.md`, or `test/` in the diff

**Dependencies:** None
**Files likely touched:** `.pi/extensions/learning-gate/gate-core/primitives.ts`,
`.pi/extensions/learning-gate/gate-core/engine.ts`,
`.pi/extensions/learning-gate/index.ts`
**Estimated scope:** M

## Task R2: Prompt, skill skeleton, and router entries

**Description:** Create `.pi/prompts/read.md` (9th prompt, `[[FLOW:read]]`)
and `.pi/skills/learning-read/SKILL.md` (6th skill) as a skeleton: session
pipeline overview, the module map, and placeholders for the Phase-2 behavior
sections. Add router entries in `.pi/APPEND_SYSTEM.md` ("I'm going to read",
"I'm reading", "reading session" → learning-read + `[[FLOW:read]]`) and the
trigger note in `.pi/skills/learning-system/SKILL.md`. Confirm the
presence-based resource checks tolerate the extra files before Phase 3
(expected-list edits are deferred to V1).

**Acceptance criteria:**
- [x] "I'm going to read X" routes to the reading flow and loads
      learning-read; teach/review/solo routes unchanged
- [x] `scripts/learn-check --no-load` stays green with the new files present
      (presence-based checks tolerate extras; if not, stop and move the
      expected-list edits into V1's commit)
- [x] The prompt carries exactly one `[[FLOW:read]]` tag matching the check's
      regex shape

**Verification:**
- [x] `scripts/learn-check --no-load` green
- [x] Manual: a routing sentence in a scratch pi session starts the reading
      flow, not a teach session (routing trace + gate flow-detection smoke;
      live confirmation comes with the Checkpoint 4 dry run)

**Dependencies:** Task R1
**Files likely touched:** `.pi/prompts/read.md`, `.pi/skills/learning-read/SKILL.md`,
`.pi/APPEND_SYSTEM.md`, `.pi/skills/learning-system/SKILL.md`
**Estimated scope:** M

## Checkpoint 3

- [x] A reading session starts gated (one turn tag per message enforced)
- [x] Teach/review/solo flows unchanged (suites green)
- [ ] Review with human before Phase 2

## Task B1: Session brief (`benchmark-session`)

**Description:** The behavior section of `learning-read/SKILL.md` for the
brief: four parts in order (session scope from the attached text, outcome
definition, exactly 5 low / 5 mid / 5 high free-recall questions written at
use-level with real cues, plain keyword list), the stated 90/80/70 targets and
+1d/+1w/+1m retrieval dates, the no-attached-text rule (ask for the text, no
questions), and the no-teaching rule (no answers, no summaries; gist-level
orientation only). Extend `.pi/agents/fact-check.md` with the reading-flow
grounding rule: every question and keyword must be traceable to the attached
source, else the turn is withheld.

**Acceptance criteria:**
- [x] The brief is one turn, then stops; 15 questions, all free-recall
- [x] A declaration without attached text yields a text request and zero
      questions
- [x] fact-check rules state the grounding withhold for unanchored brief items
- [x] No teaching content in the brief per the skill's own examples

**Verification:**
- [x] `scripts/learn-check --no-load` green
- [ ] Manual dry run: declare + attach a short text; brief comes back with all
      four parts, each question answerable from that text (Checkpoint 4)

**Dependencies:** Task R2
**Files likely touched:** `.pi/skills/learning-read/SKILL.md`, `.pi/agents/fact-check.md`
**Estimated scope:** M

## Task F1: Free recall (`free-recall`)

**Description:** The free-recall procedure in `learning-read/SKILL.md`:
closed-book dump (never interrupted, never corrected mid-dump), then
`sure|hunch|no-idea` confidence marks, then an itemized check (wrong /
missing / right) where every verdict quotes the source, feedback only after
generation. `sure`-but-wrong items are flagged as priority gaps and carried
into the session handoff. Add the generate-before-feedback and
quoted-verdict rules to the relevant verifier prose (fact-check / quiz-audit
rules as they apply to reading turns).

**Acceptance criteria:**
- [x] No feedback before dump completion + confidence marks, stated as a rule
      the verifier enforces
- [x] Every verdict shape includes a source quote requirement
- [x] The handoff records `sure`-wrong items as priority gaps
- [x] The same procedure is written to run verbatim at retrieval sessions

**Verification:**
- [x] `scripts/learn-check --no-load` green
- [ ] Manual dry run: dump a remembered section; check arrives only after
      confidence marks; every verdict carries a quote (Checkpoint 4)

**Dependencies:** Task R2 (parallel-safe with B1 and M1)
**Files likely touched:** `.pi/skills/learning-read/SKILL.md`, `.pi/agents/fact-check.md`,
`.pi/agents/quiz-audit.md`
**Estimated scope:** M

## Task M1: Model diagnosis (`model-diagnose`)

**Description:** The diagnosis procedure in `learning-read/SKILL.md`: one
structured verdict per presentation (right / wrong / missing / misplaced),
each verdict quoting both the learner's words and the source, one diagnosis
turn per presentation, the revision loop closing on a clean or consciously
parked model, the final model version verbatim in the handoff. State the
forbidden move explicitly: pi never rewrites, redraws, or "cleans up" the
learner's model (the existing anti-ghostwriting stance carries into the
reading flow). Reference the existing photo → excalidraw ingestion path for
photographed maps; no attack battery, no repair ladder, no clones in this
flow.

**Acceptance criteria:**
- [ ] The four verdict categories are defined with quote requirements for each
- [ ] Diagnose-never-rewrite stated as a withhold-level rule
- [ ] Session close records the final model + diagnosis history

**Verification:**
- [ ] `scripts/learn-check --no-load` green
- [ ] Manual dry run: paste a small mermaid/ascii model; diagnosis quotes
      learner + source; pi produces no corrected model

**Dependencies:** Task R2 (parallel-safe with B1 and F1)
**Files likely touched:** `.pi/skills/learning-read/SKILL.md`, `.pi/agents/fact-check.md`
**Estimated scope:** M

## Checkpoint 4

- [ ] Full session dry-run under the gate: declare + attach → brief → (read) →
      dump + confidence → quoted check → model → diagnosis → close
- [ ] No teach-flow machinery fired anywhere in the session
- [ ] Review with human before Phase 3

## Task P1: ops.py benchmark type + attempt `--level`

**Description:** Add `"benchmark": [1, 7, 30]` to `DEFAULT_INTERVALS` in
`state/scripts/ops.py`, with result-agnostic index advance for benchmark rows
(every attempt advances the index; a fail never steps back — the ladder never
resets). Add a validated optional `--level low|mid|high` stored on the
attempt record (record-only; never a scheduling input). Unit tests in
`state/scripts/ops_test.py` for both.

**Acceptance criteria:**
- [x] A benchmark attempt advances the interval index on pass AND on fail
- [x] Unknown types still fall back to the concept schedule (unchanged)
- [x] `--level` is validated, stored, and ignored by scheduling
- [x] `ops_test.py` covers the new type and the level field

**Verification:**
- [x] `python3 -m unittest discover -s state/scripts -p '*_test.py'` green
- [x] `scripts/learn-check --no-load` green

**Dependencies:** None (parallel-safe with Phase 2)
**Files likely touched:** `state/scripts/ops.py`, `state/scripts/ops_test.py`
**Estimated scope:** M

## Task P2: Benchmark ledger + queue integration

**Description:** One `Active Concepts` row per reading session
(`Type benchmark`), with the 15 questions, level labels, and source
reference in a benchmark ledger file under `state/Learning System/Core/`.
`ops.py queue` emits due benchmark items at +1/+7/+30 as one grouped unit
(one reading session = one queue entry carrying its 15 questions). A miss
writes a Mistakes row so the question re-appears at the next session
(existing due-mistake queue slots) without moving the ladder dates. After
the +1m shot the row graduates per the existing clerk prose pattern. Update
the schedule prose that today names only the four types:
`.pi/agents/review-clerk.md`, `.pi/agents/review-session-audit.md`,
`state/AGENTS.md` SRS section, `.pi/skills/learning-system/SKILL.md`
intervals line.

**Acceptance criteria:**
- [ ] A due reading session appears in the queue with all 15 questions
- [ ] A missed question re-appears next session; its +1/+7/+30 dates never
      change
- [ ] The third shot graduates the row (far-future next_review + graduated
      marking)
- [ ] Concept/memory/procedure/design scheduling is unaffected
- [ ] The audit's interval-consistency check knows the fifth schedule

**Verification:**
- [ ] `ops_test.py`: simulated +1/+7/+30 queue dates, miss-no-reset, graduation
- [ ] `scripts/learn-check --no-load` green

**Dependencies:** Task P1
**Files likely touched:** `state/scripts/ops.py`, `state/scripts/ops_test.py`,
`state/Learning System/Core/` (ledger file), `.pi/agents/review-clerk.md`,
`.pi/agents/review-session-audit.md`
**Estimated scope:** L (prose updates beyond the code are called out in the
plan's risk table; split the prose-only edits into a follow-up ordinary commit
if the session runs long)

## Task P3: Retrieval session shape and close

**Description:** The retrieval-session section of
`learning-read/SKILL.md` (or `learning-review`, wherever the queue session
reads): open with the free-recall dump + confidence (F1's procedure,
verbatim), then the 15 benchmark questions as one quiz batch (`qtype
free-recall`), grade batch, quoted check with `sure`-wrong flags, then a
per-level score report (hit rate vs 90/80/70 for this shot plus the
trajectory across shots) written into the session note by `review-clerk` and
tallied by `review-session-audit`. Close through the existing review-close
machinery; benchmark items are exempt from the concept/design clone mandate
(type-gated rule, unchanged).

**Acceptance criteria:**
- [ ] Session order is dump → questions → graded check → score report, with
      feedback withheld until generation completes
- [ ] The score report derives from attempt records and matches them
- [ ] Close passes the review-session audit with the fifth schedule + tally

**Verification:**
- [ ] `scripts/learn-check --no-load` green
- [ ] Manual dry run of one retrieval session end-to-end

**Dependencies:** Tasks P2, F1
**Files likely touched:** `.pi/skills/learning-read/SKILL.md`,
`.pi/agents/review-clerk.md`, `.pi/agents/review-session-audit.md`,
`state/AGENTS.md`
**Estimated scope:** M

## Checkpoint 5

- [ ] Simulated +1d/+1w/+1m retrieval in `ops_test.py` green
- [ ] One full retrieval dry-run closes cleanly through the review machinery
- [ ] Review with human before the revise door

## Task V1: Author the contract change (invariants + tests)

**Description:** Write, without committing: the `R-*` invariants in
`contracts/learning-core.json` (brief grounding, no-teaching-in-brief,
generate-before-feedback, quoted verdicts, diagnose-never-rewrite,
fixed 1d/1w/1m schedule, benchmark/concept scheduling isolation,
score-report-matches-attempts), each bound to its named test; the
`CONTRACT.md` prose mirror in the existing section format; the `test/`
updates — `test/contract/check_learning_layer.py` expected lists (9th
prompt, 6th skill), new gate-suite cases (ungrounded brief withheld,
premature feedback withheld, unquoted diagnosis withheld, ghostwritten
model withheld, score-report mismatch withheld, benchmark schedule
integrity), and `test/contract/load_probe.py` expectations if it pins
prompt counts. The contract version field bumps; its value is read from the
JSON, never restated in prose. Run the full battery including the load probe.

**Acceptance criteria:**
- [ ] Every new invariant has ≥1 passing test; every listed test name matches
- [ ] `scripts/learn-check` (full, with load) green
- [ ] The staged diff touches only `contracts/`, `CONTRACT.md`, and `test/`
      beyond what Phases 1–3 already landed

**Verification:**
- [ ] `scripts/learn-check` full pass
- [ ] `python3 scripts/check-docs` green
- [ ] `node scripts/floor-guard.mjs` clean (no suppressions, no weakened bar)

**Dependencies:** Checkpoint 5
**Files likely touched:** `contracts/learning-core.json`, `CONTRACT.md`,
`test/contract/check_learning_layer.py`, `test/contract/load_probe.py`,
gate-suite test files
**Estimated scope:** L (by design — the door requires the triplet in one
commit; Phases 1–3 are already landed, so the diff is contract + tests only)

## Task V2: User-approved `revise(contract)` commit + docs

**Description:** Present the full contract diff to the user. On approval,
land it as one `revise(contract):` commit (the CI subject gate requires it
for any commit touching `contracts/`, `CONTRACT.md`, or `test/`). Then the
ordinary docs commit: `docs/README.md` source-of-truth map gains the
`docs/specs/` row and the new flow/skill entries; this plan and the todo
checkboxes tick.

**Acceptance criteria:**
- [ ] User approved the contract diff before the commit landed
- [ ] Commit subject carries `revise(contract):`
- [ ] `docs/README.md` maps the new flow, skill, and specs

**Verification:**
- [ ] `scripts/learn-check` full pass; `python3 scripts/check-docs` green;
      `scripts/check-skills` green; `node scripts/floor-guard.mjs` clean
- [ ] CI's subject gate passes on the revise commit

**Dependencies:** Task V1
**Files likely touched:** `contracts/`, `CONTRACT.md`, `test/` (the approved
diff), `docs/README.md`, `tasks/todo.md`, `tasks/plan.md`
**Estimated scope:** M

## Final checkpoint

- [ ] User runs one real reading session: declare + attach → brief → read →
      dump + confidence → model → diagnosis → close
- [ ] The +1d retrieval fires the next day and the score report records
- [ ] `/teach` still runs an interrogation session unchanged
