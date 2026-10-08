#!/usr/bin/env bash
# Poll until all four reviewer outputs exist and are non-empty. Re-runnable.
#
#   wait-for-reviews.sh [timeout_seconds]   (default 300)
#
# Exit 0 when docs/roadmap/reviews/{P0,P1,P2,P3}.md all exist and are non-empty.
# Exit 1 on timeout. If the calling agent's shell tool times out, just run it
# again — it always re-checks from scratch.
set -uo pipefail

ROOT="/home/delightaheebwa/learning-pi"
DIR="$ROOT/docs/roadmap/reviews"
TIMEOUT="${1:-300}"
DEADLINE=$(( $(date +%s) + TIMEOUT ))

while :; do
  missing=""
  for cp in P0 P1 P2 P3; do
    [ -s "$DIR/$cp.md" ] || missing="$missing $cp"
  done
  if [ -z "$missing" ]; then
    echo "all reviews present"
    exit 0
  fi
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    echo "timeout: review file(s) still missing:$missing"
    exit 1
  fi
  sleep 15
done
