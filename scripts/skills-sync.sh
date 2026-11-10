#!/usr/bin/env bash
# Re-vendor the agent-skills pack from the pinned upstream commit, reapply the
# project's local patches, and verify the result. See .opencode/UPSTREAM.md.
set -euo pipefail

TAG="0.6.15"
SHA="301b02b12bff98e4688e6984af6556802322bbde"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "skills-sync: fetching $TAG ($SHA)"
curl -fsSL "https://github.com/addyosmani/agent-skills/archive/${SHA}.tar.gz" \
  -o "$TMP/src.tgz"
tar -xzf "$TMP/src.tgz" -C "$TMP"
SRC="$TMP/agent-skills-${SHA}"

if [[ ! -d "$SRC/skills" ]]; then
  echo "skills-sync: unexpected archive layout (no skills/ in $SRC)" >&2
  exit 1
fi

# --exclude LICENSE keeps the vendored MIT notice; --delete removes skills that
# upstream dropped so the local inventory matches the pin.
rsync -a --delete --exclude LICENSE "$SRC/skills/" "$ROOT/.opencode/skills/"
rsync -a --delete "$SRC/references/" "$ROOT/.opencode/references/"

mkdir -p "$ROOT/.opencode/docs"
cp "$SRC/docs/agents.md" "$SRC/docs/opencode-setup.md" "$ROOT/.opencode/docs/"

python3 "$ROOT/patches/apply.py"
"$ROOT/scripts/check-skills"

echo "skills-sync: done. Review the diff, then commit."
