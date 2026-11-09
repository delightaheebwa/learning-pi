<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Imperative_programming ; https://en.wikipedia.org/wiki/Declarative_programming | verified-by=fact-check-agent | date=2026-10-26 -->

# Imperative and Declarative Programming

Two contrasting paradigms for expressing computation:

- **Imperative**: Explicitly details the **steps** to achieve a result.
- **Declarative**: States the **desired result**; the system figures out how.

## Imperative Languages

Programmers specify control flow in detail.

| Language | Notes |
|----------|-------|
| **C** | Quintessential imperative language; manual memory management |
| **Java** | Widely used, highly structured imperative language |
| **Python** | Multi-paradigm but commonly used imperatively |
| **JavaScript** | Multi-paradigm but often written imperatively |

## Declarative Languages/Frameworks

Programmers describe what they want, not how to get it.

| Tool | Domain |
|------|--------|
| **SQL** | State what data you want, not how to retrieve it |
| **React** | Declare UI as a function of state |
| **SwiftUI** | Declarative UI framework for Apple platforms |
| **Terraform/Kubernetes** | Declare desired infrastructure state |

## Why Imperative Dominates

Despite declarative approaches being more concise for many tasks, imperative programming remains the mainstream default for three reasons:

### 1. Hardware Mimicry

CPUs execute instructions imperatively (fetch-decode-execute cycle). Early programming languages were thin wrappers over machine code. Because decades of software history built on these early languages, the imperative model became the default foundation of modern computing.

### 2. Human Intuition

Humans naturally think imperatively when giving instructions. If you tell someone how to get to your house, you give step-by-step directions ("Turn left at the light, drive two miles, then turn right..."). This maps directly to imperative programming's step-by-step model.

### 3. Legacy and Ecosystem

Decades of libraries, tools, frameworks, and education have been built around imperative programming. Switching costs are enormous — even when declarative approaches would be better suited.

## When to Use Each

| Criterion | Imperative | Declarative |
|-----------|-----------|-------------|
| Need fine-grained control | ✓ | ✗ |
| Want conciseness/readability | ✗ | ✓ |
| Performance-critical path | ✓ | ✗ |
| Defining "what" not "how" | ✗ | ✓ |
| Complex state management | ✓ | ✗ |

## Related

- [[Compiler]] — compilers translate imperative (and declarative) source to machine code
- [[Runtime]] — declarative systems require sophisticated runtimes to resolve "how"

---

*Source: `raw/sources/2026-06-04 - programming-paradigms-expressions-closures-arguments.md`*

## Sources
- Wikipedia, "Imperative programming": https://en.wikipedia.org/wiki/Imperative_programming
- Wikipedia, "Declarative programming": https://en.wikipedia.org/wiki/Declarative_programming
