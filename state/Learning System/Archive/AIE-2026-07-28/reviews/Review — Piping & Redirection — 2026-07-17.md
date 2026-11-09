# Review — Piping & Redirection — 2026-07-17

**Track:** aie
**Interval kept:** 7d
**Next review:** 2026-07-24

**What was tested:** Run an ML training script, split stderr to a separate file while seeing both streams live.

**Response:** `train.py 2>&1` (stderr→stdout merge, missing `tee` for live terminal + file capture)

**Nuance added:** `tee` is the key tool for ML work — `train.py 2> >(tee stderr.log) | tee stdout.log` streams to both terminal and files. Used `2>&1` syntax correctly.

**Status:** developing
