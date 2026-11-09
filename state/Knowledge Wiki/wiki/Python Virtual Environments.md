<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Python Virtual Environments

> Dependency hell is real in AI/ML. Virtual environments are the cure.

## The Problem

Different projects need different (sometimes conflicting) package versions. Installing globally creates impossible conflicts. The fix: every project gets its own isolated environment.

## Three Options

### uv (Recommended)
10-100x faster than pip. Handles environments, Python versions, and dependency resolution in one tool.

```bash
uv venv                          # create
source .venv/bin/activate       # activate
uv pip install torch numpy       # install
```

### venv (Built-in)
Works everywhere Python is installed. Slower than uv.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### conda (When Needed)
Manages non-Python dependencies like CUDA toolkits, cuDNN, C libraries. Use when you need a specific CUDA toolkit without installing it system-wide.

**Rule:** If you use conda, use conda for everything in that environment. Mixing pip into conda causes painful conflicts.

## pyproject.toml

The modern Python project config file, replacing setup.py, setup.cfg, and requirements.txt:

```toml
[project]
name = "my-ai-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["numpy>=1.26", "jupyter>=1.0"]

[project.optional-dependencies]
torch = ["torch>=2.3"]
llm = ["anthropic>=0.39"]
```

## Lockfiles

Pin every dependency (including transitive ones) to exact versions for reproducibility. Commit the lockfile to git.

## Common Mistakes

1. **Installing globally** — Always activate the virtual environment first. Check: `which python` should show `.venv/bin/python`.
2. **Mixing pip and conda** — Pick one environment manager and stick with it.
3. **Forgetting to activate** — Your shell prompt should show `(.venv) $`.
4. **Committing .venv to git** — Virtual environments are 200MB-2GB. Add `.venv/` to `.gitignore`.
5. **CUDA version mismatch** — PyTorch's CUDA version must be ≤ your GPU driver's CUDA version.

## Per-Phase Strategy

For the AI engineering course, create separate environments per phase (or group of compatible phases) rather than one massive environment.

## Related
- [[AI Engineering - Dev Environment Stack]]
- [[GPU Computing]]
- [[Docker for AI Development]]

## Sources (verified)

- https://docs.astral.sh/uv/
- https://docs.python.org/3/library/venv.html
- https://docs.conda.io/
