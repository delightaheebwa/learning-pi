---
description: Run a review session on the active learning track
---
Run a review session. Load the `learning-system` skill and follow its Review flow.

Derive the active track and current position from `Learning System/CURRICULUM.md` and `Learning System/MISSION.md`; if they disagree, stop and report. Dispatch a foreground `grade-audit` subagent for every grade — do not bypass the gate. Commit state only (`Learning System/`, `Knowledge Wiki/`) when done.
