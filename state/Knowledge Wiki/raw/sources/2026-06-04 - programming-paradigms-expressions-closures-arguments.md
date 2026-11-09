# 2026-06-04 — Programming Paradigms, Expressions, Closures, and Arguments

## Source type: User-provided notes (partial, truncated in chat)

This source covers four concepts from a programming/programming-languages context:

### Expressions vs Statements

Where an expression's main job is to produce a value, a statement's job is to produce an effect. An expression followed by a semicolon (;) promotes the expression to statement-hood. This is called an expression statement.

### Imperative vs Declarative Programming

Most general-purpose programming languages support an imperative style, and many use it as their primary paradigm:

- **C**: A quintessential imperative language that requires manual memory management.
- **Java**: Widely used and highly structured imperative language.
- **Python**: Multi-paradigm but commonly used imperatively.
- **JavaScript**: Multi-paradigm but often written imperatively.

Declarative languages/paradigms include:
- **SQL**: State what data you want, not how to retrieve it.
- **React**: Declare UI as a function of state.
- **SwiftUI**: Declarative UI framework.
- **Terraform/Kubernetes**: Declare desired infrastructure state.

**Why imperative is more mainstream:**
1. **Hardware mimicry** — CPUs execute instructions imperatively (fetch-decode-execute cycle). Early languages were thin wrappers over machine code. Because software history built upon these early languages, the imperative model became the default foundation of modern computing.
2. **Human intuition** — Humans naturally think imperatively when giving instructions. If you tell someone how to drive to your house, you give them step-by-step directions ("Turn left, drive two miles...").
3. **Legacy and ecosystem** — Decades of libraries, tools, and education built around imperative programming.

### Arguments vs Parameters

- **Parameter**: The variable listed in the function definition that holds the value passed in.
- **Argument**: The actual value passed to the function when it is called.

Key context: local functions, first-class functions (functions that can be assigned to variables, passed as arguments, or returned).

### Closures

- **Block scope**: Variables only exist within the block of code `{ }` where they were born.
- **Closure**: The combination of a function bundled together with references to its surrounding state.

The backpack analogy: When an inner function is returned from an outer function, it "packs" the outer variables into its backpack and carries them along. This means the inner function retains access to those variables even after the outer function has completely finished running.

**A Modern Note**: Today, people often call any function passed around a "closure." Technically, it is only a closure if it actually grabs and holds onto a variable from outside its own body.

## References

[1-23] Truncated chat content — Perplexity conversation about programming language concepts.
