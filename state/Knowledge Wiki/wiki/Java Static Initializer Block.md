<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Java Static Initializer Block

## Key Insight

A `static {}` block is a **setup box** for static variables — it runs automatically during class initialization, before the class is first used (before instances are created or static members are accessed), and provides a place for multi-step initialization actions.

## The Problem It Solves

Creating a static variable is a declaration (allowed in the class body). But *filling* it with data requires calling `.put()` or `.add()` — which are **action statements** (forbidden in the open class body per [[Java Class Body Rules]]).

### Without a static block (does NOT compile)

```java
class Scanner {
    private static final Map<String, TokenType> keywords; // Allowed (Declaration)

    keywords = new HashMap<>();     // FORBIDDEN! (Action in open class)
    keywords.put("if", IF);         // FORBIDDEN! (Action in open class)
}
```

### With a static block (compiles and works)

```java
class Scanner {
    private static final Map<String, TokenType> keywords;

    static {
        keywords = new HashMap<>();
        keywords.put("if", IF);
        keywords.put("else", ELSE);
    }
}
```

## Runtime Timeline

1. **Class Loading/Initialization**: the JVM initializes the class when it is first used
2. **Static Field Initializers & Static Blocks**: run in textual order — the map is created and filled
3. **`main()` / First Use**: the program's main method or first use of the class begins; the static map is already ready
4. **Object Creation**: instances are created — the static map is already ready

Think of it like a restaurant kitchen: the `static {}` block is the prep work done before opening (chopping vegetables, heating ovens). The main code is the cooking done after a customer orders.

## When to Use It

**Use the setup box when:**
- You need loops or error handling to initialize a static variable
- You're using Java 8 or earlier (where `Map.of()` doesn't exist)
- The initialization takes multiple steps (configure, set timeout, enable)

**It's overkill when:**
- You can do it in a single line (`static int maxCount = 100;`)
- You're using modern Java 9+ (use `Map.of()`, `List.of()`, `Set.of()`)
- The variable is NOT static (use a constructor instead)

## Related

- [[Java Class Body Rules]]
- [[Modern Java Collection Factory Methods]]

## Sources

- https://docs.oracle.com/javase/tutorial/java/javaOO/initial.html
- https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.7
