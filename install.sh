#!/usr/bin/env bash
# install.sh — wire the pi learning layer into a learning-system checkout.
#
# Creates symlinks in <STATE_ROOT>/.pi pointing at this repo's .pi/, and makes
# git ignore them. Nothing is copied or committed into the state repo.
#
# Usage:
#   ./install.sh [STATE_ROOT]
# STATE_ROOT resolution: arg, else $LEARNING_SYSTEM_ROOT, else ~/learning-system.

set -euo pipefail

PI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_ROOT="${1:-${LEARNING_SYSTEM_ROOT:-$HOME/learning-system}}"
STATE_ROOT="$(cd "$STATE_ROOT" 2>/dev/null && pwd || true)"

if [ -z "$STATE_ROOT" ] || [ ! -d "$STATE_ROOT/Learning System" ]; then
  echo "error: '$STATE_ROOT' does not look like a learning-system checkout (missing 'Learning System/')." >&2
  exit 2
fi

ENTRIES=(APPEND_SYSTEM.md settings.json skills prompts agents extensions)
mkdir -p "$STATE_ROOT/.pi"

for entry in "${ENTRIES[@]}"; do
  src="$PI_ROOT/.pi/$entry"
  dst="$STATE_ROOT/.pi/$entry"
  [ -e "$src" ] || { echo "skip (missing): $entry"; continue; }
  rm -rf "$dst"
  ln -s "$src" "$dst"
  echo "linked .pi/$entry"
done

# Keep the overlay out of the state repo without touching its tracked .gitignore.
EXCLUDE="$STATE_ROOT/.git/info/exclude"
if [ -d "$STATE_ROOT/.git/info" ]; then
  if ! grep -qxF ".pi/" "$EXCLUDE" 2>/dev/null; then
    printf "\n# pi learning layer (local-only)\n.pi/\n" >> "$EXCLUDE"
    echo "excluded .pi/ in .git/info/exclude"
  else
    echo ".pi/ already excluded"
  fi
else
  echo "warning: no .git/info/exclude (not a git repo?) — .pi/ will show as untracked"
fi

cat <<EOF

Installed. Next:
  1) cd "$STATE_ROOT"
  2) run: pi
  3) approve/trust the project once when prompted (.pi resources load after trust)
  4) try: /review, /lesson, /continue, /teach <topic>, /ingest <content>

State repo:  $STATE_ROOT  (untouched except for the untracked .pi/ symlinks)
Pi layer:    $PI_ROOT
EOF
