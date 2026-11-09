<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Decorator Pattern

> Related: [[Strategy Pattern]], [[Shy Code]]

## Definition

The **Decorator Pattern** is a structural design pattern that adds functionality to objects without modifying their original code. Instead of changing the class, you wrap it in a decorator object that layers on new behavior while preserving the original interface.

## Core idea

> "Adding functionality to things without changing them."

This is a direct application of the Open/Closed Principle — open for extension, closed for modification.

## How it works

1. You have an existing object (the *component*)
2. You create a wrapper (the *decorator*) that holds a reference to the component
3. The decorator implements the same interface as the component
4. Before or after delegating to the component, the decorator adds its own behavior

## Example (conceptual)

```python
# Original
plain_coffee = Coffee()

# Decorated — same interface, extra behavior
milk_coffee = MilkDecorator(plain_coffee)
sugar_milk_coffee = SugarDecorator(milk_coffee)
```

## When to use

- When you need to add behavior at runtime, not compile time
- When subclassing would create an explosion of combinations (e.g., Coffee, CoffeeWithMilk, CoffeeWithSugar, CoffeeWithMilkAndSugar...)
- When you can't or shouldn't modify the original class (third-party code, or to preserve the Single Responsibility Principle)

## Sources

- Wikipedia — Decorator pattern: https://en.wikipedia.org/wiki/Decorator_pattern
- Gamma et al., *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF): https://en.wikipedia.org/wiki/Design_Patterns
