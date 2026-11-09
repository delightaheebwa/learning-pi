# Review — Short-Circuit Evaluation — 2026-06-10

**Result:** ⚠️ Mostly right, nuance missed. Interval kept at 3d

**Question:** What does `A and B` actually return, and what's the danger when chaining operators?

**User's answer:** Returns the right operand if the left is true. Danger: if left is False, the right is skipped since the expression immediately evaluates to False — side effects silently dropped.

**Evaluation:** Captured the danger correctly (silently skipped side effects) but the return rule was imprecise. Correct rule: `A and B` returns A if A is falsy, else B — these operators return actual operand values, not booleans. `0 and "hello"` returns `0`, not `False`. The skipped operand doesn't make anything "evaluate to False" — it just never runs. Keeping at 3d to tighten the precision.

**Next review:** 2026-06-13
