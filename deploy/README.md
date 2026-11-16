# Open WebUI in front of pi-bridge

Runs [Open WebUI](https://github.com/open-webui/open-webui) in Docker on this
machine as the chat front-end. It talks to the host-run `pi-bridge` over the
Docker bridge. pi, with the learning gate, subagents, and skills, stays the
brain, and the bridge drives a real shell. Treat this deployment as security
sensitive.

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
| `docker-compose.search.yml` | Optional searxng for web search, added on demand |
| `searxng/settings.yml` | Enables JSON output for Open WebUI's web search |
| `pi-bridge.service` | systemd `--user` unit for the bridge |
| `pi-bridge-wait-docker0` | ExecStartPre gate that waits for `docker0` at `PI_BRIDGE_HOST` before bind |
| `pi-bridge.env.example` | EnvironmentFile for that unit |
| `.env.example` | Compose secrets, the key and the webui secret |
| `openui/` | Installer-written OpenUI widget assets, mounted read-only. See [Self-hosted OpenUI widgets](#self-hosted-openui-widgets). |
| `SECURITY.md` | Threat model and hardening checklist |

## Prerequisites

- Docker Engine and Compose v2, which are present on Omarchy. The daemon is
  often disabled by default, so start it:
  `sudo systemctl enable --now docker`.
- Your user can talk to Docker. Either run the commands with `sudo`, or add
  yourself to the `docker` group with `sudo usermod -aG docker "$USER"` and then
  re-login. This deploy does not change group membership for you. The `docker`
  group is root-equivalent, so `sudo` with explicit commands is the more
  conservative choice.
- `python3` for the bridge, and the `learning-pi` repo checked out at
  `~/learning-pi` with the learning system's state repo, by default
  `~/learning-pi/state`.
- ufw is enabled on this machine with default deny incoming, and by default it
  also blocks containers from reaching a host service. Step 3 below adds one
  narrow allow rule. Without that rule the container cannot reach the bridge.
  Check with `sudo ufw status`.

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

# 4. Bridge service. ExecStartPre waits for PI_BRIDGE_HOST (docker0) to exist,
#    so this is safe even when the user session starts before Docker does.
mkdir -p ~/.config/systemd/user ~/.local/bin
cp pi-bridge.env.example ~/.config/pi-bridge.env
$EDITOR ~/.config/pi-bridge.env   # SAME PI_BRIDGE_API_KEY; set PI_BRIDGE_STATE_REPO
chmod 600 ~/.config/pi-bridge.env
cp pi-bridge.service ~/.config/systemd/user/
cp pi-bridge-wait-docker0 ~/.local/bin/ && chmod 755 ~/.local/bin/pi-bridge-wait-docker0
systemctl --user daemon-reload
systemctl --user enable --now pi-bridge.service
sudo loginctl enable-linger "$USER"     # keep pi-bridge running after logout/reboot
systemctl --user status pi-bridge.service
```

Omit `sudo` from the `docker compose` lines if you added yourself to the `docker`
group.

> Adjust both `172.17.0.1` values, which are the compose `host-gateway` target and
> the ufw rule, if your `docker0` uses a different address. Check
> `ip -4 addr show docker0`.

## Wire up the OpenAI connection

`docker-compose.yml` pre-wires the bridge on first boot through
`OPENAI_API_BASE_URL` and `OPENAI_API_KEY`, so the `learning` model should
already appear. To add or repair it by hand in the UI:

1. Open <http://127.0.0.1:3000> and register the first account. That account
   becomes admin.
2. Go to Admin panel → Settings → Connections → OpenAI API and choose Manage.
   - Base URL: `http://host.docker.internal:8790/v1`
   - API key: the value of `PI_BRIDGE_API_KEY`, the same value as
     `~/.pi-bridge-key`
   - Save, then use Verify Connection.
3. In a chat, open the model picker and choose `learning`. The aliases
   `learning-tutor`, `learning-review`, `learning-teach`, and `learning-ingest`
   are also exposed.

### Live action trace

Tool and thinking step cards need no extra setup, because the bridge streams
them as message content. For the optional live status line, with a shimmer and a
timeline, add two custom forwarded headers to the OpenAI connection. Open WebUI
0.10 and later support the placeholders:

| Header | Value |
|---|---|
| `X-OpenWebUI-Chat-Id` | `{{CHAT_ID}}` |
| `X-OpenWebUI-Message-Id` | `{{MESSAGE_ID}}` |

The bridge needs the same Open WebUI REST configuration as widget delivery to
post the `status` events, which is `PI_BRIDGE_OPENWEBUI_BASE_URL` plus a user API
key. Without a message id it posts nothing, and the step cards still render. See
`../bridge/README.md#live-action-trace`.

The `X-OpenWebUI-Chat-Id` header is also what lets the bridge mirror fork and
delete into pi. The chat id becomes the pi session identity. A fork copies the
parent's branch, and a delete sweep removes the session. Without the header,
fork starts a fresh pi chat, and deleting an Open WebUI chat leaves the pi
transcript behind. See `../bridge/README.md#chat-actions-mirror-into-pi`.

> Inside the container, `extra_hosts: host.docker.internal:host-gateway` maps
> `host.docker.internal` to Docker's default bridge gateway, `docker0`, normally
> `172.17.0.1`. Confirm it with `ip -4 addr show docker0`. The host's `127.0.0.1`
> is not reachable from a container, which is why the bridge binds that
> docker-bridge IP through `PI_BRIDGE_HOST` instead of loopback.

## Documents and RAG

Open WebUI's document retrieval is configured in Admin panel → Settings →
Documents. This deployment uses local models with no external embedding API:

| Setting | Value | Why |
|---|---|---|
| Embedding model | `BAAI/bge-base-en-v1.5` | 512-token context, better than MiniLM |
| Reranking model | `BAAI/bge-reranker-base` | CrossEncoder precision on the top candidates |
| Hybrid search | on | BM25 catches exact names and IDs |
| Top K and reranker pool | 8 and 20 | more context, reranked |
| Relevance threshold | 0.3 | drop chunks the reranker scores as noise |
| Chunk size and overlap | 800 and 100 | about one page for technical books |

The model settings live in the `open-webui` volume and are set in the Admin
panel, not in compose. Two env-only knobs do live here: the reranker's boot guard
and the BGE query instruction. See the comments in `docker-compose.yml`.

### Front matter and indexes hurt retrieval

Open WebUI has no ingestion-time filter, so whatever the extractor returns is
chunked and embedded. A technical book's back index lists every term in the
book, so it outranks the prose for almost any query. Front matter, which includes
the cover, TOC, intro, and acknowledgements, adds noise and can surface when
nothing is relevant. `rag-clean` removes both and writes `[[p.N]]` markers, so
citations still point at the original PDF pages.

```sh
# What would be dropped? (writes nothing)
deploy/rag-clean inspect book.pdf

# Clean, embed, and add to a knowledge base (created if missing)
deploy/rag-clean ingest book.pdf --kb "Head First Software Architecture"

# Rebuild PDFs previously uploaded through the UI
deploy/rag-clean audit          # report only
deploy/rag-clean audit --fix    # rebuild polluted files
```

For PDFs, `ingest` uploads a `<name> (clean).txt`, and other text files pass
through under their own name. Re-running it updates that same file and keeps its
knowledge-base membership instead of duplicating it. Page numbers are 1-based PDF
pages. Detection is heuristic, `--content-start` and `--index-start` are 0-based
overrides, and `inspect` shows the decision first.

The UI upload button cannot be intercepted. After you upload a book that way, run
`audit --fix`, or install the optional timer so the audit runs automatically
within 30 minutes:

```sh
cp deploy/rag-clean.service deploy/rag-clean.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now rag-clean.timer
```

The audit keeps a small cache in `~/.cache/rag-clean/state.json` and skips files
whose stored text already starts with `[[p.N]]`. A PDF is therefore downloaded
once before it is marked clean, and a report-only run re-checks any file still
flagged polluted. It never touches non-PDF files, and images keep flowing to pi as
`ImageContent`.

> The external document engine, `CONTENT_EXTRACTION_ENGINE=external`, is the only
> fully automatic ingestion hook. It is admin-wide and also takes over image and
> docx extraction. Do not enable it just for this.

## Math rendering

Open WebUI renders standard LaTeX with KaTeX, so no add-on is needed. The bridge
sets `PI_MATH_MODE=latex` for its pi sessions, because headless pi otherwise sees
no terminal image protocol and writes plain Unicode. KaTeX is active whenever
Settings → Interface → Chat → Render Markdown in Assistant Messages is on. Inline
`$...$` needs whitespace or punctuation on both sides, as in `foo $x$ bar` and
not `foo$x$bar`.

## Self-hosted OpenUI widgets

A verified `[[TURN:ui]]` widget is delivered as a same-origin embed at
`http://127.0.0.1:3000/static/openui/0.2.1/widget.html#…`. The pinned
`@openuidev/browser-bundle@0.2.1` (MIT license) and the shell, `widget.html` plus
`widget.js`, are not committed. The legacy `state/scripts/setup_openwebui.py`
installer writes them into `./openui/` with a sha256 pin, and
`--openui-static-dir` overrides the target. `docker-compose.yml` mounts that
directory read-only at Open WebUI's `/static/openui`:

```sh
# after the stack is up and you have an Open WebUI API key (~/.openwebui_key)
cd ~/learning-pi/state
OPENWEBUI_BASE_URL=http://127.0.0.1:3000 python3 scripts/setup_openwebui.py
python3 scripts/audit_openwebui.py        # verifies the served bundle sha256 + shell
```

`docker-compose.yml` also pins `IFRAME_CSP` to `connect-src 'none'` with no CDN
origin. Keep Personal → Interface → "iframe Sandbox Allow Same Origin" OFF. The
shell's CSP names the loopback hosts. If you reach Open WebUI through another
host, such as Tailscale, a reverse proxy, or a domain, re-run the installer with
`--base-url` set to that browser-facing URL so the shell allows its own scripts.

The iframe is opaque-origin, so the shell cannot read Open WebUI's in-app theme.
It follows the OS `prefers-color-scheme` instead and sets `data-openui-theme`
from `matchMedia`. It also re-measures height on resize, font load, disclosure
toggles, and chart changes. It gives the bundle's copy buttons an `execCommand`
fallback and ships keyboard-focus and invalid-input styles. Re-running the
installer rewrites `widget.html` and `widget.js` in place. The pinned bundle is
untouched, but a browser may cache the old shell until a hard refresh.

## Keep the bridge private

- `pi-bridge.env` sets `PI_BRIDGE_HOST=172.17.0.1`, Docker's default bridge
  gateway. The bridge is reachable only from this machine and local containers,
  never the LAN. Do not change it to `0.0.0.0`.
- The only inbound firewall opening is the narrow `ufw allow` in Step 3: TCP 8790
  on `172.17.0.1` from docker subnets in `172.16.0.0/12`. It does not open the
  bridge to the LAN, and the bridge still requires the API key.
- Open WebUI publishes `127.0.0.1:3000` only.
- If you need remote access, do not publish `0.0.0.0`. Put the machine, or a
  reverse proxy, on Tailscale and bind the published port to the Tailscale
  address or interface. Alternatively add an explicit ufw or nftables rule. See
  `SECURITY.md`.

## Auth requirements

- The bridge refuses to start without an API key from `PI_BRIDGE_API_KEY`,
  `--api-key`, or `~/.pi-bridge-key`. Keep that requirement.
- After you create the first admin account, set `ENABLE_SIGNUP=false` in
  `deploy/.env` and restart Open WebUI so no one else can self-register.
- Keep `WEBUI_SECRET_KEY` long, random, and stable. Rotating it logs everyone
  out.

## Web search

The base stack enables Open WebUI's web-search toggle with the keyless
DuckDuckGo engine, so search works without another container. Queries leave the
machine to DuckDuckGo. Set `ENABLE_RAG_WEB_SEARCH=false` in `deploy/.env` to turn
the feature off.

For private search, run the optional searxng profile instead:

```sh
# in deploy/.env: set SEARXNG_SECRET (openssl rand -hex 32)
sudo docker compose -f docker-compose.yml -f docker-compose.search.yml up -d
```

`docker-compose.search.yml` overrides `RAG_WEB_SEARCH_ENGINE` to `searxng`,
because service-level environment wins over the base default. searxng has no
host-port publish. Open WebUI reaches it at
`http://searxng:8080/search?q=<query>` on `pi-net`. `searxng/settings.yml` is
mounted read-only and enables the JSON output format that Open WebUI requires.
The stock image serves `html` only and returns HTTP 403 for `format=json`.
`SEARXNG_SECRET` overrides the file's `secret_key` at runtime, so no secret is
stored in that file.

## Back up `webui.db`

Open WebUI's database holds users, chats, and the bridge key. It lives in the
`open-webui` volume at `/app/backend/data/webui.db`. Back it up while the
container is stopped:

```sh
sudo docker compose stop open-webui
sudo docker run --rm \
  -v pi-webui_open-webui:/data:ro \
  -v "$PWD":/backup \
  alpine tar czf /backup/webui-$(date +%F).tgz -C /data .
chmod 600 webui-$(date +%F).tgz
sudo docker compose start open-webui
```

To restore, stop Open WebUI, extract the archive back into the same volume, then
start Open WebUI again. Keep these archives private because they contain the
bridge key.

## Upgrade Open WebUI

`docker-compose.yml` pins the exact release index digest, never a moving tag.
Some releases include one-way database migrations, and v0.13.0 does. A
rolled-back container may not be able to read a migrated `webui.db`. Before you
change the pin:

1. Back up the volume with the recipe above while the container is stopped, and
   keep the archive until the new version has run cleanly.
2. Resolve the new release's index digest and pin it on the `image:` line, for
   example with
   `docker buildx imagetools inspect ghcr.io/open-webui/open-webui:vX.Y.Z`. Use
   the top-level `Digest`, not a per-platform digest.
3. Run `sudo docker compose pull open-webui && sudo docker compose up -d`, then
   wait for `healthy` in `sudo docker compose ps`.

To roll back, first stop the new container and restore the pre-upgrade
`webui.db` archive. Then set the old digest and start the old image.

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

Open WebUI receives the key as `OPENAI_API_KEY`. The `-e` above passes a copy to
the one-off `python3`, so the snippet can read it as `PI_BRIDGE_API_KEY`.

## Rollback

```sh
# stop the stack (keeps volumes) and the bridge
cd ~/learning-pi/deploy && sudo docker compose down
sudo ufw delete allow from 172.16.0.0/12 to 172.17.0.1 port 8790 proto tcp
systemctl --user disable --now pi-bridge.service
rm ~/.config/systemd/user/pi-bridge.service
rm -f ~/.local/bin/pi-bridge-wait-docker0
systemctl --user daemon-reload
# optionally remove data: sudo docker compose down -v   (DELETES webui.db)
# optionally stop docker if you enabled it just for this:
#   sudo systemctl disable --now docker
```

## Related

- Bridge behavior and options: `../bridge/README.md`
- Security note: `./SECURITY.md`
