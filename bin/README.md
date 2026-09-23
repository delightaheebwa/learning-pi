# bin/ — pinned launcher and control command

`pi` here is the **canonical launcher**. It is installed (or symlinked) as
`~/.local/bin/pi` and it **never updates anything**.

- It reads the pinned pi version from `../versions.lock.json`.
- It runs that exact binary directly, so a `mise use -g pi` elsewhere cannot
  silently change what a learning session runs on.
- It starts `notify-if-outdated` in the background at most once per day; that
  script only *reports* a newer candidate (status file in
  `$XDG_CACHE_HOME/learning-pi/`, plus a desktop notification).

Updates happen **only** through `lpi update` (backed by
`../harness/pi-safe-update`), which tests a candidate against `lpi test` before
promoting it into `versions.lock.json`.

`lpi` is the umbrella control command:

```bash
lpi                 # what's newer (read-only)
lpi update          # stage + gate + promote pi and extensions; diagnose on failure
lpi test            # run the learning-layer test suite
lpi doctor          # re-test the current pins
lpi rollback        # undo the last promotion
```

## Install

```bash
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
install -m644 ~/learning-pi/harness/man/lpi.1 ~/.local/share/man/man1/
```

## Disable the availability check

Set `PI_OFFLINE=1` in the environment (also disables pi's own startup network
operations).
