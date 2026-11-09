# Review — PATH & Program Recovery — 2026-08-04

**Concept**: PATH & Program Recovery
**Source**: MIT Missing Semester — Shell
**Question type**: definitional
**Confidence**: good

## Question
When you type `grep` in a terminal, walk me through how the shell finds and runs it. What happens if the command isn't in any of those directories?

## Answer
Shell looks for the command in PATH directories and executes whatever is at that directory. If it isn't in any of those directories, an error occurs and nothing is executed.

## Feedback
Correct core mechanism. Added detail: shell also checks aliases and builtins (cd, echo) before walking PATH. `which` or `command -v` can locate a command's path.

## Interval
3d → 7d → next review: 2026-08-11
