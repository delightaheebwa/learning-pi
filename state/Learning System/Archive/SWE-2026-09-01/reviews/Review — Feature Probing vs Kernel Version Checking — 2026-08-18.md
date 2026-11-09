# Review — Feature Probing vs Kernel Version Checking — 2026-08-18

**Track:** SWE (C / Runtime Detection)
**Question Type:** discriminative
**Interval:** 3d → 7d (advanced)

**Question:** Tools like `free`/`top` need to know whether a feature exists (e.g. `MemAvailable`, added in Linux 3.14). Why is checking the kernel version (`uname -r`) the wrong way — and what does "probe the feature, not the version" mean in practice?

**Answer:** Version-checking is brittle in production; probe whether the feature actually exists at runtime instead.

**Assessment:** ✅ Correct-direction (thin on the *why*). Full picture: features get backported to older kernels by RHEL/Debian, `uname` is spoofable, and multi-binary shims are a maintenance nightmare. Pattern: sentinel default (e.g. ULONG_MAX) → if key still sentinel after parse, feature unsupported → use documented fallback (pre-3.14: MemFree + Buffers + Cached). Probe capability at runtime; degrade gracefully, never crash or lie.

**Next Review:** 2026-08-25 (7d)
