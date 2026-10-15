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
import queue
import subprocess
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
    ) -> None:
        self.pi_bin = pi_bin
        self.cwd = cwd
        self.env = env
        self.name = name
        self.extra_args = list(extra_args)
        self.proc: Optional[subprocess.Popen] = None
        self._q: "queue.Queue[dict]" = queue.Queue()
        self._write_lock = threading.Lock()
        self._turn_lock = threading.Lock()
        self._reader: Optional[threading.Thread] = None
        self._stderr: list[str] = []
        self._closed = False

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> None:
        cmd = [self.pi_bin, "--mode", "rpc", "--name", self.name, *self.extra_args]
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

    def fork_last_user_message(self, timeout: float = 30.0) -> Optional[str]:
        """Rewind the active branch to the last user message (for regenerate).

        Returns the forked-from text, or None if there is nothing to fork.
        """
        data = self.command({"type": "get_fork_messages"}, "get_fork_messages", timeout)
        messages = data.get("messages") or []
        if not messages:
            return None
        entry = messages[-1].get("entryId")
        if not entry:
            return None
        res = self.command({"type": "fork", "entryId": entry}, "fork", timeout)
        if res.get("cancelled"):
            return None
        return res.get("text")

    def prompt(
        self,
        message: str,
        on_record: Callable[[dict], None],
        timeout: float = 900.0,
    ) -> list[dict]:
        """Run one prompt to `agent_settled`, streaming records to `on_record`.

        Returns every non-response record observed for the turn.
        """
        if not self._turn_lock.acquire(timeout=10.0):
            raise PiError("session busy; a turn is already running")
        try:
            cid = uuid.uuid4().hex
            self._write({"id": cid, "type": "prompt", "message": message})
            deadline = time.monotonic() + timeout
            seen: list[dict] = []
            accepted = False
            while True:
                rec = self._next(deadline)
                if rec is None:
                    self.abort()
                    raise PiError("prompt timed out")
                t = rec.get("type")
                if t == "response" and rec.get("id") == cid:
                    if not rec.get("success", True):
                        raise PiError(f"prompt rejected: {rec.get('error')}")
                    accepted = True
                    continue
                on_record(rec)
                seen.append(rec)
                if accepted and t == "agent_settled":
                    return seen
        finally:
            self._turn_lock.release()

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
            except OSError:
                pass
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
