<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Jupyter Notebook Workflow

> Notebooks are the lab bench of AI engineering: prototype here, ship what works as scripts.

## Architecture

A notebook is a list of cells. Each cell is either code or markdown.

```
Markdown Cell → Code Cell (► Run → output) → Code Cell (► Run → inline plot)
```

The **kernel** is a Python process running in the background. All cells share the same kernel — variables persist between cells. This is both the superpower and the foot-gun.

## Essential Magic Commands

| Command | What it does |
|---------|-------------|
| `%timeit` | Run code many times and average (microbenchmarks) |
| `%%time` | Run code once (training runs) |
| `%matplotlib inline` | Render plots directly in the notebook |
| `!pip install` | Install packages without leaving the notebook |
| `%env VAR` | Check environment variables |

## Keyboard Shortcuts That Matter

| Key | Action |
|-----|--------|
| `Shift+Enter` | Run cell, move to next (learn this first) |
| `A` / `B` | Insert cell above / below |
| `DD` | Delete cell |
| `M` / `Y` | Convert to markdown / code |

`Shift+Enter` is the one you'll use a thousand times a day.

## Notebooks vs Scripts

| Use Notebooks For | Use Scripts For |
|-------------------|-----------------|
| Exploring a dataset | Training pipelines |
| Prototyping a model | Reusable utilities |
| Visualizing results | Production code |
| Course exercises | Code that runs on a schedule |

**The rule:** explore in notebooks, ship in scripts.

## Three Common Traps

1. **Out-of-order execution** — You run cell 5, then cell 2, then cell 7. Breaks when someone runs top-to-bottom. Fix: Kernel > Restart & Run All before sharing.
2. **Hidden state** — A deleted cell's variable still lives in memory. Fix: restart the kernel regularly.
3. **Memory leaks** — Loading large datasets without freeing. Fix: `del variable_name` + `gc.collect()`, or restart the kernel.

## Google Colab

Free Jupyter in the cloud with a T4 GPU. Pre-installed libraries. Files don't persist between sessions — save to Drive or download. Sessions time out after 90 minutes of inactivity (free tier).

## Key Terms

| Term | Meaning |
|------|---------|
| Kernel | Separate Python process that executes cells and keeps variables in memory |
| Cell | Independently runnable unit in a notebook (code or markdown) |
| Magic command | Special `%` / `%%` commands controlling the notebook environment |
| `.ipynb` | JSON file containing cells, outputs, and metadata |

## Related
- [[Python Virtual Environments]]
- [[GPU Computing]]

## Sources

- https://docs.jupyter.org/en/latest/
- https://colab.research.google.com/
