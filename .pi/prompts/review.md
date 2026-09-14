---
description: Run a review session on the active learning track
---
[[FLOW:review]]
Run a review session. Load the `learning-system` skill and follow its Review flow.

Derive the active track and current position from `Learning System/CURRICULUM.md` and `Learning System/MISSION.md`; if they disagree, stop and report. Dispatch a foreground `grade-audit` subagent for every grade — do not bypass the gate. Add budgets to each verifier dispatch so a slow one cannot balloon the session: `toolBudget: {soft:20,hard:35}`, `usageBudget: {tokens:{soft:150000,hard:300000}}`. Before committing, run the read-only state audit (`python3 "$HOME/learning-pi/pi/audit_state.py" --root .`); fix any error or warning this review touched using the `STATE_AUDIT_FIXES` hints, re-run once, surface hint-less/unrelated findings, report loudly, and emit `STATE_AUDIT_VERDICT: {"errors":N,"warnings":M}` on the final line. Commit state only (`Learning System/`, `Knowledge Wiki/`) when done.

Context discipline (keep the session light): never dump a full `git diff` — use `git diff --stat` (or `--numstat`) and only `git diff -- <path>` for a file you actually need; read state/wiki files by section (`python3 scripts/ops.py bundle "PATH@^## "`), never re-read a file already in context; keep the audit report to its verdict line plus any ❌/⚠️. Do not switch the model mid-review. Cap the review at 5 grades and end the flow when done rather than continuing into unrelated work.

Begin every assistant message with a turn tag on its first line — `[[TURN:claims]]`, `[[TURN:quiz]]`, `[[TURN:grade]]`, or `[[TURN:none]]`. The gate strips the tag before the learner sees it.
