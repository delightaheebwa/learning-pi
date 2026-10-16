# harness/

- `pi-safe-update` — update conductor behind `lpi update` (pin check → sandbox → `learn-check` → promote → diagnosis report on failure).
- `e2e-runner.py` — e2e runner (`--tier smoke|full --jobs N`); full tier needs real models.
- `mk-sandbox.sh` — isolated duplicate harness builder (`--layer --model-access`); used by `lpi update` and the `lpi` skill.
- `locktool.py` — `versions.lock.json` / journal helper.
- `audit-recent-sessions.sh` + `systemd/` — weekly provenance audit over real sessions.
- `man/lpi.1` — `lpi` man page.
