# Antigravity Desktop Learning Layer

This directory (`antigravity/`) contains the Antigravity Desktop-native control layer for the spaced-repetition learning system. It is symlinked by `install.sh` into your learning state repository (`~/learning-system/.agents/`) and excluded from git there.

---

## 1. Quick Setup

```bash
# In ~/learning-pi:
./install.sh ~/learning-system
```

This creates:
- `~/learning-system/.pi` -> `~/learning-pi/.pi` (for the CLI / pi runtime)
- `~/learning-system/.agents` -> `~/learning-pi/antigravity` (for Antigravity Desktop)
- Adds `.agents/` and `.pi/` to `~/learning-system/.git/info/exclude`.

Then launch Antigravity Desktop and open `~/learning-system` as a workspace.

---

## 2. Slash Commands (`/`)

All workflows are available as native slash commands in the Antigravity Desktop chat box:

| Command | Action | Backing Agents |
| :--- | :--- | :--- |
| **`/teach <topic>`** | Teach a topic: scout sources -> probe -> scope contract -> Collision/Sketch-the-Move/Anatomical-Read/Boundary-Hunt/Counterexample ladder -> auto-ingest at lesson end | `scout`, `verifier`, `clerk`, `auditor`, `naive-student` |
| **`/lesson`** | Resume or teach the next sequential curriculum lesson (auto-ingests at lesson end) | `scout`, `verifier`, `clerk`, `auditor`, `naive-student` |
| **`/continue`** | Resume an in-progress lesson at its exact mini-checkpoint (scout always recovers the resume pointer) | `scout`, `verifier`, `clerk`, `auditor`, `naive-student` |
| **`/pause`** | Bank progress cleanly, write partial handoff files, and exit ticket | `verifier`, `auditor` |
| **`/review`** | Daily spaced-repetition review: unlabeled interleaved + synthesis + decoy items, trace-graded (no MCQs), then a learner Q&A pause before auto-persisting and auto-ingesting | `scout`, `verifier`, `clerk`, `auditor`, `naive-student` |
| **`/solo`** | AI-free closed-book assessment (no hints/teaching/widgets/MCQs; operational items only; feeds independence gate) | `scout`, `verifier`, `clerk`, `auditor`, `naive-student` |
| **`/ingest [content]`** | Reconcile lesson handoffs or raw notes into Knowledge Wiki + Active Concepts | `clerk`, `auditor` |
| **`/audit`** | Read-only state consistency audit + wiki provenance check | None (runs local python scripts) |
| **`/llm-wiki`** | Karpathy-style knowledge wiki guidelines & provenance rules | None (guidelines) |

---

## 3. Subagents Architecture

When running in Antigravity Desktop, 5 custom subagents are defined in `.agents/agents/` and invoked via `invoke_subagent`:

