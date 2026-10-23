#!/usr/bin/env python3
"""pre_tool_gate.py — PreToolUse lifecycle hook for Antigravity Desktop learning layer.

Enforces:
1. Read-only subagents (verifier, auditor, naive-student) cannot modify files —
   detected by a state machine over the transcript so a role never sticks after
   the subagent's run closes with its receipt (stale roles would deadlock
   legitimate subagent writes or bypass the pure-teaching stance).
2. Tutor/Reviewer main session cannot directly overwrite Clerk-owned state files
   (MISSION, CURRICULUM, Active Concepts, Mistakes, Learner History, wiki pages),
   and cannot author widget HTML (that is ui-generator's only write).
3. ui-generator writes only one `.html` artifact, outside the learning repository.
4. Solo mode (FLOW:solo) cannot create HTML widget artifacts (SOLO_NO_AIDS).
"""
import json
import os
import re
import sys

ROLE_MARKERS = {
    "[SUBAGENT_ROLE:verifier]": "verifier",
    "[SUBAGENT_ROLE:auditor]": "auditor",
    "[SUBAGENT_ROLE:clerk]": "clerk",
    "[SUBAGENT_ROLE:scout]": "scout",
    "[SUBAGENT_ROLE:naive-student]": "naive-student",
    "[SUBAGENT_ROLE:ui-generator]": "ui-generator",
}
# Receipt that closes (ends) a subagent run: the Tutor resumes on its wakeup.
ROLE_RECEIPT = {
    "verifier": "VERIFIER_RECEIPT",
    "auditor": "AUDITOR_RECEIPT",
    "naive-student": "NAIVE_STUDENT_RECEIPT",
    "scout": "SCOUT_RECEIPT",
    "clerk": "CLERK_RECEIPT",
    "ui-generator": "UI_GENERATOR_RECEIPT",
}


def get_arg(args, *names):
    """Fetch an arg by any of the given key spellings (PascalCase or snake_case)."""
    for n in names:
        if n in args:
            return args[n]
    lowered = {k.lower(): v for k, v in args.items()}
    for n in names:
        if n.lower() in lowered:
            return lowered[n.lower()]
    return None


