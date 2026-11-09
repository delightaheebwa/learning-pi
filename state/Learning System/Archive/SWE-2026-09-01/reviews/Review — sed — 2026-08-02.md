# Review: sed (Stream Editor)
**Date:** 2026-08-02
**Type:** discriminative
**Source:** MIT Missing Semester — Shell

## Question
What's the difference between `sed 's/foo/bar/' file` and `sed -i 's/foo/bar/' file`? Why would you never want -i in a pipeline?

## Answer
-i means inline. Swapping text inline in terminal. Wouldn't be ideal because big documents would bloat the terminal.

## Verdict: ❌ Wrong
-i means **in-place edit** — modifies the original file on disk. Without -i, sed prints to stdout. In pipelines, -i is dangerous because it bypasses stdout entirely (nothing flows downstream), and can mutate source files before downstream commands see them.

## Key Insight
-i writes directly to the file, not stdout. Pipelines rely on stdout. Breaking the stdout chain breaks composition.
