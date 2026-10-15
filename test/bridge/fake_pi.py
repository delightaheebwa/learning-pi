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


def out(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def note(path, line):
    """Append a line to an env-named log file if set, so a test can observe it."""
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def _final_text():
    if SCENARIO == "withhold":
        return "⛔ WITHHELD (NO_SCOUT_CONTEXT)\nRun the `scout` subagent first for a new lesson."
    return "VERIFIED_FINAL"


def run_prompt(cid):
    if SCENARIO == "handled":
        # An extension command consumed the prompt: no run starts, so the bridge
        # must return immediately instead of waiting for agent_settled.
        out({"id": cid, "type": "response", "command": "prompt", "success": True,
             "data": {"disposition": "handled"}})
        return
    out({"id": cid, "type": "response", "command": "prompt", "success": True,
         "data": {"disposition": "started"}})
    if SCENARIO == "slow":
        time.sleep(1.5)
    out({"type": "agent_start"})
    out({"type": "turn_start"})
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
            note(os.environ.get("FAKE_PI_PROMPT_LOG"), str(rec.get("message", "")))
            run_prompt(rec.get("id"))
        elif t == "get_fork_messages":
            out({"id": rec.get("id"), "type": "response", "command": "get_fork_messages",
                 "success": True, "data": {"messages": [{"entryId": "e1", "text": "hello"}]}})
        elif t == "fork":
            if SCENARIO == "forkfail":
                out({"id": rec.get("id"), "type": "response", "command": "fork",
                     "success": False, "error": "cannot fork"})
            else:
                note(os.environ.get("FAKE_PI_FORK_LOG"), str(rec.get("entryId", "")))
                out({"id": rec.get("id"), "type": "response", "command": "fork",
                     "success": True, "data": {"text": "hello", "cancelled": False}})
        elif t == "abort":
            out({"id": rec.get("id"), "type": "response", "command": "abort",
                 "success": True, "data": {}})
        elif t == "extension_ui_response":
            continue
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
