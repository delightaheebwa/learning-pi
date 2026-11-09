# Teach ↔ Learning System Bridge Workflow

> Protocol for extracting concepts from completed teach lessons and wiring them into the spaced repetition system.

---

## Trigger

This workflow runs automatically whenever a teach session completes a lesson. No user confirmation needed.

**Trigger signal**: A lesson file was created or updated in `Teach/<mission-slug>/lessons/`.

---

## Step 1 — Read the Lesson Context

Before extracting concepts, read:

1. **The lesson HTML** (the completed lesson file) — understand what was taught
2. **The learning record** (`learning-records/NNNN-*.md`) — what insight did the learner gain?
3. **MISSION.md** — what is the learner's goal?
4. **Existing Active Concepts** — what does the learner already have scheduled?

---

## Step 2 — Determine ZPD-Based Concept Count

The number of concepts extracted is not a fixed cap. It's determined by:

1. **Read learning records**: How many lessons deep is the learner on this topic? Early lessons → fewer concepts (2–4). Later lessons → more (4–7). The learner has more scaffolding.
2. **Read Active Concepts**: How many active concepts already exist in this domain? If the learner already has 30+ concepts in a related area, they can handle more new ones.
3. **Gauge concept difficulty**: Simple definitions → fewer, deeper concepts needed. Complex multi-step skills → more granular breakdown needed.

**Heuristic**:

| Learner Stage | Concepts per Lesson |
|---|---|
| First 3 lessons in a mission | 2–3 (build foundation carefully) |
| Lessons 4–8 | 3–5 (zone of proximal development widens) |
| Lessons 9+ | 4–7 (scaffolding exists, can handle more) |

These are guidelines, not rules. Use judgment based on the actual content.

---

## Step 3 — Extract Distinct Concepts

For each concept:

1. **Name it** clearly — a retrievable label (e.g. "Eval Loop Architecture", not "The thing about interpreters")
2. **Define it** — one paragraph that captures the key insight. This becomes the wiki page content.
3. **Identify prerequisites** — does this concept depend on others already in Active Concepts?
4. **Tag the source** — the relative path to the lesson HTML (e.g. `Teach/compilers/lessons/0001-eval-loop.html`)

Quality over quantity. A "concept" must be something that can be tested via retrieval — a fact, a process, a principle, a distinction. Not a vague topic name.

---

## Step 4 — Create/Update Wiki Pages

For each extracted concept:

1. Create or update `Knowledge Wiki/wiki/<Concept-Name>.md`
2. Content structure:
   ```markdown
   # <Concept Name>
   
   <One-paragraph key insight>
   
   ## Source
   - Lesson: [Teach/compilers/lessons/0001-eval-loop.html](<relative-path>)
   - Date learned: <today>
   
   ## Connections
   - Prerequisites: <list from step 3>
   - Related concepts: <cross-refs to other wiki pages>
   ```
3. Update `Knowledge Wiki/index.md` — add entry under Concepts
4. Update `Knowledge Wiki/log.md` — add ingest entry for today

---

## Step 5 — Add to Active Concepts

For each concept, add a row to the appropriate track in `📚 Active Concepts.md`:

| Concept | Status | Prerequisites | Last Reviewed | Next Review | Source | Notes |
|---|---|---|---|---|---|---|
| Concept Name | developing | prereq list or None | today | today + 3d | Teach/<mission>/lessons/NNNN-file.html | Brief summary + wiki link |

Track selection:
- If the concept fits an existing track (aie, swe), add it there
- If it's a new domain, add a note to Live System Notes about the teach mission

---

## Step 6 — Tell the User

After extraction, give a brief summary:

```
📘 Lesson complete. Auto-scheduled {N} concepts for review:

1. **Eval Loop Architecture** — first review Jul 7
2. **AST Walking** — first review Jul 7  
3. **Bytecode vs Tree Walking** — first review Jul 7

They're in your Active Concepts. First reviews in 3 days.
```

No confirmation step — just report what happened.

---

## Step 7 — Consistency Verification

Same as the standard Learning System verification:

- [ ] Every concept in Active Concepts with today's date
- [ ] Every concept's next_review = today + 3d
- [ ] Every wiki page created → in index.md
- [ ] log.md has today's ingest entry
- [ ] Source column populated for each new concept

---

## Granularity Guidelines

| Too broad (bad) | Too narrow (bad) | Just right |
|---|---|---|
| "Compilers" | "The specific line where lexer reads a semicolon" | "Lexer Tokenization" |
| "Python" | "print() function argument syntax" | "Python Virtual Environments" |
| "Linear Algebra" | "The (1,1) entry of a rotation matrix" | "Eigendecomposition" |

A good concept passes the **retrieval test**: can I ask you about this in 7 days and get a meaningful answer that shows understanding, not just memorization?

---

## Special Cases

**Case: Concept already exists in Active Concepts**
→ Don't duplicate. If the lesson teaches a concept that's already scheduled, update the wiki page with new insights and add a note to the existing concept row referencing the lesson as additional source material. Don't reset the interval.

**Case: Lesson is a revision of a prior lesson**
→ Extract *new* or *significantly deepened* concepts only. If the lesson is truly just a re-teach of the same concepts, create a learning record noting the revision but don't add duplicate Active Concept entries.

**Case: Mission change mid-course**
→ If the mission shifts, pause existing concepts from the old mission direction and start fresh. Add a learning record capturing why the mission changed.
