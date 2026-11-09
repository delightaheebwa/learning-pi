<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Closures

A **closure** is the combination of a function bundled together with references to its surrounding state. It allows inner functions to access variables from outer functions **even after the outer function has finished executing**.

## The Problem

In traditional programming, when a function finishes running, all its local variables are cleaned up and inaccessible. A closure defies this — the inner function "remembers" and retains access to the outer function's variables.

## The Backpack Analogy

When an inner function is returned from an outer function, it packs the outer variables into its **backpack** and carries them along:

```javascript
function makeCounter() {
    let count = 0;                      // outer variable
    return function() {                 // inner function (closure)
        count += 1;                     // accesses "count" from backpack
        return count;
    };
}

const counter = makeCounter();
console.log(counter());  // 1
console.log(counter());  // 2  — count survives between calls!
console.log(counter());  // 3
```

`makeCounter()` has already finished running, but `counter()` still has access to `count` because the inner function packed it in its backpack before leaving.

## Key Prerequisites

- **Block scope**: Variables exist only within the `{ }` block where they were defined. Closures depend on lexical scoping.
- **First-class functions**: Functions that can be assigned to variables, passed as arguments, and returned from other functions — without this, closures can't exist.
- **Nested functions**: A function defined inside another function.

## Technical Precision

Today, people often casually call any function passed around a "closure." Technically, it is only a closure if it **actually grabs and holds onto a variable from outside its own body**. A function that only uses its own parameters and local variables is just a function — not a closure.

## Why Closures Matter

Closures are the foundation of many patterns:

- **Data hiding / private state** — The `count` variable in the example above is private; nothing outside can modify it directly
- **Callback functions** — Event handlers and callbacks that "remember" context
- **Partial application / currying** — Functions that pre-bind some arguments
- **Module pattern** — Encapsulating state and behavior

## Related

- [[Arguments and parameters]] — closure parameters vs outer function parameters
- [[Runtime]] — closures require a runtime that supports capturing environment state
- [[Imperative and declarative programming]] — closures are used in both paradigms

---

*Source: `raw/sources/2026-06-04 - programming-paradigms-expressions-closures-arguments.md`*

## Sources

- Closures (MDN): https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures
- First-class functions: https://en.wikipedia.org/wiki/First-class_function
