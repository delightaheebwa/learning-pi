# Session — awk Enrichment

- **Date:** 2026-08-11
- **Topic:** awk internals from handwritten lecture-1 quiz notes (photo, 2026-08-10) + MIT Missing Semester — Shell
- **Type:** Ingest (enrichment, not review)
- **Concepts enriched (1, SWE track):** awk — insight row updated, `last_reviewed` 2026-08-11, `next_review` 2026-08-18, interval 3d→7d
- **Wiki page:** MIT Missing Semester — Shell (awk section extended)
- **Key insights ingested:**
  - awk condition-action pairs: every line triggers exactly one pass; a bare pattern (`awk '/err/'`) is an implicit filter on the whole line (`$0`)
  - `FS` (input) and `OFS` (output) are variables: `-F,` and `-v OFS=,` change them; print separates fields with OFS, not the input separator
  - `~` matches a regex, `!~` does not match — the awk counterparts of grep's matching; can be applied to any field (`$3 ~ /.../`)
  - `$0` = entire line, `$1`..`$NF` = fields, `NF` = count; `BEGIN {}` runs before the first line (for headers/initialization)
  - FPAT solves quoted-CSV parsing where commas sit inside quotes: `awk -v FPAT='[^,]+|"[^"]*"'` — `-F` can't do this
  - Example: `awk -F: '{print $1}' /etc/passwd` — 7-col colon-separated record; `$1` = username
  - Source-scope note added: lecture teaches awk pattern/filter basics; FS/OFS, FPAT, BEGIN, and the /etc/passwd walkthrough are beyond-source expansion (reviewer-requested clarity)
- **Verification:** learning-review quality gate — awk flag resolved pass 2; remaining flags (GNU Make HIGH; permissions/globs/quoting/built-ins/jobs/parameter-expansion medium) are pre-existing sections outside this session's scope, surfaced to user
- **Open questions:** none new
