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
