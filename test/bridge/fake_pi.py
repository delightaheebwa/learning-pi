#!/usr/bin/env python3
"""A deterministic fake `pi --mode rpc` for bridge tests.

Speaks just enough of the protocol: a prompt produces `message_update` deltas
(including a secret draft), a `message_end`, and `agent_settled`. Scenarios via
$FAKE_PI_SCENARIO let the tests prove the bridge buffers text (deltas never
reach the client). Also answers get_fork_messages/fork for regenerate.
"""
import json
import os
import sys
import time

SECRET = "SECRET_DRAFT_MUST_NOT_LEAK"
SCENARIO = os.environ.get("FAKE_PI_SCENARIO", "default")
SESSION_FILE = os.environ.get("FAKE_PI_SESSION_FILE") or os.path.join(
    os.environ.get("TMPDIR", "/tmp"), f"fake-pi-{os.getpid()}.jsonl"
)
# The active branch's user messages, so fork/regenerate/edit alignment can be
# exercised end to end. Entry ids are e1, e2, ... in conversation order.
USERS: list[str] = []


def out(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def note(path, line):
    """Append a line to an env-named log file if set, so a test can observe it."""
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def _final_text():
    if SCENARIO == "provider_error":
        # A provider failure: no content, stopReason=error, errorMessage set.
        return ""
    if SCENARIO == "withhold":
        return "⛔ WITHHELD (NO_SCOUT_CONTEXT)\nRun the `scout` subagent first for a new lesson."
    if SCENARIO == "turn_tag":
        # A non-learning message: the gate passes it through untouched, so the
        # final text still carries the internal turn tag the bridge must clean.
        return "[[TURN:none]] 2 plus 2 equals 4."
    return "VERIFIED_FINAL"


def _steps_trace():
    """A realistic tool-using turn: think -> tool -> think -> answer.

    Carries `args`, a result, and thinking text (with the secret in the thinking
    and result) so tests can prove a learning flow renders only action metadata,
    while a general chat gets the fuller trace.
    """
    out({"type": "message_start",
         "message": {"role": "assistant", "content": [], "stopReason": "pending"}})
    out({"type": "message_update",
         "assistantMessageEvent": {"type": "thinking_delta", "delta": "pondering " + SECRET}})
    out({"type": "message_end",
         "message": {"role": "assistant", "stopReason": "toolUse",
                     "content": [{"type": "thinking", "thinking": "pondering " + SECRET}]}})
    out({"type": "tool_execution_start", "toolCallId": "call_1",
         "toolName": "bash", "args": {"command": "ls -la"}})
    if SCENARIO == "steps_slow":
        time.sleep(0.7)  # the turn stays open: the step must already be on the wire
    out({"type": "tool_execution_end", "toolCallId": "call_1", "toolName": "bash",
         "result": {"content": [{"type": "text", "text": "file.txt " + SECRET}],
                    "details": {}},
         "isError": SCENARIO == "steps_error"})
    out({"type": "message_start",
         "message": {"role": "assistant", "content": [], "stopReason": "pending"}})
    out({"type": "message_update",
         "assistantMessageEvent": {"type": "text_delta", "delta": SECRET}})
    if SCENARIO == "steps_provider_error":
        out({"type": "message_end",
             "message": {"role": "assistant", "stopReason": "error", "content": [],
                         "errorMessage": "429: quota exhausted"}})
    else:
        out({"type": "message_end",
             "message": {"role": "assistant", "stopReason": "stop",
                         "content": [{"type": "thinking", "thinking": "wrapping up"},
                                     {"type": "text", "text": _final_text()}]}})
    out({"type": "turn_end"})
    out({"type": "agent_end"})
    out({"type": "agent_settled"})


def run_prompt(cid):
    if SCENARIO == "handled":
        # An extension command consumed the prompt: no run starts, so the bridge
        # must return immediately instead of waiting for agent_settled.
        out({"id": cid, "type": "response", "command": "prompt", "success": True,
             "data": {"disposition": "handled"}})
        return
    out({"id": cid, "type": "response", "command": "prompt", "success": True,
         "data": {"disposition": "started"}})
    if SCENARIO == "silent":
        # A hung turn: the prompt is accepted, then pi emits nothing at all. The
        # bridge's idle budget must abort it with an actionable reason.
        return
    if SCENARIO in ("trickle", "trickle_endless"):
        # An active-but-long turn: records arrive faster than the idle budget but
        # the turn outlives it, so only an idle (not wall-clock) budget finishes.
        rounds = 40 if SCENARIO == "trickle_endless" else 6
        for i in range(rounds):
            time.sleep(0.05 if SCENARIO == "trickle_endless" else 0.15)
            out({"type": "message_update",
                 "assistantMessageEvent": {"type": "thinking_delta", "delta": "tick %d" % i}})
        out({"type": "message_end",
             "message": {"role": "assistant", "stopReason": "stop",
                         "content": [{"type": "text", "text": _final_text()}]}})
        out({"type": "turn_end"})
        out({"type": "agent_end"})
        out({"type": "agent_settled"})
        return
    if SCENARIO == "slow":
        time.sleep(1.5)
    out({"type": "agent_start"})
    out({"type": "turn_start"})
    if SCENARIO in ("steps", "steps_slow", "steps_error", "steps_provider_error"):
        _steps_trace()
        return
    out({"type": "message_start",
         "message": {"role": "assistant", "content": [], "stopReason": "pending"}})
    # The raw draft streams as deltas BEFORE verification — the bridge must drop these.
    for piece in (SECRET, " ", "more draft text"):
        out({"type": "message_update",
             "assistantMessageEvent": {"type": "text_delta", "delta": piece}})
    out({"type": "message_update",
         "assistantMessageEvent": {"type": "thinking_delta", "delta": "thinking " + SECRET}})
    out({"type": "tool_execution_start", "toolName": "bash"})
    out({"type": "tool_execution_end", "toolName": "bash", "isError": False})
    if SCENARIO == "provider_error":
        out({"type": "message_end",
             "message": {"role": "assistant", "stopReason": "error",
                         "content": [],
                         "errorMessage": "401: {\"code\":\"api_key_expired\"}"}})
    else:
        out({"type": "message_end",
             "message": {"role": "assistant", "stopReason": "stop",
                         "content": [{"type": "text", "text": _final_text()}]}})
    out({"type": "turn_end"})
    out({"type": "agent_end"})
    out({"type": "agent_settled"})


def main():
    # Emit two fire-and-forget UI requests; the bridge must not choke on them.
    out({"type": "extension_ui_request", "id": "w1", "method": "setWidget", "widgetKey": "x"})
    out({"type": "extension_ui_request", "id": "c1", "method": "confirm", "message": "run?"})
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = rec.get("type")
        if t == "prompt":
            message = str(rec.get("message", ""))
            note(os.environ.get("FAKE_PI_PROMPT_LOG"), message)
            if rec.get("images"):
                note(os.environ.get("FAKE_PI_IMAGE_LOG"), json.dumps(rec["images"]))
            USERS.append(message)
            run_prompt(rec.get("id"))
        elif t == "get_state":
            out({"id": rec.get("id"), "type": "response", "command": "get_state",
                 "success": True,
                 "data": {"sessionFile": SESSION_FILE, "sessionId": "fake-session"}})
        elif t == "switch_session":
            out({"id": rec.get("id"), "type": "response", "command": "switch_session",
                 "success": True, "data": {"cancelled": False}})
        elif t == "get_fork_messages":
            out({"id": rec.get("id"), "type": "response", "command": "get_fork_messages",
                 "success": True,
                 "data": {"messages": [
                     {"entryId": f"e{i + 1}", "text": text}
                     for i, text in enumerate(USERS)
                 ]}})
        elif t == "fork":
            if SCENARIO == "forkfail":
                out({"id": rec.get("id"), "type": "response", "command": "fork",
                     "success": False, "error": "cannot fork"})
            else:
                entry = str(rec.get("entryId", ""))
                note(os.environ.get("FAKE_PI_FORK_LOG"), entry)
                index = None
                if entry.startswith("e") and entry[1:].isdigit():
                    index = int(entry[1:]) - 1
                text = USERS[index] if index is not None and 0 <= index < len(USERS) else ""
                if index is not None:
                    del USERS[index:]
                out({"id": rec.get("id"), "type": "response", "command": "fork",
                     "success": True, "data": {"text": text, "cancelled": False}})
        elif t == "abort":
            note(os.environ.get("FAKE_PI_ABORT_LOG"), "abort")
            out({"id": rec.get("id"), "type": "response", "command": "abort",
                 "success": True, "data": {}})
            if SCENARIO == "silent":
                # Exit so the bridge's post-abort drain sees EOF instead of
                # waiting out its grace window.
                return 0
        elif t == "extension_ui_response":
            continue
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
