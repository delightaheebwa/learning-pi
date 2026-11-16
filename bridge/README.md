# pi-bridge

`pi-bridge` is the OpenAI-compatible endpoint in front of the pinned pi runtime. Open WebUI is the face and pi is the brain. The learning-gate, the subagents, and the skills run unchanged, and Open WebUI holds only chat transcripts.

```
Open WebUI (Docker, this machine)
      │  OpenAI API  (http://172.17.0.1:8790/v1 via host.docker.internal)
   pi-bridge  ── one `pi --mode rpc` process per chat (host systemd, binds 172.17.0.1:8790)
      │
   pi runtime (learning-gate withholds turns before emission)
      │
   the real machine: state repo, files, shell
```

## Design decisions from the Phase 0 spike

The bridge takes assistant text from `message_end` only. The `message_update` deltas carry the raw draft from before verification. In the Phase 0 spike, a withheld teaching draft streamed in full before the gate replaced it. The bridge never forwards deltas, so unverified content cannot reach the learner. The live action trace described below is built from completed `tool_execution_*` records and thinking durations, which is metadata and never delta text.

A withheld turn already arrives as a `⛔ WITHHELD (…)` banner inside the `message_end` text. The learner sees the gate's verdict with no extra wiring.

Sessions run with `--bash-guard-disabled`, and only when bash-guard is installed. Routine commands, including `git status`, pass. The catastrophic floor stays blocked: `rm -r` and `rm -rf`, `sudo`, `curl|sh`, `mkfs*`, `dd of=/dev/…`, disk and power tools, and `git reset --hard`, among others. In a headless session, bash-guard's default blocks even read-only `git`, which would make computer use unusable.

Each chat gets one pi session, with a deterministic `--session-id` derived from the chat key: `chat-<uuid>` or `fp-<hash>`. pi resumes that id, so a bridge restart or a pi crash reconnects the chat to its saved transcript. The chat does not start blank and does not re-derive context from the state repo.

Before each prompt, the bridge aligns the posted transcript with pi's own user messages. A new message appends. A regenerate re-answers the last user. An edited or deleted message forks pi at the replaced turn. A Continue click extends the previous answer without forking. After a fork, the bridge moves the new branch over the chat's deterministic file and has pi switch to it. A restart then resumes the post-fork branch, and deleting the chat removes it.

## Run

```sh
# key: --api-key, $PI_BRIDGE_API_KEY, or ~/.pi-bridge-key
python3 -m bridge --port 8790 --state-repo ~/learning-pi/state
```

In Open WebUI, open Settings → Connections → + and choose OpenAI API. The Base URL must be one a container can reach. For the default Docker bridge network, bind the bridge to that interface and use `http://172.17.0.1:8790/v1`. Or run Open WebUI with `--network host` and use `http://127.0.0.1:8790/v1`. A bridge bound to `127.0.0.1` is not reachable from a normal container through `host.docker.internal` on Linux. Set the API key to your bridge key, then pick the `learning` model.

The bridge takes these options: `--host/--port`, `--models a,b,c`, `--timeout`, `--max-turn`, `--max-sessions`, `--agent-dir`, `--session-dir`, `--ledger-dir`, `--openwebui-base-url`, `--openwebui-key-file`, `--sync-interval`, `--no-abort-on-disconnect`, and `--allow-bash-guard`. The `--allow-bash-guard` flag means you do not pass `--bash-guard-disabled`. Headless use of bash-guard is not recommended.

### Turn timeouts

`--timeout`, or the env var `PI_BRIDGE_TIMEOUT`, defaults to 1800 s. It is an idle budget: the longest pi may stay silent mid-turn. Every record resets the budget. A turn that spends 15 minutes inside a scout subagent is not killed, because no records arrive between `tool_execution_start` and its result. `--max-turn`, or `PI_BRIDGE_MAX_TURN`, defaults to 7200 s and is the absolute ceiling for one turn, so a runaway turn still releases the single-writer learning lock. An expired budget aborts the turn and surfaces `⚠️ pi runtime error: …` naming the budget to raise. Before 2026-10-29, `--timeout` was a 900 s wall-clock cap. That cap aborted healthy resume turns in Open WebUI.

### Sessions and restarts

The registry of live pi processes lives in memory, but every session starts with `--session-id` set to a deterministic value derived from the chat key. systemd restarts, reboots, LRU eviction from `--max-sessions`, and pi crashes all resume the same transcript. The id is `chat-<uuid>` when the client supplies a chat id, and `fp-<fingerprint>` otherwise. Any other key collapses to a stable hash.

