# Review: awk
**Date:** 2026-08-02
**Type:** discriminative
**Source:** MIT Missing Semester — Shell

## Question
What does awk do that grep and cut can't? When would you pick awk over the other two?

## Answer
Awk can select certain parts in a data table while the other two can only select patterns in text.

## Verdict: ⚠️ Directionally Right
Missed the real power: awk filters AND transforms in one pass. It's a mini programming language — filter lines, extract fields, run conditional logic and arithmetic on them. grep filters lines, cut extracts columns, awk does both plus computes.

## Key Example
`awk -F',' '$3 > 100 {print $1, $3 * 0.9}'` — filter, extract, and transform in one command.
