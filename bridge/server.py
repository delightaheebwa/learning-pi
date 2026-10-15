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

import hashlib
import hmac
import json
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

from .rpc import PiSession, PiError
from .stream import TurnStream

_LEARNING_CMD_RE = re.compile(
    r"^\s*/(review|solo|ingest|teach|lesson|continue|pause|audit|show|viz)\b",
    re.IGNORECASE,
)
_FLOW_MARKER = "[[FLOW:"


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


def last_user_text(messages) -> str:
    if not isinstance(messages, list):
        return ""
    for m in reversed(messages):
        if isinstance(m, dict) and m.get("role") == "user":
            return message_text(m)
    return ""


def is_learning_flow(text: str) -> bool:
    return bool(text) and (_FLOW_MARKER in text or bool(_LEARNING_CMD_RE.match(text)))


def session_key(body: dict, messages) -> str:
    """Stable per-conversation key.

    Prefer a client-supplied id (Open WebUI sends `metadata.chat_id`); fall back
    to a fingerprint of the first user message plus the requested model, which is
    stable across the turns of one conversation.
    """
    md = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
    for cand in (md.get("chat_id"), body.get("chat_id"), body.get("conversation_id")):
        if isinstance(cand, str) and cand:
            return "chat:" + cand
    first = ""
    if isinstance(messages, list):
        for m in messages:
            if isinstance(m, dict) and m.get("role") == "user":
                first = message_text(m)
                break
    seed = f"{body.get('model', '')}|{first}"
    return "fp:" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]


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
        self.last_user_text = ""
        self.answered = False
        self.last_used = time.monotonic()


class SessionRegistry:
    def __init__(self, config: "BridgeConfig") -> None:
        self.config = config
        self._mu = threading.Lock()
        self._entries: dict[str, SessionEntry] = {}

    def get_or_create(self, key: str) -> SessionEntry:
        with self._mu:
            entry = self._entries.get(key)
            if entry is not None and entry.session.alive():
                entry.last_used = time.monotonic()
                return entry
            if entry is not None:
                entry.session.close()
            # Evict the least-recently-used *idle* session if we are at the cap,
            # so a long-lived bridge does not accumulate one pi process per chat.
            # Never evict a session with a turn in flight (its lock is held);
            # overshoot the cap rather than kill live work.
            cap = self.config.max_sessions
            if cap > 0 and len(self._entries) >= cap:
                idle = [k for k, e in self._entries.items() if k != key and not e.lock.locked()]
                if idle:
                    victim = min(idle, key=lambda k: self._entries[k].last_used)
                    self._entries.pop(victim).session.close()
            session = PiSession(
                pi_bin=self.config.pi_bin,
                cwd=self.config.state_repo,
                env=self.config.child_env(),
                name=f"bridge-{key.replace(':', '-')[:12]}",
                extra_args=self.config.session_args(),
            )
            session.start()
            entry = SessionEntry(key, session)
            self._entries[key] = entry
            return entry

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
        timeout: float = 900.0,
        models: Optional[list] = None,
        agent_dir: Optional[str] = None,
        session_dir: Optional[str] = None,
        ledger_dir: Optional[str] = None,
        disable_bash_guard: bool = True,
        max_sessions: int = 8,
        child_env_extra: Optional[dict] = None,
    ) -> None:
        self.pi_bin = pi_bin
        self.state_repo = state_repo
        self.api_key = api_key
        self.host = host
        self.port = port
        self.timeout = timeout
        self.models = models or ["learning"]
        self.agent_dir = agent_dir
        self.session_dir = session_dir
        self.ledger_dir = ledger_dir
        self.disable_bash_guard = disable_bash_guard
        self.max_sessions = max_sessions
        self.child_env_extra = child_env_extra or {}

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
        user = last_user_text(messages)
        if not user.strip():
            self._send_json(400, {"error": {"message": "no user message"}})
            return

        key = session_key(body, messages)
        learning = is_learning_flow(user)

        acquired = False
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
        try:
            entry = self.server.registry.get_or_create(key)  # type: ignore[attr-defined]
            turn = self._run_turn(entry, user)
        except (PiError, OSError) as exc:
            turn = TurnStream()
            turn.text = f"⚠️ pi runtime error: {exc}"
        finally:
            if acquired:
                self.server.learning.release(key)  # type: ignore[attr-defined]

        content = turn.final_text()
        if stream:
            self._stream_from(model, content)
        else:
            self._send_json(200, self._completion(model, content))

    # -- turn execution ----------------------------------------------------
    def _run_turn(self, entry: SessionEntry, user: str) -> TurnStream:
        with entry.lock:
            regenerate = entry.answered and entry.last_user_text == user
            if regenerate and entry.session.alive():
                try:
                    entry.session.fork_last_user_message()
                except PiError:
                    pass  # fall back to appending the prompt
            turn = TurnStream()
            entry.session.prompt(user, turn.feed, timeout=self.cfg.timeout)
            entry.last_user_text = user
            entry.answered = True
            entry.last_used = time.monotonic()
            return turn

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

    def _stream_constant(self, model: str, content: str) -> None:
        self._sse_headers()
        self._write_sse(self._chunk(model, {"role": "assistant", "content": content}))
        self._write_sse(self._chunk(model, {}, "stop"))
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
        self.close_connection = True

    def _stream_from(self, model: str, content: str) -> None:
        self._sse_headers()
        self._write_sse(self._chunk(model, {"role": "assistant"}))
        if content:
            self._write_sse(self._chunk(model, {"content": content}))
        self._write_sse(self._chunk(model, {}, "stop"))
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
        self.close_connection = True


def serve(config: BridgeConfig) -> None:
    httpd = BridgeServer(config)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.registry.close_all()
        httpd.server_close()
