"""Minimal Open WebUI REST client for delivering widget embeds.

pi-bridge is an OpenAI-compatible endpoint, not an Open WebUI Filter/Pipe, so it
cannot use the Filter `__event_emitter__` path. It uses the public REST route
instead: append a second assistant message to the chat and attach an `embeds`
event to it, so the widget renders **below** the prose (Rich UI message embeds
render above a message's own text; see docs/plans/intelligent-ui/PHASE0-FINDINGS.md).
"""
from __future__ import annotations

import json
import os
import queue
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import quote

DEFAULT_KEY_FILE = "~/.openwebui_key"


def read_key(key_file: Optional[str] = None) -> str:
    """Read the Open WebUI API key from `OPENWEBUI_API_KEY` or a key file."""
    env = os.environ.get("OPENWEBUI_API_KEY", "").strip()
    if env:
        return env
    path = Path(os.path.expanduser(key_file or DEFAULT_KEY_FILE))
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


class OpenWebUIError(Exception):
    """A REST call failed (network, non-2xx, or a rejected write)."""


class OpenWebUIClient:
    """Tiny urllib-based client; no third-party dependency."""

    def __init__(self, base_url: str, key: str, timeout: float = 20.0) -> None:
        self.base = base_url.rstrip("/")
        self.key = key
        self.timeout = timeout

    def call(self, method: str, path: str, body: Optional[dict] = None):
        """Return `(status, parsed_or_text)`. HTTP errors are not raised."""
        url = self.base + path
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", "Bearer " + self.key)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                if not raw:
                    return resp.status, None
                try:
                    return resp.status, json.loads(raw)
                except ValueError:
                    # A 2xx with a non-JSON body is still a valid "call done" for
                    # callers that only inspect `status` (the embed event returns
                    # a bare `true`); never let it raise past this boundary.
                    return resp.status, raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = raw.decode("utf-8", "replace")
            return exc.code, parsed

    def _history(self, chat: dict) -> dict:
        return ((chat or {}).get("chat") or {}).get("history") or {}

    def post_message_event(self, chat_id: str, message_id: str, event: dict) -> bool:
        """Post one per-message event (`status`, `embeds`, …) to Open WebUI.

        Requires the Open WebUI chat/message ids, normally supplied by the
        connection's custom forwarded headers (`{{CHAT_ID}}` / `{{MESSAGE_ID}}`).
        Best-effort: a non-2xx (e.g. a mid-stream message Open WebUI has not
        persisted yet) returns False instead of raising.
        """
        if not chat_id or not message_id:
            return False
        status, ok = self.call(
            "POST",
            f"/api/v1/chats/{quote(chat_id, safe='')}/messages/"
            f"{quote(message_id, safe='')}/event",
            event,
        )
        return status == 200 and ok is True

    def post_status(self, chat_id: str, message_id: str, description: str, done: bool) -> bool:
        """Post one `status` event (the live line above the reply)."""
        return self.post_message_event(
            chat_id,
            message_id,
            {"type": "status", "data": {"description": description, "done": bool(done)}},
        )

    def _wait_for_assistant_parent(self, chat_id: str, attempts: int, delay: float):
        """Poll until the chat's current node is the just-saved assistant message.

        Open WebUI persists the assistant message after it finishes consuming the
        bridge's stream, so the bridge's post-turn REST write can race it. Wait
        for the current node to be an assistant message, then parent the widget
        to it. Returns `(parent_id, models)` or `(None, None)`.
        """
        for i in range(max(1, attempts)):
            status, chat = self.call("GET", f"/api/v1/chats/{quote(chat_id, safe='')}")
            if status == 200 and isinstance(chat, dict):
                history = self._history(chat)
                current = history.get("currentId")
                node = (history.get("messages") or {}).get(current)
                if isinstance(node, dict) and node.get("role") == "assistant":
                    return current, chat.get("chat", {}).get("models") or []
            if i < attempts - 1:
                time.sleep(delay)
        return None, None

    def append_widget(
        self,
        chat_id: str,
        embed_urls: list,
        *,
        model: str = "",
        caption: str = "",
        attempts: int = 10,
        delay: float = 0.4,
    ) -> bool:
        """Append a second assistant message carrying `embed_urls` beneath the prose.

        Returns True only after the new message is confirmed present in the
        server's response and the embed event is accepted.
        """
        urls = [u for u in (embed_urls or []) if isinstance(u, str) and u]
        if not urls:
            return False
        parent, models = self._wait_for_assistant_parent(chat_id, attempts, delay)
        if not parent:
            return False
        qid = quote(chat_id, safe="")
        new_id = str(uuid.uuid4())
        node = {
            "id": new_id,
            "parentId": parent,
            "childrenIds": [],
            "role": "assistant",
            "content": caption or "",
            "model": model or (models[0] if models else ""),
            "modelName": model or (models[0] if models else ""),
            "modelIdx": 0,
            "done": True,
            "timestamp": int(time.time()),
        }
        body = {
            "chat": {
                "models": models,
                "history": {"messages": {new_id: node}, "currentId": new_id},
            }
        }
        status, updated = self.call("POST", f"/api/v1/chats/{qid}", body)
        if status != 200:
            raise OpenWebUIError(f"append message failed: HTTP {status}: {updated}")
        updated_msgs = self._history(updated).get("messages") if isinstance(updated, dict) else None
        if not isinstance(updated_msgs, dict) or new_id not in updated_msgs:
            # update_chat_by_id swallows exceptions and can return None.
            raise OpenWebUIError("append message failed: widget message missing from the response")
        status, ok = self.call(
            "POST",
            f"/api/v1/chats/{qid}/messages/{quote(new_id, safe='')}/event",
            {"type": "embeds", "data": {"embeds": urls}},
        )
        if status != 200 or ok is not True:
            raise OpenWebUIError(f"attach embed failed: HTTP {status}: {ok}")
        return True


