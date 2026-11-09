# Review — Docker for AI Development — 2026-07-16

**Track:** aie
**Interval:** 7d → 14d (advancing)

**Question:** What two things do you need to make Docker see and use the GPU inside the container?
**Your answer:** NVIDIA Container Toolkit and the `--gpus all` flag
**Evaluation:** ✅ Correct. Need NVIDIA Container Toolkit on the host and `--gpus all` (or `--gpu '"device=0"'` for specific GPU) on `docker run`.

**Next Review:** 2026-07-30
