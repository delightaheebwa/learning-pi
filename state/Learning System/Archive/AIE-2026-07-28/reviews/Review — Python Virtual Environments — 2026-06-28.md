# Review — Python Virtual Environments

**Date:** 2026-06-28
**Track:** AI Engineering (aie)
**Status:** developing — kept interval (3d reset)

## Result

Understood `uv add` correctly — adds packages to pyproject.toml and updates lockfile. But `uv sync` was wrong: it reads existing pyproject.toml/lockfile and syncs the venv to match, not creates them. CUDA gotcha: PyTorch's CUDA version must match what the NVIDIA driver supports, or PyTorch falls back to CPU silently (10x slowdown). The `nvidia-smi` check is key.

## Action

Keep interval. Retest in 3 days.
