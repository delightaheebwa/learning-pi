# Review: Pipes (`|`) & Pipeline Composition
**Date:** 2026-08-02
**Type:** discriminative
**Source:** MIT Missing Semester — Shell

## Question
What's the key difference between | and &&? If I run `cat file.txt | sort | uniq -c`, at what point does sort start producing output?

## Answer
| sends stdout to stdin. Sort produces output at the pipe after sort.

## Verdict: ⚠️ Partial
Got the pipe direction right. Missed two things: (1) && chains on exit status, not data. (2) sort buffers ALL input before producing any output — it must see every line to sort them.

## Key Insight
| passes data. && chains on success/failure. Sort is a full-buffer sort, not streaming.
