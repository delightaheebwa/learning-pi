---
description: Run the read-only state consistency audit
---
Run the read-only state consistency audit and report findings loudly.

Do not prefix messages with a turn tag — this is not a learning flow and no verification gate applies.

Execute:

```bash
python3 "$HOME/learning-pi/pi/audit_state.py" --root .
```

This checks MISSION ↔ CURRICULUM positions, lesson files vs curriculum rows, Learning Profile focus, Active Concepts dates, wiki index vs wiki/source files, Pending Ingest / Scout digest residue, and stale host paths. It never writes.

Report every ❌ error and ⚠️ warning, naming the exact file/lesson it references. If there are errors, state plainly which position-of-record files disagree and what the reconciled value should be. Do not silently merge or "fix" state here — this command reports only; edits to state require the normal flow.

End with the machine-readable summary line the script prints, on its own line:

`STATE_AUDIT_VERDICT: {"errors":N,"warnings":M}`
