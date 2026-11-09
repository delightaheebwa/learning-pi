# Review — systemd Services — 2026-07-16

**Date:** 2026-07-16 | **Track:** aie | **Interval:** 3d → 3d ❌

**Question:** You've written a script `/opt/train/runner.sh` and want it to auto-restart if it crashes. What's the shortest systemd unit file that would do this?

**Response:** "autorestart.sh"

**Evaluation:** Wrong. systemd uses `.service` files with a declarative config. Answer should be a `.service` file with `[Service] ExecStart=... Restart=always`. Concept not solid → reset to 3d.

**Next Review:** 2026-07-19