Configure the connection's forwarded headers. This is recommended, and it is required for fork and delete mirroring:

```
X-OpenWebUI-Chat-Id:    {{CHAT_ID}}
X-OpenWebUI-Message-Id: {{MESSAGE_ID}}
```

The chat id is then authoritative, and two chats never share a pi session. Without the chat-id header, the bridge falls back to a fingerprint of the first user message plus the model name. Two chats whose first user message is identical then share one pi session, and editing that first message starts a new one. The first turn of an existing chat that has no chat-id session is migrated once from its fingerprint session. That migration happens only when the chat already has an assistant message, so upgrading does not blank an ongoing conversation.

## Chat actions mirror into pi

Open WebUI calls the bridge only for completions. It never tells an OpenAI-compatible backend that a chat was uploaded, forked, or deleted. The bridge closes that gap with the same REST key it uses for widgets: `--openwebui-base-url` plus `--openwebui-key-file`.

- Uploads turn image content parts into pi `ImageContent` blocks and send them on the `prompt` as `{type: image, data, mimeType}`. An image with no text gets a neutral prompt. Text plus images keep both. Non-image files follow Open WebUI's own file-context and RAG path, which puts the extracted text into the user message that the bridge already forwards.
- Fork and clone copy the parent branch. On the first turn of a chat whose metadata says it was forked (`meta.forked_from` or `chat.originalChatId`), the bridge copies the parent pi session's branch at the fork point into a new session file owned by the new chat id. A fork at a user message keeps that message. A fork at an assistant message keeps the turn that produced it. The copy is reused after a bridge restart, not duplicated.
- Edit, delete, regenerate, and Continue align pi with the posted transcript. The bridge compares the posted transcript's user messages with pi's active branch. An edited or deleted message forks pi at the turn being replaced before prompting. A regenerate re-answers the last user. A Continue click, where the transcript ends with the assistant, sends a marked continuation prompt without forking. The bridge filters the marker from later alignment. A compacted transcript, marked by a `[CONVERSATION SUMMARY]` system message, appends or continues without forking, so pi keeps its fuller context instead of losing the summarized turns. After any fork, the new branch replaces the chat's session file and pi switches to it, so restart and delete see the active transcript.
- Stop aborts the running turn. Open WebUI's Stop closes the streaming connection. The bridge watches the socket and aborts the pi turn, even while pi is silent inside a long tool call. It then drains to settlement and releases the learning lock. Leaving a chat mid-turn counts as Stop too. `--no-abort-on-disconnect`, or `PI_BRIDGE_ABORT_ON_DISCONNECT=false`, restores the old consume-to-settlement behavior.
- Delete removes the transcript. A background sweep runs every `--sync-interval` seconds, default 60, and a value of 0 disables it. The sweep proves the API key with the chat-list probe, then asks Open WebUI about every `chat-<id>` session and closes or removes it on a per-chat 401, 404, or 422. Open WebUI reports a missing chat as 401. A network error, an invalid key, a server error, an existing chat, or a turn still in flight never deletes a transcript. An in-flight session is retried on the next pass.

Fork and delete mirroring require the chat-id header above and the Open WebUI REST configuration. Without them the bridge keeps working, but fork starts a fresh chat and delete leaves the pi transcript alone. The sweep reads all chats individually, so it suits the normal single-user self-hosted deployment, not a large multi-tenant instance.

## Math rendering

Open WebUI renders standard LaTeX with KaTeX: `$...$`, `$$...$$`, `\(...\)`, and `\[...\]`. The bridge therefore sets `PI_MATH_MODE=latex` for its pi sessions. That setting overrides `math-mode`'s terminal detection. Headless pi has no image protocol, so without the setting the Tutor would fall back to plain Unicode. Set `PI_MATH_MODE=unicode`, or `auto`, only when you point a text-only client at the bridge.

## Intelligent-UI widgets

A verified `[[TURN:ui]]` turn carries one ` ```openui ` OpenUI Lang payload. The learning-gate's `ui-audit` verifies the payload and the prose. The bridge then lifts the fence out of the prose and builds a same-origin embed URL from `bridge/server.py`: `/static/openui/<version>/widget.html#<base64url payload>`. When the Open WebUI REST config is present, the bridge appends a second assistant message to the chat with an `embeds` event from `bridge/openwebui.py`, so the widget renders below the prose. Mermaid and HTML fences stay in the prose for Open WebUI's native rendering.

