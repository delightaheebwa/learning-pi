# Review — Python Virtual Environments

**Date:** 2026-06-25
**Concept:** Python Virtual Environments
**Status:** Developing (kept interval)

## Retrieval Performance

**Question:** What problem do virtual environments solve, and how does `uv` specifically differ from `venv` or `conda` in terms of speed and configuration? Also, what's the gotcha with CUDA version matching across environments?

**Result:** Had gaps — knew core purpose and that uv is faster. Was unclear on uv's modern workflow (`uv add` + `uv sync`), its Rust-based 10-100x speed advantage, and didn't know the CUDA driver vs toolkit gotcha.

## Correction

1. **uv specifics**: Written in Rust, 10-100x faster, global content-addressed cache, modern workflow is `uv add` + `uv sync` (like pnpm/npm), manages Python versions too (`uv python install 3.12`)
2. **CUDA gotcha**: CUDA has two parts — **driver** (system-level, handles GPU comms) and **toolkit** (libraries frameworks link against). Install PyTorch for CUDA 12.x on a system with only CUDA 11.x driver → **silent CPU fallback**, no error

## Next Review: 2026-06-28
