<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Runtime

The **runtime** is the invisible background system that keeps a program alive while it executes. Your code never runs completely alone — it has a "crew" of background assistants.

## What the runtime does

- **Memory management** — allocating and freeing memory (garbage collection in managed languages)
- **Logic checks** — bounds checking, type checking, null checks
- **Exception handling** — catching and propagating errors
- **Scheduling** — managing threads, async operations, and concurrency
- **I/O handling** — files, network, and device interactions

## The two components

A runtime is comprised of two distinct parts:

- **Engine** — the executor that reads and runs code (e.g., JavaScript engine like V8, Java's JVM, Python's CPython interpreter). This is the "musician" that plays the notes.
- **Environment** — the surrounding context and capabilities provided to the program (e.g., browser APIs like `document` and `fetch`, Node.js APIs like `fs` and `http`, Python's standard library). This is the "concert hall" — the acoustics and stage that make the performance possible.

Together they form a **musicians-and-concert-hall metaphor**: the musicians (engine/VM) read and play the notes, while the hall provides the acoustics and stage (the environment) for the performance to happen. Neither is complete without the other — the best musicians sound terrible in a poor hall, and the finest hall is silent without musicians.

## Compiled vs interpreted runtimes

- **Compiled languages** (Go, Rust): the runtime is compiled directly into the binary executable — you "travel with your own crew"
- **Interpreted/JIT languages** (Java, Python, JavaScript): the runtime is a separate piece of software installed on the user's computer ([[Virtual Machine|JVM]], Python interpreter)

## Related

- [[Virtual Machine]]
- [[Compiler]]
- [[Interpreter]]
- [[Compiled vs Interpreted]]
- [[Waterbed Theory]]

---

*Sources: [[2026-05-29 - compilers-interpreters-virtual-machines]], [[2026-06-06 - waterbed-theory-runtime-components]]*

## Sources (verified)

- https://en.wikipedia.org/wiki/Runtime_system
