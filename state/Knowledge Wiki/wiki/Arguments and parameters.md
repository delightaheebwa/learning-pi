<!-- provenance: status=verified | source=https://developer.mozilla.org/en-US/docs/Glossary/Parameter (MDN) | verified-by=fact-check-agent | date=2026-10-26 -->

# Arguments and Parameters

Although often used interchangeably in casual conversation, **argument** and **parameter** refer to distinctly different things.

## Definitions

| Term | Definition |
|------|-----------|
| **Parameter** | The **variable** listed in the function definition that receives the passed value |
| **Argument** | The **actual value** passed to the function at the call site |

## Visual Distinction

```javascript
//           ↓ parameter ↓
function greet(name) {
    console.log("Hello, " + name);
}

//            ↓ argument ↓
greet("Alice");
```

- `name` is the **parameter** — a placeholder variable in the function definition
- `"Alice"` is the **argument** — the concrete value supplied when calling the function

## Key Context

This distinction becomes especially important when discussing:

- **Local functions**: Functions defined inside other functions have their own parameter scopes
- **First-class functions**: When functions are passed as arguments themselves, parameters can hold function references
- **Closures**: Inner functions capture (close over) the **parameters** of their enclosing function

## Common Pitfall

Confusing "passing parameters" with "passing arguments" — you pass **arguments** to a function; the function receives them as **parameters**.

## Related

- [[Closures]] — closures capture the parameters of outer functions as part of their backpack
- [[Expressions and statements]] — function calls are expressions; the arguments are the expressions evaluated at the call site

---

*Source: `raw/sources/2026-06-04 - programming-paradigms-expressions-closures-arguments.md`*

## Sources
- MDN Glossary — Parameter: https://developer.mozilla.org/en-US/docs/Glossary/Parameter
- MDN Glossary — Argument: https://developer.mozilla.org/en-US/docs/Glossary/Argument
