#!/usr/bin/env bash
# Backup the named Docker volumes that hold ALL learning-system state.
#   open-webui volume  -> chats, presets, skills, prompts, functions, configs, tools (webui.db + vector_db + uploads)
#   open-terminal vol  -> /home/user/learning-system working repo
# The GitHub repo (source of truth) is backed up by git itself.
#
# Usage: infra/backup.sh [dest-dir]     (default: ./backups/<date>)
set -euo pipefail
DEST="${1:-./backups/$(date +%Y-%m-%d)}"
mkdir -p "$DEST"

for vol in open-webui open-terminal; do
  echo "== $vol =="
  docker run --rm -v "$vol":/src:ro -v "$(cd "$DEST" && pwd)":/dst alpine \
    tar czf "/dst/${vol}.tar.gz" -C /src .
done

# Optional: logical DB snapshot of webui.db (cleaner than raw volume for the DB alone)
docker exec open-webui python3 -c "
import sqlite3, hashlib
db = sqlite3.connect('/app/backend/data/webui.db')
db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
print('wal checkpointed')
" 2>/dev/null || echo "(skip wal checkpoint — container not running)"

echo "Done. Backups in: $DEST"
ls -lh "$DEST"
