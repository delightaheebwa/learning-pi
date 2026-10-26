# pi-bridge

OpenAI-compatible endpoint in front of the pinned pi runtime. **Open WebUI is
the face; pi is the brain** (the learning-gate, subagents, and skills run
unchanged; Open WebUI holds only chat transcripts).

```
Open WebUI (Docker, this machine)
      │  OpenAI API  (http://172.17.0.1:8790/v1 via host.docker.internal)
   pi-bridge  ── one `pi --mode rpc` process per chat (host systemd, binds 172.17.0.1:8790)
      │
   pi runtime (learning-gate withholds turns before emission)
      │
   the real machine: state repo, files, shell
```

## Why it is shaped this way (Phase 0 spike findings)

* Assistant text is taken **only** from `message_end`. `message_update` deltas
  carry the raw, *pre-verification* draft — the spike watched a withheld teaching
  draft stream in full before the gate replaced it. The bridge never forwards
  deltas, so unverified content cannot leak to the learner.
* A withheld turn already arrives as a `⛔ WITHHELD (…)` banner inside the
  `message_end` text, so the learner sees the gate's verdict with no extra wiring.
* Sessions run with `--bash-guard-disabled` (only when bash-guard is installed):
  routine commands (including `git status`) pass, while the catastrophic floor
  (`rm -r/-rf`, `sudo`, `curl|sh`, `mkfs*`, `dd of=/dev/…`, disk/power tools,
  `git reset --hard`, …) stays blocked — bash-guard's default in a headless
  session blocks even read-only `git`, which would make computer use unusable.
* One pi session per chat; only the **newest** user message is forwarded (pi owns
  its context). A resend of the same message is treated as a regenerate and forks
  the session back to that user message first.

## Run

```sh
# key: --api-key, $PI_BRIDGE_API_KEY, or ~/.pi-bridge-key
python3 -m bridge --port 8790 --state-repo ~/learning-system
```

In Open WebUI: **Settings → Connections → +** (OpenAI API). The Base URL must be
one a container can reach — for the default Docker bridge network bind the
bridge to that interface and use `http://172.17.0.1:8790/v1`, or run Open WebUI
with `--network host` and use `http://127.0.0.1:8790/v1`. (A bridge bound to
`127.0.0.1` is **not** reachable from a normal container via
`host.docker.internal` on Linux.) Set the API key to your bridge key, then pick
the `learning` model.

Options: `--host/--port`, `--models a,b,c`, `--timeout`, `--max-sessions`,
`--agent-dir`, `--session-dir`, `--ledger-dir`, `--openwebui-base-url`,
`--openwebui-key-file`, `--allow-bash-guard` (do **not**
pass `--bash-guard-disabled`; not recommended headless).

## Math

Open WebUI renders standard LaTeX with KaTeX (`$...$`, `$$...$$`, `\(...\)`,
`\[...\]`), so the bridge sets `PI_MATH_MODE=latex` for its pi sessions. That
overrides `math-mode`'s terminal detection: headless pi has no image protocol, so
without it the Tutor would fall back to plain Unicode. Set `PI_MATH_MODE=unicode`
(or `auto`) only when pointing a text-only client at the bridge.

## Intelligent-UI widgets

A verified `[[TURN:ui]]` turn carries one ` ```openui ` OpenUI Lang payload. The
learning-gate's `ui-audit` verifies the payload and prose; the bridge then lifts
the fence out of the prose, builds a same-origin embed URL
(`bridge/genui.py`: `/static/openui/<version>/widget.html#<base64url payload>`), and
— when configured — appends a second assistant message to the Open WebUI chat with
an `embeds` event (`bridge/openwebui.py`), so the widget renders **below** the
prose. Mermaid/HTML fences are left in the prose for Open WebUI's native rendering.

The widget cannot be a `data:` URL: Open WebUI's `FullHeightIframe` only treats
`http(s)://` / protocol-relative strings as URLs and renders a `data:` embed as
literal text, so the shell is a served document. The pinned, MIT
(`@openuidev/browser-bundle@0.2.1`) bundle, the `widget.html` shell, and its
`widget.js` are self-hosted under `deploy/openui/<version>/` (installer-written by
`learning-system/scripts/setup_openwebui.py`, mounted read-only into Open WebUI's
`/static/openui`). The verified payload rides in the URL fragment — not an HTTP
request body, but persisted as chat embed metadata alongside the transcript, so it
is declarative OpenUI Lang only. `deploy/docker-compose.yml` pins `IFRAME_CSP`
(`connect-src 'none'`, no CDN). The shell follows OS light/dark (the opaque-origin
iframe cannot read Open WebUI's in-app theme), re-measures on resize/fonts/disclosure,
and falls back to `execCommand` when the sandbox denies the Clipboard API. See
`docs/plans/intelligent-ui/`.

Enable it with `--openwebui-base-url` (or `PI_BRIDGE_OPENWEBUI_BASE_URL`) and a
user API key (Settings → Account → API Keys) in `--openwebui-key-file` /
`PI_BRIDGE_OPENWEBUI_KEY_FILE` (default `~/.openwebui_key`, mode 600). Widget
delivery is best-effort: the prose always renders, and an unconfigured or failing
Open WebUI REST call is swallowed. The fence is lifted from any flow's prose (the
audit is pi-side correctness; the bridge only transports the already-verified
payload).

## Single-writer policy

The learning system forbids two concurrent writers on the state repo. The bridge
holds a learning lock for the duration of each learning turn and releases it when
the turn ends, so concurrent learning turns — including two from the same chat —
cannot overlap; a second chat that starts a learning turn meanwhile is told to
wait. General (non-learning) chats are exempt. Idle pi sessions are evicted LRU
(`--max-sessions`).

## Limits

* Tool activity is buffered with the turn (no live status lines yet) — the turn
  arrives whole, which matches "generated then verified then emitted".
* Regenerate uses `fork`; if pi cannot fork, the bridge falls back to appending
  the prompt.
* Interactive extension UI (approval dialogs) is declined, not surfaced.

## Tests

`python3 -m unittest discover -s test/bridge` — deterministic, uses a fake pi
(`test/bridge/fake_pi.py`); no models or network.

`test/bridge/run_tests.py` runs the same suite and prints one `PASS <test id>`
line per passing test, so `scripts/learn-check` binds the bridge invariants
(`B-*` in `contracts/learning-core.json`) into the same contract-coverage check
as the deno gate suites.
