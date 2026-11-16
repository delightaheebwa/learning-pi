# Security note

The bridge executes real commands on this machine through pi. Anything that reaches the bridge with the key can drive a shell. The key is worth as much as your login. This deployment keeps the blast radius local.

## What is exposed where

| Component | Listens on | Reachable from |
|---|---|---|
| Open WebUI | `127.0.0.1:3000` (container `:8080`) | this machine's browser only |
| pi-bridge | `172.17.0.1:8790` (Docker default bridge gateway) | host + local containers |
| searxng (optional) | private `pi-net` address, no host port | `pi-net` containers |

Web search is on by default with keyless DuckDuckGo, so search queries leave this machine for DuckDuckGo. To turn it off, set `ENABLE_RAG_WEB_SEARCH=false` in `deploy/.env`. Or run the searxng profile to proxy queries through the self-hosted searxng instance on `pi-net`. Upstream engines are still queried, but the browser no longer talks to them directly.

Neither the bridge nor Open WebUI is published to the LAN. Do not bind either to `0.0.0.0`. ufw is enabled by default on this machine and denies incoming traffic from the LAN. The only opening is the narrow rule in the README that lets docker subnets reach `172.17.0.1:8790`. Remote access is a deliberate, separate step: bind to a Tailscale address or interface, or add a firewall rule. Never publish a raw `0.0.0.0`.

## Rules that preserve the guarantees

- Keep the bridge keyed. The bridge already refuses to run unauthenticated. Do not add `--api-key ""` or an empty `PI_BRIDGE_API_KEY`.
- Turn signup off (`ENABLE_SIGNUP=false`) after the first admin account exists.
- Protect the secret files. `deploy/.env` and `~/.config/pi-bridge.env` must be mode `600` and must never be committed. The optional widget path adds a third secret: the Open WebUI user API key at `~/.openwebui_key`, or at `PI_BRIDGE_OPENWEBUI_KEY_FILE`. That file is also mode `600`, and it authorizes the bridge's post-turn chat writes.
- Keep the widget sandbox closed. `IFRAME_CSP` in `docker-compose.yml` sets `connect-src 'none'`, so rendered widgets and HTML artifacts cannot reach the network. The pinned OpenUI bundle is self-hosted same-origin under `deploy/openui/`, written by the installer, with no CDN origin. Leave Personal → Interface → "iframe Sandbox Allow Same Origin" off. Widgets then run in an opaque-origin sandbox and talk to the chat only through the confirm-dialog `input:prompt:submit` path.
- Keep the ufw rule narrow. The bridge is reachable only from docker subnets (`172.16.0.0/12`) on `172.17.0.1:8790`. Do not widen the rule to the LAN or to `0.0.0.0`, and remove it when you tear the stack down.
- Keep bash-guard's floor. The unit does not pass `--allow-bash-guard`, so catastrophic commands stay blocked even though the bridge drives a shell.
- Treat backups as secrets. `webui.db` holds the bridge API key and chat transcripts, so restrict access to `webui-*.tgz`.
- Rotate the key. Change `PI_BRIDGE_API_KEY` in both env files, restart the bridge and Open WebUI, and update the OpenAI connection if you entered it in the UI.

## Accepted residual risks

- The bridge binds Docker's default bridge gateway, `docker0`, so any container on the host can reach it if it has the key, including containers outside this stack. Only run trusted images and keep the key secret.
- The bridge binds a docker-owned IP, so it is up only while Docker is. If Docker stops, the service keeps failing and retrying with `Restart=on-failure`.
- Membership in the `docker` group is root-equivalent on the host. Prefer `sudo docker ...` if you do not need daily access.
