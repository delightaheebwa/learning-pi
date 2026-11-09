# Review — Derivative for ML — 2026-07-17

**Track:** aie
**Interval kept:** 7d
**Next review:** 2026-07-24

**What was tested:** What the derivative tells you during training (one sentence).

**Response:** "It tells you by how much you should tweak the weights to reduce the loss."

**Nuance added:** Derivative = instantaneous rate of change (direction + steepness). The negative gradient points downhill. How much you actually move = learning_rate × gradient. Core intuition: derivative signals *which way and how steep*, LR decides the step size.

**Status:** developing
