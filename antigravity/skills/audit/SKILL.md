---
name: audit
description: Run a read-only state consistency and wiki provenance audit across MISSION, CURRICULUM, Active Concepts, Attempts, and the Knowledge Wiki. Trigger with /audit.
---

# State Audit Flow (`/audit`)

Execute a comprehensive read-only audit of learner state tables, position pointers, review schedules, and Knowledge Wiki provenance.

---

## Instructions

1. **Read-Only Invariant**: Do NOT modify, create, or commit any files during this flow.
2. **Run State Audit**:
   Execute the deterministic state audit script:
   ```bash
   python3 "$HOME/learning-pi/pi/audit_state.py" --root .
   ```
   Inspect the output for:
   - Contradiction classes (e.g. MISSION vs CURRICULUM vs Active Concepts).
   - Position pointer drift (active lesson vs track header vs checkpoint counts).
   - Review schedule drift (`Next Review` date in `Active Concepts.md` vs `Attempts.json`).
   - Scout digest TTL warnings (>7 days old).
   - Stale host paths.
3. **Run Wiki Provenance Audit**:
   Execute the wiki provenance check:
   ```bash
   python3 scripts/wiki_provenance.py --root .
   ```
   Inspect the trust-mix breakdown and check for missing provenance blocks.
4. **Report Findings Loudly**:
   Present the results categorized cleanly:
   - ❌ **Errors**: Serious inconsistencies requiring immediate correction.
   - ⚠️ **Warnings**: Minor drift, stale digests, or schedule alerts.
   - ✓ **Passing Invariants**: Health indicators.
   - If mechanical fixes exist, list the `STATE_AUDIT_FIXES` remediation suggestions so the learner or clerk can resolve them.
