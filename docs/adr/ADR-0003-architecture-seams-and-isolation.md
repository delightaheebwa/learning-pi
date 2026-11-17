# ADR-0003: Keep the modular monolith and leave the learning lock as it is

- Status: Accepted
- Date: 2026-11-17
- Deciders: repo owner

## Context

A review asked whether a different architecture pattern would better serve six goals: swap components easily, maintainability, low complexity, easy tests, low latency, and isolation of a review from a teaching failure.

The review found the intended pattern already present in small form. `gate-core/` is pure and must not import pi shapes. `pi-adapter/` is the only file that knows pi's wire format. The judge and the ledger are injected. `bridge/stream.py`, `bridge/align.py`, and `bridge/session_store.py` are pure. `test/bridge/fake_pi.py` is a test double. Commit `c0cd848` made the core and adapter split. ADR-0001 records why the cross-language boundary is the wire format and not a shared module.

Teaching and review are the same main pi persona, chosen by a flow marker. They are not separate services, so there is no service hop to remove. Their response time is the serial verifier chain, and the contract pins that chain.

Isolation already has strong protection. Each chat runs its own `pi` process. A new flow marker resets the gate run. Receipts are per process and consumed per message. Content verdicts fail closed. Only the clerks write. File moves are atomic.

The remaining coupling is the bridge's learning lock. The bridge holds it for the whole learning turn (`bridge/server.py`). A hung teaching turn makes learning and review turns in other chats wait.

## Decision

Adopt no new pattern. Keep the modular monolith and state two rules. Behavior lives in `gate-core/`. The pi wire format is absorbed by `pi-adapter/` or a new adapter file. Each chat keeps its own pi process, and that process is the isolation boundary.

Do not narrow the learning lock in this change. The single-writer rule is a hard invariant in `contracts/learning-core.json`, in the `B-*` bridge set, and its tagged tests live in the frozen `test/` tree. The bridge also cannot scope the lock to the write step. The notebook writes happen inside the pi subprocess, and the bridge does not observe them. Narrowing the lock needs either a contract change through the revise door or a new gate-to-bridge write signal. Both are larger than a refactor, and neither was taken.

Do not add a runtime notebook port. Agents write the notebook through `state/scripts/ops.py`, not through bridge code, so a Python port would have no runtime consumer. The existing test doubles and temp-root tests already cover the Python readers.

## Consequences

- No source behavior changes. The gate and adapter split, the per-chat process, and the lock stay as they are.
- A teaching hang can still delay a review by up to the turn budget. That is the accepted cost of the single-writer rule.
- Changing a model or judge backend stays a `pi-adapter` or `settings.json` change. Changing the notebook format stays a coordinated change across the sidecars, the prompts, and the contract tests.
- The async run-id regex is now pinned across the two languages by `harness/wire_parity_test.py`, so a pi-subagents change cannot update one copy and miss the other.

## Revisit when

- A review turn must be provably unaffected by a hung teaching turn. Then choose one: a gate-to-bridge write signal, or a revise-door change to the lock.
- A second runtime consumer of the notebook appears. Then the store port has a consumer and earns an adapter.
- A third consumer of the pi wire format appears. ADR-0001's revisit condition then applies.
