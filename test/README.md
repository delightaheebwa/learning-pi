# test/ — suite → invariant map (run via `scripts/learn-check`)

- `gate_test.mjs` — core gate behavior (mocked pi).
- `golden/` — write-gate / scout / review-delegation / retry / demotion scenarios.
- `judge_test.mjs` / `judge_model_test.mjs` / `judge_router_test.mjs` / `judge_dump_test.mjs` — judge suites; `live_judge_test.mjs` needs real models (opt-in).
- `redteam/` — adversarial suites.
- `contract/` (`check_learning_layer.py`, `load_probe.py`) — resource checks; load probe needs the pi binary (`--no-load` skips it in CI).
- `bridge/` (`test_bridge.py`, `fake_pi.py`, `run_tests.py`) — bridge `B-*` coverage; deterministic, no models/network.
- `e2e/scenarios/` (7 scenarios) — smoke runs by default; `*-full.json` need models (`--tier full`).
- `fixtures/make_state_fixture.py` — synthetic learning-system state (never real data).
- `pi_review_status_test.sh` — `bin/pi-review-status` boundary tests.
