"""Turn the raw pi RPC record stream into learner-facing text.

The whole point of this module is the buffering rule the Phase 0 spike forced:
`message_update` deltas carry the *pre-verification* draft (the spike watched a
withheld teaching draft stream in full before the gate replaced it at
`message_end`). So the bridge never forwards deltas. It emits only the text of a
completed, non-tool assistant message — the post-gate turn (verified text, or a
withheld/`unverified` banner that the gate wrote into the message itself).

Alongside the buffered text, a turn records *steps* — completed tool executions
(`tool_execution_start/end`: name, args, status, duration) and completed thinking
blocks (duration, and text only in a general chat). Steps are display metadata
rendered by `bridge/steps.py`; they never carry delta text, and a learning flow
never carries a tool result. `on_step` is called as each step completes so the
HTTP layer can stream it live.

Kept free of I/O so it can be unit-tested against synthetic records.
"""
from __future__ import annotations

import re
import time
from typing import Callable, Optional

# Mirror of the learning-gate's own turn-tag vocabulary (`TURN_TAG_RE` /
# `stripTag` in `.pi/extensions/learning-gate/gate-core/primitives.ts`): one tag
# at the very start of a turn (leading whitespace allowed), plus the whitespace /
# newline that follows it. A gated learning turn reaches the bridge already
# stripped, but a non-learning message (no `[[FLOW:…]]` marker) is passed through
# untouched by the gate — so the bridge cleans its own learner-facing output here
# and the internal protocol never leaks into the chat. Only a tag at the very
# start is matched; a `[[TURN:…]]` later in the body is left alone.
_TURN_TAG_RE = re.compile(
    r"^\s*\[\[TURN:(?:claims|quiz|grade|ui|none)\]\]\s*", re.IGNORECASE
)


def strip_turn_tag(text: str) -> str:
    """Remove one leading `[[TURN:…]]` tag and the whitespace that follows it."""
    if not text:
        return text
    return _TURN_TAG_RE.sub("", text, count=1)


# Fenced ` ```openui ` payloads. The gate has already verified the payload (a
# `[[TURN:ui]]` turn needs a passing `ui-audit` bound to it); the bridge lifts
# the fence out of the prose and delivers it to Open WebUI as an interactive
# widget embed below the prose. Mermaid/HTML fences are left intact for Open
# WebUI's native rendering. Non-greedy body so several fences extract cleanly.
_OPENUI_FENCE_RE = re.compile(r"```openui[^\n]*\n([\s\S]*?)```")


def extract_openui_fences(text: str) -> list[str]:
    """Return the payloads of every ` ```openui ` fence in `text` (order kept)."""
    if not text:
        return []
    return [m.group(1).strip() for m in _OPENUI_FENCE_RE.finditer(text) if m.group(1).strip()]


def strip_openui_fences(text: str) -> str:
    """Remove every ` ```openui ` fence (opening line through closing fence)."""
    if not text:
        return text
    return _OPENUI_FENCE_RE.sub("", text)



# stopReasons that represent a completed learner-facing message. `error`,
# `aborted`, and `length` are the gate's "partial pass-through" cases
# (G-partial-ungated): it strips the turn tag and emits them, so the bridge does
# too — a later retry replaces the text. `toolUse` is skipped because the gate
# does not gate it (any text there is ungated narration); unknown/pending
# reasons are skipped rather than guessed.
_EMISSIBLE = {"stop", "error", "aborted", "length"}


def text_of_content(content) -> str:
    """Extract text from a pi message `content` (string or part list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict) and p.get("type") == "text" and isinstance(p.get("text"), str):
                parts.append(p["text"])
        return "".join(parts)
    return ""


def thinking_text_of_content(content) -> str:
    """Extract completed thinking parts from a pi message `content`.

    Only called on `message_end` (authoritative, post-completion content) — never
    on `message_update` deltas.
    """
    if not isinstance(content, list):
        return ""
    parts = []
    for p in content:
        if not isinstance(p, dict) or p.get("type") != "thinking":
            continue
        text = p.get("thinking")
        if not isinstance(text, str):
            text = p.get("text")
        if isinstance(text, str):
            parts.append(text)
    return "".join(parts)


def result_text(result) -> str:
    """Text of a `tool_execution_end.result` payload (`{content: [...]}`)."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return text_of_content(result.get("content"))
    return text_of_content(result)


