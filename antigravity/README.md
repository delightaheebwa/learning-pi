# Antigravity Desktop Learning Layer

`antigravity/` holds the Antigravity Desktop control layer for the spaced-repetition learning system. `install.sh` symlinks it into the learning state repository (`~/learning-system/.agents/`) and excludes it from git there.

---

## 1. Quick Setup

```bash
# In ~/learning-pi:
./install.sh ~/learning-system
```

Creates:
- `~/learning-system/.pi` -> `~/learning-pi/.pi` (CLI / pi runtime)
- `~/learning-system/.agents` -> `~/learning-pi/antigravity` (Antigravity Desktop)
- Adds `.agents/` and `.pi/` to `~/learning-system/.git/info/exclude`.

Launch Antigravity Desktop and open `~/learning-system` as a workspace.

---

## 2. Slash Commands (`/`)

Workflows are available as slash commands in the Antigravity Desktop chat:

| Command | Action | Backing Agents |
| :--- | :--- | :--- |
| **`/teach <topic-or-source>`** | Stress-test your own model: bring the material, your notes, and a closed-book model; scout grounds sources → triage → targeted attacks → model patch (v1→v2) → auto-ingest | `scout`, `verifier`, `ui-generator`, `clerk`, `auditor`, `naive-student` |
| **`/lesson`** | Next sequential curriculum lesson: point at the raw material and its Further Reading, then interrogate the model you bring back (auto-ingests at session end) | `scout`, `verifier`, `ui-generator`, `clerk`, `auditor`, `naive-student` |
| **`/continue`** | Resume a paused interrogation at the first unresolved attack (scout always recovers the resume pointer) | `scout`, `verifier`, `ui-generator`, `clerk`, `auditor`, `naive-student` |
| **`/pause`** | Bank the learner's model + open attack list cleanly, deliver a model-recall exit ticket, and exit | `verifier`, `clerk`, `auditor` |
| **`/review`** | Daily spaced-repetition review: unlabeled interleaved + synthesis + decoy items, trace-graded (no MCQs), then a learner Q&A pause before auto-persisting and auto-ingesting | `scout`, `verifier`, `ui-generator`, `clerk`, `auditor`, `naive-student` |
| **`/solo`** | AI-free closed-book assessment (no hints/teaching/widgets/MCQs; operational items only; feeds independence gate) | `scout`, `verifier`, `clerk`, `auditor`, `naive-student` |
| **`/ingest [content]`** | Reconcile lesson handoffs or raw notes into Knowledge Wiki + Active Concepts | `clerk`, `auditor` |
| **`/audit`** | Read-only state consistency audit + wiki provenance check | None (runs local python scripts) |
| **`/llm-wiki`** | Karpathy-style knowledge wiki guidelines & provenance rules | None (guidelines) |

### Workflow stance: you read, the AI interrogates

This layer is not a primary teacher. You read raw material (books, papers, docs, code, projects, exercises), build a mental model, and take notes. You then hand the material, your notes, and a closed-book model to the system, which stress-tests you: triage of solid / missing / suspect claims, one targeted attack per flaw (mechanism press, counterexample, perturbation, source clash, sabotage), then a model patch preserved verbatim as v1 → breaking case → v2. The AI never teaches a topic cold, never rewrites your words, and never ends a session with a quiz-and-summary. Gaps and false confidence go into `Mistakes.md` / `Attempts.json` so `/review` and `/solo` re-test them.

---

## 3. Subagents Architecture

Six custom subagents are defined in `.agents/agents/` and invoked via `invoke_subagent`:

