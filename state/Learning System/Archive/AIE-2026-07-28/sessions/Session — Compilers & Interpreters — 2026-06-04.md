# Session — Compilers & Interpreters — 2026-06-04

## Date

2026-06-04

## Reviews completed

1. **Python dynamic execution model** — Partial (variables as PyObject labels, not fixed boxes). Interval kept.
2. **Python distribution model** — Partial (interpreter bundled in executable, not compiler+VM). Interval kept.
3. **Dynamic language optimization limits** — Incomplete (missed Cython tradeoff). Reset to 3d.
4. **Memory management models** — Partial (concepts right, imprecise terminology). Interval kept.
5. **Compiler** — Wrong (confused compiler output with interpreter execution). Reset to 3d.

## Ingested concepts

### Memory management models (updated)

Expanded existing concept with deeper dive:
- **Reference counting**: each object tracks how many references point to it; counter hits zero → immediate deletion. Flaw: circular references (A↔B with no active root → never reach zero → leak). Used by Python (backed by cyclic GC) and Swift.
- **Tracing GC (mark-and-sweep)**: starts from "roots" (active functions, global variables), walks the reference graph marking reachable objects, then sweeps away unmarked ones. Flaw: "stop-the-world" pauses during collection. Used by Java, JavaScript, Go.
- **Circular references**: solvable by tracing GC (unreachable from roots → not marked → deleted), unsolvable by pure reference counting.

### Short-circuit evaluation (new)

- `and`/`or` are implicit control flow: `A and B` = if A then B else A; `A or B` = if A then A else B.
- Return actual operand values (not just booleans): `"Apple" or "Banana"` → `"Apple"`; `None or "Banana"` → `"Banana"`.
- Use cases: guard clauses (`obj and obj.method()` prevents null errors), default values (`name or "Anonymous"`).
- Pitfall: right-hand side effects may be skipped if short-circuited.
- When to avoid: complex chained logic — use explicit if-else for readability.
- Status: developing, first review 2026-06-07.

## File updates

- Updated `📚 Active Concepts.md` — 5 reviewed concepts + 1 new concept + updated Memory management models notes
- Created 5 review notes in `Reviews/`
- Updated this session note

## Next due

- **2026-06-04 (today):** Bytecode, JIT Compilation (2 concepts — in queue)
- **2026-06-05:** Compiled vs Interpreted, Transpiler, Interpreter internals, Interpreter overhead, Compiler optimizations, JIT compilation tradeoffs, Dev vs Production workflow (7 concepts)
- **2026-06-07:** Python dynamic execution model, Python distribution model, Dynamic language optimization limits, Memory management models, Compiler, Short-circuit evaluation (6 concepts)
