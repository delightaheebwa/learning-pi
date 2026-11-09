# Review: grep
**Date:** 2026-08-02
**Type:** discriminative
**Source:** MIT Missing Semester — Shell

## Question
When would you reach for grep vs ripgrep, and what's the one practical reason ripgrep usually wins?

## Answer
Grep for scripts on other people's machines (portability). Ripgrep on own machine for speed.

## Verdict: ✅ Correct
Both points land — portability vs speed tradeoff.

## Insight
grep ships everywhere (POSIX standard), ripgrep doesn't. ripgrep's speed comes from parallel search, .gitignore awareness, and default recursive mode.
