# Review — Chain Rule & Backpropagation — 2026-07-17

**Track:** aie
**Interval kept:** 7d
**Next review:** 2026-07-24

**What was tested:** Key insight about how gradients flow from output back to the first layer during backprop.

**Response after hint:** Upstream gradient × local derivative = weight adjustment, propagated backward through the graph.

**Nuance added:** User's description captures the mechanics. One boundary to keep straight: the gradient isn't "subtracted" during the backward pass — it's computed. The actual weight update (subtraction) happens in a separate optimizer step after the full backward pass.

**Status:** developing
