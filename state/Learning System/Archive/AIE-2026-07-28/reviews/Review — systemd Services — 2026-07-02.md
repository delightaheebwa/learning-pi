# Review — systemd Services

**Date:** 2026-07-02
**Track:** AI Engineering (aie)
**Concept:** systemd Services
**Source:** ai-engineering-from-scratch Phase 0, Lesson 11

## Performance

**Retrieval attempt:** Confused systemctl enable ("grants rights"), start ("boots system"), status ("system statistics"), restart vs reload.

### Correct definitions:
- **`systemctl enable`** — configures service to auto-start at boot
- **`systemctl start`** — starts the service immediately
- **`systemctl status`** — shows current state of a specific service (running/stopped/failed + logs)
- **`systemctl restart`** — full stop then start (downtime)
- **`systemctl reload`** — re-reads config without stopping (SIGHUP, zero downtime)

**Verdict:** ❌ Reset to 3d
**Next review:** 2026-07-05
