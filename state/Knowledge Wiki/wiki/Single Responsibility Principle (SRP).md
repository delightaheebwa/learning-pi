<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Single Responsibility Principle (SRP)

One of the SOLID principles of object-oriented design.

> A piece of code (class or method) should do one thing and do it well.

## Core idea

When a method or class has multiple responsibilities, it becomes harder to understand, test, and modify. Splitting responsibilities means each piece has a single, crisp job.

## Example from tokenizer design

Given two `addToken` methods:

- **Short version**: Only responsibility — provide a clean default input (null) for simple tokens. Zero text processing.
- **Long version**: Only responsibility — take inputs, extract text substring, bundle into a Token object, and save.

By splitting them, the long version avoids `if (literal == null)` checks everywhere. Each method has one job.

## Why it matters

- Changes to one responsibility don't risk breaking another
- Each method is easier to test in isolation
- Code becomes more readable — each piece's purpose is obvious

## Sources

- Single-responsibility principle (Wikipedia): https://en.wikipedia.org/wiki/Single-responsibility_principle
- SOLID (Wikipedia): https://en.wikipedia.org/wiki/SOLID

## Related

- [[DRY Principle]] — distinct but complementary: SRP is about one thing per unit, DRY is about one representation per piece of knowledge
- [[Delegation Pattern]] — SRP often leads to delegation (split responsibility, then delegate)
- [[Orthogonality]] — independent, self-contained components support SRP
