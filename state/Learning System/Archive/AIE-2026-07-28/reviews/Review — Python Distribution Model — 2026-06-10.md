# Review — Python Distribution Model — 2026-06-10

**Result:** ✅ Mostly correct, interval advanced to 7d

**Question:** What happens when you package a Python program into a standalone executable, and why is the result so much bigger than a Go or Rust binary?

**User's answer:** Python packages its "background workers" like the garbage collector that kick off at runtime; Go/Rust handles things ahead of time before compiling to machine code.

**Evaluation:** Directionally right about bundling extra runtime components vs. not needing them, but misidentified the main culprit. The core issue is that PyInstaller bundles the **entire CPython interpreter** — your code isn't compiled to machine code at all. The executable unpackages the interpreter, which then reads and executes source code. Go/Rust compile directly to native machine code with no interpreter needed. Kept at 7d since the fundamental concept (bundling vs. compiling) was understood.

**Next review:** 2026-06-17
