"""OpenAI-compatible HTTP face over the pi RPC runtime.

Endpoints:
  GET  /healthz                liveness (no auth)
  GET  /v1/models              the model aliases Open WebUI can pick
  POST /v1/chat/completions    one chat turn -> one pi prompt (streaming or not)

The bridge is intentionally thin: it owns session routing, the buffering rule
(see `stream.py`), the single-writer learning lock, and auth. All learning
behaviour lives in pi (the gate, subagents, skills).
"""
from __future__ import annotations

import base64
import hmac
import json
import os
import re
import select
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

from .align import plan_turn
from .chatsync import ChatSync
from .rpc import PiSession, PiError
from .session_key import session_id_for, session_key
from .stream import TurnStream, render_steps
from . import openwebui

_LEARNING_CMD_RE = re.compile(
    r"^\s*/(review|solo|ingest|teach|lesson|continue|pause|audit)\b",
    re.IGNORECASE,
)
_FLOW_MARKER = "[[FLOW:"

# --- widget embeds ----------------------------------------------------------
# A verified `[[TURN:ui]]` payload is delivered as an Open WebUI Rich UI embed.
# It cannot be a `data:` URL: Open WebUI's `FullHeightIframe` only treats an
# `http(s)://` (or protocol-relative) string as a URL, and renders a `data:`
# embed as literal text. So the shell document, the pinned OpenUI bundle, and
# its stylesheet are self-hosted same-origin (written by
# `learning-system/scripts/setup_openwebui.py`), and the payload rides in the
# URL fragment (persisted as chat embed metadata alongside the transcript). The
# payload is declarative OpenUI Lang (no script, no network), so a data-only
# fragment is safe. See `docs/plans/intelligent-ui/`.
OPENUI_BUNDLE_VERSION = "0.2.1"  # pinned per docs/plans/intelligent-ui/PHASE0-FINDINGS.md
_OPENUI_STATIC_PATH = "/static/openui"
_OPENUI_WIDGET_FILE = "widget.html"


def default_bundle_base(openwebui_base_url: str) -> str:
    """Absolute same-origin URL of the self-hosted pinned bundle + shell."""
    return f"{openwebui_base_url.rstrip('/')}{_OPENUI_STATIC_PATH}/{OPENUI_BUNDLE_VERSION}"


