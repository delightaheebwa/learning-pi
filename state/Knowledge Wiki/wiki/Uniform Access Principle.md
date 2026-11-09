<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Uniform Access Principle

From Bertrand Meyer's *Object-Oriented Software Construction*: all services offered by a module should be available through a **uniform notation** that does not reveal whether they are implemented through storage (a field) or computation (a method).

## Core ideas

### Accessor functions
Always use getter and setter functions (methods) to read and write object attributes, rather than exposing raw data structures directly. This prevents **coupling** — if you change the internal data structure later, external code that used accessors doesn't break.

### Uniform notation
The caller shouldn't know (or care) whether `user.name` returns a stored field or computes it on the fly. The syntax looks identical either way. This gives you freedom to change the implementation behind the scenes.

## Modern implementation: Properties

Languages like Python (`@property`), JavaScript (get/set), Swift, and C# implement Uniform Access through properties. You can start by exposing a plain variable, then later turn it into a property with caching, validation, or computation — without breaking any calling code.

## When to skip it

**Data Transfer Objects (DTOs)**: Simple data buckets with no behavior, no caching, no logic. These are just containers for moving data between layers (e.g., database → webpage). Accessors add unnecessary ceremony here.

## Related

- [[DRY Principle]] — accessors prevent DRY violations by centralizing data access
- [[Representational Duplication]] — accessors abstract away how data is stored or retrieved

## Source

The Pragmatic Programmer (Hunt & Thomas), citing Meyer's *Object-Oriented Software Construction*

## Sources
- https://en.wikipedia.org/wiki/Uniform_access_principle
- Meyer, B. Object-Oriented Software Construction (origin of the Uniform Access Principle)
