<!-- provenance: status=verified | source=https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/ ; https://en.wikipedia.org/wiki/Global_variable | verified-by=fact-check-agent | date=2026-10-26 -->

# Global Data Avoidance

> Related: [[Orthogonality]], [[Shy Code]], [[Self-Contained Components]]

## Definition

**Global Data Avoidance** is the practice of explicitly passing required context into modules rather than reaching into shared global state. Every reference to global data ties your code into every other component that shares that data.

## The problem with globals

> "Every time your code references global data, it ties itself into the other components that share that data."

Even **read-only globals** cause trouble:
- Multithreading: suddenly you need synchronization for what seemed harmless
- Testing: you can't test a module in isolation because it depends on hidden global state
- Reasoning: you can't understand a function by reading it in isolation — you need to know what's in the global scope

## The solution: explicit context

Pass context explicitly — as constructor parameters (OOP) or as structures containing the context:

```python
# Avoid
def process():
    result = GLOBAL_CONFIG.threshold * GLOBAL_DATA.value  # depends on invisible state
    ...

# Prefer
def process(config, data):
    result = config.threshold * data.value  # dependencies are explicit
    ...
```

## Singletons as global variables in disguise

The **Singleton pattern** (from the Gang of Four) ensures only one instance of a class. Many developers use singletons as a way to have global variables in languages like Java that don't otherwise support globals. **Be careful** — singletons carry the same coupling risks as global variables.

## Benefits of avoidance

- **Testability** — inject test doubles instead of real globals
- **Thread safety** — no shared mutable state to protect
- **Understandability** — a function's signature tells you everything it depends on
- **Reuse** — modules can be dropped into different contexts without modification

## Sources

- https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/
- https://en.wikipedia.org/wiki/Global_variable
