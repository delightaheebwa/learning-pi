# Review — Make: Timestamp Evaluation — 2026-08-04

**Date**: 2026-08-04
**Concept**: Make: Timestamp Evaluation
**Status**: developing
**Question Type**: discriminative
**Source**: Makefile: Targets, Prerequisites & Recipes (MIT Missing Semester)

## Question
When does `make` decide to skip rebuilding a target vs rebuild it? What specific comparison determines the outcome?

## Answer
Make compares target timestamp vs prerequisite timestamps. If target is more recent than all prereqs → skip. Otherwise → rebuild.

**Feedback**: Correct. Clean articulation of the core comparison.

## Next Review
- Interval: 7d (developing → 7d)
- Next: 2026-08-11
