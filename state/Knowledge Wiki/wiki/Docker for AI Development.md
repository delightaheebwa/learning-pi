<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Docker for AI Development

> Containers make "works on my machine" a thing of the past — critical for AI projects with complex dependency chains.

## Why AI Needs Docker

1. **GPU drivers are fragile** — CUDA 12.4 code doesn't run on CUDA 11.8. Docker isolates the CUDA toolkit inside the container while sharing the host GPU driver.
2. **Model weights are large** — A 7B model is 14 GB in fp16. Docker volumes mount models from the host so you don't re-download.
3. **Multi-service architectures are common** — Inference server + vector database + web frontend. Docker Compose orchestrates all with one command.

## Key Vocabulary

| Term | Meaning |
|------|---------|
| **Image** | A read-only template (your recipe). Built from a Dockerfile. |
| **Container** | A running instance of an image (your kitchen). |
| **Dockerfile** | Instructions to build an image, layer by layer. |
| **Volume** | Persistent storage that survives container restarts. |
| **docker-compose** | Define multi-container applications in YAML. |

## Base Image Strategy

| Image | Use | Size |
|-------|-----|------|
| `nvidia/cuda:12.4.1-devel-ubuntu22.04` | Building packages needing nvcc (flash-attn, bitsandbytes) | ~4 GB |
| `nvidia/cuda:12.4.1-runtime-ubuntu22.04` | Running pre-built code | ~1.5 GB |
| `pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime` | PyTorch pre-installed | ~3.6 GB |
| `python:3.12-slim` | CPU-only inference, lightweight tools | ~150 MB |

## NVIDIA Container Toolkit

Exposes host GPUs to Docker containers. Test with:

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## Volume Mounts for AI

```bash
docker run --rm -it --gpus all \
    -v $(pwd):/workspace \      # mount code
    -v ~/models:/models \        # mount models (persist!)
    -v ~/datasets:/data          # mount datasets
    ai-dev python -c "import torch; print(torch.cuda.is_available())"
```

Volume mounts are critical — without them, your 14 GB models vanish when the container stops.

## Docker Compose Pattern

A RAG app needs an inference container and a vector database:

```yaml
services:
  ai-dev:
    build: .
    volumes:
      - ../../../:/workspace
      - ~/models:/models
    ports:
      - "8888:8888"
    command: jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

  qdrant:
    image: qdrant/qdrant:v1.12.5
    ports:
      - "6333:6333"
```

Services reach each other by name (`http://qdrant:6333`).

## Sources

- Docker docs — NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/
- Docker Hub — nvidia/cuda: https://hub.docker.com/r/nvidia/cuda
- Docker Hub — pytorch/pytorch: https://hub.docker.com/r/pytorch/pytorch
- Docker Hub — qdrant/qdrant: https://hub.docker.com/r/qdrant/qdrant

## Related
- [[GPU Computing]]
- [[Python Virtual Environments]]
- [[AI Engineering - Dev Environment Stack]]
