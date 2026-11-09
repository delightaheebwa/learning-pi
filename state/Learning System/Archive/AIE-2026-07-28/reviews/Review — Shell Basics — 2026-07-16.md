# Review — Shell Basics — 2026-07-16

**Track:** aie
**Interval:** 3d → 3d (fuzzy — reset)

**Question:** How do you run `train.py` in the background, ignore hangups, and log stdout+stderr to `run.log`?
**Your answer:** `nohup 1>&2 run.log` (incorrect)
**Evaluation:** ❌ Syntax was fuzzy. Correct command: `nohup python train.py > run.log 2>&1 &` or shorthand `nohup python train.py &> run.log &`. Redirections go before the command, not after. Identified as term issue (knew concepts, mixed syntax).

**Next Review:** 2026-07-19
