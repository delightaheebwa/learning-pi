"""Pure session-file operations used to mirror Open WebUI chat actions.

pi owns its session files. Two Open WebUI actions still need the bridge to touch
them:

* **fork** — a forked Open WebUI chat must start from the parent chat's pi
  branch, not blank and not the parent's current leaf when the fork point was
  earlier. `write_fork` copies the selected branch into a new session file whose
  id matches the new chat, so pi's normal `--session-id` lookup finds it.
* **delete** — deleting an Open WebUI chat must remove the chat's pi transcript,
  not leave it to be resumed by a later chat that reuses the id. `delete_session_files`
  removes every matching `<timestamp>_<id>.jsonl`.

Everything here is filesystem-only and side-effect free unless explicitly called,
so the branch-selection rules can be unit-tested without pi or the network.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

SESSION_EXT = ".jsonl"


def default_session_dir(session_dir: Optional[str] = None) -> Path:
    """The pi session root, matching pi's own resolution order."""
    if session_dir:
        return Path(os.path.expanduser(str(session_dir)))
    env = os.environ.get("PI_CODING_AGENT_SESSION_DIR", "").strip()
    if env:
        return Path(os.path.expanduser(env))
    return Path.home() / ".pi" / "agent" / "sessions"


def project_dir_name(cwd: str) -> str:
    """pi's per-project session directory name (`--home-user-state--`)."""
    path = os.path.abspath(os.path.expanduser(cwd or "."))
    return "--" + path.lstrip("/").replace("/", "-").replace("\\", "-").replace(":", "-") + "--"


def _session_files_in(directory: Path, session_id: str) -> list[Path]:
    if not directory.is_dir():
        return []
    found = list(directory.glob(f"*_{session_id}{SESSION_EXT}"))
    exact = directory / f"{session_id}{SESSION_EXT}"
    if exact.is_file():
        found.append(exact)
    return found


def find_session_files(
    session_id: str,
    *,
    session_dir: Optional[str] = None,
    cwd: Optional[str] = None,
) -> list[Path]:
    """Every session file for `session_id`, newest first.

    The project directory is searched first (the common case), then the whole
    session root as a fallback so a moved/legacy checkout still resolves.
    """
    if not session_id:
        return []
    root = default_session_dir(session_dir)
    found: list[Path] = []
    if cwd:
        found.extend(_session_files_in(root / project_dir_name(cwd), session_id))
    if not found:
        found.extend(_session_files_in(root, session_id))
    if not found and root.is_dir():
        found.extend(root.rglob(f"*_{session_id}{SESSION_EXT}"))
    unique = {str(p): p for p in found if p.is_file()}
    return sorted(unique.values(), key=lambda p: p.stat().st_mtime, reverse=True)


