# omarchy/

Omarchy review integration: a `local.pi-review` bar widget, a desktop reminder,
and a systemd timer.

- To install, run `~/learning-pi/omarchy/install.sh`.
- The shared `bin/pi-review-status` reports review status. It matches the
  calendar date, sets `visible` from 18:00 to 03:59, and sets `missed` from
  23:00.
