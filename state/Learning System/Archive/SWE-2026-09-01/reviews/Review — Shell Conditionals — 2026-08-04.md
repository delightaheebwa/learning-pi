# Review — Shell Conditionals — 2026-08-04

**Q Type:** discriminative
**Concept:** Shell Conditionals
**Source:** MIT Missing Semester — Shell

**Question:** You're writing a script that checks if a file exists and is readable before processing it. What's the difference between using `[ -f file && -r file ]` and `[[ -f file && -r file ]]`? When does it matter?

**Answer:** User said: "The first doesn't allows variables to be in quotes while the second does."

**Assessment:** ❌ Incorrect. Key differences missed:
1. `[ -f file && -r file ]` **fails** — `[ ]` doesn't support `&&` inside. You need `[ -f file ] && [ -r file ]` or `[ -f file -a -r file ]`.
2. `[[ ]]` supports `&&`/`||` natively as logical operators.
3. `[[ ]]` is a bash builtin that handles unquoted variables safely (no word splitting/globbing). `[ ]` is an external command requiring quoted variables.
4. The user's quoting point is partially valid but stated backwards — `[[ ]]` is the one that handles variables safely.

**Score:** Incorrect — reset interval
