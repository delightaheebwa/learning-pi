---
name: pi-diagnosis-fix
description: Repair a failed pi learning-system update from its diagnosis report. Use ONLY when the user mentions an lpi update failure or diagnosis, a rejected pi/extension update, or asks to make lpi test pass after an update.
---

# pi-diagnosis-fix

Turn a rejected `lpi update` into a green `lpi test` on the current or candidate pins.

## 1. Read the evidence

- Newest report: `ls -t ~/.cache/learning-pi/diagnosis-*.md | head -1` — read it in full.
- The contract: `~/learning-pi/CONTRACT.md` and `~/learning-pi/contracts/learning-core.json`.
- Reproduce: `lpi test` (`~/learning-pi/bin/lpi test`). Keep the `FAIL` lines; each names an invariant.

## 2. Classify

Two leading words decide the fix:

- **Adapter drift** — the load probe fails, or a test fails while `gate-core/` logic is sound. pi or an extension renamed a wire shape. Fix `~/learning-pi/.pi/extensions/learning-gate/pi-adapter/` only.
- **Behavior drift** — the adapter loads but an assertion fails. Either pi behaves differently and the adapter must absorb it, or the learning system's *expectation* must change. An expectation change is the **revise door**: `CONTRACT.md`, `contracts/learning-core.json`, the tagged test, and the implementation change together — and you get the user's explicit agreement before touching any of them.
- **Package breakage** — a staged extension (`pi-subagents`, `pi-web-access`, `pi-math`) changed shape. Treat as adapter drift; if it cannot be absorbed, keep that package pinned.

## 3. Fix under the invariants

- `gate-core/` stays pi-independent; version knowledge lands in `pi-adapter/`.
- Never edit `test/` or `contracts/` to make a red test pass — that is the revise door, and it needs the user.
- A failing test is a finding, not an obstacle.

## 4. Verify

`lpi test` green, every invariant covered. If it is not, return to step 2 with the new failure.

## 5. Hand back

Tell the user to re-run `lpi update`. If the revise door was used, state the contract change and that the update will now pass. If the break is an upstream pi regression you cannot absorb, leave the pin in place, record the blocker, and suggest an upstream issue.

Completion: `lpi test` passes, and the failing step named in the diagnosis is gone.
