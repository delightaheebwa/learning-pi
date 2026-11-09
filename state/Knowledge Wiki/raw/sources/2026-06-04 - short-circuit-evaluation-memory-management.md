# Short-Circuit Evaluation and Memory Management

Source: Perplexity conversation, 2026-06-04.

---

## Short-Circuit Evaluation: Logical Operators as Control Flow

Short-circuiting behavior turns logical operators into stealth control flow structures.

**Why they act like control flow:** Because the second operand is conditionally evaluated, `and` and `or` act like compressed if-else statements:

- `A and B` behaves like: if A then B else A
- `A or B` behaves like: if A then A else B

**What operators actually return (Python, JavaScript):** They don't just return booleans — they return the actual value of one of the operands.

For `and`: Keep looking until you find a False, or return the last thing.
- `None and "Hello"` → `None` (A is False, returns A immediately)
- `"Apple" and "Banana"` → `"Banana"` (A is True, returns B)

For `or`: Keep looking until you find a True, or return the last thing.
- `"Apple" or "Banana"` → `"Apple"` (A is True, returns A immediately)
- `None or "Banana"` → `"Banana"` (A is False, returns B)

**Common use cases:**
- **Guard clauses:** `if (object != null && object.hasProperty())` — if object is null, the second check never runs, preventing a null pointer crash.
- **Default values:** `const name = inputName || "Anonymous"` — if inputName is falsy, falls back to the string literal.

**The dark side:** If the right operand has side effects, they may be skipped silently. E.g., `condition or performAction()` — if condition is true, `performAction()` is never called.

**When to avoid:** Do not use for complex logic. Chaining too many operators together makes code unreadable. If your team cannot understand the code at a glance, use standard if-else statements.

---

## Memory Management: Reference Counting vs Tracing Garbage Collection

### Reference Counting

Every piece of data tracks how many things are pointing to it:
- Counter increases when a new pointer connects to the data
- Counter decreases when a pointer is removed
- Data deletes instantly when its counter hits zero

**The flaw:** Cannot easily detect circular references (two items pointing to each other but disconnected from the main program). Pure reference counting leaks these cycles.

**Real-world use:** Python (backed by a cyclic GC for cycles) and Swift.

### Tracing Garbage Collection (Mark-and-Sweep)

The system periodically pauses to look for all data currently in use:
- Starts at "roots" — active functions, global variables — the core parts of the running program
- Follows all active links to find and mark reachable data
- Sweeps away and deletes anything not marked

**What "reachable" means:** There is a chain of connections from a root.
1. Scanner looks at a root variable
2. If that root points to an object, that object is marked
3. If that object contains pointers to other objects, those are also marked
4. Repeats until it runs out of links

**Circular references solved:** If Object A and Object B only point to each other, but no active root points to either of them, the scanner never visits them. Because they're unreachable from the roots, they remain unmarked and get deleted.

**The flaw:** The program must occasionally pause to run this search ("stop-the-world" pauses).

**Real-world use:** Java, JavaScript, and Go.

### Comparison

| Aspect | Reference Counting | Tracing GC |
|--------|-------------------|------------|
| Speed | Cleans up instantly | Cleans up in batches |
| Memory overhead | Extra memory for counters | Extra memory to run its search |
| Completeness | Can miss leaked data (cycles) | Finds everything |
| Pause times | No pauses | Stop-the-world pauses |
