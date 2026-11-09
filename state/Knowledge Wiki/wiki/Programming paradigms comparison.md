<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Programming Paradigms Comparison

A programming paradigm is a style or approach to structuring code. The three most popular are Imperative, Functional, and Object-Oriented Programming (OOP).

## 1. Imperative Programming

**"Tell the computer HOW to do it"**

Step-by-step instructions. Relies on changing states, updating variables, and loops (`for`, `while`).

| Aspect | Detail |
|--------|--------|
| Pros | High performance (maps directly to hardware), memory efficient (in-place changes), easy for beginners |
| Cons | Hard to maintain as codebase grows, concurrency bugs from shared mutable state |
| When | Operating systems, device drivers, embedded systems, game engines |

## 2. Functional Programming (FP)

**"Tell the computer WHAT to calculate"**

Mathematical functions, immutable data, no side effects. Data flows through pipelines of pure functions.

| Aspect | Detail |
|--------|--------|
| Pros | Highly predictable, concurrency-safe, short declarative code |
| Cons | High memory usage (copying vs mutating), steep learning curve |
| When | Big data, analytics, distributed systems, math-heavy projects |

## 3. Object-Oriented Programming (OOP)

**"Group data and behavior into OBJECTS"**

Models programs after real-world entities. Bundles data (properties) and actions (methods) into classes. Uses inheritance and encapsulation.

| Aspect | Detail |
|--------|--------|
| Pros | Great for modeling complex systems, code reuse via inheritance, large teams work independently on different objects |
| Cons | Over-engineering risk (deep class hierarchies), hidden state bugs |
| When | Enterprise software, web applications, GUIs, game development |

## The Hybrid Reality

Most modern languages (Python, JavaScript, Java) are **multi-paradigm**. Practical rule of thumb:

- **OOP** for structure and architecture (the "nouns")
- **Functional** for business logic and data transformations (the "verbs")
- **Imperative** for performance bottlenecks and direct hardware/filesystem access

## Related

- [[Functional programming]]
- [[Imperative and declarative programming]]
- [[Method scoping and namespaces]]

## Sources (verified)

- https://en.wikipedia.org/wiki/Programming_paradigm
