# AGENTS.md — mandatory worktree isolation (this repo)

Do not edit the main checkout directly. Work in a dedicated `git worktree` on
its own `agent/<slug>-<date>` branch.

## 0. Are you already isolated?

```bash
git rev-parse --show-toplevel          # where you are
git rev-parse --abbrev-ref HEAD        # which branch
git worktree list                      # all checkouts
```

- If `--show-toplevel` is **not** `~/learning-pi` (or the `main` checkout) —
  you are already in a worktree. Stay there, skip to §2.
- If you are in the main checkout on `main` — isolate first (§1). Read-only
  commands (`git status`, `git log`, `grep`, `Read`) may run anywhere; any
  **write, edit, or branch change** requires a worktree.

The `reviewer` subagent is read-only and needs no worktree.

## 1. Create your worktree (one command)

```bash
scripts/agent-worktree new <slug>      # e.g. scripts/agent-worktree new fix-gate
# prints the new worktree path — cd there and do ALL work inside it
```

What the script does: `git fetch origin main`, creates branch
`agent/<slug>-YYYYMMDD` from `origin/main`, and adds a worktree at
`<repo-parent>/learning-pi-worktrees/<branch-sanitized>` (sibling of the
repo, never nested inside it). Branch names carry the date so concurrent
agents never collide.

Other commands:

```bash
scripts/agent-worktree list            # show all worktrees + branches
scripts/agent-worktree clean           # prune stale entries, remove merged worktrees
```

If the script is unavailable, the equivalent by hand:

```bash
git fetch origin main
git worktree add -b agent/<slug>-$(date +%Y%m%d) ../learning-pi-worktrees/agent-<slug>-$(date +%Y%m%d) origin/main
```

## 2. Rules inside your worktree

- Do **all** edits, test runs, commits here. Never touch the main checkout.
- Keep the branch to your own task. Never commit to `main`, never push to
  `main` by hand, never force-push. (The only exception: `main` is updated
  by `scripts/agent-worktree land` after reviewer `CLEAN`, §4.)
- Verify here: `scripts/learn-check` (add `--no-load` if offline). Proceed
  only on pass.
- Push with `git push -u origin <your-branch>` (plain push, never force),
  then follow the ship loop (§3). After reviewer `CLEAN`, land it yourself
  (§4) — do not leave the merge to the user.

## 3. Ship loop (runs inside the worktree)

Follow `.opencode/loop.md`: verify → commit + push your branch → spawn the
`reviewer` subagent with worktree path + SHA + intent → fix every `blocking`
finding → re-verify → new commit (never amend pushed work) → push →
re-review. Stop at `CLEAN` or after 3 rounds. On `CLEAN`, land (§4). With
`blocking` findings left after 3 rounds, do **not** land — report the branch,
the SHA, and the leftovers to the user.

## 4. Landing (auto-merge — you do this, no one else)

After reviewer `CLEAN`, run from inside your worktree:

```bash
scripts/agent-worktree land
```

This fast-forwards `main` to your branch (this repo keeps linear history),
pushes `main`, deletes the branch (local and remote), and removes your
worktree — continue in the main checkout
afterwards. If `main` moved while you worked, `land` merges `origin/main`
back into your branch and retries (max 3 attempts). It never rebases, never
force-pushes, and never resolves conflicts itself.

If `land` stops with a conflict (exit 3), resolve it in your worktree:

- `git status` → read every conflicted file **in full**. Keep **both**
  sides' intent: leave the main-side code intact and adapt your change
  around it. When the same lines genuinely disagree, prefer the version
  that keeps existing tests and contracts passing.
- Never bulk `checkout --ours/--theirs`. Never resolve by deleting or
  weakening tests, `contracts/`, or `CONTRACT.md` — that is the revise door
  and needs the user.
- A conflict in `contracts/`, `CONTRACT.md`, or `test/` expectations you do
  not fully understand → stop and report to the user instead of guessing.
- After resolving: `scripts/learn-check` must pass → commit → push → if the
  resolution touched code beyond the conflict markers, re-run the reviewer
  → re-run `scripts/agent-worktree land`.
- Still conflicted after 3 land attempts, or anything above tells you to
  stop → report the branch, the SHA, and the conflicted files to the user.
