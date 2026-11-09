# Review — find — 2026-08-19

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 7d (held — needs more work)

**Question:** For `find . -type f -name "*.zip" -delete` — what do `-type f` and `-name "*.zip"` each filter by, and why are the quotes around `"*.zip"` load-bearing here?

**Answer (user):** (1) `-type f` filters by files, `-name "*.zip"` filters by zip files. (2) The quotes signify an argument being passed and ensure no whitespace splitting on matching filenames.

**Assessment:** ⚠️ Needs More Work (partial). Part (1) correct: `find` searches by *attributes* — `-type f` = regular file (vs `d` directory, `l` symlink), `-name` = name pattern — not content (that's grep's job). Part (2) **wrong reason**: the quotes here protect against **globbing/pathname expansion**, NOT word-splitting. Without quotes the shell expands `*.zip` into the *matching files in cwd* before `find` runs (e.g. `find . -name a.zip b.zip`), so `find` gets literal filenames instead of the pattern. This is the opposite of the `[ -f $FILE ]` case, where quotes prevent *word-splitting* of a variable. The distinction — `$VAR` unquoted → word-splits; `*.glob` unquoted → expands — is the 20% to internalize.

**Next Review:** 2026-08-26 (7d, held)
