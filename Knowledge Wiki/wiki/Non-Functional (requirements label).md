<!-- provenance: status=synthesis | source=raw/sources/2026-11-06 - software-architecture - head-first-ch1.md (learner-supplied Ch.1 index entry) + 2026-11-06 session repair close | verified-by=— | date=2026-11-06 | `## My understanding` block is status=learner-note (learner's words, verbatim) -->
# Non-Functional (requirements label)

**Insight:** "non-functional" is a **requirements category**, not a failure state. Functional requirements say *what the system does*; non-functional requirements say *how well it behaves while doing it* — the quality attributes (reliability, performance, availability, security, scalability). A system with an unmet non-functional requirement is a system that **runs and behaves badly**, not one that never runs.

## The two readings

| Reading | What it names | Kind of thing |
|---|---|---|
| "nothing is functioning / the system never starts" | a deployment failure — a dead system | the **system's state** |
| "non-functional" (as filed under requirements) | an expectation about behaviour while running | a **kind of requirement** |

- The collision is lexical: *not functioning* (a state of the system) vs *non-functional* (a class of requirement). They share words, not objects.
- The index placement is the tell: Head First Software Architecture Ch.1 files "non-functional" **under requirements** — which is where a *kind of requirement* files, not where an outage files. The label answers "how well?", not "is it up?".
- Why the misreading matters: using "non-functional" to mean "broken" turns a missed quality target into an outage story, and hides the real engineering situation — the requirement was never met, rather than the system having fallen over.

## My understanding
> status=learner-note — the learner's words, verbatim, 2026-11-06 (fresh-surface repair close; typos preserved).

> "so nothing is funcioning means not running completely while non-functional means unreliable"

**What it fixes (repair close PASS):** the discrimination itself — "nothing is functioning" is the *not-running* case, and "non-functional" is a different thing. The two readings are separated in the learner's own words, which is exactly what the first free-recall attempt could not do.

**Missing piece (annotation, not a rewrite):** the learner equates *non-functional* with *unreliable*. Reliability is **one** non-functional requirement; the label covers the quality-attribute family — performance/latency, availability, security, scalability, maintainability, observability. "Unreliable" is a correct *instance* promoted to the definition.

**Source framing:** the requirements filing comes from the Ch.1 index entry the learner surfaced; no chapter body was read in this session.

## Notes

- **Open:** which quality attributes the learner can generate unprompted — only "unreliable" has surfaced so far. The first review item should press for the family, not the single instance.
- **Cross-links:** [[Software Architecture (intro)]] · [[Bits vs Nats]] (the same "one label, two objects" failure shape: a unit question read as a model question)
