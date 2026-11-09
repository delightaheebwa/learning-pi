# REVIEW: GCC Compilation Stages — 2026-08-06

> **Purpose:** When a concept comes up for spaced repetition review, use this note to capture the review session. Zo will test you on the concept and the results update the Knowledge Base.

## Review Info

- **Date:** [[2026-08-06]]
- **Concept:** GCC Compilation Stages
- **Last Reviewed:** 2026-08-03
- **Review Interval:** 3d
- **Status Before Review:** developing

---

## Zo's Prompt

> *"Zo asked: What's the difference between `gcc -c main.c` and `gcc -S main.c`, and what would each give you?"* (discriminative)

---

## Your Answer

- **Confidence before evaluation:** n/a (user answered directly)
- **Answer:** "gcc -c main.c is for compilation and gcc -S main.c is for linking"

---

## Zo's Evaluation

- **Result:** Needs More Work
- **Feedback:** `-c` produces `main.o` (runs stages 1–3, preprocess → compile → assemble). `-S` produces `main.s` assembly source (stops after stage 2, compilation proper). Both stop BEFORE linking — linking is stage 4, only run by `gcc main.o -o program` or plain `gcc main.c`. Got the `-c` half, missed `-S` entirely (thought it was linking).
- **Status After Review:** developing (kept at 3d interval)

---

## Updated Concept Record

- **status:** developing
- **last_reviewed:** 2026-08-06
- **next_review:** 2026-08-09
- **review_interval:** 3d (unchanged — got it wrong)
- **notes:** Flagged gap: stage-to-flag mapping (`-E` = preprocess only, `-S` = assembly source, `-c` = object file, no flag = link).

---

## Queue / Deferred Note

- **Queue position:** active
- **If deferred:** —

---

## Key Takeaway

> Both `-S` and `-c` stop short of linking; `-c` goes one stage deeper. The flags are stage-stop signs, not modes.
