# Open WebUI in front of pi-bridge

Runs [Open WebUI](https://github.com/open-webui/open-webui) in Docker on this
machine as the chat front-end, talking to the **host-run** `pi-bridge` over the
Docker bridge. pi (the learning gate, subagents, skills) stays the brain and the
bridge keeps driving a real shell — so treat this deployment as security-sensitive.

```
browser 127.0.0.1:3000 ─▶ open-webui (container, pi-net)
                              │  OpenAI API  http://host.docker.internal:8790/v1
                              ▼
                    pi-bridge (host, systemd --user, binds 172.17.0.1:8790)
                              │
                    pi runtime: state repo, files, shell
```

Files in this directory:

| File | Purpose |
|---|---|
| `docker-compose.yml` | Open WebUI, private `pi-net`, loopback-only port |
| `docker-compose.search.yml` | Optional searxng (web search), added on demand |
| `searxng/settings.yml` | Enables JSON output for Open WebUI's web search |
| `pi-bridge.service` | systemd `--user` unit for the bridge |
| `pi-bridge.env.example` | EnvironmentFile for that unit |
| `.env.example` | Compose secrets (key, webui secret) |
| `openui/` | installer-written OpenUI widget assets, mounted read-only (see below) |
| `SECURITY.md` | Threat model + hardening checklist |

## Prerequisites

- Docker Engine + Compose v2 (present on Omarchy). The daemon is often **disabled**
  by default — start it: `sudo systemctl enable --now docker`.
- Your user can talk to Docker. Either run the commands with `sudo`, or add
  yourself to the `docker` group (`sudo usermod -aG docker "$USER"`, then re-login).
  **This deploy does not change group membership for you**; note that the `docker`
  group is root-equivalent, so `sudo` + explicit commands is the more conservative
  choice.
- `python3` (for the bridge) and the `learning-pi` repo checked out at
  `~/learning-pi` with the learning system's state repo (default `~/learning-system`).
- **ufw is enabled on this machine** (default deny incoming) and by default it also
  blocks containers from reaching a host service. Step 3 below adds one narrow
  allow rule; without it the container cannot reach the bridge. Check with
  `sudo ufw status`.

## Apply

```sh
cd ~/learning-pi/deploy

# 1. Compose secrets
cp .env.example .env
openssl rand -hex 32           # -> PI_BRIDGE_API_KEY  (the bridge's key)
openssl rand -hex 32           # -> WEBUI_SECRET_KEY   (Open WebUI session signing)
$EDITOR .env                   # paste the two values (SEARXNG_SECRET only if using search)
chmod 600 .env

# 2. Docker + the stack (Open WebUI published on 127.0.0.1:3000)
sudo systemctl enable --now docker
sudo docker compose up -d
sudo docker compose ps         # wait for open-webui "healthy"

# 3. Let containers reach the bridge on the docker bridge IP (nothing else).
#    ufw is active and would otherwise drop this traffic. This rule persists.
sudo ufw allow from 172.16.0.0/12 to 172.17.0.1 port 8790 proto tcp \
  comment 'pi-bridge (docker only)'

# 4. Bridge service (start after Docker so docker0 exists; it retries anyway)
mkdir -p ~/.config/systemd/user
cp pi-bridge.env.example ~/.config/pi-bridge.env
$EDITOR ~/.config/pi-bridge.env   # SAME PI_BRIDGE_API_KEY; set PI_BRIDGE_STATE_REPO
chmod 600 ~/.config/pi-bridge.env
cp pi-bridge.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now pi-bridge.service
sudo loginctl enable-linger "$USER"     # keep pi-bridge running after logout/reboot
systemctl --user status pi-bridge.service
```

Omit `sudo` from the `docker compose` lines if you added yourself to the `docker`
group.

> Adjust both `172.17.0.1` values (compose's `host-gateway` target and the ufw
> rule) if your `docker0` uses a different address — check `ip -4 addr show docker0`.

## Wire up the OpenAI connection

`docker-compose.yml` pre-wires the bridge on first boot via
`OPENAI_API_BASE_URL` / `OPENAI_API_KEY`, so the `learning` model should already
appear. To add or repair it by hand in the UI:

1. Open <http://127.0.0.1:3000> and register the first account (it becomes admin).
2. **Admin panel → Settings → Connections → OpenAI API** → *Manage*:
   - **Base URL:** `http://host.docker.internal:8790/v1`
   - **API key:** the value of `PI_BRIDGE_API_KEY` (same as `~/.pi-bridge-key`)
   - Save, then use **Verify Connection**.
3. In a chat, open the model picker and choose **`learning`** (aliases
   `learning-tutor`, `learning-review`, `learning-teach`, `learning-ingest` are
   also exposed).

> Inside the container, `extra_hosts: host.docker.internal:host-gateway` maps
> `host.docker.internal` to Docker's **default** bridge gateway — `docker0`,
> normally `172.17.0.1` (confirm with `ip -4 addr show docker0`). The host's
> `127.0.0.1` is **not** reachable from a container, which is why the bridge
> binds that docker-bridge IP (via `PI_BRIDGE_HOST`) instead of loopback.

## Math rendering

Open WebUI renders standard LaTeX with KaTeX, so no add-on is needed: the bridge
sets `PI_MATH_MODE=latex` for its pi sessions (headless pi otherwise sees no
terminal image protocol and writes plain Unicode). KaTeX is active whenever
**Settings → Interface → Chat → Render Markdown in Assistant Messages** is on.
Inline `$...$` needs whitespace or punctuation on both sides (`foo $x$ bar`, not
`foo$x$bar`).

## Self-hosted OpenUI widgets

A verified `[[TURN:ui]]` widget is delivered as a same-origin embed
(`http://127.0.0.1:3000/static/openui/0.2.1/widget.html#…`). The pinned
`@openuidev/browser-bundle@0.2.1` (MIT) and the shell (`widget.html` + `widget.js`)
are **not** committed — the learning-system installer writes them into `./openui/`
(sha256-pinned; override with `--openui-static-dir`), which `docker-compose.yml`
mounts read-only at Open WebUI's `/static/openui`:

```sh
# after the stack is up and you have an Open WebUI API key (~/.openwebui_key)
cd ~/learning-system
OPENWEBUI_BASE_URL=http://127.0.0.1:3000 python3 scripts/setup_openwebui.py
python3 scripts/audit_openwebui.py        # verifies the served bundle sha256 + shell
```

`docker-compose.yml` also pins `IFRAME_CSP` (`connect-src 'none'`, no CDN origin).
Keep Personal → Interface → **"iframe Sandbox Allow Same Origin" OFF**. The shell's
CSP names the loopback host(s); if you reach Open WebUI through another host (Tailscale,
reverse proxy, a domain), re-run the installer with `--base-url` set to that browser-facing
URL so the shell allows its own scripts.

## Keep the bridge private

- `pi-bridge.env` sets `PI_BRIDGE_HOST=172.17.0.1` (Docker's default bridge
  gateway) — reachable only from this machine and local containers, never the
  LAN. Do **not** change it to `0.0.0.0`.
- The only inbound firewall opening is the narrow `ufw allow` in step 3: TCP 8790
  on `172.17.0.1` from docker subnets (`172.16.0.0/12`). It does not open the
  bridge to the LAN, and the bridge still requires the API key.
- Open WebUI publishes `127.0.0.1:3000` only.
- If you need remote access, do **not** publish `0.0.0.0`: put the machine (or a
  reverse proxy) on Tailscale and bind the published port to the Tailscale
  address/interface, or add an explicit ufw/nftables rule. See `SECURITY.md`.

## Auth requirements

- The bridge **refuses to start without an API key** (`PI_BRIDGE_API_KEY`,
  `--api-key`, or `~/.pi-bridge-key`). Keep that requirement.
- After creating the first (admin) account, set `ENABLE_SIGNUP=false` in
  `deploy/.env` and restart Open WebUI so no one else can self-register.
- Keep `WEBUI_SECRET_KEY` long, random, and stable (rotating it logs everyone out).

## Optional: searxng web search

```sh
# in deploy/.env: set SEARXNG_SECRET (openssl rand -hex 32) and ENABLE_RAG_WEB_SEARCH=true
sudo docker compose -f docker-compose.yml -f docker-compose.search.yml up -d
```

searxng has no host-port publish; Open WebUI reaches it at
`http://searxng:8080/search?q=<query>` on `pi-net`. `searxng/settings.yml` is
mounted read-only and enables the **JSON** output format Open WebUI requires
(the stock image serves `html` only and returns HTTP 403 for `format=json`);
`SEARXNG_SECRET` overrides its `secret_key` at runtime, so no secret is stored
in that file.

## Back up `webui.db`

Open WebUI's database (users, chats, the bridge key) lives in the `open-webui`
volume at `/app/backend/data/webui.db`. Back it up while the container is stopped:

```sh
sudo docker compose stop open-webui
sudo docker run --rm \
  -v pi-webui_open-webui:/data:ro \
  -v "$PWD":/backup \
  alpine tar czf /backup/webui-$(date +%F).tgz -C /data .
chmod 600 webui-$(date +%F).tgz
sudo docker compose start open-webui
```

Restore: stop Open WebUI, then extract the archive back into the same volume
before starting it again. Keep these archives private — they contain the bridge key.

## Verify

```sh
# bridge is up and bound privately (run on the host)
curl -fsS http://172.17.0.1:8790/healthz && echo OK

# the container can reach the bridge and sees the learning model
PI_BRIDGE_API_KEY="$(grep '^PI_BRIDGE_API_KEY=' .env | cut -d= -f2-)"
sudo docker exec -i -e PI_BRIDGE_API_KEY="$PI_BRIDGE_API_KEY" open-webui python3 - <<'PY'
import json, os, urllib.request
req = urllib.request.Request(
    "http://host.docker.internal:8790/v1/models",
    headers={"Authorization": "Bearer " + os.environ["PI_BRIDGE_API_KEY"]},
)
print([m["id"] for m in json.load(urllib.request.urlopen(req, timeout=10))["data"]])
PY
```

(Open WebUI receives the key as `OPENAI_API_KEY`; the `-e` above passes a copy to
the one-off `python3` so the snippet can read it as `PI_BRIDGE_API_KEY`.)

## Rollback

```sh
# stop the stack (keeps volumes) and the bridge
cd ~/learning-pi/deploy && sudo docker compose down
sudo ufw delete allow from 172.16.0.0/12 to 172.17.0.1 port 8790 proto tcp
systemctl --user disable --now pi-bridge.service
rm ~/.config/systemd/user/pi-bridge.service
systemctl --user daemon-reload
# optionally remove data: sudo docker compose down -v   (DELETES webui.db)
# optionally stop docker if you enabled it just for this:
#   sudo systemctl disable --now docker
```

## Related

- Bridge behavior and options: `../bridge/README.md`
- Security note: `./SECURITY.md`
