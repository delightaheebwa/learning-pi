# Access: legacy Open WebUI stack (frozen)

This is an inherited record from the retired standalone `learning-system`
checkout. The table and networking notes that used to be here described a
two-repo setup: a WSL maintenance checkout, an Open Terminal container
checkout, a `learning-system` GitHub remote, and a Windows-side Docker Desktop
host. None of that is current. Do not follow its paths, remotes, or commands.
The old text stays in git history.

Current access references:

- The Open WebUI face lives in [`deploy/`](../../deploy/README.md) and is Linux
  only. Compose publishes it on `127.0.0.1:3000`. See `deploy/docker-compose.yml`
  and [`deploy/SECURITY.md`](../../deploy/SECURITY.md) for the loopback binding
  and the firewall requirements.
- The pi layer and the learner state are one repo:
  [`learning-pi`](https://github.com/delightaheebwa/learning-pi), with state
  under `state/`. Run `pi` from `~/learning-pi/state`.
- Teaching behavior and models: the root [`README.md`](../../README.md) and
  [`FIELD-GUIDE.md`](../../FIELD-GUIDE.md). Configuration lives in
  `.pi/settings.json`.
- `state/infra/` holds the compose file, the backup and restore scripts, and the
  version notes. It is a frozen snapshot of the retired stack, kept for
  historical reference.
