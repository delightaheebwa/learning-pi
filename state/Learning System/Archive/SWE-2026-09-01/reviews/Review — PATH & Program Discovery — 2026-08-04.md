# Review — PATH & Program Discovery — 2026-08-04

**Date**: 2026-08-04
**Concept**: PATH & Program Discovery
**Status**: developing
**Question Type**: definitional
**Source**: What is the Shell (MIT Missing Semester)

## Question
When you type `grep` in a terminal, walk me through how the shell finds and runs it. What happens if the command isn't in any of those directories?

## Answer
Shell searches PATH directories for the command. If not found, an error occurs and nothing is executed. Correct.

**Feedback**: Solid. Added detail about aliases/builtins checked before PATH, and `which`/`command -v` to locate commands.

## Next Review
- Interval: 7d (developing → 7d)
- Next: 2026-08-11
