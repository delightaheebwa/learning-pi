<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Virtual Machine

A **Virtual Machine (VM)** is a program that emulates a hypothetical chip — a "fake chip" that provides a portable execution environment for bytecode.

## How it works

- Reads [[Bytecode]] and executes it, typically via an interpreter loop (and, in many implementations, a JIT compiler that compiles hot paths to native machine code)
- May translate bytecode to native machine code ahead of time or on demand, or interpret it directly
- Executes the resulting instructions on the host CPU

## Why VMs exist

Without a VM, compiled code only runs on the specific chip architecture it was compiled for. A VM lets the same bytecode run anywhere — the VM handles the device-specific translation.

The hard work is building different VM implementations for every major device (Windows, Mac, Linux, different CPU architectures) so that programs "just work everywhere instantly."

## Examples

- **JVM (Java Virtual Machine)** — runs Java bytecode
- **Python VM** — runs Python bytecode (`.pyc` files)
- **JavaScript engines** (V8, SpiderMonkey) — run JavaScript, often with [[JIT Compilation]]

## Related

- [[Bytecode]]
- [[Compiler]]
- [[Interpreter]]
- [[JIT Compilation]]
- [[Runtime]]

---

*Source: [[2026-05-29 - compilers-interpreters-virtual-machines]]*

## Sources
- https://en.wikipedia.org/wiki/Virtual_machine
