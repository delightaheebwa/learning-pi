<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Modern Java Collection Factory Methods

## Key Insight

Java 9+ introduced `List.of()`, `Set.of()`, and `Map.of()` — single-line factory methods that create and populate immutable collections, making `static {}` blocks unnecessary for simple initialization.

## The Old Way (Java 8 and earlier)

Required a `static {}` block for multi-step population:

```java
private static final Map<String, TokenType> keywords;

static {
    keywords = new HashMap<>();
    keywords.put("and", AND);
    keywords.put("class", CLASS);
    keywords.put("if", IF);
}
```

## The Modern Way (Java 9+)

Single declaration line — no setup box needed:

```java
// Simple map (up to 10 entries)
private static final Map<String, TokenType> keywords = Map.of(
    "and", AND,
    "class", CLASS,
    "if", IF
);

// Larger maps (unlimited entries)
private static final Map<String, TokenType> keywords = Map.ofEntries(
    Map.entry("and", AND),
    Map.entry("class", CLASS),
    Map.entry("if", IF)
);
```

## Available Methods

| Method | Creates | Max elements (simple) |
|--------|---------|----------------------|
| `List.of(...)` | Immutable list | Unlimited (varargs) |
| `Set.of(...)` | Immutable set | Unlimited (varargs) |
| `Map.of(k1,v1, k2,v2, ...)` | Immutable map | 10 key-value pairs |
| `Map.ofEntries(...)` | Immutable map | Unlimited |

## Important: Immutability

The collections returned by these factory methods are **immutable** — you cannot add, remove, or modify elements after creation. If you need a mutable collection, you must still use `new HashMap<>()` (and potentially a static block).

## When This Replaces Static Blocks

This replaces static blocks when your initialization is a simple "create and populate a collection." You still need a static block if:
- You need mutable collections
- The initialization involves loops, conditionals, or error handling
- You're configuring complex objects with multiple setup steps

## Related

- [[Java Static Initializer Block]]
- [[Java Class Body Rules]]

## Sources

- OpenJDK JEP 269 — Convenience Factory Methods for Collections: https://openjdk.org/jeps/269
- Oracle — Creating Immutable Lists, Sets, and Maps: https://docs.oracle.com/javase/9/core/creating-immutable-lists-sets-and-maps.htm
- Baeldung — Java 9 Collections Factory Methods: https://www.baeldung.com/java-9-collections-factory-methods
