<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# JIT Compilation

**JIT (Just-In-Time) compilation** is a technique where [[Bytecode]] is compiled to native machine code *at runtime* — while the program is running — rather than ahead of time.

## How it works

1. Source is compiled to [[Bytecode]]
2. A [[Virtual Machine]] starts interpreting the bytecode
3. The JIT compiler identifies frequently executed ("hot") code paths
4. Those hot paths are compiled to native machine code on the fly
5. Subsequent calls use the optimized native code instead of interpretation

## Why JIT?

- **Startup speed** — program starts immediately via interpretation (no wait for full compilation)
- **Runtime optimization** — JIT can observe actual program behavior and optimize based on real usage patterns, not just static analysis
- **Cross-platform** — same bytecode, JIT handles device-specific compilation

## Examples

- V8 (Chrome/Node.js JavaScript engine)
- JVM HotSpot
- .NET CLR
- PyPy (Python JIT)

## Downsides

While JIT combines interpreter-like startup with compiler-like speed, it has real tradeoffs:

1. **Startup latency (warm-up period)** — the JIT must parse and compile code while the program runs, creating a noticeable delay before peak performance kicks in
2. **Memory footprint** — the runtime must hold the original bytecode, the compilation framework, _and_ the generated machine code in RAM simultaneously
3. **CPU overhead** — the compiler thread consumes cycles that could serve the main application; wasteful for short-running scripts
4. **Implementation complexity** — building a stable, optimizing JIT requires specialized engineering and far more effort than a simple interpreter
5. **Platform constraints** — some systems forbid dynamic code generation. Apple's iOS restricts executable memory pages, making JIT compilers impossible for third-party apps.

## Related

- [[Compiler]]
- [[Interpreter]]
- [[Virtual Machine]]
- [[Bytecode]]

---

*Source: [[2026-05-29 - compilers-interpreters-virtual-machines]]*

## Sources

- https://en.wikipedia.org/wiki/Just-in-time_compilation
