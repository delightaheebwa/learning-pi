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

# Wire Antigravity Desktop layer (.agents/) if antigravity/ exists
AGY_ROOT="$PI_ROOT/antigravity"
if [ -d "$AGY_ROOT" ]; then
  mkdir -p "$STATE_ROOT/.agents"
  AGY_ENTRIES=(AGENTS.md hooks.json scripts agents skills)
  for entry in "${AGY_ENTRIES[@]}"; do
    src="$AGY_ROOT/$entry"
    dst="$STATE_ROOT/.agents/$entry"
    [ -e "$src" ] || { echo "skip (missing): $entry"; continue; }
    rm -rf "$dst"
    ln -s "$src" "$dst"
    echo "linked .agents/$entry"
  done
fi

# Keep overlays out of the state repo without touching its tracked .gitignore.
EXCLUDE="$STATE_ROOT/.git/info/exclude"
if [ -d "$STATE_ROOT/.git/info" ]; then
  for excl in ".pi/" ".agents/"; do
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

  Antigravity Desktop:
    1) Open "$STATE_ROOT" as a project/workspace in Antigravity Desktop
    2) Slash commands: /teach, /lesson, /continue, /pause, /review, /solo, /ingest, /audit
    3) Subagents (scout, verifier, ui-generator, clerk, auditor) run via invoke_subagent and monitor in the Subagents panel

State repo:  $STATE_ROOT  (untouched except for untracked .pi/ & .agents/ symlinks)
Control repo: $PI_ROOT
EOF
