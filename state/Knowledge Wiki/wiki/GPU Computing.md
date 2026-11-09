<!-- provenance: status=verified | source=https://developer.nvidia.com/cuda-zone ; https://pytorch.org/docs/stable/notes/cuda.html | verified-by=fact-check-agent | date=2026-10-26 -->

# GPU Computing

> GPU acceleration is the difference between an 8-hour training run and a 10-minute one.

## Three Options for GPU Access

| Option | Cost | Best For |
|--------|------|----------|
| Local NVIDIA GPU | $0 (already owned) | Regular use, large datasets |
| Google Colab (free T4) | $0 | Quick experiments, no local GPU |
| Cloud GPU (Lambda, RunPod, Vast.ai) | $0.20-2.00/hr | Serious training, large models |

## Key Concepts

- **CUDA** — NVIDIA's parallel computing platform; lets you run code on the GPU.
- **VRAM** — Video RAM on the GPU, separate from system RAM. Limits model size.
- **fp16 (half precision)** — 16-bit floating point, uses half the memory of fp32 with minimal accuracy loss. Rule of thumb: 2 bytes per parameter.
- **Tensor Cores** — Specialized GPU hardware for matrix multiplication, 4-8x faster than regular CUDA cores.

## GPU Benchmark Pattern

```python
import torch, time
size = 5000
a_cpu, b_cpu = torch.randn(size, size), torch.randn(size, size)
start = time.time()
c_cpu = a_cpu @ b_cpu
cpu_time = time.time() - start

if torch.cuda.is_available():
    a_gpu, b_gpu = a_cpu.cuda(), b_cpu.cuda()
    torch.cuda.synchronize()
    start = time.time()
    c_gpu = a_gpu @ b_gpu
    torch.cuda.synchronize()
    gpu_time = time.time() - start
    print(f"Speedup: {cpu_time / gpu_time:.0f}x")
```

## Device-Agnostic Code

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

## Related
- [[AI Engineering - Dev Environment Stack]]
- [[Docker for AI Development]]

## Sources
- NVIDIA CUDA overview: https://developer.nvidia.com/cuda-zone
- PyTorch CUDA semantics: https://pytorch.org/docs/stable/notes/cuda.html
- NVIDIA Tensor Cores: https://developer.nvidia.com/blog/programming-tensor-cores-cuda-9/
