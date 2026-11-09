# Review — Docker for AI Development

**Date:** 2026-07-02
**Track:** AI Engineering (aie)
**Concept:** Docker for AI Development
**Source:** ai-engineering-from-scratch Phase 0

## Performance

**Retrieval attempt:** Knew `pytorch/pytorch:2.x.x-cuda12.x-cudnn8-runtime` as base image. Couldn't recall the GPU passthrough mechanism — guessed "nvlink" (wrong).

### Correct GPU passthrough:
- **NVIDIA Container Toolkit** installed on host
- Runtime flag: `--gpus all` (or `--gpu device=0`)
- Without this, container can't see GPU even with CUDA libraries inside

### Dockerfile approach:
```dockerfile
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime
RUN pip install your-dependencies
COPY . /workspace
WORKDIR /workspace
CMD ["python", "train.py"]
```
Run: `docker run --gpus all -v /data:/data your-image`

**Verdict:** ❌ Reset to 3d
**Next review:** 2026-07-05
