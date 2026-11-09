# Session: SWE Shell Tools Review
**Date:** 2026-08-02
**Track:** swe
**Topic:** MIT Missing Semester — Shell tools review

## Concepts Reviewed (5)

1. **grep** (discriminative) — Portability vs speed tradeoff with ripgrep. ✅ Correct.
2. **Shell Navigation & Paths** (discriminative) — cd vs pushd/popd. Got home dir right, mischaracterized pushd as pushing files (it pushes directories onto a stack). ❌ Partially correct.
3. **Pipes** (discriminative) — `|` passes data, `&&` chains on exit status. Missed `&&` entirely. Key insight about sort buffering missed. ❌ Partially correct.
4. **awk** (discriminative) — Recognized column selection but missed the key power: awk does filtering + transformation + conditional logic in one pass, which grep/cut can't. ❌ Partially correct.
5. **sed** (discriminative) — Knew `-i` means inline edit but misunderstood it as terminal output bloat rather than in-place file mutation bypassing stdout. ❌ Incorrect.

## Summary

3/5 partially correct or incorrect. The pattern: understanding directionally but missing the precise mechanism. pushd → directory stack, `&&` → exit status chaining, sort buffering, awk's transformation power, sed `-i` bypasses stdout.

Next review: 2026-08-09 for all 5.

Interleaving: 5 concepts shuffled, 0 same-source adjacency issues, 5 discriminative questions.
