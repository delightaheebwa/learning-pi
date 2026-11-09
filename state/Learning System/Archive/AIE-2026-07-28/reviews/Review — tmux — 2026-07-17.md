# Review — tmux (Terminal Multiplexer) — 2026-07-17

**Track:** aie
**Interval kept:** 7d
**Next review:** 2026-07-24

**What was tested:** Detach from a training job on a GPU box, go home, reattach from laptop.

**Response:** Ctrl+B + D to detach, `tmux attach -t my-session` to reattach.

**Nuance added:** Name sessions with `tmux new -s train-run` for easy reattach. Use `tmux ls` to list active sessions.

**Status:** developing
