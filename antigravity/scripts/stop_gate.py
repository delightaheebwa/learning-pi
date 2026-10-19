#!/usr/bin/env python3
"""stop_gate.py — Stop lifecycle hook for Antigravity Desktop learning layer.

Enforces:
1. When background subagents are executing (fullyIdle=false), allows the agent to yield/pause.
2. In active learning flows (teach, resume, review, solo), ensures required subagents
   (scout for lesson context, verifier for claims/quizzes/grades, auditor for handoffs/close)
   have returned passing receipts before the turn completes.
3. Implements the 2-retry safety cap to prevent deadlocks.
"""
import json
import os
import re
import sys


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"decision": "allow"}))
            return
        payload = json.loads(raw_input)
    except Exception as exc:
        print(json.dumps({"decision": "allow", "reason": f"hook error: {exc}"}))
        return

    # If background tasks or subagents are actively running, allow yielding to wait
    fully_idle = payload.get("fullyIdle") if "fullyIdle" in payload else payload.get("fully_idle", True)
    if fully_idle is False:
        print(json.dumps({"decision": "allow"}))
        return

    transcript_path = payload.get("transcriptPath") or payload.get("transcript_path") or ""
    if not transcript_path or not os.path.isfile(transcript_path):
        print(json.dumps({"decision": "allow"}))
        return

    # Parse transcript steps
    steps = []
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.strip():
                    steps.append(json.loads(line))
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    if not steps:
        print(json.dumps({"decision": "allow"}))
        return

    # Check for subagent role. Subagents are not gated on Stop.
    for step in steps:
        content = str(step.get("content", ""))
        if any(role in content for role in [
            "[SUBAGENT_ROLE:scout]",
            "[SUBAGENT_ROLE:verifier]",
            "[SUBAGENT_ROLE:clerk]",
            "[SUBAGENT_ROLE:auditor]",
        ]):
            print(json.dumps({"decision": "allow"}))
            return

    # Identify active learning flow
    active_flow = None
    for step in steps:
        content = str(step.get("content", ""))
        m = re.search(r"\[\[FLOW:([a-z]+)\]\]", content)
        if m:
            active_flow = m.group(1)

    # Non-learning conversations are never gated
    if not active_flow:
        print(json.dumps({"decision": "allow"}))
        return

    # Locate the start of the current user turn
    last_user_idx = 0
    for idx, step in enumerate(steps):
        if step.get("source") == "USER_EXPLICIT" and step.get("type") == "USER_INPUT":
            last_user_idx = idx

    current_turn_steps = steps[last_user_idx:]

    # Check retry cap to prevent infinite loop
    retry_count = 0
    for step in current_turn_steps:
        content = str(step.get("content", ""))
        if "GATE:" in content:
            retry_count += 1
    if retry_count >= 2:
        print(json.dumps({"decision": "allow", "reason": "Retry cap reached; failing open."}))
        return

    # Aggregate text and tool calls in current turn
    turn_text = []
    invoked_subagents = set()
    written_files = set()
    latest_receipts = {}

    for step in current_turn_steps:
        # Check tool calls
        for tc in step.get("tool_calls", []):
            name = tc.get("name", "")
            args = tc.get("args", {})
            if name == "invoke_subagent":
                if "TypeName" in args:
                    invoked_subagents.add(args["TypeName"])
                for sa in args.get("Subagents", []):
                    if isinstance(sa, dict) and "TypeName" in sa:
                        invoked_subagents.add(sa.get("TypeName"))
            elif name in ("write_to_file", "replace_file_content"):
                tf = args.get("TargetFile", "")
                if tf:
                    written_files.add(tf)

        content = str(step.get("content", ""))
        turn_text.append(content)

        # Detect receipts in tool results or incoming subagent messages
        decoder = json.JSONDecoder()
        for receipt_name in ["SCOUT_RECEIPT", "REVIEW_SCOUT_RECEIPT", "VERIFIER_RECEIPT", "CLERK_RECEIPT", "AUDITOR_RECEIPT"]:
            marker = f"{receipt_name}:"
            idx = content.find(marker)
            while idx != -1:
                brace_idx = content.find("{", idx + len(marker))
                if brace_idx != -1:
                    try:
                        obj, end_pos = decoder.raw_decode(content[brace_idx:])
                        latest_receipts[receipt_name] = obj
                        idx = content.find(marker, brace_idx + end_pos)
                        continue
                    except Exception:
                        pass
                idx = content.find(marker, idx + len(marker))

    full_turn_text = "\n".join(turn_text)

    # Check 1: Ingest or Review Close
    if active_flow in ("ingest", "review", "solo") and ("CLERK_RECEIPT" in latest_receipts or "clerk" in invoked_subagents):
        # Once clerk has persisted state, auditor must audit writes before closing
        auditor_receipt = latest_receipts.get("AUDITOR_RECEIPT")
        if not auditor_receipt:
            print(
                json.dumps(
                    {
                        "decision": "continue",
                        "reason": (
                            "GATE: State persistence complete. You must invoke the auditor subagent "
                            "(review_gate or review_session_audit) to verify writes before finishing the closing summary."
                        ),
                    }
                )
            )
            return
        if auditor_receipt.get("verdict") == "ISSUES":
            print(
                json.dumps(
                    {
                        "decision": "continue",
                        "reason": (
                            "GATE: Auditor reported issues with state or wiki writes. "
                            "Fix the issues with clerk and re-audit before finalizing."
                        ),
                    }
                )
            )
            return

    # Check 2: Handoff Writes (Lessons/, Sessions/, Pending Ingest.json) via Clerk or direct
    clerk_receipt = latest_receipts.get("CLERK_RECEIPT", {})
    clerk_handoff = clerk_receipt.get("mode") in ("lesson_handoff", "pause_handoff")
    handoff_files = [f for f in written_files if any(p in f for p in ["Learning System/Lessons/", "Learning System/Sessions/", "Pending Ingest.json"])]
    if handoff_files or clerk_handoff:
        auditor_receipt = latest_receipts.get("AUDITOR_RECEIPT")
        if not auditor_receipt or auditor_receipt.get("mode") != "tutor_audit":
            print(
                json.dumps(
                    {
                        "decision": "continue",
                        "reason": (
                            "GATE: Lesson handoff writes completed. You must invoke the auditor subagent "
                            "(mode: 'tutor_audit') to verify file consistency before finishing this handoff."
                        ),
                    }
                )
            )
            return
        if auditor_receipt.get("verdict") == "ISSUES":
            print(
                json.dumps(
                    {
                        "decision": "continue",
                        "reason": (
                            "GATE: Tutor audit reported issues in handoff files. "
                            "Correct the handoff files with clerk and re-audit before finishing."
                        ),
                    }
                )
            )
            return

    # Check 3: Every-Turn Verifier Check for Teaching / Review Turns
    # If the turn generated substantial text to the learner (outside of a short status or slash command routing)
    if active_flow in ("teach", "resume", "review", "solo"):
        # Did the assistant formulate a substantive response?
        last_step = steps[-1] if steps else {}
        last_content = str(last_step.get("content", ""))

        # Exclude purely procedural transitions
        is_substantive = len(last_content.strip()) > 80 and not any(kw in last_content for kw in ["Verifying step", "Checking draft", "Running scout"])

        if is_substantive:
            verifier_receipt = latest_receipts.get("VERIFIER_RECEIPT")
            if not verifier_receipt:
                print(
                    json.dumps(
                        {
                            "decision": "continue",
                            "reason": (
                                "GATE: Every-turn verification required. Before presenting teaching claims, hints, "
                                "quizzes, or grades to the learner, you must invoke the verifier subagent with your proposed draft."
                            ),
                        }
                    )
                )
                return

            if verifier_receipt.get("verdict") == "ISSUES" or verifier_receipt.get("agrees") is False:
                print(
                    json.dumps(
                        {
                            "decision": "continue",
                            "reason": (
                                "GATE: Verifier returned ISSUES or grading disagreement. "
                                "You must apply the corrections and re-verify until obtaining a PASS receipt."
                            ),
                        }
                    )
                )
                return

            if verifier_receipt.get("omitted_foundations"):
                print(
                    json.dumps(
                        {
                            "decision": "continue",
                            "reason": (
                                "GATE: Verifier reported omitted foundational theory from the sources. "
                                "Integrate the missing theoretical mechanism into your draft and re-verify."
                            ),
                        }
                    )
                )
                return

    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
