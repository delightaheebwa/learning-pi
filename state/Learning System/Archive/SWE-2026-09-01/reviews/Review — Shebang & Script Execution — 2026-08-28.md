# REVIEW: Shebang & Script Execution — 2026-08-28

## Review Info
- **Date:** 2026-08-28
- **Concept:** Shebang & Script Execution
- **Last Reviewed:** 2026-08-25
- **Review Interval:** 3d (due)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): `./run.sh` vs `bash run.sh` — which needs chmod +x, which needs only read, and what does `#!` do differently in each?

## Your Answer
- **Confidence:** partial
- **Answer:** `./run.sh` needs chmod +x; `bash run.sh` needs only read. But claimed both routes use the shebang the same way.

## Assistant's Evaluation
- **Result:** Fail
- **Feedback:** Permission half correct. Misconception: `#!` is NOT load-bearing in `bash run.sh` — bash already IS the interpreter, so it just reads the file (r only) and treats `#!` as a comment. Only `./run.sh` (kernel executes the file directly) consults `#!` as the absolute interpreter path. Two routes: kernel-executes-file (needs x; shebang = path) vs interpreter-reads-file (needs r; shebang inert).
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-28
- **next_review:** 2026-08-31 (held 3d)
- **Last Q Type:** discriminative
- **notes:** Fail — route split (kernel-executes vs interpreter-reads) still missing; mistake row stays active.

## Queue / Deferred Note
- **Queue position:** active (mistake, retry 2026-08-31)

## Key Takeaway
> `./script` = kernel executes file (needs x; #! = interpreter path). `bash script` = bash reads file (needs r; #! is just a comment).
