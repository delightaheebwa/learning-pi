#!/usr/bin/env bash
# Re-vendor the agent-skills pack from the pinned upstream commit, reapply the
# project's local patches, and verify the result. See .opencode/UPSTREAM.md.
set -euo pipefail

# TAG is display-only. SHA is authoritative: fetching by SHA makes git verify
# the objects against it, so a tampered download cannot silently change content.
TAG="0.6.15"
SHA="301b02b12bff98e4688e6984af6556802322bbde"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "skills-sync: fetching $TAG ($SHA)"
git init --quiet "$TMP/src"
git -C "$TMP/src" remote add origin https://github.com/addyosmani/agent-skills
git -C "$TMP/src" fetch --quiet --depth 1 origin "$SHA"
git -C "$TMP/src" checkout --quiet --detach FETCH_HEAD
SRC="$TMP/src"

if [[ ! -d "$SRC/skills" ]]; then
  echo "skills-sync: unexpected checkout layout (no skills/ in $SRC)" >&2
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
