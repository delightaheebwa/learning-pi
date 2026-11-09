# Review — tmux — 2026-07-07

**Track:** AI Engineering (aie)
**Type:** Spaced Repetition Review (3rd review)
**Previous review:** 2026-07-04 (kept at 3d)

## Question
You share a GPU server with teammates. You start a training run that'll take 6 hours, then want to close your laptop and check on it later. How? One command.

## Answer
`Ctrl+B d` to detach, then later `tmux attach` to reattach.

## Evaluation
🟡 Mostly right. Knew `Ctrl+B d` for detach, but used uppercase `D` (which is `choose-client`, not detach). Didn't mention the reattachment step (`tmux attach`).

## Outcome
- Status: developing
- Interval: kept at 3d
- Next review: 2026-07-10
