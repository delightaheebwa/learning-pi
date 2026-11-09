# Review — 4-Layer AI Environment Stack — 2026-09-12

- **Q(a) (discriminative MCQ):** torch imports + `torch.version.cuda` prints + driver current per `nvidia-smi`, yet `torch.cuda.is_available()` False → which layer? **Answer: C (Runtimes). PASS** (grade-audit agreed).
- **Q(b) (free recall):** name the 4 layers in order → answered "system, runtime, packages, ai libraries" — **FAIL**: positions 2–3 swapped (correct: System → Packages → Runtimes → AI Libs). Recurrence of the 09-08 ordering failure. Cue given: *packages install the runtimes*.
- **State:** Attempts pass then fail → mastery 0.28, interval_index 0, next_review 2026-09-15. Mistake row (2026-09-05) stays `active`, retries 0. Active Concepts row updated (last 2026-09-12, next 2026-09-15, Last Q Type discriminative).
