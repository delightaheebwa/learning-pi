# Review — Dynamic Language Optimization Limits — 2026-06-10

**Result:** ✅ Solid, interval advanced to 7d

**Question:** Why can't PyPy's tracing JIT handle all Python code well, and what's the tradeoff with Cython?

**User's answer:** PyPy can't handle all code because Python allows mutation — tricky to handle ever-changing code. Cython forces Python to be like C to compile to machine code; at that point, why not just write C?

**Evaluation:** Nailed both parts. Tracing JIT needs type stability to optimize; Python's dynamic nature fights that. Cython's tradeoff sacrifices Python's strengths for speed — you're writing C with Python syntax. Clear understanding of both approaches and their fundamental limitations.

**Next review:** 2026-06-17
