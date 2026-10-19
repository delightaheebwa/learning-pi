#!/usr/bin/env python3
"""pre_tool_gate.py — PreToolUse lifecycle hook for Antigravity Desktop learning layer.

Enforces:
1. Read-only subagents (verifier, auditor) cannot modify files.
2. Tutor/Reviewer main session cannot directly overwrite Clerk-owned state files
   (MISSION, CURRICULUM, Active Concepts, Mistakes, Learner History, wiki pages).
3. Solo mode (FLOW:solo) cannot create HTML widget artifacts (SOLO_NO_AIDS).
"""
import json
import os
import sys
from pathlib import Path


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"decision": "allow"}))
            return
        payload = json.loads(raw_input)
    except Exception as exc:
        # Fail open on parser error
        print(json.dumps({"decision": "allow", "reason": f"hook error: {exc}"}))
        return

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})
    transcript_path = payload.get("transcriptPath", "")

    if not transcript_path or not os.path.isfile(transcript_path):
        print(json.dumps({"decision": "allow"}))
        return

    # Inspect transcript to identify active flow and agent role
    is_learning_flow = False
    is_solo = False
    agent_role = "tutor"  # default main session

    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                step = json.loads(line)
                content = str(step.get("content", ""))

                if "[SUBAGENT_ROLE:verifier]" in content:
                    agent_role = "verifier"
                elif "[SUBAGENT_ROLE:auditor]" in content:
                    agent_role = "auditor"
                elif "[SUBAGENT_ROLE:clerk]" in content:
                    agent_role = "clerk"
                elif "[SUBAGENT_ROLE:scout]" in content:
                    agent_role = "scout"

                if "[[FLOW:" in content:
                    is_learning_flow = True
                    if "[[FLOW:solo]]" in content:
                        is_solo = True
    except Exception:
        pass

    # Non-learning sessions are never gated
    if not is_learning_flow and agent_role == "tutor":
        print(json.dumps({"decision": "allow"}))
        return

    # Rule 1: Read-only subagents cannot call file modification tools
    if agent_role in ("verifier", "auditor"):
        if tool_name in ("write_to_file", "replace_file_content"):
            print(
                json.dumps(
                    {
                        "decision": "deny",
                        "reason": f"{agent_role.capitalize()} subagent is strictly read-only and cannot write files.",
                    }
                )
            )
            return

    # Rule 2: In solo mode, no HTML widgets may be created
    if is_solo and tool_name == "write_to_file":
        target = tool_args.get("TargetFile", "")
        if target.endswith(".html"):
            print(
                json.dumps(
                    {
                        "decision": "deny",
                        "reason": "SOLO_NO_AIDS: Interactive widgets and aids are strictly forbidden during /solo assessment.",
                    }
                )
            )
            return

    # Rule 3: Main Tutor/Reviewer session write discipline
    if agent_role == "tutor" and is_learning_flow:
        clerk_owned_markers = [
            "Learning System/MISSION.md",
            "Learning System/CURRICULUM.md",
            "Learning System/Core/📚 Active Concepts.md",
            "Learning System/Core/🧯 Mistakes.md",
            "Learning System/Core/Learner History.md",
            "Learning System/Core/💡 Learning Profile.md",
            "Knowledge Wiki/wiki/",
            "Knowledge Wiki/index.md",
            "Knowledge Wiki/log.md",
            "Learning System/Reviews/",
        ]
        if tool_name in ("write_to_file", "replace_file_content"):
            target = tool_args.get("TargetFile", "")
            for marker in clerk_owned_markers:
                if marker in target:
                    print(
                        json.dumps(
                            {
                                "decision": "deny",
                                "reason": (
                                    f"Tutor write discipline: '{marker}' is owned exclusively by the clerk subagent. "
                                    "Mid-lesson state lives in conversation context; durable persistence must be delegated to clerk."
                                ),
                            }
                        )
                    )
                    return

        if tool_name == "run_command":
            cmd = tool_args.get("CommandLine", "")
            if "ops.py apply" in cmd or ("git commit" in cmd and "Learning System" in cmd):
                print(
                    json.dumps(
                        {
                            "decision": "deny",
                            "reason": "Tutor write discipline: Direct state application and git commits are owned by the clerk subagent.",
                        }
                    )
                )
                return

    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
