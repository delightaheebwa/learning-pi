# Review — GCC Compilation Stages — 2026-08-17

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 3d (keep)

**Question:** You run `gcc -c main.c -o main.o`, then later `gcc main.o utils.o -o monitor`. Walk through both commands: which of the 4 stages ran in each, and what would `gcc -S main.c` produce instead?

**Answer:** The compilation proper stage and object stage for the first command, and the linking and execution for the second. `gcc -S main.c` would produce an executable.

**Assessment:** ⚠️ Partial. `gcc -c` correctly — it runs preprocessing → compilation proper → assembly, producing `main.o` (stops before linking). ❌ The second command is **link-only**: `gcc main.o utils.o -o monitor` links existing objects into the executable — "execution" is not a gcc stage (running the program is the shell's job: `./monitor`). gcc has exactly 4 stages: preprocess → compile → assemble → link. ❌ `gcc -S main.c` emits an **assembly file** (`main.s`) — it runs preprocessing + compilation proper only and stops before the assembler; it is not an executable.

**Next Review:** 2026-08-20 (3d)