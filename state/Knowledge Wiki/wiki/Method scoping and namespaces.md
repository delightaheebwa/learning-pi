<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Method Scoping and Namespaces

## Core Idea

In object-oriented languages, methods are **scoped to their type/object** — each type has its own internal namespace (method table) of function implementations. This eliminates the need for globally unique function names.

## The Problem: Global Namespaces (Racket-style)

In languages with only top-level functions (like Racket), all function names share one global namespace, forcing type-specific prefixes:

- `hash-copy(table)` — copy a hash table
- `vector-copy(vec)` — copy a vector
- `list-copy(lst)` — copy a list

You can't just use `copy` for everything — the names would collide. The **type is encoded in the function name**.

## The Solution: Method Scoping (OO-style)

With methods scoped to types:

- `table.copy()` — HashTable's `copy`
- `vec.copy()` — Vector's `copy`
- `lst.copy()` — List's `copy`

All named `copy`, but each lives in a **different type's method table**. The **type is encoded in the receiver** (the object before the dot).

## How Method Dispatch Works

When you call `obj.method()`:

1. Runtime looks at the **type** of `obj`
2. Goes to that type's **method table** (internal namespace)
3. Looks up the method **name** in that table
4. Executes the **implementation** stored there

Same method name → different implementation, depending on the receiver's type.

## Python Examples

- `list.append(x)` vs `set.add(x)` — different method names, but both scoped to their respective types
- If Python had only global functions: `list_append(lst, x)` and `set_add(s, x)` to avoid collisions
- `len()` is a special case: it's a global built-in that internally dispatches to `obj.__len__()`, combining both patterns

## Why It Matters

- **Cleaner code**: short, generic names (`copy`, `save`, `to_json`) instead of prefixed bloat
- **Discoverability**: `obj.` shows all available operations via autocomplete
- **Organization**: each type owns its behavior, no global namespace pollution

## Related

- [[Programming paradigms comparison]]
- [[Imperative and declarative programming]]

## Sources

- https://en.wikipedia.org/wiki/Method_(computer_programming)
