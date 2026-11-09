# REVIEW: less (Pager) — 2026-08-27

## Review Info
- **Date:** 2026-08-27
- **Concept:** less (Pager)
- **Last Reviewed:** 2026-08-24
- **Review Interval:** 3d (interval_index 2, due)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative: `more` and editors like `vim` load a file before showing it; `less` is known for handling huge log/config files fast. What one property makes `less` efficient on a 50 GB file, and how does it differ from `more` there?

## Your Answer
- **Confidence:** confident
- **Answer:** `less` doesn't load the entire file into memory at once when you open it; unlike `more`, opening a 50 GB file isn't memory-intensive.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Correct — the load-bearing property is lazy reading: `less` streams the file a screen at a time and never maps the whole thing into memory, so a 50 GB log opens instantly and stays memory-flat. Bonus: `less` can scroll backwards (the "less is more" twist), which `more` historically couldn't.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing
- **last_reviewed:** 2026-08-27
- **next_review:** 2026-09-03 (interval 2 → 3, 7d)
- **Last Q Type:** discriminative

## Key Takeaway
> `less` reads lazily (a screen at a time, no full in-memory load) — fast and memory-flat on massive files, unlike `more`/editors.