def find_session_file(
    session_id: str,
    *,
    session_dir: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Optional[Path]:
    """The newest session file for `session_id`, or None."""
    files = find_session_files(session_id, session_dir=session_dir, cwd=cwd)
    return files[0] if files else None


def delete_paths(paths) -> list[Path]:
    """Delete an explicit set of session files; return what was removed."""
    removed = []
    for path in paths or []:
        try:
            Path(path).unlink()
            removed.append(Path(path))
        except FileNotFoundError:
            pass
    return removed


def delete_session_files(
    session_id: str,
    *,
    session_dir: Optional[str] = None,
    cwd: Optional[str] = None,
) -> list[Path]:
    """Delete every session file for `session_id`; return what was removed."""
    return delete_paths(
        find_session_files(session_id, session_dir=session_dir, cwd=cwd)
    )


def bridge_session_ids(
    *,
    session_dir: Optional[str] = None,
    cwd: Optional[str] = None,
) -> list[str]:
    """Session ids the bridge made for Open WebUI chats (`chat-<uuid>`).

    Scoped to the working directory's project folder when it exists, so a shared
    session root cannot make one checkout clean up another's chats.
    """
    root = default_session_dir(session_dir)
    if not root.is_dir():
        return []
    directories = []
    if cwd:
        project = root / project_dir_name(cwd)
        if project.is_dir():
            directories.append(project)
    if not directories:
        directories.append(root)
    ids = set()
    for directory in directories:
        for path in directory.glob(f"*{SESSION_EXT}"):
            name = path.stem
            sid = name.rsplit("_", 1)[-1] if "_" in name else name
            if sid.startswith("chat-"):
                ids.add(sid)
    return sorted(ids)


def read_session(path: Path) -> tuple[dict, list[dict]]:
    """Read a pi session file into its header and entries."""
    header: Optional[dict] = None
    entries: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        lines = fh.readlines()
    for index, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            # A live pi process may be mid-write on the final line. Ignore only
            # that trailing partial record; a broken middle line is real damage.
            if index == len(lines) - 1:
                break
            raise
        if not isinstance(rec, dict):
            continue
        if rec.get("type") == "session" and header is None:
            header = rec
        elif isinstance(rec.get("id"), str):
            entries.append(rec)
    if header is None:
        raise ValueError(f"not a pi session file: {path}")
    return header, entries


def message_text(content) -> str:
    """Text of a message content payload (string or content-part list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
        return "".join(parts)
    return ""


def active_branch(entries: list[dict], leaf_id: Optional[str] = None) -> list[dict]:
    """The root -> leaf branch of a pi session tree, in conversation order.

    `leaf_id` defaults to the last entry in the file, which is how pi appends an
    active branch. An unknown leaf falls back to that same last entry.
    """
    by_id = {e["id"]: e for e in entries if isinstance(e.get("id"), str)}
    if not by_id:
        return []
    leaf = leaf_id if leaf_id in by_id else entries[-1].get("id")
    branch_rev = []
    seen = set()
    current = leaf
    while current and current in by_id and current not in seen:
        seen.add(current)
        entry = by_id[current]
        branch_rev.append(entry)
        current = entry.get("parentId")
    return list(reversed(branch_rev))


def user_entries(branch: list[dict]) -> list[dict]:
    """User-message entries on a branch, in conversation order."""
    return [
        e for e in branch
        if e.get("type") == "message"
        and isinstance(e.get("message"), dict)
        and e["message"].get("role") == "user"
    ]


def choose_fork_leaf(
    entries: list[dict],
    fork_user_count: int,
    source_role: str,
    *,
    leaf_id: Optional[str] = None,
) -> Optional[str]:
    """Pick the pi entry that matches an Open WebUI fork point.

    `fork_user_count` is the number of user messages in the Open WebUI fork
    branch (which always ends at the forked message). A user-message fork keeps
    that user message; an assistant-message fork keeps everything through the
    turn that produced it. When the parent has a later user message, the entry
    just before it is the correct leaf; otherwise the parent's current leaf is.
    """
    branch = active_branch(entries, leaf_id)
    if not branch:
        return None
    users = user_entries(branch)
    if not users:
        return branch[-1].get("id")
    try:
        count = int(fork_user_count)
    except (TypeError, ValueError):
        count = 0
    if count <= 0 or count > len(users):
        return branch[-1].get("id")
    last_user = users[count - 1]
    if source_role == "user":
        return last_user.get("id")
    next_user = users[count] if count < len(users) else None
    if next_user is None:
        return branch[-1].get("id")
    return next_user.get("parentId") or last_user.get("id")


def _stamp(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H-%M-%S-") + f"{moment.microsecond // 1000:03d}Z"


def write_fork(
    parent_file: Path,
    new_id: str,
    target_leaf_id: Optional[str],
    *,
    cwd: Optional[str] = None,
) -> Path:
    """Write a new session file for `new_id` holding the selected branch.

    The file lands beside the parent session (same project directory) with pi's
    `<timestamp>_<session-id>.jsonl` shape, so a later `pi --session-id <new_id>`
    resumes it and the bridge's filename-based cleanup finds it.
    """
    parent_file = Path(parent_file)
    header, entries = read_session(parent_file)
    branch = active_branch(entries, target_leaf_id)
    if not branch:
        branch = active_branch(entries)

    new_header = {
        **header,
        "type": "session",
        "version": header.get("version", 3),
        "id": new_id,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "parentSession": str(parent_file),
    }
    cwd = cwd or new_header.get("cwd") or ""
    if cwd:
        new_header["cwd"] = cwd

    directory = parent_file.parent
    directory.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    path = directory / f"{_stamp(now)}_{new_id}{SESSION_EXT}"
    for offset in range(1, 1000):
        if not path.exists():
            break
        path = directory / f"{_stamp(now + timedelta(milliseconds=offset))}_{new_id}{SESSION_EXT}"
    else:
        raise FileExistsError(path)

    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(new_header, ensure_ascii=False) + "\n")
        for entry in branch:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    return path
