# Test suites and the invariants they cover

`scripts/learn-check` runs these suites.

- `gate_test.mjs`: core gate behavior, with a mocked pi.
- `golden/`: write-gate, scout, review-delegation, retry, and demotion
  scenarios.
- `judge_test.mjs`, `judge_model_test.mjs`, `judge_router_test.mjs`, and
  `judge_dump_test.mjs`: judge suites. `live_judge_test.mjs` needs real models,
  so you must opt in.
- `redteam/`: adversarial suites.
- `contract/` (`check_learning_layer.py`, `load_probe.py`): resource checks. The
  load probe needs the pi binary, and `--no-load` skips it in CI.
- `bridge/` (`test_bridge.py`, `fake_pi.py`, `run_tests.py`): `B-*` coverage for
  the bridge. These tests are deterministic and need no models or network.
- `e2e/scenarios/` (7 scenarios): smoke runs by default. The `*-full.json`
  scenarios need models, which you request with `--tier full`.
- `fixtures/make_state_fixture.py`: synthetic learning-system state, never real
  data.
- `pi_review_status_test.sh`: boundary tests for `bin/pi-review-status`.
