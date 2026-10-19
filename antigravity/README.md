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
| **`/teach <topic>`** | Teach a topic: scout sources -> probe -> plan -> mini-checkpoint ladder | `scout`, `verifier`, `auditor` |
| **`/lesson`** | Resume or teach the next sequential curriculum lesson | `scout`, `verifier`, `auditor` |
| **`/continue`** | Resume an in-progress lesson at its exact mini-checkpoint | `verifier` |
| **`/pause`** | Bank progress cleanly, write partial handoff files, and exit ticket | `verifier`, `auditor` |
| **`/review`** | Daily spaced-repetition review on the active track | `scout`, `verifier`, `clerk`, `auditor` |
| **`/solo`** | AI-free closed-book assessment (no hints/teaching/widgets; feeds independence gate) | `scout`, `verifier`, `clerk`, `auditor` |
| **`/ingest [content]`** | Reconcile lesson handoffs or raw notes into Knowledge Wiki + Active Concepts | `clerk`, `auditor` |
| **`/audit`** | Read-only state consistency audit + wiki provenance check | None (runs local python scripts) |
| **`/llm-wiki`** | Karpathy-style knowledge wiki guidelines & provenance rules | None (guidelines) |

---

## 3. Subagents Architecture

When running in Antigravity Desktop, 4 custom subagents are defined in `.agents/agents/` and invoked via `invoke_subagent`:

1. **`scout`** (`model: flash` - Gemini 3.8 Flash, medium effort): Fetches live curriculum docs + Further Reading URLs, persists raw text under `Knowledge Wiki/raw/sources/` with SHA-256 headers, scans contradictions, and builds the deterministic `ops.py queue`.
2. **`verifier`** (`model: flash` - Gemini 3.8 Flash, medium effort): Independent read-only gatekeeper. Checks teaching claims against raw sources, verifies the 4 theoretical foundation beats (`problem`, `where_from`, `conditions`, `contrast`), flags omitted source theory (`omitted_foundations`), audits MCQ distractor subtlety, verifies grades against the Feynman rubric, and audits interactive HTML widgets.
3. **`clerk`** (`model: flash` - Gemini 3.8 Flash, medium effort): Owns all repository writes: writes lesson and pause handoffs (`lesson_handoff`, `pause_handoff`), updates `Knowledge Wiki/wiki/`, `Active Concepts.md`, `Attempts.json`, and `Mistakes.md`, preserves learner understanding notes verbatim (`status=learner-note`), runs `audit_state.py`, and commits state files to git so Tutor stays focused purely on teaching.
4. **`auditor`** (`model: flash` - Gemini 3.8 Flash, medium effort): Independent read-only post-write auditor. Validates scout digests (`scout_audit`), clerk handoff file batches (`tutor_audit`), wiki ingests (`review_gate`), and review session closes (`review_session_audit`).

You can monitor subagent execution in real time by clicking into the **Subagents** panel on the right side of Antigravity Desktop.

---

## 4. Visuals, Math & Widgets

- **Math**: Author formulas in standard LaTeX (`$...$` inline, `$$...$$` display). Antigravity Desktop renders them natively via KaTeX.
- **Diagrams**: Flowcharts, state machines, and learning dependency trees render via native ` ```mermaid ` fences.
- **Interactive Widgets**: Interactive parameter sliders and concept visualizers are built using Antigravity's native `generative_ui` skill (`<agent-embed src="file:///..."></agent-embed>`), styled with Tailwind CSS, and verified by `verifier` before rendering.

---

## 5. Lifecycle Hooks Safety Net

Configured in `hooks.json`:
- **`PreToolUse` (`scripts/pre_tool_gate.py`)**: Protects state integrity by preventing the Tutor from directly writing to Clerk-owned state files, enforces read-only tool limits on `verifier` and `auditor`, and blocks widget artifacts during `/solo`.
- **`Stop` (`scripts/stop_gate.py`)**: Intercepts turn completion to ensure that required subagents (`scout`, `verifier`, `auditor`) ran and returned passing receipts before substantive turns are presented to the learner, with an automatic 2-retry safety cap.
