# Review — Taylor Series for ML — 2026-07-10

**Concept:** Taylor Series for ML  
**Date:** 2026-07-10  
**Result:** Kept (7d, same interval)

**Question:** In one sentence: why does a small learning rate make gradient descent safer?

**Response:** Because you reduce the risk of overshooting and missing the global minimum.

**Evaluation:** Correct in practical terms but missing the Taylor connection. Gradient descent works because of the first-order Taylor approximation f(x+h) ≈ f(x) + f'(x)h — and that linear approximation only holds for small h. Large steps invalidate the math. "Don't overshoot" is the symptom; Taylor approximation breakdown is the cause.

**Diagnostic:** Was it the name/term you forgot, or the concept itself? (not asked explicitly, but response clearly missed the Taylor link — terminology/concept connection issue)

**New Interval:** Kept at 7d — next review 2026-07-17