def payload_fragment(payload: str) -> str:
    """URL-safe (unpadded) base64 of the payload — safe to place in a fragment."""
    encoded = base64.urlsafe_b64encode((payload or "").encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def widget_embed_url(payload: str, *, bundle_base: str) -> str:
    """Deliverable embed URL for a verified OpenUI payload."""
    return f"{bundle_base.rstrip('/')}/{_OPENUI_WIDGET_FILE}#" + payload_fragment(payload)


def message_text(message: dict) -> str:
    """Text of one chat message (content may be a string or a part list)."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for p in content:
            if isinstance(p, str):
                out.append(p)
            elif isinstance(p, dict) and isinstance(p.get("text"), str):
                out.append(p["text"])
        return "".join(out)
    return ""


def is_learning_flow(text: str) -> bool:
    return bool(text) and (_FLOW_MARKER in text or bool(_LEARNING_CMD_RE.match(text)))


def transcript_is_learning_flow(messages) -> bool:
    """Whether any user message in the transcript starts a learning flow.

    The gate keeps its run state across bare learner answers, so the bridge must
    too: a chat that began with `/lesson` or `[[FLOW:…]]` stays a learning flow
    for display policy and the single-writer lock even when the newest user
    message is just an answer.
    """
    if not isinstance(messages, list):
        return False
    return any(
        is_learning_flow(message_text(m))
        for m in messages
        if isinstance(m, dict) and m.get("role") == "user"
    )


def openwebui_ids(headers, body) -> tuple[str, str]:
    """Open WebUI chat/message ids, for per-message status events.

    Normally supplied by the connection's custom forwarded headers
    (`{{CHAT_ID}}` / `{{MESSAGE_ID}}`, Open WebUI >= 0.10); `metadata.chat_id`
    is the fallback the widget path already understands.
    """
    md = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
    chat = ""
    for cand in (
        headers.get("X-OpenWebUI-Chat-Id"),
        md.get("chat_id"),
        body.get("chat_id"),
        body.get("conversation_id"),
    ):
        if isinstance(cand, str) and cand:
            chat = cand
            break
    message = headers.get("X-OpenWebUI-Message-Id")
    return chat, message if isinstance(message, str) else ""


# Images reach the bridge as OpenAI `image_url` / `input_image` content parts
# (Open WebUI converts uploaded URLs to base64 data URIs before forwarding).
_IMAGE_PART_TYPES = {"image_url", "input_image", "image"}


def _image_from_part(part: dict) -> Optional[dict]:
    """One pi `ImageContent` (`{type, data, mimeType}`) from an OpenAI part."""
    if not isinstance(part, dict):
        return None
    kind = part.get("type")
    if kind not in _IMAGE_PART_TYPES:
        return None
    if kind == "image":
        data = part.get("data")
        mime = part.get("mimeType") or part.get("mime_type") or "image/png"
        if isinstance(data, str) and data:
            return {"type": "image", "data": data, "mimeType": str(mime)}
        return None
    value = part.get("image_url")
    if isinstance(value, dict):
        url = value.get("url")
    else:
        url = value
    if not isinstance(url, str) or not url:
        return None
    header, sep, data = url.partition(",")
    if not sep or not header.startswith("data:") or ";base64" not in header:
        # Open WebUI normally converts uploads to data URIs; a remote URL is
        # not something pi's prompt command accepts, so leave it out rather
        # than inventing a fetch policy here.
        return None
    mime = header[len("data:"):].split(";", 1)[0] or "image/png"
    if not mime.startswith("image/") or not data:
        return None
    return {"type": "image", "data": data, "mimeType": mime}


def message_images(message: dict) -> list[dict]:
    """Image content of one chat message, in the order the client sent it."""
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return []
    images = []
    for part in content:
        image = _image_from_part(part)
        if image is not None:
            images.append(image)
    return images


def last_user_message(messages) -> tuple[str, list[dict]]:
    """Text and images of the newest user message."""
    if not isinstance(messages, list):
        return "", []
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            return message_text(message), message_images(message)
    return "", []


def last_user_text(messages) -> str:
    """Text of the newest user message (kept as the narrow test/helper API)."""
    return last_user_message(messages)[0]


def transcript_user_texts(messages) -> list[str]:
    """Every user-message text in the posted transcript, in order."""
    if not isinstance(messages, list):
        return []
    return [
        message_text(message) for message in messages
        if isinstance(message, dict) and message.get("role") == "user"
    ]


def ends_with_assistant(messages) -> bool:
    """Whether the posted transcript ends on an assistant message."""
    return bool(messages) and isinstance(messages[-1], dict) and messages[-1].get("role") == "assistant"


def has_conversation_summary(messages) -> bool:
    """Whether Open WebUI compacted this transcript into a summary."""
    if not isinstance(messages, list):
        return False
    for message in messages:
        if not isinstance(message, dict) or message.get("role") != "system":
            continue
        if "[CONVERSATION SUMMARY]" in message_text(message):
            return True
    return False


class LearningLock:
    """One learning turn at a time on the shared state repo.

    The learning system forbids two concurrent writers (FIELD-GUIDE). The lock is
    held only for the duration of a learning turn and released when it ends, so
    concurrent learning turns in different chats cannot overlap while the lock
    never gets stuck to an idle owner. General (non-learning) chats are exempt; a
    second chat that starts a learning turn meanwhile is told to wait.
    """

    def __init__(self) -> None:
        self._mu = threading.Lock()
        self._owner: Optional[str] = None
        self._count = 0

    def acquire(self, key: str) -> bool:
        with self._mu:
            if self._owner in (None, key):
                self._owner = key
                self._count += 1
                return True
            return False

    def release(self, key: str) -> None:
        with self._mu:
            if self._owner == key:
                self._count -= 1
                if self._count <= 0:
                    self._count = 0
                    self._owner = None

    def owner(self) -> Optional[str]:
        with self._mu:
            return self._owner


class SessionEntry:
    def __init__(self, key: str, session: PiSession) -> None:
        self.key = key
        self.session = session
        self.lock = threading.Lock()
        self.inflight = False
        self.last_user_text = ""
        self.answered = False
        # Sticky learning-flow marker: Open WebUI may compact the transcript and
        # drop the `/lesson` message, but the gate's run state is still active.
        # It is intentionally never cleared; a chat that ran a learning flow
        # stays conservative (lock + hidden tool output) rather than risk
        # exposing an active gate's draft.
        self.learning_flow = False
        # Visible user messages from the previous turn. Comparing the next
        # transcript against this list is exact even when pi stored a RAG
        # envelope instead of the original query.
        self.open_user_texts = None
        self.last_used = time.monotonic()


class SessionRegistry:
    def __init__(self, config: "BridgeConfig") -> None:
        self.config = config
        self._mu = threading.Lock()
        self._entries: dict[str, SessionEntry] = {}

    def get_or_create(self, key: str, *, session_file=None) -> SessionEntry:
        with self._mu:
            entry = self._entries.get(key)
            if entry is not None and entry.session.alive():
                entry.last_used = time.monotonic()
                entry.inflight = True
                return entry
            if entry is not None:
                entry.session.close()
                self._entries.pop(key, None)
            # Evict the least-recently-used *idle* session if we are at the cap,
            # so a long-lived bridge does not accumulate one pi process per chat.
            # Entries returned by get_or_create are marked inflight under this
            # lock (and cleared when the turn ends), so a session can never be
            # evicted between allocation and its turn; overshoot rather than kill
            # live work.
            cap = self.config.max_sessions
            if cap > 0 and len(self._entries) >= cap:
                idle = [
                    k for k, e in self._entries.items()
                    if k != key and not e.inflight and not e.lock.locked()
                ]
                if idle:
                    victim = min(idle, key=lambda k: self._entries[k].last_used)
                    self._entries.pop(victim).session.close()
            session = PiSession(
                pi_bin=self.config.pi_bin,
                cwd=self.config.state_repo,
                env=self.config.child_env(),
                # The id is the identity; the display name mirrors it so two
                # chats cannot look ambiguous in pi's session list.
                name=f"bridge-{session_id_for(key)}",
                extra_args=self.config.session_args(),
                session_id=session_id_for(key),
                session_file=str(session_file) if session_file else None,
            )
            session.start()
            entry = SessionEntry(key, session)
            entry.inflight = True
            self._entries[key] = entry
            return entry

    def peek(self, key: str) -> Optional[SessionEntry]:
        """The current entry without creating one or marking it in flight."""
        with self._mu:
            return self._entries.get(key)

    def has_live(self, key: str) -> bool:
        """Whether this key already has a running pi session."""
        with self._mu:
            entry = self._entries.get(key)
            if entry is not None and entry.session.alive():
                entry.last_used = time.monotonic()
                return True
            return False

    def chat_keys(self) -> list[str]:
        """Keys for chats that may need cleanup, snapshot under the lock."""
        with self._mu:
            return [k for k in self._entries if k.startswith("chat:")]

    def pop_if_idle(self, key: str) -> tuple[Optional[SessionEntry], bool]:
        """Remove an idle entry for deletion; `(entry, busy)`.

        A session with a turn in flight is left in place so the next sweep can
        retry: deleting the transcript while pi is writing it is worse than a
        short delay.
        """
        with self._mu:
            entry = self._entries.get(key)
            if entry is None:
                return None, False
            if entry.inflight or entry.lock.locked():
                return None, True
            self._entries.pop(key, None)
            return entry, False

    def close_all(self) -> None:
        with self._mu:
            for entry in self._entries.values():
                entry.session.close()
            self._entries.clear()


class BridgeConfig:
    def __init__(
        self,
        pi_bin: str,
        state_repo: str,
        api_key: str,
        host: str = "127.0.0.1",
        port: int = 8790,
        timeout: float = 1800.0,
        max_turn: float = 7200.0,
        models: Optional[list] = None,
        agent_dir: Optional[str] = None,
        session_dir: Optional[str] = None,
        ledger_dir: Optional[str] = None,
        disable_bash_guard: bool = True,
        max_sessions: int = 8,
        child_env_extra: Optional[dict] = None,
        openwebui_base_url: str = "",
        openwebui_key_file: str = openwebui.DEFAULT_KEY_FILE,
        sync_interval: float = 60.0,
        abort_on_disconnect: bool = True,
    ) -> None:
        self.pi_bin = pi_bin
        self.state_repo = state_repo
        self.api_key = api_key
        self.host = host
        self.port = port
        # Idle budget: the longest pi may stay silent mid-turn. A learning turn
        # can spend ~15 minutes inside one scout subagent with no records in
        # between, so a wall-clock cap here would abort healthy turns (the
        # 2026-10-29 Open WebUI "pi runtime error" sessions).
        self.timeout = timeout
        # Absolute ceiling for one turn: a runaway turn must still release the
        # single-writer learning lock.
        self.max_turn = max_turn
        self.models = models or ["learning"]
        self.agent_dir = agent_dir
        self.session_dir = session_dir
        self.ledger_dir = ledger_dir
        self.disable_bash_guard = disable_bash_guard
        self.max_sessions = max_sessions
        self.child_env_extra = child_env_extra or {}
        self.openwebui_base_url = openwebui_base_url
        self.openwebui_key_file = openwebui_key_file
        # Seconds between delete sweeps; 0 disables the background worker.
        self.sync_interval = sync_interval
        # Treat a streaming client disconnect as Stop (abort the pi turn).
        self.abort_on_disconnect = abort_on_disconnect

    def openwebui_client(self) -> Optional[openwebui.OpenWebUIClient]:
        """A client for the post-turn widget embed, or None when unconfigured."""
        if not self.openwebui_base_url:
            return None
        key = openwebui.read_key(self.openwebui_key_file)
        if not key:
            return None
        return openwebui.OpenWebUIClient(self.openwebui_base_url, key)

    def session_args(self) -> list:
        args: list = []
        # Only pass the flag when bash-guard is actually loaded: it is a global
        # extension, and pi rejects an extension flag that no loaded extension
        # registered (the sandbox has no bash-guard, so the flag would kill pi).
        if self.disable_bash_guard and self._bash_guard_present():
            args.append("--bash-guard-disabled")
        return args

    def _bash_guard_present(self) -> bool:
        base = self.agent_dir or os.environ.get("PI_CODING_AGENT_DIR") or str(Path.home() / ".pi" / "agent")
        return (Path(base) / "extensions" / "bash-guard").exists()

    def child_env(self) -> dict:
        env = dict(os.environ)
        if self.agent_dir:
            env["PI_CODING_AGENT_DIR"] = self.agent_dir
        if self.session_dir:
            env["PI_CODING_AGENT_SESSION_DIR"] = self.session_dir
        if self.ledger_dir:
            env["LEARNING_GATE_LEDGER_DIR"] = self.ledger_dir
        # The bridge's front-end is Open WebUI, which renders LaTeX with
        # KaTeX/MathJax even though the headless pi process has no terminal
        # image protocol. Force LaTeX authoring unless the operator overrides it
        # (PI_MATH_MODE=unicode for a text-only client).
        env.setdefault("PI_MATH_MODE", "latex")
        env.update(self.child_env_extra)
        return env


class BridgeServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, config: BridgeConfig) -> None:
        super().__init__((config.host, config.port), Handler)
        self.config = config
        self.registry = SessionRegistry(config)
        self.learning = LearningLock()
        self.sync = ChatSync(config, self.registry)


class Handler(BaseHTTPRequestHandler):
    server_version = "pi-bridge/0.1"
    protocol_version = "HTTP/1.1"

    # -- helpers -----------------------------------------------------------
    @property
    def cfg(self) -> BridgeConfig:
        return self.server.config  # type: ignore[attr-defined]

    def log_message(self, fmt, *args):  # keep the default log on stderr, quiet
        pass

    def _send_json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _auth_ok(self) -> bool:
        header = self.headers.get("Authorization", "")
        token = header[7:] if header.lower().startswith("bearer ") else ""
        if not self.cfg.api_key:
            return False
        # compare bytes: a non-ASCII header byte must yield False, not a
        # TypeError from hmac.compare_digest on str inputs.
        try:
            return hmac.compare_digest(
                token.encode("utf-8", "surrogateescape"),
                self.cfg.api_key.encode("utf-8"),
            )
        except (UnicodeError, TypeError):
            return False

    def _read_body(self) -> Optional[dict]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    # -- routes ------------------------------------------------------------
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/healthz":
            self._send_json(200, {"status": "ok"})
            return
        if path == "/v1/models":
            if not self._auth_ok():
                self._send_json(401, {"error": {"message": "unauthorized"}})
                return
            now = int(time.time())
            self._send_json(
                200,
                {
                    "object": "list",
                    "data": [
                        {"id": m, "object": "model", "created": now, "owned_by": "learning-pi"}
                        for m in self.cfg.models
                    ],
                },
            )
            return
        self._send_json(404, {"error": {"message": "not found"}})

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/v1/chat/completions":
            self._send_json(404, {"error": {"message": "not found"}})
            return
        if not self._auth_ok():
            self._send_json(401, {"error": {"message": "unauthorized"}})
            return
        body = self._read_body()
        if body is None:
            self._send_json(400, {"error": {"message": "invalid JSON body"}})
            return
        stream = bool(body.get("stream", False))
        model = str(body.get("model") or (self.cfg.models[0] if self.cfg.models else "learning"))
        messages = body.get("messages") or []
        user, images = last_user_message(messages)
        if not user.strip() and not images:
            self._send_json(400, {"error": {"message": "no user message"}})
            return
        if not user.strip():
            user = "Describe the attached image." if len(images) == 1 else "Describe the attached images."

        chat_id, message_id = openwebui_ids(self.headers, body)
        key = session_key(body, messages, chat_id=chat_id)
        transcript_users = transcript_user_texts(messages)
        if not (transcript_users and transcript_users[-1].strip()):
            # An image-only turn has no text; keep alignment's last user equal
            # to the neutral prompt actually sent to pi.
            if transcript_users:
                transcript_users[-1] = user
            else:
                transcript_users = [user]
        # A learning flow stays active for its bare learner answers (the gate
        # keeps its run state across prompts), so classify the whole transcript:
        # a bare answer after `/lesson` must still take the single-writer lock
        # and hide tool results/thinking. The per-entry flag survives transcript
        # compaction, which can drop the original `/lesson` message.
        existing = self.server.registry.peek(key)  # type: ignore[attr-defined]
        learning = transcript_is_learning_flow(messages) or bool(
            existing is not None and existing.learning_flow
        )
        continuation = ends_with_assistant(messages)
        compacted = has_conversation_summary(messages)
        self._client_gone = False
        self._disconnect_done = threading.Event()

        acquired = False
        reporter = None
        turn = None
        try:
            if learning:
                if not self.server.learning.acquire(key):  # type: ignore[attr-defined]
                    note = (
                        "⛔ Another learning session is currently active in a different chat. "
                        "Finish or pause it before starting a learning flow here."
                    )
                    if stream:
                        self._stream_constant(model, note)
                    else:
                        self._send_json(200, self._completion(model, note))
                    return
                acquired = True

            reporter = self._status_reporter(chat_id, message_id)
            sink = self._step_sink(model, learning, reporter, stream)
            if stream:
                self._sse_headers()
                self._try_write_sse(self._chunk(model, {"role": "assistant"}))

            try:
                entry = self._session_entry(key, chat_id, model)
                if learning:
                    entry.learning_flow = True
                if stream and self.cfg.abort_on_disconnect:
                    threading.Thread(
                        target=self._watch_disconnect,
                        args=(self._disconnect_done,),
                        daemon=True,
                    ).start()
                turn = self._run_turn(
                    entry,
                    user,
                    images=images,
                    transcript_users=transcript_users,
                    continuation=continuation,
                    compacted=compacted,
                    learning=learning,
                    on_step=sink,
                    should_abort=(
                        (lambda: self._client_gone)
                        if stream and self.cfg.abort_on_disconnect
                        else None
                    ),
                )
            except (PiError, OSError) as exc:
                # Surface the reason in the journal too: a bare UI bubble left no
                # trace of the 2026-10-29 turn-timeout incident.
                print(f"pi-bridge: turn failed: {exc}", file=sys.stderr, flush=True)
                turn = TurnStream(learning=learning)
                turn.text = f"⚠️ pi runtime error: {exc}"
            finally:
                if acquired:
                    self.server.learning.release(key)  # type: ignore[attr-defined]
                    acquired = False

            content = turn.final_text()
            if stream:
                self._finish_stream(model, content)
            else:
                steps_text = render_steps(turn.steps, learning=learning)
                self._send_json(200, self._completion(model, steps_text + content))
            self._deliver_widgets(key, model, turn.openui_payloads())
        finally:
            self._disconnect_done.set()
            if acquired:
                self.server.learning.release(key)  # type: ignore[attr-defined]
            if reporter is not None:
                failed = turn is not None and (
                    turn.error or turn.text.startswith("⚠️ pi runtime error")
                )
                reporter.close("pi runtime error" if failed else "Done")

    def _session_entry(self, key: str, chat_id: str, model: str):
        """A live session, preparing a forked chat's branch on first use."""
        registry = self.server.registry  # type: ignore[attr-defined]
        session_file = None
        if key.startswith("chat:") and not registry.has_live(key):
            # Idempotent: an existing fork file is reused across bridge restarts.
            session_file = self.server.sync.plan_fork(  # type: ignore[attr-defined]
                chat_id, model, session_id_for(key)
            )
        return registry.get_or_create(key, session_file=session_file)

    def _status_reporter(self, chat_id: str, message_id: str):
        """A live-status reporter, or None without ids / Open WebUI config."""
        if not chat_id or not message_id:
            return None
        client = self.cfg.openwebui_client()
        if client is None:
            return None
        return openwebui.StatusReporter(client, chat_id, message_id)

    def _step_sink(self, model: str, learning: bool, reporter, stream_cards: bool):
        """Turn a `Step` into UI output.

        A completed step is written as a complete SSE chunk the moment it
        finishes, so Open WebUI shows the action before the turn settles; a
        transient start step has no card, only a status line. Status events are
        supplementary (live shimmer + timeline); failures there are swallowed by
        the reporter.
        """

        def sink(step) -> None:
            if stream_cards:
                text = step.render(learning=learning)
                if text:
                    self._try_write_sse(self._chunk(model, {"content": text}))
            if reporter is not None:
                reporter.status(step.status_line())

        return sink

    def _deliver_widgets(self, key: str, model: str, payloads: list) -> None:
        """Deliver verified OpenUI payloads as an embed on a 2nd assistant message.

        Best-effort and off the response path: the prose already rendered, and no
        delivery failure may surface to the learner. Only chats with a real Open
        WebUI id (`chat:<id>`) are eligible; a fingerprint-only session has no
        chat to attach to.
        """
        if not payloads or not key.startswith("chat:"):
            return
        client = self.cfg.openwebui_client()
        if client is None:
            return
        bundle_base = default_bundle_base(self.cfg.openwebui_base_url)
        urls = [widget_embed_url(p, bundle_base=bundle_base) for p in payloads]
        chat_id = key[len("chat:") :]
        threading.Thread(
            target=self._deliver_widgets_bg,
            args=(client, chat_id, model, urls),
            daemon=True,
        ).start()

    @staticmethod
    def _deliver_widgets_bg(client, chat_id: str, model: str, urls: list) -> None:
        try:
            client.append_widget(chat_id, urls, model=model)
        except Exception:
            pass  # best-effort: the learner already has the prose

    # -- turn execution ----------------------------------------------------
    def _run_turn(
        self,
        entry: SessionEntry,
        user: str,
        *,
        images=None,
        transcript_users=None,
        continuation: bool = False,
        compacted: bool = False,
        learning: bool = True,
        on_step=None,
        should_abort=None,
    ) -> TurnStream:
        # Mark in flight before taking the lock so the registry cannot evict this
        # session in the window between get_or_create and the lock.
        entry.inflight = True
        try:
            with entry.lock:
                plan = self._turn_plan(
                    entry, transcript_users or [], continuation, compacted
                )
                if plan.fork_entry_id and entry.session.alive():
                    try:
                        entry.session.fork_to_entry(plan.fork_entry_id)
                    except PiError:
                        pass  # fall back to appending the prompt
                elif plan.fork_last and entry.session.alive():
                    try:
                        entry.session.fork_last_user_message()
                    except PiError:
                        pass  # fall back to appending the prompt

                turn = TurnStream(learning=learning, on_step=on_step)
                try:
                    entry.session.prompt(
                        plan.prompt,
                        turn.feed,
                        timeout=self.cfg.timeout,
                        max_turn=self.cfg.max_turn,
                        # An assistant continuation has no new upload; do not
                        # re-send the previous user message's images.
                        images=None if plan.continuation else images,
                        should_abort=should_abort,
                    )
                finally:
                    if entry.session.alive():
                        try:
                            entry.session.persist_fork()
                        except Exception as exc:
                            print(
                                f"pi-bridge: could not persist forked session: {exc}",
                                file=sys.stderr,
                                flush=True,
                            )
                entry.open_user_texts = list(transcript_users or [])
                entry.last_user_text = user
                entry.answered = True
                entry.last_used = time.monotonic()
                return turn
        finally:
            entry.inflight = False

    @staticmethod
    def _turn_plan(
        entry: SessionEntry,
        transcript_users: list,
        continuation: bool,
        compacted: bool = False,
    ):
        """Plan alignment against pi's own user messages (fallback if unknown)."""
        pi_messages = []
        known = False
        if entry.session.alive():
            try:
                pi_messages = entry.session.get_fork_messages(timeout=10.0)
                known = True
            except PiError:
                known = False
        return plan_turn(
            transcript_users,
            pi_messages,
            trailing_assistant=continuation,
            answered=entry.answered,
            last_user_text=entry.last_user_text,
            pi_known=known,
            previous_open_users=entry.open_user_texts,
            compacted=compacted,
        )

    # -- serialisation -----------------------------------------------------
    def _completion(self, model: str, content: str) -> dict:
        return {
            "id": f"chatcmpl-{int(time.time() * 1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    def _sse_headers(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

    def _write_sse(self, payload: dict) -> None:
        self.wfile.write(f"data: {json.dumps(payload)}\n\n".encode("utf-8"))
        self.wfile.flush()

    def _chunk(self, model: str, delta: dict, finish=None) -> dict:
        return {
            "id": f"chatcmpl-{int(time.time() * 1000)}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
        }

    def _watch_disconnect(self, done: threading.Event) -> None:
        """Mark the client gone when the streaming socket reaches EOF.

        Open WebUI's Stop aborts the fetch; the bridge otherwise only notices
        on the next failed write, which may not happen while pi is silent in a
        long tool call. The watcher polls the socket directly so the turn can be
        aborted promptly.
        """
        conn = self.connection
        while not done.wait(0.25):
            if self._client_gone:
                return
            try:
                readable, _, _ = select.select([conn], [], [], 0)
            except (OSError, ValueError):
                return
            if not readable:
                continue
            try:
                chunk = conn.recv(1, socket.MSG_PEEK)
            except (BlockingIOError, InterruptedError):
                continue
            except (OSError, ValueError):
                chunk = b""
            if chunk == b"":
                self._client_gone = True
                return
            # Unexpected client data mid-request: back off instead of spinning.
            time.sleep(0.25)

    def _try_write_sse(self, payload: dict) -> bool:
        """Write one SSE chunk unless the client already went away."""
        if self._client_gone:
            return False
        try:
            self._write_sse(payload)
            return True
        except OSError:
            # The disconnect watcher will abort the turn; keep consuming until
            # pi settles so records cannot bleed into the next prompt.
            self._client_gone = True
            return False

    def _finish_stream(self, model: str, content: str) -> None:
        """Emit the post-gate prose, the terminal chunk, and `[DONE]`."""
        if content:
            self._try_write_sse(self._chunk(model, {"content": content}))
        self._try_write_sse(self._chunk(model, {}, "stop"))
        if not self._client_gone:
            try:
                self.wfile.write(b"data: [DONE]\n\n")
                self.wfile.flush()
            except OSError:
                self._client_gone = True
        self.close_connection = True

    def _stream_constant(self, model: str, content: str) -> None:
        self._sse_headers()
        self._write_sse(self._chunk(model, {"role": "assistant", "content": content}))
        self._write_sse(self._chunk(model, {}, "stop"))
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
        self.close_connection = True


def serve(config: BridgeConfig) -> None:
    httpd = BridgeServer(config)
    httpd.sync.start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.sync.stop()
        httpd.registry.close_all()
        httpd.server_close()