class TurnStream:
    """Accumulate one prompt's records, its display steps, and the final text.

    `learning` selects the display policy: a learning turn never exposes tool
    results or thinking text (the gate may still withhold the answer), while a
    general chat shows both. `on_step` receives transient start events
    (`tool_start`, `thinking_start`) and completed steps as they happen; it is
    best-effort and must never break the turn.
    """

    def __init__(
        self,
        *,
        learning: bool = True,
        on_step: Optional[Callable[[dict], None]] = None,
        clock: Optional[Callable[[], float]] = None,
    ) -> None:
        self.learning = learning
        self.on_step = on_step
        self._clock = clock or time.monotonic
        self.text: str = ""
        self.error: str = ""
        self.steps: list[dict] = []
        self._tools: dict[str, dict] = {}
        self._step_seq = 0
        self._msg_started: Optional[float] = None
        self._thinking_started: Optional[float] = None

    # -- step plumbing -----------------------------------------------------
    def _notify(self, step: dict) -> None:
        if self.on_step is None:
            return
        try:
            self.on_step(step)
        except Exception:  # a display sink must never abort a turn
            pass

    def _emit_step(self, step: dict) -> None:
        self.steps.append(step)
        self._notify(step)

    def _next_id(self) -> str:
        self._step_seq += 1
        return f"step-{self._step_seq}"

    # -- record handling ---------------------------------------------------
    def feed(self, rec: dict) -> None:
        t = rec.get("type")
        if t == "message_start":
            self._msg_started = self._clock()
            self._thinking_started = None
        elif t == "message_update":
            ev = rec.get("assistantMessageEvent") or {}
            if ev.get("type") == "thinking_delta":
                # Timing only: the delta text itself is deliberately ignored
                # (B-deltas-never-forwarded).
                now = self._clock()
                if self._thinking_started is None:
                    self._thinking_started = now
                    self._notify({"kind": "thinking_start"})
        elif t == "message_end":
            self._finish_message(rec)
        elif t == "tool_execution_start":
            self._tool_start(rec)
        elif t == "tool_execution_end":
            self._tool_end(rec)

    def _finish_message(self, rec: dict) -> None:
        m = rec.get("message") or {}
        if m.get("role") != "assistant":
            return
        now = self._clock()
        thinking = thinking_text_of_content(m.get("content"))
        if self._thinking_started is not None:
            # The thought ends when its message does; measuring from the first
            # delta keeps the tool phase that follows out of the duration.
            duration = now - self._thinking_started
        elif thinking:
            duration = now - (self._msg_started or now)
        else:
            duration = None
        if duration is not None:
            step = {"kind": "thinking", "duration": round(max(0.0, duration), 2)}
            if not self.learning:
                step["text"] = thinking
            self._emit_step(step)
        self._msg_started = None
        self._thinking_started = None

        if m.get("stopReason") not in _EMISSIBLE:
            return
        text = text_of_content(m.get("content"))
        if text.strip():
            self.text = text
            self.error = ""
        elif m.get("stopReason") == "error":
            # A provider failure (expired key, quota, outage) arrives as an
            # assistant message with no content and stopReason=error. Record
            # it so the bridge can tell the learner instead of streaming an
            # empty bubble they cannot act on.
            message = m.get("errorMessage")
            self.error = message.strip() if isinstance(message, str) and message.strip() else "unknown provider error"

    def _tool_start(self, rec: dict) -> None:
        name = rec.get("toolName") or "tool"
        cid = rec.get("toolCallId")
        if not isinstance(cid, str) or not cid:
            cid = self._next_id()
        self._tools[cid] = {
            "name": name,
            "args": rec.get("args"),
            "started": self._clock(),
        }
        self._notify({"kind": "tool_start", "name": name})

    def _tool_end(self, rec: dict) -> None:
        name = rec.get("toolName") or "tool"
        cid = rec.get("toolCallId")
        info = None
        if isinstance(cid, str) and cid:
            info = self._tools.pop(cid, None)
        if info is None:
            # Older/stub records carry no id: pair with the last open call of
            # the same name, or fall back to a synthetic one.
            for key in reversed(list(self._tools)):
                if self._tools[key]["name"] == name:
                    info = self._tools.pop(key)
                    cid = key
                    break
        if info is None:
            info = {"name": name, "args": rec.get("args"), "started": None}
            cid = cid if isinstance(cid, str) and cid else self._next_id()
        started = info.get("started")
        duration = (self._clock() - started) if started is not None else 0.0
        step = {
            "kind": "tool",
            "id": cid,
            "name": name,
            "args": info.get("args", rec.get("args")),
            "status": "error" if rec.get("isError") else "done",
            "duration": round(max(0.0, duration), 2),
        }
        if not self.learning:
            step["result"] = result_text(rec.get("result"))
        self._emit_step(step)

    def final_text(self) -> str:
        text = strip_turn_tag(self.text)
        if _OPENUI_FENCE_RE.search(text):
            text = strip_openui_fences(text).strip()
        if not text.strip() and self.error:
            return f"⚠️ pi runtime error: {self.error}"
        return text

    def openui_payloads(self) -> list[str]:
        """OpenUI Lang payloads emitted this turn (rendered via embeds)."""
        return extract_openui_fences(strip_turn_tag(self.text))