1. **`scout`** (`model: flash` - Gemini 3.8 Flash, medium effort): Fetches and persists the material the learner is about to read (curriculum docs + every Further Reading URL), hashes sources, scans contradictions, and harvests anomaly and misapplication candidates used to build grounded attacks. Never summarizes material for the learner.
2. **`verifier`** (`model: flash` - Gemini 3.8 Flash, medium effort): Independent read-only gatekeeper policing **two dimensions** — epistemic truth (claims vs raw sources, conceptual `omitted_foundations`, contradiction surfacing) and mental-model integrity (`MODEL_GHOSTWRITING`, `UNGROUNDED_HOLE`, `LECTURE_SLIP`, `SPOONFEEDING_DETECTED`, `CUE_LEAKAGE`, `SHALLOW_PASS`), plus triage grounding, counterexample validity, MCQ legality (legacy probes only), concept-label scoping, qualitative-trace requirements, battery grading, visual sufficiency (`VISUAL_PLAN_MISSING`, `VISUAL_MISSED`), and Predict-Before-Render widget audits. Explicitly does **not** flag a missing derivation as an omission.
3. **`ui-generator`** (`model: flash` - Gemini 3.8 Flash, high effort): Widget builder. Receives the Tutor's complete spec (idea, mechanism/knobs, controls, exact prediction prompt, reveal, grounded values) plus the conversation artifact directory and slug, writes one self-contained Predict-Before-Render `.html` artifact, and returns `UI_GENERATOR_RECEIPT` with its path + SHA-256. Never authors prose, audits, or embeds.
4. **`clerk`** (`model: flash` - Gemini 3.8 Flash, medium effort): Owns all repository writes: writes lesson and pause handoffs (`lesson_handoff`, `pause_handoff`) with the material refs, learner model (v1→v2 verbatim), triage, attacks, and attempts; updates `Knowledge Wiki/wiki/`, `Active Concepts.md`, `Attempts.json`, and `Mistakes.md`; preserves versioned learner understanding verbatim (`status=learner-note`); runs `audit_state.py`; and commits state files to git so the Tutor stays focused purely on interrogation.
5. **`auditor`** (`model: flash` - Gemini 3.8 Flash, medium effort): Independent read-only post-write auditor. Validates scout digests (`scout_audit`, incl. attack grounding), clerk handoff batches (`tutor_audit`, incl. model provenance, triage coverage, attacks, and graduation), wiki ingests (`review_gate`), and review session closes (`review_session_audit`).
6. **`naive-student`** (`model: flash` - Gemini 3.8 Flash, medium effort): Intuitive-novice clone persona for the executable Feynman test (Operational Intuition Battery Protocol C). Knows only lesson prerequisites, holds a seeded misconception, makes a **qualitative prediction or tool choice** using only what the learner explicitly taught, and reports failure honestly (`NAIVE_STUDENT_RECEIPT`).

Antigravity's custom-agent frontmatter selects only a model tier (`flash`/`pro`); thinking level is controlled by the session/model selector, not the agent file. `ui-generator` runs at high effort, so set the session thinking level to High (or `/effort high` in the CLI) before widget-heavy lessons.

Monitor subagent execution in real time via the **Subagents** panel on the right side of Antigravity Desktop.

---

## 4. Visual Composition, Math & Widgets

Visuals are automatic, never opt-in: every teaching turn is prose plus the smallest format that carries the idea. The Tutor never waits for a "show me" request and declares the choice in `visual_plan` on every substantive verifier dispatch.

- **Math**: Author formulas in standard LaTeX (`$...$` inline, `$$...$$` display). Antigravity Desktop renders them via KaTeX.
- **Diagrams**: Shapes, flows, state machines, causal chains, and lesson-end dependency trees render via native ` ```mermaid ` fences.
- **Interactive Widgets**: A parameter/regime the learner must vary, a checkable prediction, or a counterexample they must watch break gets a widget. The Tutor hands `ui-generator` the spec; the generator writes one self-contained HTML file (Tailwind + inline CSS/JS) into the current conversation's Antigravity artifact directory, and the Tutor embeds the audited file as `<agent-embed src="file:///..."></agent-embed>`. Every widget implements **Predict-Before-Render**: the output is locked until the learner commits a prediction, then revealed overlaid against it (Predicted vs Actual). Full contract: [`skills/teach/references/generative-ui.md`](./skills/teach/references/generative-ui.md).
- **Gate binding**: `verifier` audits the exact widget file and prose (`mode: "ui_audit"`) and returns `widget_file` + `widget_sha256`; the Stop hook blocks any `<agent-embed>` whose file has no matching passing audit. If a widget cannot pass, the Tutor degrades to Mermaid, never to an unaudited widget.
- **Solo**: No widgets and no method diagrams (`SOLO_NO_AIDS`).

---

## 5. Lifecycle Hooks Safety Net

Configured in `hooks.json`:
- **`PreToolUse` (`scripts/pre_tool_gate.py`)**: Protects state integrity by preventing the Tutor from directly writing to Clerk-owned state files or authoring widget HTML, scopes `ui-generator` to one `.html` artifact in the conversation artifact directory (and its `sha256sum`), enforces read-only tool limits on `verifier`, `auditor`, and `naive-student`, and blocks widget artifacts during `/solo`.
- **`Stop` (`scripts/stop_gate.py`)**: Intercepts turn completion to ensure required subagents (`scout`, `verifier`, `auditor`) ran and returned passing receipts before substantive turns reach the learner, and binds every `<agent-embed>` to a passing `ui_audit` receipt for the same file and SHA-256 (hard block — no fail-open tier, and no widgets in `/solo`). Retry discipline elsewhere is two-tiered: schema gates (auditor housekeeping) fail open after 2 blocks to avoid deadlocks, while critical gates (unverified teaching, grading disagreements, omitted foundations — anything in `/solo`) never silently fail open: they escalate up to 6 blocks and, if still unresolved, release the turn only with a mandatory visible `⚠️ UNVERIFIED` banner.
