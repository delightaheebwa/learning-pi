# Constraints

Last reviewed: 2026-11-11 by @delightaheebwa

This is the **engineering** quality bar: what "good enough to ship" means for
any change, and what must never be weakened in a diff. Product behavior is a
separate bar — see `CONTRACT.md` and `contracts/learning-core.json`, which are
frozen behind the revise door. Neither bar may be weakened to make a change
pass. Read this file before writing code.

## Floor (always enforced, no setup required)

- No new suppression comments: `@ts-ignore`, `@ts-nocheck`, `eslint-disable`,
  `biome-ignore`, `deno-lint-ignore`, `# noqa`, `# type: ignore`,
  `# pyright: ignore`, `# pylint: disable`, `# shellcheck disable`.
- No unimplemented stubs: `throw new Error("Not implemented")`,
  `raise NotImplementedError`, an empty `catch {}`, or `pass  # stub` where the
  implementation belongs.
- No skipped or deleted tests without a reason in the commit message.
- No secrets in source.
- Do not restate the contract JSON's version, invariant count, or
  per-invariant test names; point at `contracts/learning-core.json`.
- This file does not get weakened to make a change pass.

## Enforced with numbers

| Dimension | Rule | Checked by | Runs at |
| --- | --- | --- | --- |
| Skill-pack integrity | 0 broken links; the pinned 25 skills, 7 shared references, and 4 personas are present | `scripts/check-skills` | task end, CI |
| Floor | 0 floor violations in the diff against `origin/main` | `scripts/floor-guard.mjs` | task end, CI |
| Contract invariants | every active invariant binds to a passing test | `scripts/learn-check --no-load` | CI |
| Doc drift | 0 retired paths or stale tokens in current docs | `python3 scripts/check-docs` | CI |
| Secrets | No secrets in tracked source | `gitleaks dir . --config .gitleaks.toml --redact --no-banner` | CI |

Every row names the command that produces the verdict. A dimension with a
number and no command here is an aspiration, not a constraint. The numbered
inventory above is the pinned upstream pack, not the product contract; it is
kept honest by `scripts/check-skills`.

**Blocking policy.** The floor, secrets, the contract invariant gate, and the
doc-drift gate block. `scripts/check-skills` warns until **2026-11-24**; on that
date, promote it only if it stayed clean for the whole window. A gate that
stalls the agent gets switched off, and a gate people switch off is worse than
no gate.

## Measured, not yet enforced

| Metric | Today | Direction |
| --- | --- | --- |
| Test files | 19 | must not fall |
| Suppression comments or `TODO` markers in first-party source | 30 | must not rise |

These are recorded, not gated: no coverage, performance, or accessibility tool
is installed yet, and a number without a command would be an aspiration.
Coverage, performance, and accessibility remain deferred; secrets are covered by
`gitleaks` in CI. Measure with:

```sh
find test state/scripts scripts harness -type f \( -name '*_test.py' -o -name '*_test.mjs' -o -name '*_test.sh' -o -name 'test_*.py' \) | wc -l
grep -rIn --exclude-dir=node_modules --exclude-dir=.git -E '@ts-ignore|@ts-nocheck|eslint-disable|# *noqa|# *type: *ignore|TODO' bridge pi harness scripts bin test .pi state/scripts deploy | wc -l
```

## Exceptions

| ID | Rule | Path | Reason | Owner | Expires |
| --- | --- | --- | --- | --- | --- |

None currently. A new row here is a move that lowers the bar: it must be discussed in review and
carry an owner and an expiry no more than 90 days out. A revise-door change that
removes or replaces tests gets its own row; it is never covered by a blanket
ignore.
