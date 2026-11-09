<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Strategy Pattern

> Related: [[Decorator Pattern]], [[DRY Principle]], [[Orthogonality]]

## Definition

The **Strategy Pattern** is a behavioral design pattern (from the Gang of Four) that defines a family of interchangeable algorithms, encapsulates each one in its own class, and makes them interchangeable via a common interface.

## The problem it solves

> "Often you'll come across a set of functions that all look similar — maybe they share common code at the start and end, but each has a different central algorithm."

When functions share structure but differ in their core algorithm, you get **duplicate code** — a symptom of structural problems. Copy-pasting the common scaffolding around each variant is brittle.

## How Strategy Pattern fixes it

1. Extract the varying algorithm into a common interface
2. Create a concrete class for each variant
3. The context (caller) holds a reference to a strategy and delegates to it
4. Strategies can be swapped at runtime

## Conceptual example

```
Instead of:
  function sort_quick(arr) { ... common setup ... quick_sort(arr) }
  function sort_merge(arr) { ... same setup ... merge_sort(arr) }
  function sort_bubble(arr) { ... same setup ... bubble_sort(arr) }

Use:
  class Sorter:
      def __init__(self, strategy):
          self.strategy = strategy   # strategy interface

      def sort(self, arr):
          # Common setup once
          return self.strategy.sort(arr)

  # Strategies: QuickSort, MergeSort, BubbleSort — all implement sort()
```

## When to use

- Multiple algorithms differ only in their behavior, not their structure
- You need to switch algorithms at runtime
- A class has a large conditional (if/switch) picking between behaviors — each branch is a candidate strategy
- You want to avoid exposing complex algorithm-specific data structures

## Sources

- Refactoring Guru — Strategy pattern: https://refactoring.guru/design-patterns/strategy
- Wikipedia — Strategy pattern: https://en.wikipedia.org/wiki/Strategy_pattern
- Gamma, Helm, Johnson & Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF), 1994
