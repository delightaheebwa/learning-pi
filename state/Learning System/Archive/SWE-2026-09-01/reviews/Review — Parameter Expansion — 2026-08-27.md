# REVIEW: Parameter Expansion — 2026-08-27

## Review Info
- **Date:** 2026-08-27
- **Concept:** Parameter Expansion
- **Last Reviewed:** 2026-08-18
- **Review Interval:** 3d (interval_index 0, due)
- **Status Before Review:** developing

## Assistant's Prompt
> Definitional: You know `${FILE%.txt}` strips the `.txt` extension. Write one expression that does the *opposite job* on `/home/delight/notes/report.md` — and name what each half extracts.

## Your Answer
- **Confidence:** partial
- **Answer:** Guessed `${FILE##!.txt}` — thought it "adds a .txt extension."

## Assistant's Evaluation
- **Result:** Fail
- **Feedback:** All parameter expansion is *removal* — `#`/`##` strip a prefix, `%`/`%%` strip a suffix; there is no "add extension" operator (concatenate instead, e.g. `$FILE.bak`). `##` is greedy prefix-removal and `!` is not negation here, so `${FILE##!.txt}` just returns the string unchanged. The opposite job to `${FILE%.txt}` is `${FILE##*/}` → `report.md` (basename): `##` = remove longest matching prefix, `*/` = pattern "everything up through the last `/`.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing
- **last_reviewed:** 2026-08-27
- **next_review:** 2026-08-30 (interval 0 → 0, 3d)
- **Last Q Type:** definitional

## Key Takeaway
> Parameter expansion only *removes*: `${FILE##*/}` peels the directory (basename); `${FILE%.txt}` peels the suffix (extension). No operator "adds" anything.
