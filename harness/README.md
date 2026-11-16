# harness/

- `pi-safe-update`: the update conductor behind `lpi update`. It runs a pin
  check, a sandbox, and `learn-check`, then promotes the candidate. On failure
  it writes a diagnosis report.
- `e2e-runner.py`: the e2e runner (`--tier smoke|full --jobs N`). The full tier
  needs real models.
- `mk-sandbox.sh`: builds an isolated duplicate harness. Its flags are `--layer`
  and `--model-access`. `lpi update` and the `lpi` skill use it.
- `locktool.py`: helper for `versions.lock.json` and the journal.
- `audit-recent-sessions.sh` and `systemd/`: a weekly provenance audit over real
  sessions.
- `man/lpi.1`: the `lpi` man page.
- `protocol_sync_test.py`: pins the shared markers of the two stress-test
  protocol copies. It checks presence, not semantics.
