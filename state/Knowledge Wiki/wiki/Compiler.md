<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Compiler | verified-by=fact-check-agent | date=2026-10-26 -->

# Compiler

A **compiler** is a pipeline that translates source code (C++, Rust, Go) into machine code that a CPU can execute directly.

## Pipeline stages

1. **Frontend** — source-language-specific; handles lexing, parsing, semantic analysis; transforms source into an intermediate representation (IR)
2. **Middle end (optimization)** — IR-level, target-independent optimizations (dead-code elimination, constant propagation, etc.)
3. **Backend (code generation)** — target-architecture-specific; handles register allocation, instruction selection/scheduling, and emits machine code or bytecode

### Why compilers can optimize heavily

Unlike an [[Interpreter]], a compiler sees the **entire program at once** before any code runs. This "big picture" view enables powerful optimizations:

- **Math simplification** — replacing slow formulas with faster tricks the CPU prefers (e.g., `x * 2` → `x << 1`)
- **Dead code elimination** — removing lines and branches that never actually execute
- **Register allocation** — placing frequently accessed data directly into the CPU's fastest internal memory slots (registers) instead of slower RAM

An interpreter, executing line-by-line, simply doesn't have time for this analysis — it trades optimization for instant feedback.

## Output forms

- **Machine code** — native instructions for a specific CPU
- **Bytecode** — portable intermediate code that runs on a [[Virtual Machine]]
- **Intermediate representations** — e.g., three-address code, used internally by compilers during optimization

## Compiled vs Interpreted

See: [[Compiled vs Interpreted]]

## Related

- [[Interpreter]]
- [[Virtual Machine]]
- [[Bytecode]]
- [[JIT Compilation]]
- [[Transpiler]]

---

*Source: [[2026-05-29 - compilers-interpreters-virtual-machines]]*
## Sources

- https://en.wikipedia.org/wiki/Compiler
- https://en.wikipedia.org/wiki/Front_end_and_back_end
