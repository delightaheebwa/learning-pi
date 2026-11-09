<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Expression_(computer_science) ; https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements | verified-by=fact-check-agent | date=2026-10-26 -->

# Expressions and Statements

The fundamental distinction between expressions and statements is about their **purpose**:

- **Expression**: Its main job is to **produce a value**.
- **Statement**: Its main job is to **produce an effect** (side effects, control flow).

## Expression Statements

An expression followed by a semicolon (`;`) **promotes** the expression to statement-hood. This is called an **expression statement** — you take something that computes a value and turn it into a standalone action.

## Examples

```javascript
// Expression: produces a value
x + 5
getUserName()

// Statement: produces an effect
if (x > 5) { ... }
for (let i = 0; i < 10; i++) { ... }

// Expression statement: expression used as a statement
console.log("hello");   // the expression console.log(...) followed by ;
x = 5;                  // the assignment expression followed by ;
```

## Key Insight

Many languages blur the line by allowing expressions where statements are expected (expression-oriented languages like Rust). But conceptually, the distinction is about **intent**: computing a value vs executing an action.

## Related

- [[Imperative and declarative programming]] — imperative code is built from statements that produce effects
- [[Compiler]] — compilers must distinguish expressions and statements during parsing

---

*Source: `raw/sources/2026-06-04 - programming-paradigms-expressions-closures-arguments.md`*

## Sources

- https://en.wikipedia.org/wiki/Expression_(computer_science)
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements
