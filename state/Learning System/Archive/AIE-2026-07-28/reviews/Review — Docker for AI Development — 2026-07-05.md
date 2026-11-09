# Review — Docker for AI Development
**Date:** 2026-07-05
**Track:** AI Engineering (aie)
**Interval:** 3d (reset) → 3d (kept)

## Result: ⚠️ Mostly right — Kept at 3d

**Prompt:** Walk me through the Docker setup for an AI training environment that needs GPU access. What's the key tool, what flags do you need, and what's the recommended base image strategy?

**Response:**
- Base image with PyTorch and CUDA pre-installed ✅
- `--gpus-all` in Dockerfile ❌ (should be `--gpus all` at `docker run`, not in Dockerfile)
- NVIDIA CUDA Toolkit enables GPU passthrough ❌ (should be NVIDIA Container Toolkit / nvidia-ctk)

**Evaluation:** Got the base image strategy right. Knew `--gpus` concept but syntax and what enables GPU passthrough were off. Keeping current interval.

**Next review:** 2026-07-08
