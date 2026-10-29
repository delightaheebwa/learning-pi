"""Stable pi session identities for Open WebUI conversations.

A chat key is the bridge's in-memory handle for one conversation; the session id
is what pi persists. Keeping the two derivations here (rather than in `server`)
lets the chat-sync code resolve a parent chat's session file without importing
the HTTP server.
"""
from __future__ import annotations

import hashlib
import re

# pi's `--session-id` accepts letters, numbers, `.`, `_`, and `-`, and requires
# the id to start and end with a letter or number.
_PI_SESSION_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9]")


def _message_text(message: dict) -> str:
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for part in content:
            if isinstance(part, str):
                out.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                out.append(part["text"])
        return "".join(out)
    return ""


def session_key(body: dict, messages, chat_id: str = "") -> str:
    """Stable per-conversation key.

    The forwarded `X-OpenWebUI-Chat-Id` header is authoritative: it is the only
    client signal that distinguishes two chats with the same first message (a
    fork) and that still exists after the chat is deleted (for cleanup). Metadata
    and the first-message fingerprint remain fallbacks for clients that cannot
    forward the header.
    """
    if isinstance(chat_id, str) and chat_id:
        return "chat:" + chat_id
    md = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
    for cand in (md.get("chat_id"), body.get("chat_id"), body.get("conversation_id")):
        if isinstance(cand, str) and cand:
            return "chat:" + cand
    first = ""
    if isinstance(messages, list):
        for m in messages:
            if isinstance(m, dict) and m.get("role") == "user":
                first = _message_text(m)
                break
    seed = f"{body.get('model', '')}|{first}"
    return "fp:" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]


def session_id_for(key: str) -> str:
    """Deterministic pi session id for a bridge chat key.

    Passing this id to `pi --session-id` makes pi resume the transcript it
    already wrote for this chat. The bridge's registry is in memory only, so
    without a stable id a systemd restart (or a pi crash) would start a blank
    session and pi would re-derive context from the state repo — which is
    exactly how a lesson chat once answered from a review in another chat.

    `chat:<uuid>` -> `chat-<uuid>`, `fp:<hex>` -> `fp-<hex>`. Any other key — or
    one that would be too long or contain characters pi rejects — collapses to a
    stable hash, so two different keys do not collide by sanitising.
    """
    if key.startswith("chat:") or key.startswith("fp:"):
        sid = key.replace(":", "-", 1)
        if len(sid) <= 100 and _PI_SESSION_ID_RE.fullmatch(sid):
            return sid
    return "s-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:24]
