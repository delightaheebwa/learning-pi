"""Mirror Open WebUI chat lifecycle actions into the pi runtime.

Open WebUI calls the bridge only for completions; it never tells an
OpenAI-compatible backend that a chat was forked or deleted. The bridge already
has a best-effort REST key for widget delivery, so this module uses it to close
that gap:

* **fork** — the first turn of a forked chat creates the new pi session from the
  parent's transcript at the fork point (`plan_fork`).
* **delete** — a background sweep asks Open WebUI whether each `chat-<id>` pi
  session still has a chat, and removes the session file on an explicit 404
  (`sweep`).

Both are best-effort: a missing REST configuration, a transient network error,
or an unreadable session file leaves the turn working with today's behaviour
instead of failing the learner's request.
"""
from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Optional

from . import openwebui, session_store
from .session_key import session_id_for, session_key


class ChatSync:
    """Bridge-side view of Open WebUI chat objects and pi session files."""

    def __init__(self, config, registry, *, client=None, interval=None) -> None:
        self.config = config
        self.registry = registry
        self._client = client
        self.interval = float(config.sync_interval if interval is None else interval)
        self._plan_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._started = False

    # -- Open WebUI access -------------------------------------------------
    def client(self):
        if self._client is not None:
            return self._client
        if not self.config.openwebui_base_url:
            return None
        key = openwebui.read_key(self.config.openwebui_key_file)
        if not key:
            return None
        # Fork lookup sits in front of a new chat's first turn, so keep its
        # timeout short; the local REST call normally answers in milliseconds.
        self._client = openwebui.OpenWebUIClient(
            self.config.openwebui_base_url, key, timeout=5.0
        )
        return self._client

    def _session_dir(self):
        return session_store.default_session_dir(self.config.session_dir)

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> None:
        """Start the delete-sweep worker (no-op when REST or interval is off)."""
        if self._started:
            return
        self._started = True
        if self.interval <= 0 or not self.config.openwebui_base_url:
            return
        self._thread = threading.Thread(
            target=self._run, name="pi-bridge-chatsync", daemon=True
        )
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            try:
                self.sweep()
            except Exception as exc:  # never let housekeeping kill the worker
                print(f"pi-bridge: chat sweep failed: {exc}", file=sys.stderr, flush=True)

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    # -- fork --------------------------------------------------------------
    def plan_fork(self, chat_id: str, model: str, session_id: str) -> Optional[Path]:
        """Prepare a forked chat's pi session, returning its file or None.

        Idempotent: once the fork file exists it is reused, so a bridge restart
        does not create a second copy. A chat that is not a fork, an unwritable
        parent file, or an unconfigured REST client all return None and the chat
        starts as a normal new session.
        """
        if not chat_id:
            return None
        with self._plan_lock:
            existing = self._existing(session_id)
            if existing is not None:
                return existing

        # The REST round-trip must not hold the plan lock: a slow Open WebUI
        # would serialise every other new chat's first turn behind it.
        client = self.client()
        if client is None:
            return None
        status, chat = client.get_chat(chat_id)
        if status != 200 or not isinstance(chat, dict):
            return None

        with self._plan_lock:
            # Another request may have created the file while we fetched.
            existing = self._existing(session_id)
            if existing is not None:
                return existing
            parent_id, branch_id = _fork_origin(chat)
            if not parent_id:
                # An existing chat from before chat-id routing has a fingerprint
                # session. Copy it once so the upgrade keeps its context and the
                # chat becomes deletable/forkable like any other.
                return self._migrate_fingerprint(chat, model, session_id)
            parent_file = self._parent_session_file(parent_id, chat, model)
            if parent_file is None:
                return None

            source_role, fork_users = _branch_shape(chat, branch_id)
            try:
                _, entries = session_store.read_session(parent_file)
                leaf = session_store.choose_fork_leaf(entries, fork_users, source_role)
                return session_store.write_fork(
                    parent_file,
                    session_id,
                    leaf,
                    cwd=self.config.state_repo,
                )
            except (OSError, ValueError) as exc:
                print(
                    f"pi-bridge: could not fork chat {chat_id} from {parent_file}: {exc}",
                    file=sys.stderr,
                    flush=True,
                )
                return None

    def _existing(self, session_id: str) -> Optional[Path]:
        return session_store.find_session_file(
            session_id,
            session_dir=self._session_dir(),
            cwd=self.config.state_repo,
        )

    def _migrate_fingerprint(self, chat: dict, model: str, session_id: str) -> Optional[Path]:
        """Give a pre-chat-id conversation its own session file.

        Only a chat that already has an assistant message is migrated: a brand
        new chat whose first prompt happens to match an old chat's first prompt
        must not inherit that old transcript (the fingerprint-sharing bug this
        change removes).
        """
        current = _current_id(chat)
        chain = _chain(chat, current)
        if not any(m.get("role") == "assistant" for m in chain):
            return None
        first = _first_user_text(chat)
        if not first:
            return None
        source_role, fork_users = _branch_shape(chat, current)
        body = chat.get("chat") if isinstance(chat.get("chat"), dict) else {}
        models = [model]
        for candidate in body.get("models") or []:
            if isinstance(candidate, str):
                models.append(candidate)
        messages = [{"role": "user", "content": first}]
        seen = set()
        for candidate_model in models:
            if not candidate_model:
                continue
            legacy_id = session_id_for(session_key({"model": candidate_model}, messages))
            if legacy_id in seen:
                continue
            seen.add(legacy_id)
            legacy_file = session_store.find_session_file(
                legacy_id,
                session_dir=self._session_dir(),
                cwd=self.config.state_repo,
            )
            if legacy_file is None:
                continue
            try:
                _, entries = session_store.read_session(legacy_file)
                leaf = session_store.choose_fork_leaf(entries, fork_users, source_role)
                return session_store.write_fork(
                    legacy_file, session_id, leaf, cwd=self.config.state_repo
                )
            except (OSError, ValueError) as exc:
                print(
                    f"pi-bridge: could not migrate chat {session_id} from {legacy_file}: {exc}",
                    file=sys.stderr,
                    flush=True,
                )
                return None
        return None

    def _parent_session_file(self, parent_id: str, fork_chat: dict, model: str) -> Optional[Path]:
        """Find the parent chat's pi session file.

        New sessions are keyed by chat id. Chats created before chat-id routing
        used the first-message fingerprint, so try that fallback too; an existing
        chat keeps working after this change.
        """
        candidates = [session_id_for("chat:" + parent_id)]
        body = fork_chat.get("chat") if isinstance(fork_chat.get("chat"), dict) else {}
        first = _first_user_text(fork_chat)
        messages = [{"role": "user", "content": first}] if first else []
        models = [model]
        for candidate in body.get("models") or []:
            if isinstance(candidate, str):
                models.append(candidate)
        for candidate_model in models:
            if candidate_model:
                candidates.append(
                    session_id_for(session_key({"model": candidate_model}, messages))
                )
        seen = set()
        for sid in candidates:
            if sid in seen:
                continue
            seen.add(sid)
            found = session_store.find_session_file(
                sid,
                session_dir=self._session_dir(),
                cwd=self.config.state_repo,
            )
            if found is not None:
                return found
        return None

    # -- delete ------------------------------------------------------------
    def sweep(self) -> int:
        """Delete pi sessions whose Open WebUI chat no longer exists.

        Only an explicit 404 removes a session; a network error or a bad key
        leaves everything in place. Returns the number of chats cleaned up.
        """
        client = self.client()
        if client is None:
            return 0
        chat_ids = set()
        for key in self.registry.chat_keys():
            chat_ids.add(key[len("chat:"):])
        for sid in session_store.bridge_session_ids(
            session_dir=self._session_dir(), cwd=self.config.state_repo
        ):
            if sid.startswith("chat-"):
                chat_ids.add(sid[len("chat-"):])
        removed = 0
        for chat_id in sorted(chat_ids):
            status, _ = client.get_chat(chat_id)
            if status == 404 and self.delete_chat(chat_id):
                removed += 1
        return removed

    def delete_chat(self, chat_id: str) -> bool:
        """Close and remove one chat's pi session (False when a turn is active)."""
        key = "chat:" + chat_id
        # Snapshot the files before removing the registry entry: a turn starting
        # in between may legitimately create a new file, which this sweep must
        # not unlink underneath it. The next sweep will see that file if the
        # chat is still gone.
        files = session_store.find_session_files(
            "chat-" + chat_id,
            session_dir=self._session_dir(),
            cwd=self.config.state_repo,
        )
        entry, busy = self.registry.pop_if_idle(key)
        if busy:
            return False  # retry on the next sweep, after the turn settles
        if entry is not None:
            entry.session.close()
        removed = session_store.delete_paths(files)
        if entry is not None or removed:
            print(
                f"pi-bridge: removed pi session for deleted chat {chat_id}",
                file=sys.stderr,
                flush=True,
            )
        return entry is not None or bool(removed)


