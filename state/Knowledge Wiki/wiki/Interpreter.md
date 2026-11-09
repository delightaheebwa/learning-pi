<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Interpreter_(computing) | verified-by=fact-check-agent | date=2026-10-26 -->

# Interpreter

An **interpreter** translates and executes source code line by line, without producing a standalone executable.

## How it works

Rather than compiling the entire program upfront, the interpreter reads the source, translates it, and executes it in one continuous process — often described as "one-shot line by line translation."

### The EVAL loop

At its core, an interpreter runs an **EVAL (Evaluate)** loop. For an expression like `(+ 2 3)`:

1. Reads the text `(+ 2 3)`
2. Recognizes the symbol `+`
3. Calls its own internal, pre-compiled function for addition
4. Returns `5`

The interpreter is the **only binary** running. It never creates new machine code or executable files — it reads your code as data and acts it out using its own pre-written logic.

### The "translator" overhead (why interpreters are slower)

When the interpreter runs code, the computer does two things simultaneously: **figure out what the code means** and **actually execute it**. This is like sitting with a live translator instead of reading a pre-translated manual — you stop and wait at every single line.

Because the interpreter reads code on the fly, it **cannot look ahead** to see the big picture. It executes blindly, line by line — sacrificing deep optimization for instant feedback.

### Why interpreters can't optimize

A compiler looks at the entire program at once and can perform heavy optimizations:
- **Math cleanup** — replacing slow formulas with faster equivalents
- **Dead code elimination** — removing lines that never execute
- **Register allocation** — placing data directly in the CPU's fastest internal memory

An interpreter doesn't have time for that "math homework" — it prioritizes giving you an instant response in the REPL.

### Compiler vs Interpreter at a glance

| | Compiler | Interpreter |
|---|---|---|
| What happens to code? | Turned into a new binary file | Read as text by an existing binary |
| Who executes it? | CPU directly | The interpreter software |
| Speed | Lightning-fast | Slower (extra layer) |
| Flexibility | Rigid (must recompile) | Instant updates |

## Types

- **Tree-walk interpreter** — builds an AST (Abstract Syntax Tree) from source code and walks it node by node, executing each one. Simple but slow.
- **Bytecode interpreter** — executes pre-compiled [[Bytecode]] on a [[Virtual Machine]]. Faster because parsing is done upfront.

## Interpreted languages

Languages like Python and JavaScript are typically interpreted (or JIT-compiled). They require a permanent piece of software installed on the user's computer — like the Python interpreter or a JavaScript engine.

## Related

- [[Compiler]]
- [[Virtual Machine]]
- [[Bytecode]]
- [[JIT Compilation]]
- [[Compiled vs Interpreted]]

---

*Source: [[2026-05-29 - compilers-interpreters-virtual-machines]]*

## Sources
- Wikipedia, "Interpreter (computing)": https://en.wikipedia.org/wiki/Interpreter_(computing)
- Crafting Interpreters: https://craftinginterpreters.com/
