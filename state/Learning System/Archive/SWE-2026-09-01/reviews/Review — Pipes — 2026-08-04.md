# Review — Pipes — 2026-08-04

**Date**: 2026-08-04
**Concept**: Pipes (`|`) & Pipeline Composition
**Status**: developing
**Question Type**: definitional
**Source**: Basic File Tools (MIT Missing Semester)

## Question
What does the pipe command do, and in which direction does data flow?

## Answer
The pipe command handles data flow between commands by taking the stdout of one command and passing it to stdin of the next. It flows left to right.

**Feedback**: Correct. Key additions: each command in a pipeline runs in a subshell (variable assignments don't persist), and `set -o pipefail` makes the pipeline exit code reflect the last failed command.

## Next Review
- Interval: 3d (stays at developing since question was easy, next review sooner)
- Next: 2026-08-07
