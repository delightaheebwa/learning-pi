# Session — Autograd Engine (Lessons 3–4) — 2026-07-09

**Date:** 2026-07-09 (Thursday)  
**Track:** AI Engineering (aie)  
**Mission:** Chain Rule & Autodiff  
**Source:** teach/lessons/0003-value-class-and-operations.html, teach/lessons/0004-backward-pass-and-topological-sort.html

## Concepts Ingested

| # | Concept | Status | Next Review |
|---|---------|--------|-------------|
| 1 | Value Class Architecture | developing | 2026-07-12 |
| 2 | Local Autograd Derivative Rules | developing | 2026-07-12 |
| 3 | Gradient Accumulation (+=) | developing | 2026-07-12 |
| 4 | Topological Sort for Backprop | developing | 2026-07-12 |

## Summary

Lesson 3 built the Value class skeleton (data, grad, _prev as graph, _backward, _op), then implemented operation backward rules (add, mul, pow, tanh, relu, exp, log) with the composition pattern for sub/div. Lesson 4 implemented the `backward()` method using topological sort — post-order DFS reversed to guarantee every node receives all incoming gradient contributions before propagating. Tested with a realistic expression (x·y + tanh(x²)) and multi-path gradient summation example.

## Wiki Pages

- [[Value Class Architecture]]
- [[Local Autograd Derivative Rules]]
- [[Gradient Accumulation (+=)]]
- [[Topological Sort for Backprop]]
