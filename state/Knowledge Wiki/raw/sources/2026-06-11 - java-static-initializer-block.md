# 2026-06-11 — Java Static Initializer Block

Raw source from Perplexity conversation about Java's `static {}` block, class body rules, and modern alternatives.

## Source Content

The user learned about why Java requires a `static {}` block for multi-step static initialization. Key points covered:

1. **Java Class Body Rules**: Inside a class body, only declarations are allowed (variables, methods). Action statements (prints, assignments, method calls) are forbidden and must be inside a method, constructor, or static block.

2. **Static Initializer Block**: The `static {}` block serves as a "setup box" that runs automatically when the JVM loads the class — before `main()` starts. It provides a place to run multi-step initialization actions for static variables.

3. **Runtime Timeline**: Class Loading → Static Block Execution → `main()` Starts → Object Creation. The static block is like restaurant prep work done before opening.

4. **Modern Java Alternatives**: Java 9+ `Map.of()`, `List.of()`, `Set.of()`, and `Map.ofEntries()` allow single-line immutable collection creation, making static blocks unnecessary for simple cases.

5. **Decision Criteria**: Use static blocks for multi-step initialization, loops, error handling, and complex object configuration. Skip them for single-line assignments, modern Java collection factories, and non-static (instance) variables (use constructors instead).
