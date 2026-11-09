# REVIEW: Bash Quoting — 2026-08-20

## Review Info
- **Date:** 2026-08-20
- **Concept:** Bash Quoting
- **Last Reviewed:** 2026-08-03
- **Review Interval:** Overdue (17 days)
- **Status Before Review:** developing

## Assistant's Prompt
> Definitional (alternation from last discriminative): "Pick ONE quoting flavor and describe precisely when you MUST use it — where the other two would break your intent. Give a concrete example."

## Your Answer
- **Confidence:** confident
- **Answer:** Chose ANSI-C `$'...'` quotes for variables; said `if [ -f "$'FILE'" ]`, and that single/double quotes would look up a file literally named `$FILE`.

## Assistant's Evaluation
- **Result:** Needs More Work
- **Feedback:** Semantics flipped. ANSI-C `$'...'` is for escape sequences (`\n`, `\t`) — `$`/`!` stay literal, NOT for expanding variables. Double quotes `"..."` are the ones that expand `$VAR`/`$(cmd)` while protecting spaces/wildcards. Single `'...'` is total literal (no `$`, `!`, escapes). So `"$FILE"` expands to the file the variable points to — it does NOT look up a literal `$FILE`. 20% insight: single `'` = NO expansion; double `"` = expansion yes, word-splitting/glob no — that's the tool for a variable inside a path.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-20
- **next_review:** 2026-08-27 (held at 7d)
- **Last Q Type:** definitional
- **notes:** Held — flipped quoting semantics (ANSI-C vs double-quote expansion).

## Queue / Deferred Note
- **Queue position:** active

## Key Takeaway
> Double quotes expand variables safely; single quotes are total lockdown; ANSI-C is only for escape sequences.
