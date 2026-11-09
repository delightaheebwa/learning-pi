<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Self-Contained Components

> Related: [[Orthogonality]], [[Shy Code]], [[Global Data Avoidance]], [[ETC (Easier To Change)]]

## Definition

A **self-contained component** is independent, with a single, well-defined purpose. It doesn't reach into other components for data or behavior, and it doesn't expose its internals to the outside world.

> "We want to design components that are self-contained: independent, and with a single, well-defined purpose."

## Characteristics

- **Independent** — can be understood, tested, and deployed in isolation
- **Single purpose** — does one thing and does it well (aligned with the Single Responsibility Principle)
- **Well-defined interface** — the contract with the outside world is clear and minimal
- **Internally complete** — carries everything it needs; doesn't reach into shared state

## How it relates to other principles

| Principle | How it supports self-contained components |
|-----------|------------------------------------------|
| Orthogonality | Loose coupling between components |
| Shy Code | Objects manage their own state |
| Global Data Avoidance | No hidden dependencies on shared state |
| ETC | Self-contained components are easier to change in isolation |

## Testing self-contained components

A self-contained component is testable in isolation. If you need to mock half the system to unit-test a module, that module is not self-contained — it's too coupled.

## Practical benefits

- **Parallel development** — teams can work on different components simultaneously
- **Replaceability** — swap one component for another without cascading changes
- **Composability** — build larger systems from well-understood, independent pieces

## Sources

- General software-design principle (modularity / separation of concerns): https://en.wikipedia.org/wiki/Modularity_(programming)
- Law of Demeter (related): https://en.wikipedia.org/wiki/Law_of_Demeter