class StatusReporter:
    """Fire-and-forget `status` events for one assistant message.

    Open WebUI shows the newest status as a shimmering one-liner above the reply
    and keeps the whole sequence in a clickable timeline. The bridge cannot use
    the Filter `__event_emitter__` path (it is an OpenAI-compatible endpoint, not
    a Pipe), so it posts to the public message-event route instead.

    Posting happens on a daemon worker thread: a slow or unreachable Open WebUI
    must never stall a pi turn, and every failure is swallowed (the step cards in
    the content are the guaranteed trace). A status sequence always ends with
    `done: true` — `close()` guarantees it — or the shimmer never stops.
    """

    def __init__(self, client: OpenWebUIClient, chat_id: str, message_id: str) -> None:
        self.client = client
        self.chat_id = chat_id
        self.message_id = message_id
        self._q: "queue.Queue[Optional[dict]]" = queue.Queue()
        self._mu = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._closed = False
        self._started = False

    def _ensure_worker(self) -> None:
        if self._thread is None:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def _run(self) -> None:
        while True:
            item = self._q.get()
            if item is None:
                return
            try:
                self.client.post_status(
                    self.chat_id, self.message_id, item["description"], item["done"]
                )
            except Exception:
                pass  # best-effort: the trace already renders as step cards

    def status(self, description: str, done: bool = False) -> None:
        if not description:
            return
        with self._mu:
            if self._closed:
                return
            self._started = self._started or not done
            self._ensure_worker()
            self._q.put({"description": description, "done": bool(done)})

    def close(self, description: str = "Done") -> None:
        """End the sequence with `done: true` (only if it ever started)."""
        with self._mu:
            if self._closed:
                return
            self._closed = True
            if not self._started:
                # Nothing shimmered. If a stray done-only status already started
                # a worker, still hand it the sentinel so the thread exits.
                if self._thread is not None:
                    self._q.put(None)
                return
            self._ensure_worker()
            self._q.put({"description": description, "done": True})
            self._q.put(None)
