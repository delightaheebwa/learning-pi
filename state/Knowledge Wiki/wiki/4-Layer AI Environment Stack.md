<!-- provenance: status=verified | source=https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/01-dev-environment/docs/en.md | verified-by=fact-check-agent | date=2026-10-26 -->

# 4-Layer AI Environment Stack

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P0 L01-L12 · **Lang:** Python
> **Insight:** System → Package managers → Runtimes → AI Libraries. GPU issue = check Runtimes (driver/CUDA libs) first.

## The Four Layers
Upstream (Phase 0, Lesson 01) numbers them bottom-up: 1 System Foundation → 2 Package Managers → 3 Language Runtimes → 4 AI/ML Libraries.

| Layer | What | Examples |
|-------|------|----------|
| 1. System | OS, shell, drivers, editor | NVIDIA driver, `nvidia-smi`, git |
| 2. Package managers | Install/version tools | `apt`, `uv`, `pnpm`, `cargo`, `juliaup` |
| 3. Runtimes | Language runtimes + GPU SDK/lib runtime | Python 3.11+, Node 20+, venv, CUDA toolkit/cuDNN libs |
| 4. AI libraries | Frameworks | PyTorch, JAX, TensorFlow, transformers |

## GPU Diagnosis

`nvidia-smi` OK but `torch.cuda.is_available()` False → the fault is **at or above the Runtimes layer**, and the usual culprits are:

1. a **CPU-only PyTorch wheel** installed (AI-libs layer — most common on pip/uv defaults), or
2. **missing/mismatched CUDA runtime libraries** (cuDNN/CUDA libs) or a driver too old for the wheel (Runtimes layer).

So "GPU issue = Runtimes layer" is a good first hypothesis, not a rule: check the wheel first (`torch.version.cuda`), then the CUDA runtime libs/driver.

## Sources

- Rohit, *AI Engineering from Scratch* — Phase 0, Lesson 01 "Dev Environment": https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/01-dev-environment/docs/en.md
- PyTorch CUDA semantics / troubleshooting (`torch.cuda.is_available`): https://pytorch.org/docs/stable/notes/cuda.html

## Related

- [[GPU Computing]]
- [[Python Virtual Environments]]

## Retrieval log (2026-09-26)

- Review retry PASS (MCQ "C") on a fresh prompt isolating the runtime libs (healthy driver + CUDA-enabled torch build + missing CUDA/cuDNN runtime libraries → Runtimes). Grade-audit agreed. The Packages→Runtimes split now holds under retrieval; the 2026-09-05 mistake row moves to `review` (retries 2, next retry 2026-10-03 — a second consecutive correct graduates it, since the 09-23 partial fail broke the 09-16 streak). `next_review` 2026-10-03 (interval_index 1).
