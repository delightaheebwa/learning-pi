# AGENTS.md — mandatory worktree isolation (this repo)

Any agent or model doing work in this repo **must not edit the main checkout
directly**. Work happens in a dedicated `git worktree` on its own
`agent/<slug>-<date>` branch, so two agents never step on each other.

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
  `main`, never force-push.
- Verify here: `scripts/learn-check` (add `--no-load` if offline). Proceed
  only on pass.
- Push with `git push -u origin <your-branch>` (plain push, never force),
  then report the worktree path, branch, and SHA so the user can review/merge.
- After merge, clean up: `git worktree remove <path>` (or
  `scripts/agent-worktree clean`), then `git worktree prune`.

## 3. Ship loop (runs inside the worktree)

Follow `.opencode/loop.md`: verify → commit + push your branch → spawn the
`reviewer` subagent with worktree path + SHA + intent → fix every `blocking`
finding → re-verify → new commit (never amend pushed work) → push →
re-review. Stop at `CLEAN` or after 3 rounds, then report leftovers.
