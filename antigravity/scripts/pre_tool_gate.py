#!/usr/bin/env python3
"""pre_tool_gate.py — PreToolUse lifecycle hook for Antigravity Desktop learning layer.

Enforces:
1. Read-only subagents (verifier, auditor, naive-student) cannot modify files —
   detected by a state machine over the transcript so a role never sticks after
   the subagent's run closes with its receipt (stale roles would deadlock the
   Tutor's widget writes or bypass the pure-teaching stance).
2. Tutor/Reviewer main session cannot directly overwrite Clerk-owned state files
   (MISSION, CURRICULUM, Active Concepts, Mistakes, Learner History, wiki pages).
3. Solo mode (FLOW:solo) cannot create HTML widget artifacts (SOLO_NO_AIDS).
"""
import json
import os
import sys

ROLE_MARKERS = {
    "[SUBAGENT_ROLE:verifier]": "verifier",
    "[SUBAGENT_ROLE:auditor]": "auditor",
    "[SUBAGENT_ROLE:clerk]": "clerk",
    "[SUBAGENT_ROLE:scout]": "scout",
    "[SUBAGENT_ROLE:naive-student]": "naive-student",
}
# Receipt that closes (ends) a subagent run: the Tutor resumes on its wakeup.
ROLE_RECEIPT = {
    "verifier": "VERIFIER_RECEIPT",
    "auditor": "AUDITOR_RECEIPT",
    "naive-student": "NAIVE_STUDENT_RECEIPT",
    "scout": "SCOUT_RECEIPT",
    "clerk": "CLERK_RECEIPT",
}


def infer_role(steps):
    """State machine over transcript steps, tracked as a LIFO stack so parallel
    dispatches (Subagents=[verifier, scout]) don't orphan a role.

    - invoke_subagent(TypeName=verifier|auditor|naive-student|...) opens that
      subagent's run (pushed).
    - The subagent's run closes when its receipt marker appears (popped); the
      Tutor resumes speaking.
    - A role-marked output step also opens the role (covers subagent turns whose
      invocation wasn't tracked in tool_calls).
    - Any explicit user input resets to "tutor".
    Returns the role in effect at the END of the transcript ("tutor" when none).
    """
    stack = []
    for step in steps:
        if step.get("source") == "USER_EXPLICIT" and step.get("type") == "USER_INPUT":
            stack = []
            continue

        # Opening calls (tutor dispatching subagents)
        for tc in step.get("tool_calls", []) or []:
            if tc.get("name") == "invoke_subagent":
                args = tc.get("args", {}) or {}
                type_names = set()
                if "TypeName" in args:
                    type_names.add(args["TypeName"])
                for sa in args.get("Subagents", []) or []:
                    if isinstance(sa, dict) and "TypeName" in sa:
                        type_names.add(sa.get("TypeName"))
                for sub_role in ("verifier", "auditor", "naive-student", "scout", "clerk"):
                    if sub_role in type_names:
                        stack.append(sub_role)

        content = str(step.get("content", ""))

        # Role-marked output step: that subagent is speaking
        for marker, sub_role in ROLE_MARKERS.items():
            if marker in content:
                stack.append(sub_role)

        # Closing receipt: that subagent's run ends
        for sub_role, receipt in ROLE_RECEIPT.items():
            if sub_role in stack and receipt + ":" in content:
                # Pop the most recent occurrence of this role
                for i in range(len(stack) - 1, -1, -1):
                    if stack[i] == sub_role:
                        stack.pop(i)
                        break

    return stack[-1] if stack else "tutor"


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

    tool_call = payload.get("toolCall") or payload.get("tool_call") or {}
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})
    transcript_path = payload.get("transcriptPath") or payload.get("transcript_path") or ""

    if not transcript_path or not os.path.isfile(transcript_path):
        print(json.dumps({"decision": "allow"}))
        return

    # Inspect transcript to identify the ACTIVE flow (last [[FLOW:...]] marker, not a
    # historical one) and the role in effect now
    last_flow = None
    steps = []

    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                step = json.loads(line)
                steps.append(step)
                content = str(step.get("content", ""))
                idx = content.find("[[FLOW:")
                while idx != -1:
                    end = content.find("]]", idx)
                    if end != -1:
                        last_flow = content[idx + len("[[FLOW:") : end]
                        idx = content.find("[[FLOW:", end)
                    else:
                        break
    except Exception:
        steps = []

    is_learning_flow = last_flow is not None
    is_solo = last_flow == "solo"

    agent_role = infer_role(steps) if steps else "tutor"

    # Non-learning sessions are never gated
    if not is_learning_flow and agent_role == "tutor":
        print(json.dumps({"decision": "allow"}))
        return

    # Rule 1: Read-only subagents cannot call file modification tools
    if agent_role in ("verifier", "auditor", "naive-student"):
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
    if is_solo and tool_name in ("write_to_file", "replace_file_content"):
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

    # Rule 3: Main Tutor pure teaching stance (delegates all repository writes to Clerk)
    if agent_role == "tutor" and is_learning_flow:
        if tool_name in ("write_to_file", "replace_file_content"):
            target = tool_args.get("TargetFile", "")
            if "Learning System/" in target or "Knowledge Wiki/" in target:
                print(
                    json.dumps(
                        {
                            "decision": "deny",
                            "reason": (
                                "TUTOR_PURE_TEACHING: Tutor focuses purely on teaching and does not write to the learning repository. "
                                "All lesson notes, sessions, records, pending ingest files, and state updates must be delegated to the 'clerk' subagent."
                            ),
                        }
                    )
                )
                return

        if tool_name == "run_command":
            cmd = tool_args.get("CommandLine", "")
            if "ops.py attempt" in cmd or "ops.py apply" in cmd or "git commit" in cmd:
                print(
                    json.dumps(
                        {
                            "decision": "deny",
                            "reason": "TUTOR_PURE_TEACHING: Attempt logging, state mutation, and git commits are owned exclusively by the clerk subagent.",
                        }
                    )
                )
                return

    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
