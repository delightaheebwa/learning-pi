<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# C Pointers (&, *, ->)

## Overview

`*` and `&` are **pointer operators** — they control how you read, write, and reference memory addresses directly. Think of RAM as a giant row of post-office boxes: a regular variable holds the *contents inside* a box; a memory address tells you *which box number* a variable lives at.

## The Address-of Operator (&)

"Where does this variable live?" — placing `&` before an existing variable yields its **memory address** (box number), not its value:

```c
int age = 25;
printf("%d\n", age);   // 25       (the value inside)
printf("%p\n", &age);  // 0x7ffd… (the memory address of age)
```

Why the lesson used it: calling `parse_meminfo(input, &memory)` passes the *address* of the caller's `struct memory`, letting the function modify that struct directly.

## The Pointer / Dereference Operator (*)

The `*` symbol wears **two hats** depending on placement:

**Hat A — type declaration (creating a pointer):** in a declaration, `*` says "this variable doesn't hold data directly; it holds a memory address."

```c
int *ptr = &age;  // ptr stores the memory address of age
```

**Hat B — dereferencing (opening the box):** before an existing pointer in executable code, `*` means "go to the address stored inside this pointer and read/write the value inside."

```c
int age = 25;
int *ptr = &age;
*ptr = 30;              // follow ptr to age's location, write 30 there
printf("%d\n", age);    // 30
```

## The Arrow (->)

For pointers to structs, `->` is shortcut syntax for dereference-then-field: `out->total_kb` is shorthand for `(*out).total_kb`. It follows the address to modify the original struct back in the caller:

```c
int parse_meminfo(const char *text, struct memory *out)
{
    // ...
    out->total_kb = value;   // ≡ (*out).total_kb = value;
}
```

## Key Insight

- C passes function arguments **by value**. A plain `struct memory memory` argument would be copied, and mutations would vanish when the function returns. Passing the address (`&memory`) is how C simulates pass-by-reference.
- `*p = 20` writes *through* the pointer — the pointed-to variable changes (x becomes 20), not the pointer itself.

## Pointers & Memory Lifetime (dangling pointers)

A pointer is only valid while the memory it points to is still alive — which depends on *which region* it points to (see [[C Memory Regions (Stack vs Heap vs Swap)]]).

Returning the address of a **stack** array is the classic dangling-pointer bug (added 2026-08-18 from Gemini notebook ed55c6cdf10c8c2a):

```c
char *read_file_broken(const char *path) {
    char text[4096];   // on the stack
    // ...
    return text;       // points to a stack frame that dies on return
}
```

When the function returns, its stack frame is destroyed, so the returned pointer dangles — using it later is undefined behavior. GCC/Clang warn because they can statically see it's an address to local stack memory.

**Not a leak (the half-right trap):** a stack array *cannot* leak — stack memory vanishes on return automatically. Memory leaks only happen on the **heap** when you fail to `free()`. The corrected model: the *variable* `char *buf` lives on the stack; the 4,096-byte block `malloc(4096)` returns lives on the heap.

## Self-Check

```c
int x = 10;
int *p = &x;
*p = 20;
```

`x` holds **20**: `p` holds x's address, and dereferencing (`*p`) reaches that memory location and overwrites its value.

## Sources

- Gemini Socratic tutoring on C pointers (notebook: https://gemini.google.com/app/8870dcd71e2919f5)
- Gemini C tutoring — pointers & memory lifetime / dangling pointers (notebook: https://gemini.google.com/app/ed55c6cdf10c8c2a)

Related: [[Testable Seam]], [[Sentinel Values vs Presence Flags]], [[C Memory Regions (Stack vs Heap vs Swap)]]

## References

- https://en.wikipedia.org/wiki/Pointer_(computer_programming)
- https://en.cppreference.com/w/c/language/pointer
