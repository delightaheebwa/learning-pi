# 2026-05-29 — Compilers, Interpreters, and Virtual Machines

**Type:** Handwritten notes (7 pages)
**Topic:** How programming languages execute — compilers, interpreters, VMs, bytecode, JIT

## Pages

1. ![Compiler design overview](../assets/compiler-design-overview-2026-05-29-01.jpg)
   - Compiler pipeline: Frontend → Backend → Optimization → Code gen
   - Bytecode, three-address code, virtual machine code
   - Frontend is source-language-specific

2. ![VM and architecture](../assets/compiler-vm-architecture-2026-05-29-02.jpg)
   - Language VM: a program that emulates a hypothetical chip
   - Optimizations work best when they know the strengths and weaknesses of the specific chip
   - A compiler is a pipeline that translates your code (C++, Rust) into...

3. ![Machine code and CPU](../assets/compiler-machine-code-cpu-2026-05-29-03.jpg)
   - Machine code, CPU
   - General code cleaning, last-minute tweaks
   - Your code never runs completely alone — it has a "crew" (invisible background assistants)

4. ![Compiled vs Interpreted](../assets/compiler-compiled-vs-interpreted-2026-05-29-04.jpg)
   - Fully compiled languages (Go): code gets inserted directly into the binary executable
   - Analogy: traveling with your own actors and crew vs. relying on local infrastructure
   - Java, Python, JavaScript need a permanent piece of software on the user's computer (JVM, Python interpreter)

5. ![Bytecode and VM](../assets/compiler-bytecode-vm-2026-05-29-05.jpg)
   - To run code anywhere: need Bytecode + a VM program
   - VM program = "fake chip" acting as a lightning-fast translator
   - VM reads bytecode line-by-line and executes instructions
   - VM program is device-specific, language is not

6. ![VM flowchart](../assets/compiler-vm-flowchart-2026-05-29-06.jpg)
   - The hard work of building different VMs for every major device
   - Java vs. Python: Python creates a .pyc file
   - Flowchart: Single pre-compile → parsing → analysis → code gen → machine code
   - One-shot line by line translation

7. ![JIT and Transpiler](../assets/compiler-jit-transpiler-2026-05-29-07.jpg)
   - JIT (Just-In-Time) compilation
   - Tree-walk interpreter
   - Transpiler
