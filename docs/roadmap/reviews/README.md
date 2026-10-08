# Review phase — per-checkpoint review

After the cascade finishes (P1 → P2; P3 deferred), a **review phase** runs before end-to-end testing:

```
P2 → REVIEW orchestrator (default model)      [P3 deferred]
        ├── R-P0  (Muse Spark)  review P0's changes only
        ├── R-P1  (Muse Spark)  review P1's changes only
        └── R-P2  (Muse Spark)  review P2's changes only
     → REVIEW aggregates all findings
     → REVIEW implements the fixes (default model)
     → E2E
```

Reviewers run on **`opencode-go/muse-spark-1.3-contributor`** (spawned by
`spawn-reviewer.sh`). Each reviewer reviews **only its checkpoint's changes**, writes findings to
`docs/roadmap/reviews/<CP>.md`, and stops. The orchestrator waits for all of them (P0–P2), aggregates, fixes, and
then spawns E2E.

## Reviewer rules

- **Review only. Do not edit code, do not commit, do not spawn agents.** Your single output is your
  findings file.
- Read the audit `docs/AUDIT-2026-10-08.md`, `AUDIT-ROADMAP.md`, `CONTRACT.md`, and your checkpoint's
  brief in `docs/roadmap/`.
- Be adversarial and concrete: find bugs, contract gaps, dead-ends, false claims, regressions,
  missing tests, and deviations from the audit's intent. Do not rubber-stamp.
- Cite `file:line` and a command or test as evidence. Distinguish verified findings from suspicions.
- Rank every finding by severity: **high** (wrong/unsafe/does not work), **medium** (works but
  fragile/incomplete), **low** (nit).

## Findings file format (write exactly this shape)

```markdown
# Review — <checkpoint> (<reviewer model>, <date>)

## Scope reviewed
<files/subsystems and the commit range or SHAs>

## Checks run
<commands/tests run and their results>

## Findings
### [HIGH] <one-line title>
- Where: <file:line>
- Evidence: <command output / code excerpt / test name>
- Why it matters: <impact>
- Recommended fix: <concrete change>

### [MEDIUM] ...
### [LOW] ...

## Verdict
<one paragraph: does this checkpoint do what the audit/roadmap claims? What is the single most
important thing to fix?>
```

If you find nothing at a severity, say so explicitly ("no high findings"). A short, honest review is
better than a padded one.
