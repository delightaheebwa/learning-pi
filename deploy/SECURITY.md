# Security note

The bridge executes real commands on this machine through pi. Anything that can
reach the bridge with the key can drive a shell, so the key is worth as much as
your login. This deployment is built to keep the blast radius local.

## What is exposed where

| Component | Listens on | Reachable from |
|---|---|---|
| Open WebUI | `127.0.0.1:3000` (container `:8080`) | this machine's browser only |
| pi-bridge | `172.17.0.1:8790` (Docker default bridge gateway) | host + local containers |
| searxng (optional) | private `pi-net` address, no host port | `pi-net` containers |

Neither the bridge nor Open WebUI is published to the LAN. Do not bind either to
`0.0.0.0`. ufw (enabled by default on this machine) denies incoming traffic from
the LAN; the only opening is the narrow rule in the README that lets docker
subnets reach `172.17.0.1:8790`. Remote access is a deliberate, separate step:
bind to a Tailscale address/interface or add a firewall rule — never a raw
`0.0.0.0` publish.

## Rules that preserve the guarantees

- **Keep the bridge keyed.** The bridge already refuses to run unauthenticated;
  don't add `--api-key ""` or an empty `PI_BRIDGE_API_KEY`.
- **Turn signup off** (`ENABLE_SIGNUP=false`) after the first admin account exists.
- **Protect the two secret files:** `deploy/.env` and `~/.config/pi-bridge.env`
  should be mode `600` and never committed. The optional widget path adds a third:
  the Open WebUI user API key at `~/.openwebui_key` (or `PI_BRIDGE_OPENWEBUI_KEY_FILE`)
  — also mode `600`; it authorizes the bridge's post-turn chat writes.
- **Keep the ufw rule narrow.** The bridge is only reachable from docker subnets
  (`172.16.0.0/12`) on `172.17.0.1:8790`. Don't widen it to the LAN or to
  `0.0.0.0`, and remove it when you tear the stack down.
- **Keep bash-guard's floor.** The unit does not pass `--allow-bash-guard`;
  catastrophic commands stay blocked even though the bridge drives a shell.
- **Treat backups as secrets.** `webui.db` holds the bridge API key and chat
  transcripts — restrict access to `webui-*.tgz`.
- **Rotate the key** by changing `PI_BRIDGE_API_KEY` in both env files, restarting
  the bridge and Open WebUI, and updating the OpenAI connection if it was entered
  in the UI.

## Residual risks (accepted)

- The bridge binds Docker's default bridge gateway (`docker0`), so **any**
  container on the host can reach it if it has the key, not just this stack's
  containers. Only run trusted images and keep the key secret.
- The bridge binds a docker-owned IP, so it is only up while Docker is; if Docker
  is stopped the service keeps failing and retrying (`Restart=on-failure`).
- Membership in the `docker` group is root-equivalent on the host; prefer
  `sudo docker ...` if you don't need daily access.
