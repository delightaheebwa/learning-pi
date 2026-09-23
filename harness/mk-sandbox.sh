#!/usr/bin/env bash
# mk-sandbox.sh — build an isolated duplicate harness for learn-check.
#
# Everything runs under a throwaway directory; the real ~/.pi/agent and
# ~/learning-system are never read or written (CONTRACT.md S-2). Isolation uses
# documented pi levers: PI_CODING_AGENT_DIR, a pre-seeded trust.json, and a
# fixture project whose .pi/ is the learning-pi overlay.
#
# Usage:
#   harness/mk-sandbox.sh [--pi BIN] [--layer DIR] [--dest DIR]
# Prints the sandbox root (absolute) on stdout. Layout:
#   <root>/agent     PI_CODING_AGENT_DIR (trust.json, settings.json)
#   <root>/sessions  PI_CODING_AGENT_SESSION_DIR
#   <root>/state     fixture learning-system checkout + .pi overlay
#   <root>/probe     load-probe extension (imports the real layer modules)
set -euo pipefail

LAYER="${LEARNING_PI_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PI_BIN="${LEARN_CHECK_PI:-$LAYER/bin/pi}"
DEST=""
PACKAGES_JSON=""

while [ $# -gt 0 ]; do
  case "$1" in
    --pi) PI_BIN="$2"; shift 2 ;;
    --layer) LAYER="$2"; shift 2 ;;
    --packages) PACKAGES_JSON="$2"; shift 2 ;;
    --dest) DEST="$2"; shift 2 ;;
    *) echo "mk-sandbox: unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$DEST" ]; then
  DEST="$(mktemp -d "${TMPDIR:-/tmp}/learning-pi-sandbox.XXXXXX")"
fi
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"

mkdir -p "$DEST/agent" "$DEST/sessions" "$DEST/state" "$DEST/probe"

# Synthetic state (never the real learning-system).
python3 "$LAYER/test/fixtures/make_state_fixture.py" "$DEST/state" >/dev/null

# Project overlay: symlinks, exactly like install.sh.
mkdir -p "$DEST/state/.pi"
for entry in APPEND_SYSTEM.md settings.json skills prompts agents extensions; do
  src="$LAYER/.pi/$entry"
  [ -e "$src" ] || continue
  rm -rf "$DEST/state/.pi/$entry"
  ln -s "$src" "$DEST/state/.pi/$entry"
done

# Sandbox pi config: trust the fixture project so project resources load
# headless, and add the load probe as an explicit extension path. Optionally
# carry candidate package specs so `pi install` stages them here, not in the
# real ~/.pi/agent.
printf '{"%s": true}\n' "$DEST/state" > "$DEST/agent/trust.json"
if [ -n "$PACKAGES_JSON" ]; then
  python3 - "$PACKAGES_JSON" <<'PY' >"$DEST/agent/packages.json" || { echo "mk-sandbox: --packages must be a JSON array" >&2; exit 2; }
import json, sys
data = json.loads(sys.argv[1])
if not isinstance(data, list):
    raise SystemExit("not a list")
print(json.dumps(data))
PY
  python3 - "$DEST" "$DEST/agent/packages.json" <<'PY'
import json, sys
dest, pkgfile = sys.argv[1], sys.argv[2]
packages = json.load(open(pkgfile))
settings = {"extensions": [f"{dest}/probe/lp-load-probe.ts"], "packages": packages}
open(f"{dest}/agent/settings.json", "w").write(json.dumps(settings))
PY
else
  printf '{"extensions": ["%s/probe/lp-load-probe.ts"]}\n' "$DEST" > "$DEST/agent/settings.json"
fi

# Load probe: importing the real entry modules validates the module graph
# resolves under the candidate pi; the sentinel command proves the probe itself
# loaded. A broken import/throw fails the probe factory loudly (stderr).
cat > "$DEST/probe/lp-load-probe.ts" <<EOF
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import "$LAYER/.pi/extensions/learning-gate/index.ts";
import "$LAYER/.pi/extensions/math-mode/index.ts";
export default function (pi: ExtensionAPI): void {
  pi.registerCommand("lp-load-probe", {
    description: "learning-pi load probe (harness only)",
    handler: async () => {},
  });
}
EOF

printf '%s\n' "$DEST"
