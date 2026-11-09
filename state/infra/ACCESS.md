# ACCESS — every surface, how to reach it, what lives there

> Read this before touching the system. Cross-reference: `infra/VERSIONS.md`
> (what is pinned), `AGENTS.md` (repo conventions + change protocol).

## Surfaces

| Surface | Where | Access | What lives there |
| --- | --- | --- | --- |
| Open WebUI UI | http://localhost:3000 (from Windows/WSL) | browser login | chats, presets, skills, prompts, functions, tools, configs |
| Open WebUI REST API | http://localhost:3000/api/v1/… | `Authorization: Bearer $(cat ~/.openwebui_key)` | same objects as UI; correct list routes: `/api/v1/models`, `/api/v1/skills/list`, `/api/v1/prompts/list`, `/api/v1/functions/list`, `/api/v1/configs/subagents` (no trailing slash) |
| open-webui container | `docker exec -it open-webui bash` | shell | `/app/backend/data` = named volume `open-webui` (webui.db, vector_db, uploads) |
| Open Terminal container | `docker exec -it open-terminal bash` | shell | `/home/user/learning-system` (runtime repo checkout, volume `open-terminal`) |
| Open Terminal tool-server | http://172.17.0.1:8000 (from open-webui container) | key in webui.db `tool_server.connections` | what powers the models' terminal capability |
| SearXNG | http://localhost:8080 | HTTP | web search backend (portable file uses named volume `searxng-config`; legacy live setup used host dir `~/searxng-docker/searxng/settings.yml`) |
| GitHub | https://github.com/delightaheebwa/learning-system | git (GCM in WSL / store in container) | the durable source of truth |
| WSL maintenance checkout | `/home/delightaheebwa/learning-system` | this shell | refactor work; push/pull to sync |
| webui.db direct | `docker exec open-webui python3 -c "import sqlite3; …"` (no sqlite3 binary in image) | python | chats, models, config, prompts, functions, tools tables |

## Networking facts (learned the hard way)

- Docker Desktop runs **Windows-side**; WSL is a separate engine view. From WSL,
  the UI is `http://localhost:3000`; from inside the containers, the WSL/host is
  `host.docker.internal` (open-webui reaches SearXNG at `host.docker.internal:8080`,
  Ollama at `host.docker.internal:11434`, and Open Terminal at `172.17.0.1:8000`).
- The two repo checkouts (container `/home/user/learning-system` vs WSL
  `/home/delightaheebwa/learning-system`) are SEPARATE working copies of the same GitHub
  remote. Sync only via git push/pull — never edit both in one session.
- `webui.db` is SQLite. There is no `sqlite3` CLI in the image — use
  `docker exec open-webui python3 -c …` with the sqlite3 module.
- API key file: `~/.openwebui_key` (WSL). Export as `OPENWEBUI_API_KEY` for
  `scripts/setup_openwebui.py` / `scripts/audit_openwebui.py`.

## Common tasks

```bash
# Drift audit (read-only): does live Open WebUI match the repo?
OPENWEBUI_API_KEY=$(cat ~/.openwebui_key) python3 scripts/audit_openwebui.py

# Re-seed control layer after repo edits (skills/prompts/function/subagent prompt)
OPENWEBUI_API_KEY=$(cat ~/.openwebui_key) python3 scripts/setup_openwebui.py

# Backup / restore volumes
infra/backup.sh              # -> ./backups/<date>/
infra/restore.sh <dir>       # fresh host only, before first compose up

# Full stack from scratch (fresh laptop)
docker compose -f infra/docker-compose.yml up -d

# Read a chat programmatically (debugging gate blocks)
curl -s -H "Authorization: Bearer $KEY" http://localhost:3000/api/v1/chats/<id> | python3 -m json.tool
```

## Where a given piece of state is authoritative

| State | Authoritative copy | Mirrors |
| --- | --- | --- |
| Learning state (Active Concepts, sessions, wiki, archive) | GitHub (via repo) | container + WSL checkouts |
| Control layer (skills, presets, prompts, gate function, subagent prompt) | `scripts/setup_openwebui.py` in the repo (seeded into webui.db) | live Open WebUI (webui.db) |
| Chats / conversations / memory / files | webui.db (volume `open-webui`) | none — backup via `infra/backup.sh` |
| Terminal repo working tree | GitHub | volume `open-terminal` + WSL checkout |
| Models/connection config (base models, API keys, headers) | webui.db (UI-owned) | `infra/VERSIONS.md` records current values |