The widget cannot be a `data:` URL. Open WebUI's `FullHeightIframe` treats only `http://`, `https://`, and protocol-relative strings as URLs, and it renders a `data:` embed as literal text, so the shell is a served document. The pinned MIT bundle `@openuidev/browser-bundle@0.2.1`, the `widget.html` shell, and its `widget.js` are self-hosted under `deploy/openui/<version>/`. The installer `state/scripts/setup_openwebui.py` writes them. Open WebUI mounts them read-only at `/static/openui`. The verified payload rides in the URL fragment, not in an HTTP request body, but it is persisted as chat embed metadata alongside the transcript, so it is declarative OpenUI Lang only. `deploy/docker-compose.yml` pins `IFRAME_CSP` with `connect-src 'none'` and no CDN. The shell follows the OS light or dark setting, because the opaque-origin iframe cannot read Open WebUI's in-app theme. It re-measures on resize, font, and disclosure changes, and it falls back to `execCommand` when the sandbox denies the Clipboard API. See `docs/archive/plans/intelligent-ui/`.

Enable the widgets with `--openwebui-base-url`, or `PI_BRIDGE_OPENWEBUI_BASE_URL`, and a user API key from Settings → Account → API Keys. Put the key in `--openwebui-key-file`, or in `PI_BRIDGE_OPENWEBUI_KEY_FILE`. The default path is `~/.openwebui_key`, with mode 600. Widget delivery is best-effort: the prose always renders, and the bridge swallows an unconfigured or failing Open WebUI REST call. The bridge lifts the fence from the prose of any flow. The audit is pi-side correctness, and the bridge only transports the already-verified payload.

## Live action trace

Each completed pi step streams to Open WebUI as a `<details>` content block while the turn still runs, so the chat shows the agent's actions as they happen instead of the finished turn all at once.

- A tool execution becomes a `type="tool_calls"` block carrying the tool name, its arguments truncated to 200 characters, its status, and its duration. Open WebUI groups consecutive steps into one collapsible "Explored bash, read_file" row, with an "Exploring…" spinner while the message streams.
- A completed thinking block becomes a `type="reasoning"` block that reads "Thought for Ns". A learning flow shows only the duration. A general chat shows its text.
- A tool result is never rendered in a learning flow, because a result can carry the pre-gate draft. A general chat gets a truncated preview.

The bridge still never forwards `message_update` deltas. The trace is metadata about completed actions, not the draft (`B-deltas-never-forwarded`). The bridge emits step blocks complete and strictly formatted for Open WebUI's `<details>` parser (`bridge/stream.py`).

### Live status line

Open WebUI can optionally render a shimmering one-line status and a clickable timeline above the reply. To enable it, add the connection's custom forwarded headers in Settings → Connections → OpenAI API → Manage. This needs Open WebUI 0.10 or later.

```
X-OpenWebUI-Chat-Id:    {{CHAT_ID}}
X-OpenWebUI-Message-Id: {{MESSAGE_ID}}
```

The bridge then POSTs `status` events to `/api/v1/chats/<chat>/messages/<message>/event` with the same REST key as widget delivery (`--openwebui-base-url`). It always ends a started sequence with `done: true`, including after a provider error, so the shimmer never sticks. The status line is best-effort. Open WebUI may persist a message only after the stream ends, and a rejected event changes nothing. The step cards are the guaranteed trace. Without a message id, or without the Open WebUI REST config, the bridge posts no status.

## Single-writer policy

The learning system forbids two concurrent writers on the state repo. The bridge holds a learning lock for the duration of each learning turn and releases it when the turn ends. Concurrent learning turns therefore cannot overlap, including two turns from the same chat. A second chat that starts a learning turn meanwhile is told to wait. General chats are exempt. A chat counts as a learning flow if any user message in the transcript starts one, such as `/lesson` or `[[FLOW:…]]`. A bare learner answer after `/lesson` still takes the lock and keeps the learning display policy. Idle pi sessions are evicted LRU, and `--max-sessions` sets the cap.

## Limits

- The prose and any verified widget payload still arrive only at settlement, after the text is generated then verified then emitted. Only the action trace streams live.
- Regenerate, edit, and delete use pi's `fork`. If pi cannot fork, the bridge falls back to appending the prompt. A fork whose file is not written yet is adopted after the next settlement.
- The bridge declines interactive extension UI, such as approval dialogs. It does not surface them.

## Tests

`python3 -m unittest discover -s test/bridge` runs a deterministic suite against a fake pi at `test/bridge/fake_pi.py`. The suite needs no models and no network.

`test/bridge/run_tests.py` runs the same suite and prints one `PASS <test id>` line per passing test. `scripts/learn-check` uses those lines to bind the bridge invariants into the same contract-coverage check as the deno gate suites. Those invariants are the `B-*` set in `contracts/learning-core.json`.
