# Session — Command-line Environment (B2) — 2026-08-18

**Trigger:** `lesson` (teaching flow, `learning-teach` skill). User chose B2 ahead of A5.

## Probe (7 MCQs)

Edge located precisely. 5/7 correct; both misses on the **signals** strand:
- Q1 (Ctrl-C mechanics) → A ❌ (correct: C — SIGINT, catchable)
- Q2 (SIGTERM vs SIGKILL) → B ❌ (correct: D — SIGKILL uncatchable)
- Q3 env vars → A ✅ · Q4 return codes → C ✅ · Q5 tmux → B ✅ · Q6 dotfiles → A ✅ · Q7 aliases → D ✅

Prior knowledge confirmed: env vars/`export`, `&&`/`||`/`$?`, tmux purpose, aliases, dotfiles.

## Plan (Mermaid dependency graph)

Signal (software interrupt) → { SIGINT, SIGTERM/SIGKILL, SIGTSTP→fg/bg/jobs, &/nohup/disown/SIGHUP } → job control → B2 goal. Verified env/return/tmux/alias/dotfiles as already-held.

## Fact-check (deepseek-v4-flash)

3 load-bearing claims → all **PASS**: (1) Ctrl-C → shell sends SIGINT, catchable/ignorable; (2) SIGTERM catchable vs SIGKILL uncatchable + orphan risk; (3) Ctrl-Z → SIGTSTP, resume via fg/bg.

## Teach

Three reasoning steps: signal-as-interrupt → kill ladder → suspend/resume + SIGHUP. Guided Socratic throughout (soccer ref → driving/officer analogy). Verification pass on env vars and dotfiles.

## End-of-lesson gate

- **Two-tier quiz: 5/5.** Tier 1 retrieval + Tier 2 higher-order (predict / explain-why). One interleaved item (Strand A — Make timestamp rebuild).
- **Feynman explain-back: PASS** — original driving/officer analogy covering all three signal rungs (road sign = catchable, officer at distance = graceful, instant engine-stop = SIGKILL). Bloom: Evaluate.

## Writes

- Learning record: `Learning Records/0001-signals-and-job-control.md`
- Lesson: `Lessons/Lesson — Command-line Environment — 2026-08-18.md`
- Active Concepts: +2 (Signals (Software Interrupts), Job Control (Ctrl-Z, fg/bg, nohup/disown)) — `developing`, `last_reviewed` 2026-08-18, `next_review` 2026-08-21
- CURRICULUM.md: B2 → `done`
- Wiki: `Knowledge Wiki/wiki/MIT Missing Semester — Command-line Environment.md` (created) + index + log

## Next

A5 — CPU from two samples (/proc/stat) per rotation, or B3 — Development Environment & Tools on request.
