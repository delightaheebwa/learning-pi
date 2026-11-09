<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Memory Management

Memory management keeps programs running smoothly by cleaning up unused data. There are three primary strategies, distinguished by **who decides when memory is freed**.

---

## 1. Garbage Collection (GC)

The runtime automatically tracks and reclaims unused memory. Two flavors:

### Reference Counting

Each object tracks how many references point to it.
- **Allocation:** counter increases when a new pointer connects
- **Deallocation:** counter decreases when a pointer is removed
- **Trigger:** data is freed instantly when its counter hits zero

**Flaw:** Circular references — two objects pointing to each other but disconnected from the active program — are never freed because their counters never reach zero.

**Used by:** Python (backed by a cyclic GC for cycles), Swift.

### Tracing GC (Mark-and-Sweep)

The runtime periodically pauses to identify all reachable data.
- **Roots:** Active functions and global variables — the entry points of the running program
- **Mark phase:** Follows all reference chains from roots, marking reachable objects
- **Sweep phase:** Deletes everything that wasn't marked
- **Reachability:** An object is "reachable" if there exists a chain of references from any root to that object

**Circular references solved:** If A and B only point to each other, but no root reaches either, the scanner never visits them. They remain unmarked and are swept away.

**Flaw:** "Stop-the-world" pauses — the program must halt during collection.

**Used by:** Java, JavaScript, Go.

### Reference Counting vs Tracing GC

| Aspect | Reference Counting | Tracing GC |
|--------|-------------------|------------|
| Speed | Cleans up instantly | Cleans up in batches |
| Memory overhead | Counters per object | Working memory for scan |
| Completeness | Misses cycles (needs backup) | Finds everything |
| Pause times | None | Stop-the-world pauses |

---

## 2. Manual Memory Management

The programmer explicitly allocates and frees memory.

- **Allocation:** `malloc()` (C) or `new` (C++)
- **Deallocation:** `free()` (C) or `delete` (C++)
- **Runtime overhead:** Zero — no reference counting, no GC scans
- **Flaw:** Error-prone — forgetting to `free` causes leaks; `free`-ing too early causes dangling pointers and crashes

**Used by:** C, C++.

---

## 3. Compile-Time Ownership

The compiler proves memory ownership at build time and inserts allocation/deallocation automatically.

- **Mechanism:** Ownership rules enforced by the compiler — each value has exactly one owner; when the owner goes out of scope, the value is freed
- **Runtime overhead:** Zero — all free calls are hardcoded at compile time
- **Flaw:** Steep learning curve — the borrow checker enforces strict rules that require rethinking program structure

**Used by:** Rust.

---

## Key Insight

The three strategies represent a spectrum of **who bears the burden**:
- **GC** — the runtime bears it (convenient but has performance cost)
- **Manual** — the programmer bears it (fast but error-prone)
- **Ownership** — the compiler bears it (fast and safe, but restrictive)

---

## Related

- [[Python performance tradeoffs]] — Python's GC overhead and comparison with Rust/C
- [[Compiler]] — compile-time ownership is a compiler-level guarantee
- [[Interpreter]] — interpreters include runtime memory management

---

*Source: `raw/sources/2026-06-04 - short-circuit-evaluation-memory-management.md`*

## Sources

- https://en.wikipedia.org/wiki/Garbage_collection_(computer_science)
- https://en.wikipedia.org/wiki/Reference_counting
- https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html
