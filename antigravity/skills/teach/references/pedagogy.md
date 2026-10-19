# Learning System Pedagogy & Protocols Reference

This document defines the core pedagogical procedures, scaffolding ladders, and assessment rubrics for the Antigravity learning system.

---

## 1. Mini-Checkpoint Pause Protocol

Checkpoints are never dumped as monolithic lectures. Each checkpoint is partitioned into **mini-checkpoints**:

1. **One Atomic Idea Per Message**: A mini-checkpoint introduces exactly one definition, formula, mechanism, or micro-step.
2. **Mandatory Post-Idea Pause**: After explaining the mini-checkpoint's idea, **pause and invite the learner's questions, doubts, or tangents**. Do not proceed to practice or the next mini-checkpoint until the learner is satisfied.
3. **Practice at Checkpoint End**: Only after all mini-checkpoints for the checkpoint are complete do you deliver the checkpoint's single practice problem.
4. **Post-Grading Pause**: After grading the practice problem, **pause again** to invite questions before advancing to the next checkpoint.

---

## 2. Elicit → Attempt → State → Check-and-Extend Ladder

Every mini-checkpoint idea follows this 4-rung constructivist ladder:

### Rung 1: Elicit (Prediction)
- Pose 1 prediction question ("What do you think happens when...?", "How might we measure...?") grounded in the learner's prior knowledge from `Learning System/Core/Learner History.md`.
- Formatted as a free-recall question.
- **Ungraded**: No pass/fail score, no `ops.py attempt` log, no confidence tag required. Audited via `verifier` (`mode: "quiz_audit"`).

### Rung 2: Attempt (Guided Socratic Nudge)
- If the learner is off-track, provide guiding questions rather than immediately giving the answer.
- **Hint Budget**: Fades with measured independence (`ops.py mastery <track>`):
  - No independence evidence: Up to **2** guiding questions.
  - Neutral / untested-solid: **1** guiding question.
  - Passed solo (`independence ≥ 2`): **0** guiding questions (ask learner to re-check directly).
- Record the number of hints provided (`--hints N`).

### Rung 3: State (Learner Formulation)
- Prompt the learner to express the concept in their own words (1–2 sentences).
- **Capture these exact words verbatim**. In the handoff to `clerk`, store this phrasing so it can be committed to the wiki page's `## My understanding` section (`status=learner-note`).

### Rung 4: Check-and-Extend (The Foundation Beat)
- Check the learner's statement against the source material.
- Confirm what they got right, and **add only what the learner did not produce**, labeling additions clearly (`Source framing:`, `External angle:`, or `⚠️ Sources disagree`).
- This is the **idea turn**: declare `turn_kind: "idea"` and deliver all four theoretical foundation beats.

### "Just Tell Me" Override
If the learner explicitly says "just tell me", "skip", or "give me the answer":
- Always honor it immediately without lecture or resistance.
- State the idea clearly with its complete 4-beat foundation.
- Conclude with a minimal one-line check or generation.
- Record the event in handoff `dependency_events[]` as `just_tell_me`.

---

## 3. Four-Beat Theoretical Foundation

Every turn that introduces a new idea, definition, formula, or mechanism must deliver the "why", not just the "what". The 4 beats are:

1. **Problem**: What question does this concept answer? What breakdown or limitation does it resolve?
2. **Where_From**: The derivation, causal mechanism, or physical intuition (at least one causal step; not a circular restatement).
3. **Conditions**: The boundary conditions, domain of validity, and key assumptions under which it holds.
4. **Contrast**: Nearest-neighbour distinction—what is this concept *not*? How does it differ from adjacent or easily confused concepts?

---

## 4. Assessment Integrity & Feynman Rubric

### Multiple-Choice Integrity
- **4 Options**: Every MCQ must have 4 options with parallel grammatical structure and comparable lengths.
- **Plausible Distractors**: Distractors must represent genuine conceptual slips (e.g. wrong in another regime, correct formula with transposed indices), never nonsense options or "all of the above".
- **Randomized Positions**: Randomize correct option letters (A, B, C, D).
- **Zero Leakage**: Never hint at the correct position in instructions or intro text.

### Feynman Explain-Back Rubric
Mandatory for all `concept` and `design` items at lesson end and during reviews:
1. Explain what it is in your own words (no textbook quotes).
2. When and why it is used (problem space).
3. Distinguish from its nearest neighbour.
4. One concrete example or worked micro-calculation.
Graded pass/fail via `verifier` (`mode: "grade_audit"`), logged as `feynman_pass` or `feynman_fail`. A concept cannot reach `solid` mastery without a Feynman pass.

---

## 5. Visuals & Interactive Widgets

- **KaTeX**: All mathematical formulas must be authored in valid LaTeX (`$...$` inline, `$$...$$` block).
- **Mermaid**: Use native ` ```mermaid ` fences for state diagrams, flowcharts, and dependency graphs.
- **Generative UI (`<agent-embed>`)**:
  - Interactive widgets (e.g., parameter sliders, loss surface plots, interactive matrix visualizers) are written to the artifact directory as standalone HTML files using Tailwind CSS (`https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js`).
  - Embed inline via `<agent-embed src="file:///path/to/artifact.html"></agent-embed>`.
  - Always audit the HTML code and accompanying prose with `verifier` (`mode: "ui_audit"`) before embedding.
  - Interactive widgets are strictly forbidden during `/solo` flows.
