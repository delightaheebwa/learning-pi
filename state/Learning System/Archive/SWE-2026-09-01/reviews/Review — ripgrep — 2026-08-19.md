# Review — ripgrep — 2026-08-19

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 14d (advanced)

**Question:** `rg "TODO"` in a big project — what does `rg` search by default that differs from plain `grep "TODO"` in the same spot, and what does `rg` do automatically that makes it faster and more human-friendly?

**Answer (user):** rg searches non-hidden files by default; plain grep searches everything. This makes rg faster and more human-friendly.

**Assessment:** ✅ Directionally correct on the core 20%. Sharpened the mechanism: `rg` reads `.gitignore` (and `.ignore`/`.rgignore`) and **automatically skips** ignored files (build artifacts, node_modules), and it is **recursive by default** — that's what makes it fast and focused. Plain `grep` has no ignore awareness and is not recursive by default, so it searches junk unless manually filtered (`-r`, `--exclude-dir`). The "faster" root: ignore rules prune the search space so it reads far fewer files. Pass.

**Next Review:** 2026-09-02 (14d)
