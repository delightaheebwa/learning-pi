# Plan: Teach ↔ Learning System Wiring

## Goal

Use teach for lesson creation, Learning System for long-term retention. Two systems, one pipeline.

---

## Architecture

```markdown
┌─────────────────────────────────────────────────────────────┐
│  TEACH SKILL (Pocock)                                       │
│  Creates: lessons/*.html, reference/*.html,                 │
│           learning-records/*.md, MISSION.md                 │
│  Responsibility: Authoring beautiful lessons                │
│                 + same-session quizzes (fluency)            │
│                 + zone of proximal development              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼  (after lesson completed)
┌─────────────────────────────────────────────────────────────┐
│  BRIDGE: Concept Extraction                                 │
│  - Extract key concepts from completed lesson               │
│  - Create wiki pages linking back to lesson HTML            │
│  - Add to Active Concepts with 3d interval                  │
│  - Tag concepts with source lesson path                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  LEARNING SYSTEM (spaced retrieval)                         │
│  - Active Concepts table (next_review, intervals)           │
│  - Due-review queue computed on-the-fly                    │
│  - Retrieval prompts (3d → 7d → 14d → 30d → 90d → done)   │
│  - Review notes + session notes                            │
│  Responsibility: Cross-session memory (storage strength)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼  (review reveals gaps)
┌─────────────────────────────────────────────────────────────┐
│  FEEDBACK LOOP                                             │
│  - Repeated failures on a concept → lesson may need fixing │
│  - Review notes can reference the lesson for re-study      │
│  - Learning records get updated with review insights        │
└─────────────────────────────────────────────────────────────┘
```

---

## End-to-End Flow

### Phase 1 — Learn (Teach)

User says "teach me about X". Teach skill:

1. Clarifies mission → writes `file MISSION.md`
2. Gathers resources → writes `file RESOURCES.md`
3. Creates lesson `file 0001-<topic>.html` with knowledge + interactive quiz
4. Creates reference docs (`file reference/*.html`) — cheat sheets, glossaries
5. Creates learning record (`file learning-records/0001-*.md`) — key insight captured

### Phase 2 — Ingest (Bridge)

After lesson completed:

1. Zo extracts **distinct concepts** from the lesson (3–5 max per lesson)
2. For each concept:
   - Creates or updates a Knowledge Wiki page under `Knowledge Wiki/wiki/`
   - Adds row to Active Concepts table:
     - Status: `developing`
     - Last Reviewed: today
     - Next Review: +3 days
     - Interval: `3d`
     - Source: path to the lesson HTML (e.g. `file Teach/compilers/lessons/0001-eval-loop.html`)
   - Updates `Knowledge Wiki/index.md` and `file log.md`
3. Asks user: "I found these concepts from today's lesson. Add to review schedule?" *(user confirms, or adjusts)*

### Phase 3 — Retain (Learning System)

Standard spaced repetition kicks in:

1. 3 days later: due review appears
2. Zo asks retrieval question *(no multiple choice, no hints until struggle)*
3. If correct → advance interval (3d → 7d → 14d → 30d → 90d → consolidated)
4. If wrong → re-explain, reset to 3d, **link back to the source lesson** for re-study
5. Review note written to `Learning System/Reviews/`
6. Session note written to `Learning System/Sessions/`

### Phase 4 — Feedback

If a concept from a teach lesson consistently fails reviews:

- The review note captures the failure pattern
- Next time the user opens the teach workspace, Zo can surface: "The eval loop concept has been failing review — want to revise lesson 0001?"

---

## What Changes

### Learning System (small additions)

| Change | Why |
| --- | --- |
| Add optional `source` column to Active Concepts | Links concept back to teach lesson HTML |
| During review, after retrieval attempt, show source lesson link | Context for re-study on failure |
| New rule: treat teach lessons as ingest sources | Triggers bridge after lesson completion |

### Teach Skill (no changes)

Teach runs as-is. The bridge is external wiring, not a modification of the skill. This keeps the skill updateable from upstream.

### New File: Bridge Workflow

A small document at `Learning System/Plans/teach-bridge-workflow.md` that defines:

- How to extract concepts from a completed lesson
- What granularity to use (one concept ≈ one retrievable fact/skill)
- The ingest confirmation step (ask user before scheduling)

### Directory Convention

Teach workspaces live under `Teach/<mission-slug>/`:

```markdown
Teach/
├── compilers/
│   ├── MISSION.md
│   ├── RESOURCES.md
│   ├── lessons/
│   │   ├── 0001-eval-loop.html
│   │   └── 0002-jit-compilation.html
│   ├── reference/
│   │   └── compiler-glossary.html
│   ├── learning-records/
│   │   └── 0001-eval-loop-discovery.md
│   └── assets/
│       └── shared.css
└── calculus-3/
    └── ...
```

This keeps teach workspaces cleanly separated from the Learning System files.

---

## What Stays Separate

| Teach owns | Learning System owns |
| --- | --- |
| Lesson HTML (beautiful, printable) | Concept scheduling & intervals |
| Reference docs (glossaries, cheat sheets) | Retrieval prompts & grading |
| Learning records (ADRs of insights) | Review notes & session notes |
| Quizzes (same-session fluency) | Cross-session retrieval (storage) |
| Mission.md | Wiki pages for concepts |
| Zone of proximal development | Knowledge Wiki index & log |

---

## Why Not Merge?

- Teach is designed for lesson *creation*; Learning System is designed for *retention*. Merging them would create one bloated system that does both poorly.
- Teach skill gets updates from upstream (Matt Pocock's repo). If we fork it, we lose that.
- The Learning System already has a robust ingestion path — we're just adding a new *source*.
- Two separate concerns = two files to debug, not one monolith.

---

## Implementation Order

1. **✅ Add `source` column** to Active Concepts table — Done 2026-07-04
2. **✅ Write bridge workflow doc** — Done (`Learning System/Plans/teach-bridge-workflow.md`)
3. **✅ Update the ingest rule** — Done (new rule `#75e83351` — auto-extraction from teach lessons)
4. **✅ Create `Teach/` directory** — Done 2026-07-04
5. **Test with one lesson** — teach something small, extract concepts, run the review cycle
6. **Iterate on granularity** — tune concept size so retrieval is challenging but fair

---

## Open Questions

- Should the concept extraction be automatic or manual? → **Automatic. After each lesson, concepts are extracted and added to Active Concepts with no confirmation step.**
- Max concepts per lesson into Active Concepts? → **ZPD-based. Read the learning-records to determine how much the learner already knows, then extract enough concepts to keep them at the edge of competence. Typically 3–7, but flexible.**
- When a teach lesson gets *updated* (revised), what happens to already-scheduled concepts? → **Don't auto-reset. The review cycle will reveal if re-study is needed through retrieval failures.**