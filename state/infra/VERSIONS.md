# Versions: legacy Open WebUI stack (frozen)

This is an inherited record from the retired standalone `learning-system`
checkout. The image digests, model presets, and repo-state lines that used to be
here were a 2026-09-08 snapshot of the old two-repo setup. Do not follow its
remotes, paths, model IDs, or upgrade procedure. The old text stays in git
history.

Current version references:

- Open WebUI deployment, including image pins, ports, and `pi-bridge`: see
  [`deploy/README.md`](../../deploy/README.md) and `deploy/docker-compose.yml`.
- Tutor and verifier models: `.pi/settings.json`, documented in the root
  [`README.md`](../../README.md) and [`FIELD-GUIDE.md`](../../FIELD-GUIDE.md).
- Repo and state location:
  [`learning-pi`](https://github.com/delightaheebwa/learning-pi), with state
  under `state/`. The pinned pi runtime and extension versions live in the root
  `versions.lock.json`.
- `state/infra/` holds the compose file, the backup and restore scripts, and
  these notes. It is a frozen snapshot of the retired stack, kept for historical
  reference.
