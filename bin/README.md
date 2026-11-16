# bin/

`pi` here is the canonical launcher. Install it, or symlink it, as
`~/.local/bin/pi`. It never updates anything.

- It reads the pinned pi version from `../versions.lock.json`.
- It runs that exact binary directly. A `mise use -g pi` elsewhere therefore
  cannot silently change what a learning session runs on.
- It starts `notify-if-outdated` in the background at most once per day. That
  script only reports a newer candidate: a status file in
  `$XDG_CACHE_HOME/learning-pi/`, plus a desktop notification.

Updates happen only through `lpi update`, which `../harness/pi-safe-update`
backs. That command tests a candidate against `lpi test` before it promotes the
candidate into `versions.lock.json`.

`pi-review-status` reports whether the day's spaced-repetition `/review` is
done. It matches the calendar date that review-clerk stamps on the session note,
so a review finished at 1am counts as that day's review, not the previous day's.
The `local.pi-review` Omarchy bar widget and the desktop reminder share this
single detection source:

```bash
pi-review-status --json          # {"date":"YYYY-MM-DD","done":bool,"visible":bool,"missed":bool}
pi-review-status --check DATE    # exit 0 if a review exists for DATE
```

`visible` marks the evening window (18:00–03:59), when the bar indicator shows.
`missed` is true when today's review is not done and the hour is already 23 or
later.

`lpi` is the umbrella control command:

```bash
lpi                 # what's newer (read-only)
lpi update          # stage + gate + promote pi and extensions; diagnose on failure
lpi test            # run the learning-layer test suite
lpi e2e             # replay short learner journeys in a sandbox (real models)
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

Set `PI_OFFLINE=1` in the environment. It also disables pi's own startup network
operations.
