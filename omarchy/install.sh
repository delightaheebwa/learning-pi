#!/usr/bin/env bash
# install.sh — deploy the pi review integration into an Omarchy session.
#
# Installs:
#   ~/.local/bin/pi-review-status          (symlink -> bin/pi-review-status)
#   ~/.local/bin/review-reminder.sh        (symlink -> omarchy/review-reminder.sh)
#   ~/.config/systemd/user/review-reminder.{service,timer}
#   ~/.config/omarchy/plugins/local.pi-review/   (copied, never symlinked)
#
# Then validates the plugin, rescans it, enables it, and places it in the bar.
#
# Usage: ./install.sh [--no-shell]
#   --no-shell   skip rescan/enable/restart (useful on a headless box)
set -euo pipefail

OMARCHY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PI_ROOT="$(cd "$OMARCHY_DIR/.." && pwd)"
PLUGIN_ID="local.pi-review"
PLUGIN_DEST="$HOME/.config/omarchy/plugins/$PLUGIN_ID"
BIN_DIR="$HOME/.local/bin"
UNIT_DIR="$HOME/.config/systemd/user"

DO_SHELL=1
[[ "${1:-}" == "--no-shell" ]] && DO_SHELL=0

mkdir -p "$BIN_DIR" "$UNIT_DIR" "$(dirname "$PLUGIN_DEST")"

# --- helpers (symlinks; safe to update in place) -----------------------------
ln -sf "$PI_ROOT/bin/pi-review-status" "$BIN_DIR/pi-review-status"
ln -sf "$OMARCHY_DIR/review-reminder.sh" "$BIN_DIR/review-reminder.sh"
echo "linked $BIN_DIR/pi-review-status"
echo "linked $BIN_DIR/review-reminder.sh"

# --- reminder timers ---------------------------------------------------------
install -m644 "$OMARCHY_DIR/systemd/review-reminder.service" "$UNIT_DIR/"
install -m644 "$OMARCHY_DIR/systemd/review-reminder.timer" "$UNIT_DIR/"
if command -v systemctl >/dev/null 2>&1; then
  systemctl --user daemon-reload || true
  systemctl --user enable --now review-reminder.timer || true
  echo "enabled review-reminder.timer"
fi

# --- plugin (copy: the plugin validator rejects symlinks inside the folder) --
rm -rf "$PLUGIN_DEST"
cp -R "$PI_ROOT/omarchy/plugin" "$PLUGIN_DEST"
echo "installed plugin $PLUGIN_DEST"

if command -v omarchy-plugin-validate >/dev/null 2>&1; then
  omarchy-plugin-validate "$PLUGIN_DEST" && echo "validated $PLUGIN_ID"
fi

# --- wire it into the running shell -----------------------------------------
if [[ "$DO_SHELL" == "1" ]]; then
  command -v omarchy-shell >/dev/null 2>&1 && omarchy-shell shell rescanPlugins >/dev/null 2>&1 || true
  command -v omarchy-plugin-enable >/dev/null 2>&1 && omarchy-plugin-enable "$PLUGIN_ID" >/dev/null 2>&1 || true
  command -v omarchy-bar >/dev/null 2>&1 && omarchy-bar put "$PLUGIN_ID" --after omarchy.tray >/dev/null 2>&1 || true
  command -v omarchy-restart-shell >/dev/null 2>&1 && omarchy-restart-shell >/dev/null 2>&1 || true
  echo "enabled $PLUGIN_ID (move it with: omarchy bar put $PLUGIN_ID --after <widget>)"
fi

echo
echo "Done. Status now: $(pi-review-status --json)"
