# bin/ — pinned launcher

`pi` here is the **canonical launcher**. It is installed (or symlinked) as
`~/.local/bin/pi` and it **never updates anything**.

- It reads the pinned pi version from `../versions.lock.json`.
- It runs that exact binary directly, so a `mise use -g pi` elsewhere cannot
  silently change what a learning session runs on.
- It starts `notify-if-outdated` in the background at most once per day; that
  script only *reports* a newer candidate (status file in
  `$XDG_CACHE_HOME/learning-pi/`, plus a desktop notification).

Updates happen **only** through `../harness/pi-safe-update`, which tests a
candidate against `learn-check` before promoting it into `versions.lock.json`.

## Install

```bash
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
```

## Disable the availability check

Set `PI_OFFLINE=1` in the environment (also disables pi's own startup network
operations).
