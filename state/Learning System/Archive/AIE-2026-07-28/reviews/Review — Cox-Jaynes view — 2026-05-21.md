# Review — Cox-Jaynes view — 2026-05-21

**Concept:** Cox-Jaynes view  
**Status after review:** developing  
**Next review:** 2026-05-24 (3 days)

## Question Asked

What does the Cox-Jaynes theorem derive the rules of probability from, and what are the three consistency conditions?

## Answer Given

User described basic probability properties: probabilities sum to 1, increased chance in one means decreased elsewhere, probabilities map to real-world entities.

## Evaluation

The answer is incorrect. These are properties of probability, not the Cox desiderata. The Cox-Jaynes approach derives probability rules from qualitative requirements for rational plausible reasoning.

## Correct Answer

The three Cox desiderata:

1. **Plausibility is a real number** — the plausibility of a proposition given evidence is represented by a real number that increases monotonically with plausibility.
2. **Consistency with logic** — if you can reach the same conclusion via two different reasoning paths, both must yield the same result. This forces the product rule: P(A ∧ B | C) = P(A | B,C) × P(B | C).
3. **Use all available information** — equivalent states of knowledge must lead to equivalent plausibility assignments; don't discard relevant evidence.

## Notes

User was headed in a reasonable direction (thinking about axioms) but confused the standard Kolmogorov axioms with the Cox desiderata. The key distinction: Cox starts from *qualitative reasoning principles*, not from frequencies or set measures.
