# Review — Jupyter Notebook Workflow — 2026-07-16

**Track:** aie
**Interval:** 7d → 3d (didn't recall — reset)

**Question:** You have a `.ipynb` notebook. How do you convert it to a `.py` script with `# %%` cell markers?
**Your answer:** Rename the file to have `.py` (incorrect)
**Evaluation:** ❌ Renaming gives JSON garbage. Correct approach: `jupyter nbconvert --to script notebook.ipynb`. The `# %%` format in a `.py` file is called percent format (or percent script). VS Code + Jupyter extension runs each `# %%` block as a cell. Identified as forgetting the content was even in the knowledge base.

**Next Review:** 2026-07-19
