<!-- provenance: status=synthesis | source=raw/sources/2026-11-06 - software-architecture - head-first-ch1.md (learner-supplied Ch.1 index entry) + 2026-11-06 session (Tutor-taught; no lesson file on disk) | verified-by=— | date=2026-11-06 | `## My understanding` block is status=learner-note (learner's words, verbatim) -->
# Software Architecture (intro)

**Insight:** software architecture is the part of a system that is **expensive and hard to change later** — the load-bearing structural commitments, judged by what it would cost to reverse them.

## The definition and what it rules in

- The discriminator is **cost of reversal**, not abstract importance. A logo can be important and cheap to change; the database engine, the service boundaries, or a synchronous-vs-asynchronous integration are commitments whose reversal arrives as a migration.
- Because the bill lands *later*, architecture is where deliberate up-front design effort is spent: the point of thinking hard now is that being wrong later is expensive rather than merely inconvenient.
- The claim is a **prediction about cost**, not a compliment. Calling a decision "architectural" says nothing about whether the decision is good; it says what class of decision it is.

## What the definition does not settle

- It does not say architecture is *everything structural* — code style and naming are structural and cheap to change.
- It does not, on its own, say anything about whether the system **does its job**. The reversal-cost definition is silent on that; the learner's v1 sentence couples the two, and whether that coupling holds is the open question below — **not settled here**.

## Open question — queued counterexample (not yet tested)

The learner's v1 tail claims: *with architecture → maintainable **and functional** software; otherwise → "non-functional (unreliable)"*. Two claims are fused there:

1. architecture buys **maintainability** (the standard framing);
2. the **absence** of architecture produces "non-functional (unreliable)" software — which reuses the requirements label as if it named a failure state (see [[Non-Functional (requirements label)]]).

Whether (2) survives, and how (1) should be stated, is **open**. A counterexample attack on both halves of the tail (a well-architected system that fails at its core job; a poorly-architected system that still does exactly what it was asked) is **queued for the resume** and was deliberately withheld at the pause. Treat the tail as suspect, not as established.

## My understanding
> status=learner-note — the learner's words, verbatim, 2026-11-06 (closed book; typos preserved).

> "I worked on Software architectire intro. my model is that software architecture is the part of software that is expensive and hard to change later. With it however, we can have maintainable and functional software otherwise we have software thats hard to mainiatin and non-fucntional software(unreliable)."

**Held solid (exit-ticket PASS, closed book, `sure`, 0 hints):** *"the part of software that is expensive and hard to change later"* — the reversal-cost reading.

**Suspect, untested (the tail):** *"With it however, we can have maintainable and functional software otherwise … non-functional (unreliable)"* — the tail fuses maintainability, functionality, and the "non-functional" label into one consequence of *having* architecture. Two independent repairs are candidates: (i) what "non-functional" names, and (ii) whether *function* can be attributed to architecture at all. Nothing in the session tested either half.

## Notes

- **Source limits:** the only citable source for the "non-functional" filing is the Ch.1 **index entry** the learner brought (`raw/sources/2026-11-06 - software-architecture - head-first-ch1.md`). The chapter body was never fetched or read, so no claim here rests on the book's wording beyond that entry. The architecture definition is the session's framing, retrieved closed-book by the learner.
- **Still unread / available as later material:** the rest of Ch.1 (the book's own architecture definition, its architecture properties, and its worked examples).
- **Cross-links:** [[Non-Functional (requirements label)]] · [[Prompt Engineering]] (the same interrogation loop's previous branch lesson)
