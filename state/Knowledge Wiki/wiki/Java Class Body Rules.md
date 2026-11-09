<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Java Class Body Rules

## Key Insight

Inside the main body of a Java class, top-level members must be **declarations** (fields, methods, constructors, nested types, and initializer blocks). You cannot write a bare **action statement** (a loop, print, method call, or assignment) directly in the class body. A field declaration may contain an initializer *expression* (for example `int x = foo();`), but a statement such as `System.out.println(...)` or `age = 10;` is illegal outside a method, constructor, or initializer block.

## The Golden Rule

**Declarations are allowed; actions must be inside a "box" (method, constructor, or static block).**

### Illegal (actions in open class body)

```java
class Scanner {
    int age = 5; // Allowed! (This is a declaration)

    System.out.println("Hello"); // FORBIDDEN! This is an action.
    age = 10;                     // FORBIDDEN! This is an action.
}
```

### Legal (actions inside a method box)

```java
class Scanner {
    void myMethod() {
        System.out.println("Hello"); // Allowed inside a method box!
    }
}
```

## Why This Matters

This rule is the root reason why Java needs `static {}` blocks for complex static initialization. When initializing a static `Map` or `List`, calling `.put()` or `.add()` is an **action statement** — it cannot sit in the open class body. The static block provides the required "box" for these actions.

## Related

- [[Java Static Initializer Block]]
- [[Modern Java Collection Factory Methods]]

## Sources

- https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html
- https://docs.oracle.com/javase/tutorial/java/javaOO/classdecl.html
