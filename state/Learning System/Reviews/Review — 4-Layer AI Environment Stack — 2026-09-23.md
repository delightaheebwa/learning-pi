# Review — 4-Layer AI Environment Stack — 2026-09-23

- **Track/Source:** aiefs — Rohit P0 L01–L12 (Python)
- **Type:** concept · Q type: definitional (prior: discriminative)
- **Why this slot:** due mistake (2026-09-05 row, `active`, retry 1, next retry 2026-09-19 — oldest in the ledger)
- **Question:** In the 4-layer stack (System → Packages → Runtimes → AI libs): which layer does uv/venv belong to, and which layer does the CUDA runtime belong to? One line.
- **Expected:** uv/venv = Packages; CUDA runtime = Runtimes.
- **Learner answer:** "Packages."
- **Verdict:** ❌ fail (grade-audit agreed) — only the uv/venv half answered; the CUDA→Runtimes half (the load-bearing half, exactly what the 09-05 mistake targets) was omitted.
- **Attempts.json:** mastery 0.35, interval_index 0, consecutive_wrong 1, next_review 2026-09-26
- **Mistakes ledger:** 2026-09-05 row stays `active`, retries 1, next retry 2026-09-26 (update note appended)
- **Note:** the learner still cannot state both layer attributions in one line; next retry should demand the full two-layer mapping.
