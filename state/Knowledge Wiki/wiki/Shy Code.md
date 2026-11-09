<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Shy Code

> Related: [[Self-Contained Components]], [[Global Data Avoidance]], [[Orthogonality]]

## Definition

**Shy code** follows the principle that objects should limit their interactions to a small set of immediate collaborators. An object should only talk to its close friends, not to strangers or friends-of-friends. This is formalized as the **Law of Demeter** (LoD).

## Core rule

> "If an object needs changing, change it from within."

Don't reach into other objects to change their internal state — ask them to change themselves. Each object is responsible for its own state.

## The Law of Demeter in practice

A method `m` of object `O` should only call methods of:
1. `O` itself
2. `m`'s parameters
3. Any objects created within `m`
4. `O`'s direct component objects

**Violation (reaching through):**
```python
customer.wallet.remove_cash(amount)  # reaching into wallet
```

**Shy alternative:**
```python
customer.pay(amount)  # customer handles its own wallet
```

## Why shy code works

- **Lowers coupling** — you're not tied to the internal structure of other objects
- **Makes refactoring safe** — change a class's internals without breaking callers
- **Self-documenting** — the public API tells you everything an object can do
- **Encapsulation preserved** — internal state stays internal

## Sources

- Law of Demeter (Wikipedia): https://en.wikipedia.org/wiki/Law_of_Demeter
- The Pragmatic Programmer (Hunt & Thomas): https://en.wikipedia.org/wiki/The_Pragmatic_Programmer
