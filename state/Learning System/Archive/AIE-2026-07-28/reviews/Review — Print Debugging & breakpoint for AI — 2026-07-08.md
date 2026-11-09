# Review — Print Debugging & breakpoint for AI — 2026-07-08

**Date:** 2026-07-08
**Track:** aie
**Interval status:** Kept

## Question
What fields should a tensor debug_print function output? List them.

## Response
device name, data type, min/max, NaN output. Missing: shape and mean/std.

## Evaluation
Mostly right but missed shape (most important for debugging shape mismatches) and mean/std.

## Next Review: 2026-07-11
