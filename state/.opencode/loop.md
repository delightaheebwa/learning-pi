# Ship loop (this repo)

After changing tracked files here, do all of this without asking:

1. Verify: `scripts/learn-check` (ops-only changes: `python3 -m unittest scripts.ops_test`). Proceed only on pass.
2. Commit + push: check `git status/diff/log`, stage only intended files, no secrets, repo-style message, plain `git push` (never force).
3. Spawn the `reviewer` subagent with repo path + SHA + intent. Fix every `blocking` finding, re-verify, commit (new commit — never amend pushed work), push, re-review. Fix trivial `suggestion`s. Stop at `CLEAN` or after 3 rounds, then report leftovers.
