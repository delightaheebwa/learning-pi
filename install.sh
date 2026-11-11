#!/usr/bin/env bash
# install.sh — wire the pi learning layer into a learning-state tree.
#
# Creates symlinks in <STATE_ROOT>/.pi pointing at this repo's .pi/, and makes
# git ignore them. Nothing is copied or committed into the state repo.
#
# Usage:
#   ./install.sh [STATE_ROOT]
# STATE_ROOT resolution: arg, else $LEARNING_SYSTEM_ROOT, else <layer>/state.

set -euo pipefail

PI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUESTED_ROOT="${1:-${LEARNING_SYSTEM_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/state}}"
STATE_ROOT="$(cd "$REQUESTED_ROOT" 2>/dev/null && pwd || true)"

if [ -z "$STATE_ROOT" ] || [ ! -d "$STATE_ROOT/Learning System" ]; then
  echo "error: '$REQUESTED_ROOT' does not look like a learning-system checkout (missing 'Learning System/')." >&2
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

# Keep overlays out of the state repo without touching its tracked .gitignore.
EXCLUDE="$STATE_ROOT/.git/info/exclude"
if [ -d "$STATE_ROOT/.git/info" ]; then
  for excl in ".pi/"; do
    if ! grep -qxF "$excl" "$EXCLUDE" 2>/dev/null; then
      printf "\n# learning overlays (local-only)\n%s\n" "$excl" >> "$EXCLUDE"
      echo "excluded $excl in .git/info/exclude"
    else
      echo "$excl already excluded"
    fi
  done
else
  echo "warning: no .git/info/exclude (not a git repo?) — overlays will show as untracked"
fi

cat <<EOF

Installed. Next:
  CLI (pi):
    1) cd "$STATE_ROOT"
    2) run: pi (approve/trust once)
    3) try: /review, /lesson, /continue, /teach <topic>, /ingest <content>

State repo:  $STATE_ROOT  (untouched except for untracked .pi/ symlinks)
Control repo: $PI_ROOT
EOF
