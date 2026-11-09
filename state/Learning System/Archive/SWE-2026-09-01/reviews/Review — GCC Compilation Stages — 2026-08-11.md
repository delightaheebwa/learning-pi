# Review — GCC Compilation Stages — 2026-08-11

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 3d → 3d (reset — stages/flags missed)

**Question:** List the 4 stages of `gcc` compilation in order, and name the flag that stops after each stage.

**Answer:** 1) Preprocessing — `gcc -E` (expands #include, #define, macros). 2) Compilation proper — `gcc -S` (C → assembly). 3) Assembly — `gcc -c` (→ object file .o). 4) Linking (→ executable). `-o` sets output filename, `-l` links a library — neither is a stage flag.

**Assessment:** Miss — answered "code → object code(-o) → linking(-l) → machine code(-c)". Wrong stage count, wrong flags.

**Next Review:** 2026-08-14 (3d)
