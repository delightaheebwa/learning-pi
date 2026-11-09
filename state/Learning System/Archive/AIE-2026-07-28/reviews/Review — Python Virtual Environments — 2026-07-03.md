# Review — Python Virtual Environments

**Date:** 2026-07-03
**Track:** AI Engineering (aie)
**Concept:** Python Virtual Environments
**Status:** developing — kept interval

## Performance

- **Missed:** `uv sync` installs from pyproject.toml (user thought it updates pyproject.toml; that's `uv add`)
- CUDA gotcha: correctly identified version mismatch, but missed the venv-specific nuance (CPU-only wheel or wrong CUDA wheel when `pip install torch` inside a venv)

## Verdict

Still circling these two points. Kept interval.

**Next review:** 2026-07-06
