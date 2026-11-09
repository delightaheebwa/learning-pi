<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Automatic_differentiation | verified-by=fact-check-agent | date=2026-10-26 -->

# Automatic differentiation

Automatic differentiation is a way to compute exact derivatives of a program by decomposing it into basic operations and applying local derivative rules through the chain rule.

## Core idea

- Break the program into simple ops like addition and multiplication.
- Attach exact derivative rules to each op.
- Chain those local rules through the program graph.

Unlike symbolic differentiation, automatic differentiation works on the executed program. Unlike finite differences, it does not approximate the derivative.

## Compared with other methods

- **Symbolic differentiation** manipulates algebraic expressions directly. It can produce exact formulas, but those formulas can grow very large.
- **Numerical differentiation** uses finite differences. It is simple, but it introduces truncation and round-off error.
- **Automatic differentiation** applies calculus rules directly to the operations in the program, so it stays exact to machine precision without building symbolic expressions or using finite differences.

## Two modes

### Forward mode

- Sweep left-to-right.
- As each intermediate value is computed, also propagate its sensitivity forward.
- This is useful when there are few inputs and many outputs.
- Seeding the input tangent with a direction vector \(r\) gives a Jacobian-vector product \(J_f(x)r\), which is the same quantity as a directional derivative.

### Reverse mode

- First run a forward pass to compute and store intermediates.
- Then run a backward pass right-to-left to accumulate partial derivatives.
- This is useful when there are many inputs and one scalar output, which is why it underlies [[Backpropagation]].

## Why it matters

Building on local derivative rules, automatic differentiation makes gradients practical for large models and deep neural networks. Manual differentiation would be too error-prone and slow.

## Related pages

- [[Backpropagation]]
- [[Jacobian matrix]]
- [[Jacobian-vector product]]
- [[Directional derivative]]
- [[Total differential]]

## Sources
- Wikipedia — Automatic differentiation: https://en.wikipedia.org/wiki/Automatic_differentiation
