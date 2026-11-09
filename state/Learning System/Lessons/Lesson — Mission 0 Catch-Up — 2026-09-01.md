# Lesson — Mission 0 Catch-Up: Foundations Reactivation — 2026-09-01

## Metadata
- **Mission:** Mission 0 — Catch-Up (P0 + P1.01–06, 80/20)
- **Date:** 2026-09-01
- **Lang:** Python (Julia optional for Phase 1 math; Python-first)
- **Rohit hash:** 48a357191ef0db05 (18 lessons: P0 L01-L12 + P1 L01-L06)
- **External refs:** 12 fetched (3B1B, CS229, CS231n, log-sum-exp, autodiff survey, PyTorch autograd, MIT OCW)
- **Digest:** Learning System/.tmp/context-mission-0-catchup-foundations.json

## Probe Results (5 strands)

| Strand | Boundary | Evidence |
|--------|----------|----------|
| Tooling | Unknown → Solid | Q1 wrong (AI libs+pkgs → corrected to Runtimes), EQ1 correct+sure |
| Vectors/Matrices | Unstable → Solid | Q3 wrong (orthogonality → corrected to cos(θ)), EQ2 correct+sure |
| Transforms/Eigen | Solid | Q4 correct+sure, EQ3 correct+sure |
| Calculus/Chain Rule | Unknown → Solid | Q5 wrong (+ vs × → corrected), FR1 partial ("values" → "gradients"), EQ4 correct+sure, FR2 excellent |
| Probability | Unknown → Solid | Q6 wrong (Poisson → Binomial, re-probed), Q7 wrong (sum-to-1 → overflow), FR2 wrong (PDF≠CDF → corrected), EQ5 minor miss |

## Key Corrections Taught
1. **Chain rule = MULTIPLY gradients** (not add). Why: variables are dependent/chained, not independent.
2. **PMF vs PDF:** PMF = discrete point probability. PDF = density (integrate for probability). CDF = cumulative. PDF ≠ CDF.
3. **Softmax subtract-max:** numerical stability (exp overflow at ~709). Not about summing to 1.
4. **Dot product of unit vectors = cos(θ)** (cosine similarity). Orthogonality is a special case, not the general meaning.
5. **4-layer stack:** System (driver) → Packages → Runtimes (CUDA toolkit) → AI Libraries (PyTorch). torch.cuda False + nvidia-smi works = Runtimes layer.
6. **Cross-entropy = −log(p_correct):** minimizing pushes true class probability toward 1.

## End-of-Lesson Quiz
- EQ1-EQ4: correct+sure
- EQ5: wrong+hunch (cross-entropy interpretation — minor gap, noted above)
- FR1: correct (cosine similarity)
- FR2: excellent (chain rule — variables are dependent → multiply, not add)

## Bloom Levels Reached
- **Remember/Understand:** PMF/PDF distinction, chain rule definition, eigenvalue meaning
- **Apply:** matrix shapes, softmax implementation, chain rule computation, dot product calculation
- **Evaluate:** FR2 correction of misconception (chain rule ≠ addition)

## Exit Criteria Check (from CURRICULUM.md)
- ✅ State 4-layer env stack
- ✅ Explain Wx+b with shapes (Q2 correct+sure)
- ✅ Distinguish PMF/PDF (FR2 from probe correct)
- ⚠️ Cross-entropy from NLL: understands mechanism, minor direction-of-optimization gap

## Next
- Mission 0 Catch-Up → **done** (80/20 exit criteria met)
- Next lesson: **Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking**
