---
description: Run the read-only state consistency audit
---

Run the read-only state consistency audit and report findings loudly.

Do not prefix messages with a turn tag. This is not a learning flow and no verification gate applies.

Execute:

```bash
python3 "$HOME/learning-pi/pi/audit_state.py" --root .
```

This checks MISSION and CURRICULUM positions, lesson files against curriculum rows, Learning Profile focus, Active Concepts dates, the wiki index against wiki and source files, Pending Ingest and Scout digest residue, and stale host paths. It never writes.

Report every error and warning, naming the exact file or lesson it references. If there are errors, state plainly which position-of-record files disagree and what the reconciled value should be. Do not silently merge or fix state here. This command reports only. Edits to state require the normal flow. The automatic ingest and review audits fix the findings they touched using the script's `STATE_AUDIT_FIXES` hints.

End with the machine-readable summary line the script prints, on its own line:

`STATE_AUDIT_VERDICT: {"errors":N,"warnings":M}`
