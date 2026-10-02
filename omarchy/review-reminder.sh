#!/usr/bin/env bash
#
# review-reminder.sh — nudge when the day's spaced-repetition /review was missed.
#
# Two windows, both meaning "the evening after the day's review was due":
#   23:00-23:59  -> target = today
#   00:00-03:59  -> target = yesterday   (4am cutoff, so a review done at 1am
#                                         still counts for the day it was due)
# Outside those windows it does nothing, so the systemd timer and the shell
# prompt hook can both call it freely.
#
# A successful /review always writes one Session note named
#   Session — ...Review — YYYY-MM-DD.md
# so that filename is the detection signal (not mtime / "last 24h": a 1am write
# carries yesterday's logical date but today's mtime). Detection is delegated
# to `pi-review-status --check` so the bar widget and this reminder can never
# disagree.
#
# This is a notification only — the persistent status lives in the
# local.pi-review bar widget. Reminds at most once per target day, recorded in
#   ~/.local/state/review-reminder-YYYY-MM-DD.sent
# and always silently if the review note already exists.
#
# Test hooks (harmless in normal runs):
#   REVIEW_REMINDER_TARGET=YYYY-MM-DD   force the target day
#   REVIEW_REMINDER_FORCE=1             ignore the clock window
#   LEARNING_SYSTEM_ROOT=/path          override the checkout location
#   PI_REVIEW_STATUS_BIN=/path          override the status helper
#
set -euo pipefail

ROOT="${LEARNING_SYSTEM_ROOT:-$HOME/learning-system}"
SESSIONS="$ROOT/Learning System/Sessions"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}"
STATUS_BIN="${PI_REVIEW_STATUS_BIN:-$HOME/.local/bin/pi-review-status}"

# review_done <date>: 0 if that day's review session note exists.
review_done() {
  local date=$1 hit
  if [[ "$date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] && [[ -x "$STATUS_BIN" ]]; then
    if "$STATUS_BIN" --check "$date"; then
      return 0
    fi
    return 1
  fi
  # Fallback if the helper is not deployed: same filename rule, inline.
  [[ -d "$SESSIONS" ]] || return 1
  hit="$(find "$SESSIONS" -maxdepth 1 -type f -name "Session*Review*${date}.md" -print -quit 2>/dev/null || true)"
  if [[ -n "$hit" ]]; then
    return 0
  fi
  return 1
}

# --- decide the target day ---------------------------------------------------
if [[ -n "${REVIEW_REMINDER_TARGET:-}" ]]; then
  target="$REVIEW_REMINDER_TARGET"
else
  hour=$((10#$(date +%H)))
  if ((hour >= 23)); then
    target="$(date +%F)"
  elif ((hour < 4)); then
    target="$(date -d yesterday +%F)"
  elif [[ "${REVIEW_REMINDER_FORCE:-}" == "1" ]]; then
    target="$(date +%F)"
  else
    exit 0
  fi
fi

mkdir -p "$STATE_DIR"
sentinel="$STATE_DIR/review-reminder-${target}.sent"

# --- already reviewed today? ------------------------------------------------
if review_done "$target"; then
  : >"$sentinel"
  exit 0
fi

# --- once per target day ----------------------------------------------------
[[ -e "$sentinel" ]] && exit 0
: >"$sentinel"

# --- quiet, transient notification ------------------------------------------
if command -v omarchy-notification-send >/dev/null 2>&1; then
  omarchy-notification-send -u normal -t 15000 \
    "Review reminder" \
    "No review session for $target yet — cd ~/learning-system && pi, then /review" \
    >/dev/null 2>&1 || true
fi

exit 0
