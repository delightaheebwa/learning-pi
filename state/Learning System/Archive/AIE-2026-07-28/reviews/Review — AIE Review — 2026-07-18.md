# Review — AIE Review — 2026-07-18

**Date:** 2026-07-18
**Session Type:** AI Engineering Track Review (5 due)

## Concepts Reviewed

### 1. Print Debugging & breakpoint for AI
- **Result:** Wrong — guessed `loss.nan` which isn't valid. Correct answer: `p torch.isnan(loss).sum()` or `p (loss != loss).any()`.
- **Interval:** Keep (7d → 7d)

### 2. Python Logging for Training
- **Result:** Answered "shows where error happened" — that's traceback, not logging. Two advantages: persistent file output (not lost on scroll), and severity levels (filter debug/info/warning/error per run).
- **Interval:** Keep (7d → 7d)

### 3. Dense Layer Forward Pass
- **Result:** Mostly right — `relu(wx+b)` with broadcast bias. Nuance: bias is 1 per output neuron (`[out_features]`), broadcasts over batch dim.
- **Interval:** Keep (7d → 7d)

### 4. Chain Rule Decomposition
- **Result:** "Needs local derivative + upstream gradient" — true but missed the why. The chain rule factorizes `dy/dx = dy/du · du/dx`, so each node only needs those two things.
- **Interval:** Keep (7d → 7d)

### 5. Reverse-Mode Autodiff & Backprop
- **Result:** Correct — O(1) pass for NNs (millions of weights, one loss). Trade-off: reverse mode stores computation graph (O(ops) memory), forward mode doesn't but needs O(weights) passes.
- **Interval:** Advance (7d → 14d)

## Format Adjustment
- Python Logging: user said asking for code setup isn't good for flash reviews. Re-asked as concept question — better fit.
