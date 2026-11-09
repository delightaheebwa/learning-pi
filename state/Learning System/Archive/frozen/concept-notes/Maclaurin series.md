# Maclaurin Series

> **Status:** mastered | **Domain:** Calculus Foundations
> **Prerequisites:** Taylor series, center at 0

## Definition

A Maclaurin series is a **Taylor series centered at \( a = 0 \)**:

\[
f(x) = \sum_{k=0}^{\infty} \frac{f^{(k)}(0)}{k!} x^k
\]

## Key Insight

The Maclaurin series is not a separate concept from the Taylor series — it's the same formula with \( a = 0 \). The distinction in naming is historical (Colin Maclaurin studied this special case extensively).

## Classic Examples

| Function | Maclaurin Series |
|----------|-----------------|
| \( e^x \) | \( 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots \) |
| \( \sin x \) | \( x - \frac{x^3}{3!} + \frac{x^5}{5!} - \cdots \) |
| \( \cos x \) | \( 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \cdots \) |
| \( \frac{1}{1-x} \) | \( 1 + x + x^2 + x^3 + \cdots \) (geometric series, \( |x| < 1 \)) |

## Recognition Pattern

If a series has \( x^k \) terms (not \( (x-a)^k \)), and the coefficients are derivatives evaluated at 0 divided by \( k! \), it's a Maclaurin series.

## Related Concepts

- [[Taylor series]] — the general case centered at any \( a \)
- [[Derivative]] — powers the coefficient computation
