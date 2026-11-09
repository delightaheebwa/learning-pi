# Review — Black-box vs White-box Testing — 2026-08-11

**Track:** SWE (Testing)
**Question Type:** discriminative
**Interval:** 3d → 7d (advanced)

**Question:** When would you black-box test through process I/O rather than white-box calling internal functions directly — and what does each approach protect?

**Answer:** Black-box for high-level end-to-end behavior — right outputs from the whole system given certain inputs; white-box for verifying individual functions.

**Assessment:** ✅ Correct. Nailed the visibility split (contract through the interface vs internals). Refinement added: black-box protects refactors (internals can change while the contract holds); white-box trades that freedom for precise assertions.

**Next Review:** 2026-08-18 (7d)
