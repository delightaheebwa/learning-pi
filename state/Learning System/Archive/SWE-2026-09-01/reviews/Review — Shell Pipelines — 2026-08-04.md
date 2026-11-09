# Review — Shell Pipelines — 2026-08-04

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 14d (3rd review)

**Question:** What does the pipe operator `|` do, and how does data flow between commands in a pipeline?

**Answer:** The pipe command handles data flow between commands by taking the stdout of one command and passing it to stdin of the next command. It flows left to right.

**Assessment:** Correct. The user nailed the core mechanism: stdout → stdin, left to right flow.

**Notes:** Each command in a pipeline runs in a subshell (variable assignments don't persist). `set -o pipefail` makes the pipeline's exit code reflect the last command that failed, not just the last one.

**Next Review:** 2026-08-18 (14d interval)
