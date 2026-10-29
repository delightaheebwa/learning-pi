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
  deltas, so unverified content cannot leak to the learner. The live action trace
  (below) is built from completed `tool_execution_*` records and thinking
  durations — metadata, never delta text.
* A withheld turn already arrives as a `⛔ WITHHELD (…)` banner inside the
  `message_end` text, so the learner sees the gate's verdict with no extra wiring.
* Sessions run with `--bash-guard-disabled` (only when bash-guard is installed):
  routine commands (including `git status`) pass, while the catastrophic floor
  (`rm -r/-rf`, `sudo`, `curl|sh`, `mkfs*`, `dd of=/dev/…`, disk/power tools,
  `git reset --hard`, …) stays blocked — bash-guard's default in a headless
  session blocks even read-only `git`, which would make computer use unusable.
* One pi session per chat, with a deterministic `--session-id` derived from the
  chat key (`chat-<uuid>` or `fp-<hash>`). Because pi resumes that id, a bridge
  restart or a pi crash reconnects the chat to its saved transcript instead of
  starting blank and re-deriving context from the state repo. Before each
  prompt the bridge aligns the posted transcript with pi's own user messages:
  a new message appends, a regenerate re-answers the last user, an edited or
  deleted message forks pi at the replaced turn, and a Continue click extends
  the previous answer without forking. After a fork the bridge moves the new
  branch over the chat's deterministic file and has pi switch to it, so a
  restart resumes the post-fork branch and deleting the chat removes it.

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

Options: `--host/--port`, `--models a,b,c`, `--timeout`, `--max-turn`,
`--max-sessions`, `--agent-dir`, `--session-dir`, `--ledger-dir`,
`--openwebui-base-url`, `--openwebui-key-file`, `--sync-interval`,
`--no-abort-on-disconnect`, `--allow-bash-guard` (do **not** pass
`--bash-guard-disabled`; not recommended headless).

### Turn timeouts

`--timeout` (env `PI_BRIDGE_TIMEOUT`, default **1800 s**) is an **idle** budget:
the longest pi may stay silent mid-turn. Every record resets it, so a turn that
spends 15 minutes inside a scout subagent — no records between
`tool_execution_start` and its result — is not killed. `--max-turn` (env
`PI_BRIDGE_MAX_TURN`, default **7200 s**) is the absolute ceiling for one turn,
so a runaway turn still releases the single-writer learning lock. An expired
budget aborts the turn and surfaces `⚠️ pi runtime error: …` naming the budget to
raise. (Before 2026-10-29 `--timeout` was a 900 s wall-clock cap; it aborted
healthy resume turns in Open WebUI.)

### Sessions and restarts

The registry of live pi processes is in memory, but every session is started
with `--session-id` set to a deterministic value derived from the chat key, so
systemd restarts, reboots, LRU eviction (`--max-sessions`), and pi crashes all
resume the same transcript. The id is `chat-<uuid>` when the client supplies a
chat id and `fp-<fingerprint>` otherwise; any other key collapses to a stable
hash.

With the connection's forwarded headers configured (recommended, and required
for fork/delete mirroring):

```
X-OpenWebUI-Chat-Id:    {{CHAT_ID}}
X-OpenWebUI-Message-Id: {{MESSAGE_ID}}
```

the chat id is authoritative and two chats never share a pi session. Without the
chat-id header the bridge falls back to a fingerprint of the **first** user
message plus the model name: two chats whose first user message is identical then
share one pi session, and editing that first message starts a new one. The first
turn of an existing chat that has no chat-id session is migrated once from its
fingerprint session (only when the chat already has an assistant message), so
upgrading does not blank an ongoing conversation.

## Chat actions mirror into pi

Open WebUI calls the bridge only for completions; it never tells an
OpenAI-compatible backend that a chat was uploaded to, forked, or deleted. The
bridge closes that gap with the same REST key it uses for widgets
(`--openwebui-base-url` + `--openwebui-key-file`):

* **Uploads.** Image content parts are turned into pi `ImageContent` blocks and
  sent on the `prompt` (`{type: image, data, mimeType}`). An image with no text
  gets a neutral prompt; text plus images keep both. Non-image files follow
  Open WebUI's own file-context/RAG path, which puts the extracted text into the
  user message the bridge already forwards.
* **Fork / clone.** On the first turn of a chat whose metadata says it was
  forked (`meta.forked_from` / `chat.originalChatId`), the bridge copies the
  parent pi session's branch at the fork point into a new session file owned by
  the new chat id. A fork at a user message keeps that message; a fork at an
  assistant message keeps the turn that produced it. The copy is reused after a
  bridge restart, not duplicated.
