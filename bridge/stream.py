"""Turn the raw pi RPC record stream into learner-facing text.

The whole point of this module is the buffering rule the Phase 0 spike forced:
`message_update` deltas carry the *pre-verification* draft (the spike watched a
withheld teaching draft stream in full before the gate replaced it at
`message_end`). So the bridge never forwards deltas. It emits only the text of a
completed, non-tool assistant message — the post-gate turn (verified text, or a
withheld/`unverified` banner that the gate wrote into the message itself).

Kept free of I/O so it can be unit-tested against synthetic records.
"""
from __future__ import annotations

import re

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


class TurnStream:
    """Accumulate one prompt's records and expose the learner-facing text."""

    def __init__(self) -> None:
        self.text: str = ""
        self.error: str = ""
        self.tool_events: list[str] = []

    def feed(self, rec: dict) -> None:
        t = rec.get("type")
        if t == "message_end":
            m = rec.get("message") or {}
            if m.get("role") != "assistant":
                return
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
        elif t == "tool_execution_start":
            name = rec.get("toolName")
            if name:
                self.tool_events.append(f"start:{name}")
        elif t == "tool_execution_end":
            name = rec.get("toolName")
            state = "error" if rec.get("isError") else "done"
            if name:
                self.tool_events.append(f"{state}:{name}")

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
