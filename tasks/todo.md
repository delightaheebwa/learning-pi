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