def infer_role(steps):
    """State machine over transcript steps, tracked as a LIFO stack so parallel
    dispatches (Subagents=[verifier, scout]) don't orphan a role.

    - invoke_subagent(TypeName=verifier|auditor|naive-student|...) opens that
      subagent's run (pushed).
    - The subagent's run closes when its receipt marker appears (popped); the
      Tutor resumes speaking.
    - A role-marked output step also opens the role (covers subagent turns whose
      invocation wasn't tracked in tool_calls).
    - A SYSTEM_MESSAGE carrying a subagent `mode: '...'` payload also opens that
      role (idempotently — it is evidence of an already-open run, never a second
      push, so the role still closes on its receipt).
    - GENERIC tool-output steps are skipped entirely: a file read or grep that
      happens to contain role markers, receipt text, modes, or flow markers must
      not open/close a role or change the flow.
    - Any explicit user input resets to "tutor".
    Returns the role in effect at the END of the transcript ("tutor" when none).
    """
    stack = []

    def push_role(sub_role):
        """Open a role at most once while it is already active. Invocation calls
        may push the same role twice (parallel same-role dispatches each get a
        receipt); prompt/marker detection is only evidence of an already-open
        run, so it must not double-push or the role survives its receipt."""
        if sub_role not in stack:
            stack.append(sub_role)

    for step in steps:
        if step.get("source") == "USER_EXPLICIT" and step.get("type") == "USER_INPUT":
            stack = []
            continue

        # Ignore tool outputs (type == "GENERIC") so reading/grepping files doesn't
        # trigger role changes, receipts, or flow changes.
        if step.get("type") == "GENERIC":
            continue

        # Opening calls (tutor dispatching subagents)
        for tc in step.get("tool_calls", []) or []:
            if tc.get("name") == "invoke_subagent":
                args = tc.get("args", {}) or {}
                type_names = set()
                type_name = get_arg(args, "TypeName", "typeName", "type_name")
                if type_name:
                    type_names.add(type_name)
                subagents = get_arg(args, "Subagents", "subagents") or []
                for sa in subagents:
                    if isinstance(sa, dict):
                        sa_type = get_arg(sa, "TypeName", "typeName", "type_name")
                        if sa_type:
                            type_names.add(sa_type)
                for sub_role in ("verifier", "auditor", "naive-student", "scout", "clerk", "ui-generator"):
                    if sub_role in type_names:
                        stack.append(sub_role)

        content = str(step.get("content", ""))

        # Role-marked output step: that subagent is speaking
        for marker, sub_role in ROLE_MARKERS.items():
            if marker in content:
                push_role(sub_role)

        # Detect subagent prompt in system message or mode payload
        if step.get("source") == "SYSTEM" and step.get("type") == "SYSTEM_MESSAGE":
            for mode, sub_role in [
                ("pause_handoff", "clerk"),
                ("lesson_handoff", "clerk"),
                ("ingest", "clerk"),
                ("review_close", "clerk"),
                ("fact_check", "verifier"),
                ("quiz_audit", "verifier"),
                ("grade_audit", "verifier"),
                ("ui_audit", "verifier"),
                ("tutor_audit", "auditor"),
                ("scout_audit", "auditor"),
                ("review_gate", "auditor"),
                ("review_session_audit", "auditor"),
                ("lesson", "scout"),
                ("review", "scout"),
                ("widget", "ui-generator"),
            ]:
                if f"mode: '{mode}'" in content or f'mode: "{mode}"' in content or f'"mode": "{mode}"' in content:
                    push_role(sub_role)
                    break

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
                if step.get("type") == "GENERIC":
                    continue
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

    # Rule 3: ui-generator is scoped to one HTML artifact outside the learning repo
    if agent_role == "ui-generator" and tool_name in ("write_to_file", "replace_file_content"):
        target = tool_args.get("TargetFile", "")
        repo_paths = ("Learning System/", "Knowledge Wiki/", ".tmp/", "Pending Ingest.json")
        in_artifact_dir = "/.gemini/antigravity/brain/" in target or "/.gemini/antigravity-cli/brain/" in target
        if (
            not target.lower().endswith((".html", ".htm"))
            or any(p in target for p in repo_paths)
            or not in_artifact_dir
        ):
            print(
                json.dumps(
                    {
                        "decision": "deny",
                        "reason": (
                            "UI_GENERATOR_SCOPE: the ui-generator subagent may only write one .html widget artifact "
                            "into the current conversation's Antigravity artifact directory — never into the learning repository."
                        ),
                    }
                )
            )
            return

    # Rule 3b: ui-generator's only shell command is the receipt hash. No other
    # command may run (otherwise shell redirection would bypass Rule 3).
    if agent_role == "ui-generator" and tool_name == "run_command":
        cmd = str(tool_args.get("CommandLine", "") or "")
        if not cmd.strip().startswith("sha256sum ") or "\n" in cmd or re.search(r"[;&|<>`$(){}]", cmd):
            print(
                json.dumps(
                    {
                        "decision": "deny",
                        "reason": (
                            "UI_GENERATOR_SCOPE: the ui-generator subagent may only run 'sha256sum <artifact>' "
                            "to hash its widget; no other command or shell operator is allowed."
                        ),
                    }
                )
            )
            return

    # Rule 4: Main Tutor pure teaching stance (delegates all repository writes to Clerk
    # and all widget artifacts to ui-generator)
    if agent_role == "tutor" and is_learning_flow:
        if tool_name in ("write_to_file", "replace_file_content"):
            target = tool_args.get("TargetFile", "")
            if target.lower().endswith((".html", ".htm")):
                print(
                    json.dumps(
                        {
                            "decision": "deny",
                            "reason": (
                                "UI_GENERATOR_DELEGATION: the Tutor does not author widget HTML. Hand the complete spec "
                                "to the 'ui-generator' subagent and embed the audited file it returns."
                            ),
                        }
                    )
                )
                return
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
