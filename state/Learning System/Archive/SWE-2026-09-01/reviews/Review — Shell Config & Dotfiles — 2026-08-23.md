# Review — Shell Config & Dotfiles — 2026-08-23

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative (alternated from definitional)
**Interval:** 3d → 7d (advance)

**Question:** `source ~/.bashrc` versus a fresh login — what's the difference, and why doesn't `export PATH=...` typed in the terminal survive a logout?

**Answer:** "the first runs the shell config file while the second skips it. export PATH doesnt survive logout because it is cleared on logout."

**Assessment:** ✅ Pass. Core mechanism right: hand-typed exports live only in the running shell process's memory — the process exits at logout, so the setting dies with it. `source` executes the file in the CURRENT shell (no child), while a fresh login shell reads its startup files (~/.bash_profile, which typically sources ~/.bashrc). Precision tightened during grading. Advanced 3d → 7d.

**Next Review:** 2026-08-30 (7d)
