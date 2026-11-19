# Implementation plan: solo-first operating mode

- Status: Active
- Date: 2026-11-19
- Decision record: `docs/adr/ADR-0003-solo-first-operating-mode.md`
- Task list: `tasks/todo.md`

## What the learner gets

A photograph of a paper mind-map becomes first-class state. The photo and an `.excalidraw`
transcription land in the wiki raw layer, a parser reduces the transcription to nodes and edges,
and a standalone ingest records the snapshot in the log and, when wanted, contributes subject
propositions to the graph. The learner also gets the two pilot artifacts: a learning log and the
memorization-filter protocol.

## Decisions locked

| # | Decision | Why |
|---|---|---|
| D1 | The photo is the immutable source of truth and lives in `raw/assets/` | ADR-0003 transcription discipline. `Knowledge Wiki/raw/assets/` already holds about 70 binary attachments. |
| D2 | The `.excalidraw` transcription lives in a new `raw/mindmaps/` directory, immutable once confirmed | The raw layer is immutable. Corrections are new dated files, matching the raw-source rule. |
| D3 | The parser is a mechanical reducer, not an author | Node text comes verbatim from the drawing. Curation happens at merge review, so no step authors the learner's model. |
| D4 | Binding-derived edges become chain candidates. Geometrically inferred edges go to `notes[]` only | The graph schema rejects unknown fields, so an `inferred` field would fail `merge`. `notes[]` keeps the two tiers separate, which ADR-0003 requires. |
| D5 | No render tooling in v1. The learner confirms by opening the `.excalidraw` in an editor | excalidraw.com works offline and the VS Code extension edits `.excalidraw` files in place. A render script would add a Node dependency for no new capability. |
| D6 | The parser ships as `state/scripts/parse_excalidraw.py` with a co-located test | This matches the house pattern for state scripts. CI discovers `*_test.py` automatically, so no workflow file changes. |
| D7 | Graph candidates are opt-in per ingest | The wiki snapshot is mandatory. The graph holds subject propositions, and mind-map wording is the learner's own, so each ingest decides what qualifies. |
| D8 | The plan lives here; the checkboxes live in `tasks/todo.md` | The repo keeps durable documents under `docs/`. The living checklist rides with the work. |

## Flow

```
photo of a paper mind-map
  → archived     raw/assets/mindmap-<slug>-<date>.jpg        (resized under about 1 MB)
  → transcribed  raw/mindmaps/<date>-<slug>.excalidraw       (agent, faithful copy)
  → confirmed    learner opens the file and points at misreads
  → source note  raw/sources/<date> - <slug> - mindmap.md    (embeds the photo, links the file)
  → parsed       python3 scripts/parse_excalidraw.py <file>  (run from state/)
  → ingested     standalone ingest: raw files via ops.py apply, log.md row,
                 optional curated candidates through the unchanged
                 graph-extract → merge → graph-audit path
```

The standalone ingest needs no `Pending Ingest.json`. The clerk already accepts a task payload
with inline material, and the wiki log records a standalone ingest with no handoff envelope.

## Task list (index)

- Task 1: Excalidraw parser and tests (foundation)
- Checkpoint 1: state unit tests and `learn-check` green
- Task 2: Pilot artifacts (learning log, memorization filter)
- Task 3: Transcription conventions in the Knowledge Wiki agent rules
- Task 4: First live ingest, end to end
- Checkpoint 2: the flow works on a real map
- Task 5: Pilot runbook and start

Acceptance criteria and verification steps for each task are in `tasks/todo.md`.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Excalidraw schema drift breaks the parser | Med | Parse only `elementId` and treat other binding fields as optional, per ADR-0003. Re-test on any version bump. |
| Inferred edges merge silently | High | D4 keeps inferred edges in `notes[]`, never proposed as chains. |
| A transcription error corrupts the verbatim record | High | The photo is the source of truth, and the confirm step precedes ingest. |
| Photos bloat the state tree | Med | Resize guidance keeps files under about 1 MB. Existing assets total 41 MB with a 3.1 MB maximum. |
| A task accidentally touches `.pi/`, `test/`, or `contracts/` | High | Each task lists its exact files, and `git diff --stat` is checked before every commit. The CI subject check would fail such a commit anyway. |
| A wiki page appears without an `index.md` row | Low | Mindmap-only ingests stay raw-layer, so no wiki page exists and no index row is needed. The clerk flow already covers pages it creates. |

## Out of scope

- No `.pi/`, `test/`, `contracts/`, or `CONTRACT.md` changes. The revise door stays closed.
- No Mermaid fallback, no Excalidraw MCP server, no render tooling.
- No CI edits. The state unit-test discovery pattern picks up the new test by itself.
- No ingest envelope changes. The flow uses the standalone ingest path.

## Revisit

ADR-0003's "Revisit when" list governs: pilot-log conflicts with the entry or graduation gates,
memorization-filter promotion, Excalidraw schema drift, or a superseded decision. The runbook in
Task 5 schedules the first look at the log.
