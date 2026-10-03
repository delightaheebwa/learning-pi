---
name: lpi
description: Drive the pi learning system's gated update and end-to-end testing from opencode. Use when the user asks to update pi or its extension packages, run lpi check/update/doctor/rollback, e2e the learning system, test whether an update or code change works in the learner sandbox, or triage a failed lpi update / diagnosis report and make lpi test pass.
---

# lpi

Own the `lpi` lifecycle from opencode: see what is newer, run the gated update
(including the end-to-end learner journeys), and repair a rejection under the
contract. The same skill also covers on-demand, read-only e2e testing of a code
change that is not an update.

`lpi` wraps two scripts in `~/learning-pi`:
`harness/pi-safe-update` (staged, gated updates) and `scripts/learn-check`
(the test suite). Nothing updates itself; pi is hard-pinned in
`versions.lock.json`.

## Model

Run this skill under a free model, in this order of preference:

1. longcat
2. mimo
3. big pickle

The pi sessions inside the sandbox still use pi's own flash models
(`glm-5.3-flash`, `deepseek-v4.1-flash`, `muse-spark-1.3-contributor`). Those are
the system under test; do not override them. Only this exploratory/judging layer
runs on a free model.

## Which mode

- **Update mode** — drives `lpi update`, promotes on green, repairs a rejection.
  It changes pins. Triggers: "update pi", "upgrade", "is there a newer pi",
  "lpi update", "apply the update".
- **Inspect mode** — read-only: runs `lpi e2e` and/or an improvised learner
  session in a sandbox. Never touches real state or pins. Triggers: "e2e this",
  "does this change work", "test the flow", "triage this e2e run".

## Update mode

### 1. See what is newer

```bash
~/learning-pi/bin/lpi check        # same as bare `lpi`
```

Read the pinned vs newest pi and extension-package versions and the changelog
risk scan. If nothing is newer, report that and stop.

### 2. Run the gated update with e2e

```bash
~/learning-pi/bin/lpi update --e2e
```

This resolves newer pi and packages, stages them side by side in an isolated
sandbox (never touching `~/.pi/agent` until promotion), runs `lpi test` plus the
e2e learner journeys, and promotes the whole set only if every invariant passes.
Use `--dry-run` for a preview, `--pi-only` to ignore packages, and
`--e2e-flows a,b` to narrow the journeys when the diff touches one flow. `--e2e`
is slow (real models) and off by default, but it is the point of this skill.

On success, report the promoted pi/package versions and the report path
(`~/.cache/learning-pi/diagnosis-*.md`). Done.

### 3. If rejected — read the evidence

- Newest report: `ls -t ~/.cache/learning-pi/diagnosis-*.md | head -1` — read it in full.
- The contract: `~/learning-pi/CONTRACT.md` and `~/learning-pi/contracts/learning-core.json`.
- Reproduce: `~/learning-pi/bin/lpi test`. Keep the `FAIL` lines; each names an invariant.
- If an e2e journey failed, read that run's artifacts (see Inspect mode):
  `ls -t ~/.cache/learning-pi/e2e-*/summary.json | head -1`, then the failing
  scenario's `<id>.json` and `<id>.session.jsonl`.

### 4. Classify

Two leading words decide the fix:

- **Adapter drift** — the load probe fails, or a test fails while `gate-core/`
  logic is sound. pi or an extension renamed a wire shape. Fix
  `~/learning-pi/.pi/extensions/learning-gate/pi-adapter/` only.
- **Behavior drift** — the adapter loads but an assertion fails. Either pi
  behaves differently and the adapter must absorb it, or the learning system's
  *expectation* must change. An expectation change is the **revise door**:
  `CONTRACT.md`, `contracts/learning-core.json`, the tagged test, and the
  implementation change together — and you get the user's explicit agreement
  before touching any of them.
- **Package breakage** — a staged extension (`pi-subagents`, `pi-web-access`,
  `pi-math`) changed shape. Treat as adapter drift; if it cannot be absorbed,
  keep that package pinned.

### 5. Fix under the invariants

- `gate-core/` stays pi-independent; version knowledge lands in `pi-adapter/`.
- Never edit `test/` or `contracts/` to make a red test pass — that is the revise
  door, and it needs the user.
- A failing test is a finding, not an obstacle.

### 6. Verify and re-run

`lpi test` green, every invariant covered (re-run the failed e2e flow too). If it
is not, return to step 4 with the new failure. Then re-run `lpi update --e2e` to
promote.

### 7. Hand back

State the outcome. If the revise door was used, state the contract change and
that the update will now pass. If the break is an upstream pi regression you
cannot absorb, leave the pin in place, record the blocker, and suggest an
upstream issue. If promotion changed versions and something looks wrong,
`~/learning-pi/bin/lpi rollback` restores the previous set.

## Inspect mode (read-only)

Never touch the real `~/learning-system` or `~/.pi/agent`, and never change
pins. Sandbox only.

### Start with the scripted tier

```bash
~/learning-pi/bin/lpi e2e --list                 # the journeys
~/learning-pi/bin/lpi e2e --diff                 # only flows touched by the git diff
~/learning-pi/bin/lpi e2e --flows lesson,review  # explicit flows
~/learning-pi/bin/lpi e2e --tier full            # each journey to its natural settle
```

Read `~/.cache/learning-pi/e2e-*/summary.json` and the per-scenario `<id>.json`.
Pass means: the expected subagents ran clean, receipts appeared, no terminal
withhold.

### Improvise when needed

For a bigger change, or when the scripted tier passes but you want a real pass:

1. Build a sandbox with model access (never the real agent dir):
   `S=$(~/learning-pi/harness/mk-sandbox.sh --layer ~/learning-pi --model-access | tail -1)`
2. Drive pi headless against it (RPC mode), exactly as `harness/e2e-runner.py`
   does: env `PI_CODING_AGENT_DIR=$S/agent`, `PI_CODING_AGENT_SESSION_DIR=$S/sessions`,
   cwd `$S/state`, argv `pi --mode rpc --name e2e-<tag>`.
3. Send real learner turns: `/lesson`, `/teach <topic>`, `/review`, `/ingest <text>`,
   `/show <concept>`, `/pause`, `/continue`. Wait for `agent_settled`.
4. Judge the session `.jsonl`: every gated turn must carry a real verifier receipt;
   no `⛔ WITHHELD`, `NO_REVIEW_CONTEXT`, or `NO_GRADE_AUDIT_PASS` should reach the
   learner as the final turn. Check subagent runs with
   `python3 ~/learning-pi/pi/audit_gates.py --session <file>`.
5. Remove the sandbox when done.

### Report

Write a short report: what you ran, what passed, what failed, the exact banner or
receipt that failed, and whether the cause is a layer change or model turn-hygiene.
Keep failing session transcripts as evidence.

## Rules

- Update mode changes pins; inspect mode does not. Never promote without a green gate.
- Never read or write `~/learning-system` or `~/.pi/agent` state in a sandbox session.
- Never edit `test/`, `contracts/`, or `CONTRACT.md` to make a test or journey pass —
  that is the revise door and needs the user's explicit agreement.
- A withhold is a finding, not a nuisance: report the code and the turn.
- The revise door, when agreed, edits `CONTRACT.md`, `contracts/learning-core.json`,
  the tagged test, and the implementation together, in one commit.

## References

`~/learning-pi/CONTRACT.md`, `~/learning-pi/README.md`,
`~/learning-pi/FIELD-GUIDE.md`, and `man lpi`.
