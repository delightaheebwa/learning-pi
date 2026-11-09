# Review — 4-Layer AI Environment Stack — 2026-09-26

- **Track/Source:** aiefs — Rohit P0 L01–L12 (Python)
- **Type:** concept · **Q type:** discriminative (MCQ)
- **Why this slot:** priority-1 due mistake — the structural row has chased the Runtimes half since 2026-09-05; the 09-23 retry was a partial fail that omitted exactly that half.
- **Question:** GPU invisible though the NVIDIA driver is healthy and the pytorch build is CUDA-enabled; the system's CUDA/cuDNN runtime libraries were never installed — which layer of System / Packages / Runtimes / AI Libs is missing?
- **Learner answer:** "C"
- **Verdict:** PASS — grade-audit agreed. C isolates the Runtimes layer (CUDA/cuDNN runtime libraries sit between Packages and AI Libs; a healthy driver + CUDA-enabled torch + still-no-CUDA failure lives there) — the load-bearing half is now banked under retrieval.
- **Attempts.json:** mastery 0.65, interval_index 1, next_review 2026-10-03, Feynman: —
- **Mistakes ledger:** the 2026-09-05 row moves active → review (retries 2, next retry 2026-10-03). Graduation still needs a second consecutive correct — the 09-16 pass and today's pass are not consecutive (the 09-23 partial fail broke the streak).
- **Calibration:** keep the diagnostic reading "driver healthy + torch CUDA-enabled + still no CUDA → suspect the Runtimes layer" alongside the layer order System→Packages→Runtimes→AI Libs. This ends the 3-week Runtimes chase — one more correct recall graduates the row.