1. **`scout`** (`model: flash` - Gemini 3.8 Flash, medium effort): Fetches live curriculum docs + Further Reading URLs, persists raw text under `Knowledge Wiki/raw/sources/` with SHA-256 headers, scans contradictions, harvests anomaly and misapplication candidates (Broken Worlds and Boundary Hunts), captures anatomical formula notes, and builds the deterministic `ops.py queue`.
2. **`verifier`** (`model: flash` - Gemini 3.8 Flash, medium effort): Independent read-only gatekeeper policing **two dimensions** — epistemic truth (claims vs raw sources, conceptual `omitted_foundations`, contradiction surfacing) and mental-model integrity (`SPOONFEEDING_DETECTED`, `CUE_LEAKAGE`, `PREMATURE_SYNTHESIS_LEAK`, `SHALLOW_PASS`), plus MCQ legality (probes only), concept-label scoping, qualitative-trace requirements, Operational Intuition Battery grading, visual sufficiency (`VISUAL_PLAN_MISSING`, `VISUAL_MISSED`), and Predict-Before-Render widget audits. It explicitly does **not** flag a missing derivation as an omission.
3. **`clerk`** (`model: flash` - Gemini 3.8 Flash, medium effort): Owns all repository writes: writes lesson and pause handoffs (`lesson_handoff`, `pause_handoff`), updates `Knowledge Wiki/wiki/`, `Active Concepts.md`, `Attempts.json`, and `Mistakes.md`, preserves versioned learner understanding verbatim (`status=learner-note`), records Operational Intuition Battery outcomes, runs `audit_state.py`, and commits state files to git so Tutor stays focused purely on teaching.
4. **`auditor`** (`model: flash` - Gemini 3.8 Flash, medium effort): Independent read-only post-write auditor. Validates scout digests (`scout_audit`, incl. anomaly harvest), clerk handoff file batches (`tutor_audit`, incl. intuition-battery artifacts), wiki ingests (`review_gate`), and review session closes (`review_session_audit`).
5. **`naive-student`** (`model: flash` - Gemini 3.8 Flash, medium effort): Intuitive-novice clone persona for the executable Feynman test (Operational Intuition Battery Protocol C). Knows only lesson prerequisites, holds a seeded misconception, makes a **qualitative prediction or tool choice** using only what the learner explicitly taught, and reports failure honestly (`NAIVE_STUDENT_RECEIPT`).

You can monitor subagent execution in real time by clicking into the **Subagents** panel on the right side of Antigravity Desktop.

---

## 4. Visual Composition, Math & Widgets

Visuals are **automatic, never opt-in**: every teaching turn is prose plus the smallest format that carries the idea. The Tutor never waits for a "show me" request, and it declares the choice in `visual_plan` on every substantive verifier dispatch.

- **Math**: Author formulas in standard LaTeX (`$...$` inline, `$$...$$` display). Antigravity Desktop renders them natively via KaTeX.
- **Diagrams**: Shapes, flows, state machines, causal chains, and lesson-end dependency trees render via native ` ```mermaid ` fences.
- **Interactive Widgets**: A parameter/regime the learner must vary, a checkable prediction, or a counterexample they must watch break gets a widget. The Tutor writes one self-contained HTML file (Tailwind + inline CSS/JS) into the current conversation's Antigravity artifact directory and embeds it as `<agent-embed src="file:///..."></agent-embed>`. Every widget implements **Predict-Before-Render**: the output is locked until the learner commits a prediction, then revealed overlaid against it (Predicted vs Actual). Full contract: [`skills/teach/references/generative-ui.md`](./skills/teach/references/generative-ui.md).
- **Gate binding**: `verifier` audits the exact widget file and prose (`mode: "ui_audit"`) and returns `widget_file` + `widget_sha256`; the Stop hook blocks any `<agent-embed>` whose file has no matching passing audit. If a widget cannot pass, the Tutor degrades to Mermaid, never to an unaudited widget.
- **Solo**: no widgets and no method diagrams (`SOLO_NO_AIDS`).

---

## 5. Lifecycle Hooks Safety Net

Configured in `hooks.json`:
- **`PreToolUse` (`scripts/pre_tool_gate.py`)**: Protects state integrity by preventing the Tutor from directly writing to Clerk-owned state files, enforces read-only tool limits on `verifier`, `auditor`, and `naive-student`, and blocks widget artifacts during `/solo`.
- **`Stop` (`scripts/stop_gate.py`)**: Intercepts turn completion to ensure that required subagents (`scout`, `verifier`, `auditor`) ran and returned passing receipts before substantive turns are presented to the learner, and binds every `<agent-embed>` to a passing `ui_audit` receipt for the same file and SHA-256 (hard block — no fail-open tier, and no widgets in `/solo`). Retry discipline elsewhere is two-tiered: schema gates (auditor housekeeping) fail open after 2 blocks to avoid deadlocks, while **critical gates** (unverified teaching, grading disagreements, omitted foundations — anything in `/solo`) are never silently failed open: they escalate up to 6 blocks and, if still unresolved, release the turn only with a mandatory visible `⚠️ UNVERIFIED` banner.
