# Review — AIE Review — 2026-07-04

**Date:** 2026-07-04
**Session Type:** AI Engineering Track Review (5 of 9 due)

## Concepts Reviewed

### 1. Editor & Remote Dev Setup
- **Result:** Solid core list (Pylance, Remote SSH, GitLens, Black formatter). Added Jupyter extension, format-on-save, type checking mode, LSP context.
- **Interval:** Keep current (no change)

### 2. tmux (Terminal Multiplexer)
- **Result:** Mixed. Created session correctly (`tmux new -s`). Split: used D (detach) instead of " or %. Detach: used Ctrl+Z (should be Ctrl+B D). Attach: correct (`tmux attach -t`).
- **Interval:** Keep current

### 3. System & GPU Monitoring
- **Result:** Correct — htop for system/CPU, nvtop for GPU, explained what each shows.
- **Interval:** Advanced to 7d

### 4. apt Package Management
- **Result:** Close. `apt update` refreshes package index ✅. `apt upgrade` upgrades ALL packages, not specified ones. `apt clean` removes cached .deb files from `/var/cache/apt/archives/`.
- **Interval:** Keep current

### 5. AI Debugging Levels
- **Result:** Correct — named all three levels correctly (Standard Python → Tensor Ops → Training Dynamics). Previously confused Level 3 as "TensorBoard".
- **Interval:** Advanced to 7d

## Remaining Due
- Dev Environment Stack (due 2026-07-04)
- Broadcasting (due 2026-07-04)
- Rotation Matrices (due 2026-07-04)
- Scaling Matrices (due 2026-07-04)
