#!/usr/bin/env bash
# Restore the named volumes from infra/backup.sh archives onto a fresh host.
# Run BEFORE the first `docker compose up` (volumes must not be in use).
#
# Usage: infra/restore.sh <backup-dir>
set -euo pipefail
SRC="${1:?usage: infra/restore.sh <backup-dir>}"

for vol in open-webui open-terminal; do
  if docker volume inspect "$vol" >/dev/null 2>&1; then
    echo "!! volume $vol already exists — remove it first or restore into a fresh host" >&2
    exit 1
  fi
  echo "== restoring $vol =="
  docker volume create "$vol" >/dev/null
  docker run --rm -v "$vol":/dst -v "$(cd "$SRC" && pwd)":/src:ro alpine \
    sh -c "tar xzf /src/${vol}.tar.gz -C /dst"
done

echo "Restored. Now start the stack:"
echo "  docker compose -f infra/docker-compose.yml up -d"
echo "Then re-run the installer (idempotent) to re-seed control-layer items:"
echo "  OPENWEBUI_API_KEY=sk-... python3 scripts/setup_openwebui.py --base-url http://localhost:3000"
echo "Then clone/pull the repo inside open-terminal if the volume predates it:"
echo "  docker exec -it open-terminal bash -lc 'cd /home/user && git clone https://github.com/delightaheebwa/learning-system'"
