# 2026-06-06 - Waterbed Theory & Runtime Components

## Waterbed Theory

Source: [wiki.c2](http://wiki.c2.com/?WaterbedTheory)

Waterbed Theory says that in complex systems like programming languages, tools, or software designs, you cannot eliminate complexity; if you "push it down" in one place, it will "bulge" somewhere else, much like pressing on a waterbed.

**Core idea**: The article explains that certain systems have an irreducible minimum of complexity. The goal is not to eliminate complexity but to place it where it is most manageable and least harmful for the typical user. Good design acknowledges these trade-offs and tries to position complexity where it does the least damage — hiding it behind defaults that work well for common cases, while still making it accessible when those defaults fail.

## Components of a Runtime

The runtime is comprised of two distinct components:

- **Engine** — the executor that reads and runs code (e.g., JS engine like V8, Java's JVM, CPython). This is the "musician" that plays the notes.
- **Environment** — the surrounding context and capabilities provided (e.g., browser APIs like `document`, Node.js APIs like `fs`, Python stdlib). This is the "concert hall" that provides the acoustics and stage.

**Musicians-and-concert-hall metaphor**: The musicians (interpreter/VM) read and play the notes, while the hall provides the acoustics and stage (the environment) for the performance to happen.
