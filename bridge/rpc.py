"""A minimal, dependency-free client for pi's RPC mode (JSONL over stdin/stdout).

Only the pieces the bridge needs: start a pinned pi, send correlated commands,
run one prompt and stream its records, abort, and stop. The protocol reference
is `pi/docs/rpc.md`; the Phase 0 spike confirmed the exact record shapes.

Deliberately single-flight per session: one prompt (or one command) at a time.
The HTTP layer serialises requests per chat, so this is sufficient and keeps the
record bookkeeping simple.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time
import uuid
from typing import Callable, Iterable, Optional

# UI requests pi may send when an extension wants input. Everything else
# (setWidget, setStatus, notify) is fire-and-forget and must NOT be answered.
_INTERACTIVE_UI = {"select", "input", "editor", "confirm"}

_EOF = {"__pi_bridge_eof__": True}


class PiError(RuntimeError):
    """A pi process failed to start, exited, or timed out."""


class PiSession:
    """One long-lived `pi --mode rpc` subprocess."""

    def __init__(
        self,
        pi_bin: str,
        cwd: str,
        env: dict,
        name: str,
        extra_args: Iterable[str] = (),
        session_id: Optional[str] = None,
        session_file: Optional[str] = None,
    ) -> None:
        self.pi_bin = pi_bin
        self.cwd = cwd
        self.env = env
        self.name = name
        self.extra_args = list(extra_args)
        self.session_id = session_id
        # An explicit file is used for a forked chat: the bridge writes the
        # branch under pi's session root, then opens it directly so the chat is
        # independent of any later parent-session bookkeeping.
        self.session_file = session_file
        self.proc: Optional[subprocess.Popen] = None
        self._q: "queue.Queue[dict]" = queue.Queue()
        self._write_lock = threading.Lock()
        self._turn_lock = threading.Lock()
        self._reader: Optional[threading.Thread] = None
        self._stderr: list[str] = []
        self._closed = False
        # Set after a `fork` command; `persist_fork` moves the new branch into
        # the chat's deterministic file once the turn has written it.
        self._forked = False

    # -- lifecycle ---------------------------------------------------------
    def command_line(self) -> list[str]:
        cmd = [self.pi_bin, "--mode", "rpc", "--name", self.name]
        if self.session_file:
            # A forked chat: open the exact branch file the bridge wrote.
            cmd += ["--session", self.session_file]
        elif self.session_id:
            # Resume this chat's transcript when it exists; create it otherwise.
            cmd += ["--session-id", self.session_id]
        cmd += self.extra_args
        return cmd

    def start(self) -> None:
        cmd = self.command_line()
        self.proc = subprocess.Popen(
            cmd,
            cwd=self.cwd,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()
        threading.Thread(target=self._drain_stderr, daemon=True).start()

    def _drain_stderr(self) -> None:
        assert self.proc and self.proc.stderr
        for line in self.proc.stderr:
            self._stderr.append(line.rstrip())
            if len(self._stderr) > 200:
                del self._stderr[:100]

    def _read_loop(self) -> None:
        assert self.proc and self.proc.stdout
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") == "extension_ui_request":
                self._answer_ui(rec)
                continue
            self._q.put(rec)
        self._q.put(_EOF)

    def _answer_ui(self, rec: dict) -> None:
        method = rec.get("method")
        if method not in _INTERACTIVE_UI:
            return  # setWidget / setStatus / notify are fire-and-forget
        reply = {"type": "extension_ui_response", "id": rec.get("id")}
        if method == "confirm":
            reply["confirmed"] = False
        else:
            reply["cancelled"] = True
        self._write(reply)

    def _write(self, obj: dict) -> None:
        if self._closed or not self.proc or not self.proc.stdin:
            return
        with self._write_lock:
            try:
                self.proc.stdin.write(json.dumps(obj) + "\n")
                self.proc.stdin.flush()
            except (BrokenPipeError, ValueError, OSError):
                self._closed = True

    # -- commands ----------------------------------------------------------
    def command(self, obj: dict, command: str, timeout: float = 30.0) -> dict:
        """Send one command and return its response `data` (must not be in a prompt)."""
        if not self._turn_lock.acquire(timeout=timeout):
            raise PiError(f"session busy; could not run {command}")
        try:
            cid = uuid.uuid4().hex
            obj = dict(obj, id=cid)
            self._write(obj)
            deadline = time.monotonic() + timeout
            while True:
                rec = self._next(deadline)
                if rec is None:
                    raise PiError(f"timed out waiting for {command}")
                if rec.get("type") == "response" and rec.get("id") == cid:
                    if not rec.get("success", True):
                        raise PiError(f"{command} failed: {rec.get('error')}")
                    return rec.get("data") or {}
        finally:
            self._turn_lock.release()

    def get_fork_messages(self, timeout: float = 30.0) -> list[dict]:
        """User messages on the active branch, oldest first."""
        data = self.command({"type": "get_fork_messages"}, "get_fork_messages", timeout)
        messages = data.get("messages")
        return messages if isinstance(messages, list) else []

    def _ensure_session_file(self) -> Optional[str]:
        """Learn the active session file (a `--session-id` start does not tell us)."""
        if self.session_file:
            return self.session_file
        try:
            data = self.command({"type": "get_state"}, "get_state", timeout=10.0)
        except PiError:
            return None
        path = data.get("sessionFile")
        if isinstance(path, str) and path:
            self.session_file = path
        return self.session_file

    def fork_to_entry(self, entry_id: str, timeout: float = 30.0) -> Optional[str]:
        """Fork the active branch at `entry_id` (removing it and everything after)."""
        if not entry_id:
            return None
        self._ensure_session_file()
        res = self.command({"type": "fork", "entryId": entry_id}, "fork", timeout)
        if res.get("cancelled"):
            return None
        self._forked = True
        return res.get("text")

    def fork_last_user_message(self, timeout: float = 30.0) -> Optional[str]:
        """Rewind the active branch to the last user message (for regenerate).

        Returns the forked-from text, or None if there is nothing to fork.
        """
        messages = self.get_fork_messages(timeout)
        if not messages:
            return None
        entry = messages[-1].get("entryId")
        if not entry:
            return None
        return self.fork_to_entry(entry, timeout)

    def persist_fork(self) -> bool:
        """Move a just-forked branch into the chat's deterministic session file.

        pi's `fork` command switches to a new file with a random id. Left alone,
        a bridge restart would resume the pre-fork file and a deleted chat would
        leave the forked transcript behind. After the fork's prompt has written
        the new file, rename it over the chat's file and `switch_session` so pi
        keeps writing to the same path. Returns True once the branch is adopted.
        """
        if not self._forked:
            return True
        target = self.session_file
        if not target:
            return False
        try:
            data = self.command({"type": "get_state"}, "get_state", timeout=10.0)
        except PiError:
            return False
        new_file = data.get("sessionFile")
        if not isinstance(new_file, str) or not new_file:
            return False
        if os.path.abspath(new_file) == os.path.abspath(target):
            self._forked = False
            return True
        if not os.path.exists(new_file):
            # The fork file is created lazily on the first message. Keep the
            # flag so the next settlement can adopt it.
            return False
        try:
            os.replace(new_file, target)
        except OSError as exc:
            print(
                f"pi-bridge: could not adopt forked session {new_file}: {exc}",
                file=sys.stderr,
                flush=True,
            )
            self.session_file = new_file
            self._forked = False
            return False
        try:
            res = self.command(
                {"type": "switch_session", "sessionPath": target},
                "switch_session",
                timeout=10.0,
            )
        except PiError as exc:
            # Putting the file back keeps pi's internal path and the file on
            # disk together; this turn still works, but the next restart will
            # resume the pre-fork file.
            print(
                f"pi-bridge: could not switch to forked session {target}: {exc}",
                file=sys.stderr,
                flush=True,
            )
            try:
                os.replace(target, new_file)
            except OSError:
                pass
            self.session_file = new_file
            self._forked = False
            return False
        if res.get("cancelled"):
            try:
                os.replace(target, new_file)
            except OSError:
                pass
            self.session_file = new_file
            self._forked = False
            return False
        self.session_file = target
        self._forked = False
        return True

    def prompt(
        self,
        message: str,
        on_record: Callable[[dict], None],
        timeout: float = 1800.0,
        max_turn: float = 7200.0,
        images: Optional[list] = None,
        should_abort: Optional[Callable[[], bool]] = None,
    ) -> list[dict]:
        """Run one prompt to `agent_settled`, streaming records to `on_record`.

        `timeout` is an **idle** budget: the longest pi may stay silent. Every
        record resets it, so a long but working turn (a scout subagent can run
        ~15 minutes without emitting anything between `tool_execution_start`
        and its result) is not killed by a fixed wall-clock cap.
        `max_turn` is the absolute ceiling for one turn, so a runaway turn still
        releases the single-writer learning lock.

        `should_abort` is polled while the turn runs. When it returns true (the
        streaming client disconnected, i.e. Open WebUI Stop), the bridge sends
        `abort`, drains to settlement and returns, so a canceled turn does not
        keep working or hold the learning lock.

        Returns every non-response record observed for the turn.
        """
        if not self._turn_lock.acquire(timeout=10.0):
            raise PiError("session busy; a turn is already running")
        try:
            cid = uuid.uuid4().hex
            payload = {"id": cid, "type": "prompt", "message": message}
            if images:
                # pi accepts `ImageContent` blocks directly on the prompt, so an
                # Open WebUI upload reaches the model instead of being dropped.
                payload["images"] = images
            self._write(payload)
            now = time.monotonic()
            idle_deadline = now + timeout
            turn_deadline = now + max_turn
            seen: list[dict] = []
            accepted = False
            while True:
                if should_abort and should_abort():
                    self.abort()
                    self._drain(grace=1.0)
                    return seen
                deadline = min(idle_deadline, turn_deadline)
                if should_abort:
                    # Wake periodically so a client disconnect is noticed even
                    # while pi is silent inside a long tool/subagent call.
                    deadline = min(deadline, time.monotonic() + 0.5)
                rec = self._next(deadline)
                if rec is None:
                    if should_abort and should_abort():
                        self.abort()
                        self._drain(grace=1.0)
                        return seen
                    if time.monotonic() < min(idle_deadline, turn_deadline):
                        continue
                    hit_ceiling = time.monotonic() >= turn_deadline
                    self.abort()
                    # Give the aborted turn a moment to flush its trailing
                    # records/agent_settled so they cannot bleed into the next
                    # prompt (the fast default grace is only for handled prompts).
                    self._drain(grace=1.0)
                    if hit_ceiling:
                        raise PiError(
                            f"turn ran longer than {max_turn:g}s and was aborted "
                            "(raise PI_BRIDGE_MAX_TURN for a longer ceiling)"
                        )
                    raise PiError(
                        f"pi went quiet for {timeout:g}s and the turn was aborted "
                        "(raise PI_BRIDGE_TIMEOUT if a subagent legitimately needs longer)"
                    )
                idle_deadline = time.monotonic() + timeout
                t = rec.get("type")
                if t == "response" and rec.get("id") == cid:
                    if not rec.get("success", True):
                        raise PiError(f"prompt rejected: {rec.get('error')}")
                    accepted = True
                    # A prompt "handled" by an extension command starts no run:
                    # waiting for agent_settled would block until timeout. Drain
                    # anything the extension emitted so it cannot bleed into the
                    # next turn.
                    if (rec.get("data") or {}).get("disposition") == "handled":
                        self._drain()
                        return seen
                    continue
                on_record(rec)
                seen.append(rec)
                if accepted and t == "agent_settled":
                    return seen
        finally:
            self._turn_lock.release()

    def _drain(self, grace: float = 0.05) -> None:
        """Discard records left over from a finished/aborted turn.

        Returns promptly when the queue is already empty (a `handled` prompt
        must not pay a fixed stall); the short grace only catches records that
        are still in flight.
        """
        end = time.monotonic() + grace
        while True:
            try:
                rec = self._q.get_nowait()
            except queue.Empty:
                if time.monotonic() >= end:
                    return
                time.sleep(0.005)
                continue
            if rec is _EOF or rec == _EOF or rec.get("type") == "agent_settled":
                return

    def _next(self, deadline: float) -> Optional[dict]:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        try:
            rec = self._q.get(timeout=remaining)
        except queue.Empty:
            return None
        if rec is _EOF or rec == _EOF:
            raise PiError("pi process ended")
        return rec

    def abort(self) -> None:
        self._write({"type": "abort"})

    def alive(self) -> bool:
        return (
            not self._closed
            and self.proc is not None
            and self.proc.poll() is None
        )

    def stderr_tail(self, n: int = 10) -> list[str]:
        return self._stderr[-n:]

    def close(self) -> None:
        self._closed = True
        if self.proc:
            try:
                if self.proc.stdin:
                    self.proc.stdin.close()
            except (OSError, ValueError):
                pass
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            # Close the read pipes too, or a long-lived bridge leaks FDs.
            for pipe in (self.proc.stdout, self.proc.stderr):
                try:
                    if pipe:
                        pipe.close()
                except (OSError, ValueError):
                    pass
