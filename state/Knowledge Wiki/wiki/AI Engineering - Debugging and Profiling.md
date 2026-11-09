<!-- provenance: status=verified | source=https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/12-debugging-and-profiling/docs/en.md ; https://pytorch.org/docs/stable/amp.html | verified-by=fact-check-agent | date=2026-10-26 -->

# AI Engineering — Debugging and Profiling

> **Source:** [ai-engineering-from-scratch, Phase 0, Lesson 12](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/12-debugging-and-profiling/docs/en.md)
> **Type:** Build (Python)
> **Prerequisites:** Dev Environment, basic PyTorch
> **Ingested:** 2026-06-26

## Core Insight

AI bugs are silent — they don't crash, they just train on garbage and produce a beautiful loss curve. Debugging AI code requires inspecting tensors at three levels:

1. **Standard Python** — breakpoints, logging, profiling, memory
2. **Tensor Operations** — shapes, dtypes, devices, NaN/Inf values
3. **Training Dynamics** — loss curves, gradient norms, activations

80% of AI bugs live at levels 1 and 2. Don't jump straight to staring at TensorBoard. (This is the lesson's rule of thumb, not a measured statistic.)

---

## Tools & Techniques

### 1. Print Debugging (`debug_print`)

Targeted print statements beat stepping through a debugger for tensor code because you need to see shapes, dtypes, and value ranges simultaneously.

```python
def debug_print(name, tensor):
    print(f"{name}: shape={tensor.shape}, dtype={tensor.dtype}, "
          f"device={tensor.device}, "
          f"min={tensor.min().item():.4f}, max={tensor.max().item():.4f}, "
          f"mean={tensor.mean().item():.4f}, "
          f"has_nan={tensor.isnan().any().item()}")
```

### 2. Conditional `breakpoint()`

Drop `breakpoint()` into your training loop triggered by a condition (NaN loss, loss spike):

```python
if loss.item() > 100 or torch.isnan(loss):
    breakpoint()
```

Useful pdb commands: `p tensor.shape`, `p loss.item()`, `p torch.isnan(outputs).sum()`, `p model.layer.weight.grad`

### 3. Python Logging

Replace ad-hoc prints with structured logging for persistent, timestamped records:

```python
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("training.log"), logging.StreamHandler()])
```

### 4. Code Timing

Use a context-manager Timer to measure data loading vs forward vs backward pass:

```python
class Timer:
    def __enter__(self): self.start = time.perf_counter(); return self
    def __exit__(self, *args): print(f"[{self.name}] {time.perf_counter() - self.start:.4f}s")
```

Common finding (lesson's heuristic, not a benchmark): data loading takes ~60% of training time. Fix: `num_workers > 0` in DataLoader.

### 5. cProfile & line_profiler

- `python -m cProfile -s cumtime train.py` — function-level profiling
- `line_profiler` + `kernprof -l -v train.py` — line-by-line profiling

### 6. CPU Memory Profiling

- **tracemalloc**: `tracemalloc.start()` → `tracemalloc.take_snapshot()` → `snapshot.statistics("lineno")`
- **memory_profiler**: `@profile` decorator, run with `python -m memory_profiler`

### 7. GPU Memory Profiling (PyTorch)

```python
torch.cuda.memory_summary()
torch.cuda.memory_allocated() / 1e9  # GB
torch.cuda.memory_reserved() / 1e9   # GB
```

OOM fixes (in order): reduce batch size → `torch.cuda.empty_cache()` → `del tensor` + `empty_cache()` → mixed precision (`torch.amp.autocast("cuda")` + `torch.amp.GradScaler("cuda")`; the older `torch.cuda.amp` API is deprecated) → gradient checkpointing

---

## Common AI Bugs

### Shape Mismatch
Use forward hooks to trace every shape transformation through the model:

```python
module.register_forward_hook(lambda mod, inp, out: print(f"{name}: {inp[0].shape} -> {out.shape}"))
```

### NaN Loss
Causes: LR too high, division by zero, log(0), exploding gradients in RNNs. Check both loss and gradients:

```python
torch.isnan(loss), torch.isnan(param.grad), torch.isinf(param.grad)
```

### Data Leakage
Check for ID overlap between train and test sets. Check for temporal leakage (future data predicting past).

### Wrong Device
A tensor silently on CPU while model is on GPU just makes training slow (no error). Use `check_devices` to verify.

---

## TensorBoard

```python
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter("runs/experiment_1")
writer.add_scalar("loss/train", loss.item(), step)
writer.add_histogram(f"weights/{name}", param, step)
```

Interpretation:
- Loss not decreasing → LR too low
- Loss oscillating → LR too high
- Train loss ↓, val loss ↑ → overfitting
- Weight histograms → 0 → vanishing gradients
- Gradient histograms → explosion → need gradient clipping

---

## Debugging Workflow

1. **Before training** — Run `check_shapes` with a sample batch
2. **First 10 steps** — `debug_print` loss, outputs, gradients
3. **During training** — Log loss, LR, gradient norms; TensorBoard for vis
4. **When something breaks** — `breakpoint()` at the failure point
5. **Performance** — Time data loading vs forward vs backward; profile memory near OOM

---

## Sources

- Rohit, *AI Engineering from Scratch* — Phase 0, Lesson 12 "Debugging & Profiling": https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/12-debugging-and-profiling/docs/en.md
- PyTorch AMP (`torch.amp`, `torch.cuda.amp` deprecation warning): https://pytorch.org/docs/stable/amp.html
- Python `cProfile`: https://docs.python.org/3/library/profile.html
- `tracemalloc`: https://docs.python.org/3/library/tracemalloc.html
- `line_profiler` / `memory_profiler`: https://github.com/pyutils/line_profiler · https://github.com/pythonprofilers/memory_profiler
- PyTorch CUDA memory docs (`memory_allocated`, `memory_reserved`, `memory_summary`): https://pytorch.org/docs/stable/notes/cuda.html#memory-management

## Related Concepts

- [[AI Engineering - Dev Environment Stack]]
- [[GPU Computing]]
- [[Python Virtual Environments]]
- [[Jupyter Notebook Workflow]]