* **Edit / delete / regenerate / Continue.** The bridge compares the posted
  transcript's user messages with pi's active branch. An edited or deleted
  message forks pi at the turn being replaced before prompting; a regenerate
  re-answers the last user; a Continue click (the transcript ends with the
  assistant) sends a marked continuation prompt without forking. The marker is
  filtered from later alignment. After any fork, the new branch replaces the
  chat's session file and pi switches to it, so restart and delete see the
  active transcript.
* **Stop.** Open WebUI's Stop closes the streaming connection. The bridge watches
  the socket and aborts the pi turn (even while pi is silent inside a long tool
  call), drains to settlement, and releases the learning lock. Leaving a chat
  mid-turn counts as Stop too; `--no-abort-on-disconnect` (or
  `PI_BRIDGE_ABORT_ON_DISCONNECT=false`) restores the old
  consume-to-settlement behavior.
* **Delete.** A background sweep (`--sync-interval`, default 60 s, 0 disables)
  proves the API key with the chat-list probe, then asks Open WebUI about every
  `chat-<id>` session and closes/removes it on a per-chat 401/404/422 (Open
  WebUI reports a missing chat as 401). A network error, an invalid key, a
  server error, an existing chat, or a turn still in flight never deletes a
  transcript; an in-flight session is retried on the next pass.

Requires the chat-id header above and the Open WebUI REST configuration. Without
them the bridge keeps working, but fork starts a fresh chat and delete leaves the
pi transcript alone. The sweep reads all chats individually, so it is intended
for the normal single-user self-hosted deployment, not a large multi-tenant
instance.

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
(`bridge/server.py`: `/static/openui/<version>/widget.html#<base64url payload>`), and
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

## Live action trace

Each completed pi step is streamed to Open WebUI as a `<details>` content block
while the turn is still running, so the chat shows the agent's actions as they
happen instead of the finished turn all at once:

* a tool execution becomes a `type="tool_calls"` block carrying the tool name,
  its arguments (truncated to 200 characters), its status and its duration.
  Open WebUI groups consecutive steps into one collapsible "Explored bash,
  read_file" row with an "Exploring…" spinner while the message streams;
* a completed thinking block becomes a `type="reasoning"` block ("Thought for
  Ns"). A learning flow shows only the duration; a general chat shows its text;
* a tool **result** is never rendered in a learning flow (a result can carry the
  pre-gate draft); a general chat gets a truncated preview.

`message_update` deltas are still never forwarded: the trace is metadata about
completed actions, not the draft (`B-deltas-never-forwarded`). Step blocks are
emitted complete and strictly formatted for Open WebUI's `<details>` parser
(`bridge/stream.py`).

### Live status line (optional)

Open WebUI also renders a shimmering one-line status plus a clickable timeline
above the reply. Enable it by adding the connection's custom forwarded headers in
**Settings → Connections → OpenAI API → Manage** (Open WebUI ≥ 0.10):

```
X-OpenWebUI-Chat-Id:    {{CHAT_ID}}
X-OpenWebUI-Message-Id: {{MESSAGE_ID}}
```

The bridge then POSTs `status` events to
`/api/v1/chats/<chat>/messages/<message>/event` with the same REST key as widget
delivery (`--openwebui-base-url`), and always ends a started sequence with
`done: true` — including after a provider error — so the shimmer never sticks.
It is best-effort: Open WebUI may only persist a message after the stream ends,
a rejected event changes nothing, and the step cards are the guaranteed trace.
Without a message id (or without Open WebUI REST config) no status is posted.

## Single-writer policy

The learning system forbids two concurrent writers on the state repo. The bridge
holds a learning lock for the duration of each learning turn and releases it when
the turn ends, so concurrent learning turns — including two from the same chat —
cannot overlap; a second chat that starts a learning turn meanwhile is told to
wait. General (non-learning) chats are exempt. A chat counts as a learning flow
if **any** user message in the transcript starts one (`/lesson`, `[[FLOW:…]]`,
…), so a bare learner answer after `/lesson` still takes the lock and keeps the
learning display policy. Idle pi sessions are evicted LRU (`--max-sessions`).

## Limits

* The prose and any verified widget payload still arrive only at settlement
  ("generated then verified then emitted"); only the action trace streams live.
* Regenerate/edit/delete use pi's `fork`; if pi cannot fork, the bridge falls
  back to appending the prompt. A fork whose file has not been written yet is
  adopted after the next settlement.
* Interactive extension UI (approval dialogs) is declined, not surfaced.

## Tests

`python3 -m unittest discover -s test/bridge` — deterministic, uses a fake pi
(`test/bridge/fake_pi.py`); no models or network.

`test/bridge/run_tests.py` runs the same suite and prints one `PASS <test id>`
line per passing test, so `scripts/learn-check` binds the bridge invariants
(`B-*` in `contracts/learning-core.json`) into the same contract-coverage check
as the deno gate suites.
