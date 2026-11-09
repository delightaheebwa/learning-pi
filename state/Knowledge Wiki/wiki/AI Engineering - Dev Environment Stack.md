<!-- provenance: status=verified | source=https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/01-dev-environment/docs/en.md ; https://docs.astral.sh/uv/ | verified-by=fact-check-agent | date=2026-10-26 -->

# AI Engineering — Dev Environment Stack

> The foundation of all AI engineering work: a four-layer environment stack that every engineer needs to set up once, correctly.

## The Four-Layer Stack

All AI engineering environments decompose into four layers, built bottom-up:

```
4. AI/ML Libraries — PyTorch, JAX, transformers, etc.
3. Language Runtimes — Python 3.11+, Node 20+, Rust, Julia
2. Package Managers — uv, pnpm, cargo, juliaup
1. System Foundation — OS, shell, git, editor, GPU drivers
```

Each layer depends on the one below it. Install in order, bottom to top.

## Key Tools

- **uv** — 10-100x faster pip replacement; handles Python versions, virtual environments, and dependency resolution in one CLI. Preferred over raw pip.
- **fnm** — Fast Node Manager for installing and switching Node.js versions.
- **pnpm** — Fast, disk-efficient Node.js package manager.
- **Rustup** — Toolchain installer for Rust (performance-critical AI systems work).

## GPU Verification

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

If CUDA is available, you have GPU acceleration. If not, most lessons work on CPU; use Google Colab for GPU-heavy work. (On Apple Silicon use MPS; `torch.cuda.is_available()` is expected to be `False` there.)

The lesson installs Python 3.12 and Node 22 (via `fnm`); the diagram's "3.11+ / 20+" are minimums, not the pinned versions.

## Sources

- Rohit, *AI Engineering from Scratch* — Phase 0, Lesson 01 "Dev Environment" (four-layer diagram, uv/fnm/pnpm/rustup, GPU check): https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/01-dev-environment/docs/en.md
- uv docs ("10-100x faster than pip"): https://docs.astral.sh/uv/
- fnm: https://github.com/Schniz/fnm · pnpm: https://pnpm.io/ · rustup: https://rustup.rs/
- PyTorch CUDA/MPS notes: https://pytorch.org/docs/stable/notes/cuda.html

## Related
- [[Python Virtual Environments]]
- [[GPU Computing]]
- [[Docker for AI Development]]
