# Session — Chain Rule & Autodiff (Lessons 1–2) — 2026-07-08

**Date:** 2026-07-08 (Wednesday)  
**Track:** AI Engineering (aie)  
**Mission:** Chain Rule & Autodiff  
**Source:** teach/lessons/0001-chain-rule-and-computational-graphs.html, teach/lessons/0002-forward-vs-reverse-autodiff.html

## Concepts Ingested

| # | Concept | Status | Next Review |
|---|---------|--------|-------------|
| 1 | Computational Graphs (Autodiff) | developing | 2026-07-11 |
| 2 | Two-Pass Autodiff Algorithm | developing | 2026-07-11 |
| 3 | Chain Rule Decomposition | developing | 2026-07-11 |
| 4 | Forward-Mode Autodiff | developing | 2026-07-11 |
| 5 | Reverse-Mode Autodiff & Backprop | developing | 2026-07-11 |

## Summary

Lesson 1 established computational graphs as the DAG data structure for autodiff (nodes = values, edges carry data forward / gradients backward), the chain rule as local decomposition (each node × upstream gradient), and the two-pass algorithm. Lesson 2 covered three differentiation approaches (numerical, symbolic, automatic) and the decisive forward-vs-reverse mode tradeoff: NNs have millions of weight inputs → 1 scalar loss output, so reverse mode (1 backward pass for all gradients) is the only practical choice.

## Wiki Pages

- [[Computational Graphs (Autodiff)]]
- [[Two-Pass Autodiff Algorithm]]
- [[Chain Rule Decomposition]]
- [[Forward-Mode Autodiff]]
- [[Reverse-Mode Autodiff & Backprop]]