# ---------------------------------------------------------------------------
# Open WebUI chat-object helpers (pure)
# ---------------------------------------------------------------------------
def _history_messages(chat: dict) -> dict:
    body = chat.get("chat") if isinstance(chat.get("chat"), dict) else {}
    history = body.get("history") if isinstance(body.get("history"), dict) else {}
    messages = history.get("messages")
    return messages if isinstance(messages, dict) else {}


def _fork_origin(chat: dict) -> tuple[str, str]:
    """`(parent chat id, branch-point message id)` for a fork/clone chat."""
    meta = chat.get("meta") if isinstance(chat.get("meta"), dict) else {}
    body = chat.get("chat") if isinstance(chat.get("chat"), dict) else {}
    parent = meta.get("forked_from") or body.get("originalChatId")
    branch = (
        meta.get("forked_from_message_id")
        or body.get("branchPointMessageId")
        or _current_id(chat)
    )
    return (parent if isinstance(parent, str) else "", branch if isinstance(branch, str) else "")


def _current_id(chat: dict) -> str:
    body = chat.get("chat") if isinstance(chat.get("chat"), dict) else {}
    history = body.get("history") if isinstance(body.get("history"), dict) else {}
    current = history.get("currentId")
    return current if isinstance(current, str) else ""


def _chain(chat: dict, leaf_id: str) -> list[dict]:
    """Messages root -> leaf along the fork chat's active branch."""
    messages = _history_messages(chat)
    chain = []
    seen = set()
    current = leaf_id
    while current and current in messages and current not in seen:
        seen.add(current)
        message = messages[current]
        if not isinstance(message, dict):
            break
        chain.append(message)
        current = message.get("parentId") if isinstance(message.get("parentId"), str) else ""
    return list(reversed(chain))


def _branch_shape(chat: dict, branch_id: str) -> tuple[str, int]:
    """`(role of the forked message, user-message count through it)`."""
    leaf = branch_id or _current_id(chat)
    chain = _chain(chat, leaf)
    if not chain and branch_id:
        chain = _chain(chat, _current_id(chat))
    users = [m for m in chain if m.get("role") == "user"]
    role = chain[-1].get("role") if chain else ""
    return (role if isinstance(role, str) else ""), len(users)


def _first_user_text(chat: dict) -> str:
    chain = _chain(chat, _current_id(chat))
    for message in chain:
        if message.get("role") == "user":
            return session_store.message_text(message.get("content"))
    messages = _history_messages(chat)
    # Fall back to a root user message, not arbitrary dict insertion order.
    for message in messages.values():
        if (
            isinstance(message, dict)
            and message.get("role") == "user"
            and message.get("parentId") not in messages
        ):
            return session_store.message_text(message.get("content"))
    for message in messages.values():
        if isinstance(message, dict) and message.get("role") == "user":
            return session_store.message_text(message.get("content"))
    return ""
