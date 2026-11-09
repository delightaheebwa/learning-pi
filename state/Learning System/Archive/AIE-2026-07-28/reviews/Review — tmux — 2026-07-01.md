# Review — tmux

**Date:** 2026-07-01
**Track:** AI Engineering (aie)
**Interval:** Kept current

## Retrieval Result

Understood the core value (persistent sessions surviving SSH disconnects). Missed:
- Prefix key is **Ctrl+B**, not Ctrl+D (Ctrl+D sends EOF/exit)
- Detach: `Ctrl+B d`
- Reattach: `tmux attach -t my-session` (not `tmux session -t`)
