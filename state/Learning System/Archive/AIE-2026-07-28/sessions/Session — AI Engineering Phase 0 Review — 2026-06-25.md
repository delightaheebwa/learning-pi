# Session — AI Engineering Phase 0 Review

**Date:** 2026-06-25
**Topic:** Phase 0 concepts review (spaced repetition)
**Source Context:** AI Engineering from Scratch

## Concepts Covered

| Concept | Result | Next Review |
|---------|--------|-------------|
| API Key Security | Close — missed API key as auth piece in universal pattern | 2026-06-28 (3d) |
| Jupyter Notebook Workflow | Close — missed AI/ML-specific hidden state risk | 2026-06-28 (3d) |
| Python Virtual Environments | Had gaps — uv workflow details, CUDA driver vs toolkit gotcha | 2026-06-28 (3d) |

## Key Corrections Made

1. **Universal API pattern**: endpoint + **API key** + request + response — not just URL
2. **Hidden state risk in AI/ML**: silent overwrites of model/data variables can waste hours of training
3. **uv workflow**: modern approach is `uv add` + `uv sync`, not just `uv pip install`
4. **CUDA gotcha**: driver is system-level, toolkit is package-level — mismatch → silent CPU fallback

## Open Questions

- None

## Final Statuses

- All three concepts remain at `developing` with 3d intervals
- 3 reviews completed, within 5-cap
