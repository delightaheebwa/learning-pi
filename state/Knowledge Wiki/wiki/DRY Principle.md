<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# DRY Principle

**Don't Repeat Yourself** is about the duplication of **knowledge and intent**, not just code. It's about expressing the same thing in two different places, possibly in two totally different ways.

## What DRY actually means

Not all code duplication is knowledge duplication. Two pieces of identical code that represent *different* knowledge (different reasons to change) are not a DRY violation. The question is: if one changes, must the other change too? If yes → DRY violation. If no → coincidental duplication, not a problem.

## Examples of DRY violations

- **Comments that repeat code**: A comment that describes exactly what the code does is a DRY violation. The intent is expressed twice.
- **Data structure coupling**: When changing one field in a struct requires manually changing another field to match.
- **Representational duplication**: Manually recreating an external system's schema in your code (see [[Representational Duplication]]).
- **Interdeveloper duplication**: Teammates writing the same utility without knowing it exists (see [[Interdeveloper Duplication]]).

## When to violate DRY

- **Caching for performance**: When an expensive computation's result is cached, you're technically duplicating data. The trick is to **localize the impact** — keep the duplication internal to a class/module so outside code never knows.
- The violation must not be exposed to the outside world.

## Related

- [[Uniform Access Principle]] — using accessor functions helps prevent DRY violations in data access
- [[ETC (Easier To Change)]]
- [[Representational Duplication]]

## Source

The Pragmatic Programmer (Hunt & Thomas) — https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/
