<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Compiled vs Interpreted

The distinction between how languages execute: compiled upfront vs. interpreted at runtime. In practice, this is a spectrum.

## Compiled languages (e.g., Go, Rust, C++)

- Source code is translated to machine code ahead of time
- The resulting binary executable is self-contained
- Analogy: traveling with your own actors and crew — everything you need is bundled in
- The binary runs directly on the CPU; no external software needed

## Interpreted languages (e.g., Python, JavaScript)

- Source code is read and executed at runtime by an [[Interpreter]]
- Requires a permanent piece of software on the user's computer (Python interpreter, JavaScript engine)
- Analogy: showing up with just a script and relying on local actors — the infrastructure needs to be there already

## The middle ground

Most modern languages use a hybrid approach:

- **Java** — compiled to [[Bytecode]], run on the [[Virtual Machine|JVM]] (with [[JIT Compilation]])
- **Python** — compiled to `.pyc` bytecode, then interpreted by the Python VM
- **JavaScript** — interpreted or JIT-compiled by the browser's engine

## Dev vs Production workflow

The two approaches complement each other in practice:

- **During development** — you type a line, the interpreter runs it instantly, and you see the result. Slow for the computer, but instantaneous for the human iterating at the keyboard.
- **For production** — you feed the finished project to the compiler. It takes a moment to build, but the output is a lightning-fast binary for end users.

This combination gives programmers ultimate flexibility while writing code and ultimate speed when shipping it.

## Related

- [[Compiler]]
- [[Interpreter]]
- [[Virtual Machine]]
- [[Bytecode]]
- [[JIT Compilation]]

---

*Source: [[2026-05-29 - compilers-interpreters-virtual-machines]]*

## Sources

- https://en.wikipedia.org/wiki/Compiled_language
- https://en.wikipedia.org/wiki/Interpreter_(computing)
