# Review — PATH & Program Discovery — 2026-08-29

- Track: SWE (Shell & Terminal)
- Type: concept
- Last Q Type: discriminative → asked definitional
- Grade: FAIL

## Question
You type `python` at the prompt and it runs. Where does the shell actually look to find that program, and why does it skip your current working directory?

## Expected
Shell walks `$PATH` — a colon-separated list of DIRECTORIES — in order, looking for a file named `python` inside each dir. cwd is deliberately absent from PATH (a security choice: a planted `ls` in cwd could not shadow the real one), so you must type `./python` to run something in cwd.

## Learner answer
Right mechanic (PATH walk, colon-separated) but wrong detail: said PATH entries are "paths ending in the command" (they are directories). Missed WHY cwd is excluded — the load-bearing 80% insight.

## Error analysis
- error_type: structural
- self_attribution: named the mechanic but inverted the detail (dirs vs path-suffix) and missed the security rationale for excluding cwd.
- Root: distinguished name-lookup vs path-execution weakly.

## Action
New mistake row (active, retry 2026-09-01). Next review 2026-09-01. Feynman explain-back due (advisory).