#!/usr/bin/env bash
# audit-recent-sessions.sh — weekly read-only gate-provenance audit.
#
# Runs pi/audit_gates.py over every learning-system session touched in the last
# 7 days and appends the results to a log. Read-only; exit 0 always (this is a
# standing safety net, not a gate). Invoked by the learning-pi-audit systemd
# user timer.
set -uo pipefail

LAYER="${LEARNING_PI_ROOT:-$HOME/learning-pi}"
SESS_DIR="${PI_SESSION_DIR:-$HOME/.pi/agent/sessions/--home-delight-learning-system--}"
LOG="${XDG_CACHE_HOME:-$HOME/.cache}/learning-pi/audit-recent.log"
mkdir -p "$(dirname "$LOG")"

{
  echo "=== $(date -Is) ==="
  if [ ! -d "$SESS_DIR" ]; then
    echo "no session directory: $SESS_DIR"
    echo
    exit 0
  fi
  found=0
  while IFS= read -r -d '' f; do
    found=1
    echo "--- $f"
    python3 "$LAYER/pi/audit_gates.py" --session "$f" 2>&1 | tail -40
    echo
  done < <(find "$SESS_DIR" -maxdepth 1 -name '*.jsonl' -mtime -7 -print0 2>/dev/null)
  [ "$found" = 1 ] || echo "no sessions modified in the last 7 days"
  echo
} >>"$LOG" 2>&1
