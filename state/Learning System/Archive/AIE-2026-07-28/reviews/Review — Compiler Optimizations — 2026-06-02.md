# Review — Compiler Optimizations — 2026-06-02

## Concept
Compiler optimizations

## Question Asked
"Name three specific optimizations a compiler can apply that an interpreter cannot."

## User's Answer
1. Cutting out unreachable code (dead code elimination) ✓
2. Swapping out code with its semantics (math simplification) ✓
3. Ignoring variables whose value doesn't change ✗

## Evaluation
**Result: Reset to 3d (next: 2026-06-05)**

Got 2 of 3. The third is **register allocation** (keeping frequently-used data in CPU's fastest memory), not constant folding. Also missed the *why*: compilers can do these because they see the entire program before execution — interpreters see only one line at a time.

## Correct Answer
1. Dead code elimination — remove unreachable code
2. Math simplification — replace slow expressions with faster equivalents (e.g., x * 2 * 3 → x * 6)
3. Register allocation — map variables to CPU registers across the full program
4. Why: the compiler has the full program graph before execution; the interpreter is blind beyond the current line
