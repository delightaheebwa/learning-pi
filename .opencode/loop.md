# Ship loop (this repo)

Worktree isolation is mandatory — see `AGENTS.md`. All steps below run
**inside your worktree** on your `agent/<slug>-<date>` branch, never in the
main checkout, never on `main`.

After changing tracked files here, do all of this without asking:

0. Isolate: if not already in a worktree, run `scripts/agent-worktree new <slug>`
   and move all work there. (Read-only `reviewer` runs need no worktree.)
1. Verify: `scripts/learn-check` (add `--no-load` if offline). Proceed only on pass.
2. Commit + push: check `git status/diff/log`, stage only intended files, no secrets, repo-style message, `git push -u origin <your-branch>` (never force, never push `main`).
3. Spawn the `reviewer` subagent with worktree path + SHA + intent. Fix every `blocking` finding, re-verify, commit (new commit — never amend pushed work), push, re-review. Fix trivial `suggestion`s. Stop at `CLEAN` or after 3 rounds.
4. Land: on reviewer `CLEAN`, run `scripts/agent-worktree land` — it fast-forwards `main` to your branch, pushes, and removes your worktree (continue in the main checkout afterwards). No manual merge step, no PR. If land reports a conflict (exit 3): resolve it in your worktree per `AGENTS.md` §4, re-verify, commit, push, re-review if non-trivial, re-run land (max 3 attempts, then report). With `blocking` findings left after 3 review rounds, do NOT land — report branch, SHA, and leftovers instead. `scripts/agent-worktree clean` prunes any leftover merged worktrees.
