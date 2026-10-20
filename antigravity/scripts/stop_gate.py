#!/usr/bin/env python3
"""stop_gate.py — Stop lifecycle hook for Antigravity Desktop learning layer.

Enforces:
1. When background subagents are executing (fullyIdle=false), allows the agent to yield/pause.
2. In active learning flows (teach, resume, review, solo), ensures required subagents
   (scout for lesson context, verifier for claims/quizzes/grades, auditor for handoffs/close)
   have returned passing receipts before the turn completes.
3. Two retry classes: schema gates (auditor housekeeping) fail open after 2 blocks to
   prevent deadlocks; CRITICAL gates (unverified teaching, grading disagreements, omitted
   foundations — and anything in /solo) never silently fail open. A critical gate is
   re-issued up to 6 times; if still unresolved, the turn may proceed ONLY with a visible
   `⚠️ UNVERIFIED` banner so the learner is never bluffed by a silent fail-open.
4. Substantiveness is judged over the WHOLE turn text (receipts stripped), so a long
   substantive emission cannot hide behind a short closing line.
"""
import json
import os
import re
import sys

SCHEMA_CAP = 2
CRITICAL_CAP = 6
SUBAGENT_ROLE_MARKERS = [
    "[SUBAGENT_ROLE:scout]",
    "[SUBAGENT_ROLE:verifier]",
    "[SUBAGENT_ROLE:clerk]",
    "[SUBAGENT_ROLE:auditor]",
    "[SUBAGENT_ROLE:naive-student]",
]
RECEIPT_NAMES = [
    "SCOUT_RECEIPT",
    "REVIEW_SCOUT_RECEIPT",
    "VERIFIER_RECEIPT",
    "CLERK_RECEIPT",
    "AUDITOR_RECEIPT",
    "NAIVE_STUDENT_RECEIPT",
]
# Receipt that marks the END of a subagent run (tutor resumes on wakeup)
ROLE_RECEIPT = {
    "verifier": "VERIFIER_RECEIPT",
    "auditor": "AUDITOR_RECEIPT",
    "naive-student": "NAIVE_STUDENT_RECEIPT",
    "scout": "SCOUT_RECEIPT",
    "clerk": "CLERK_RECEIPT",
}


def emit(decision, reason=None):
    payload = {"decision": decision}
    if reason:
        payload["reason"] = reason
    print(json.dumps(payload))


def detect_subagents_in_call(name, args, invoked_subagents):
    if name == "invoke_subagent":
        if "TypeName" in args:
            invoked_subagents.add(args["TypeName"])
        for sa in args.get("Subagents", []) or []:
            if isinstance(sa, dict) and "TypeName" in sa:
                invoked_subagents.add(sa.get("TypeName"))


def collect_receipts(content, latest_receipts, decoder):
    """Parse receipt JSON objects out of a step's text."""
    for receipt_name in RECEIPT_NAMES:
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


def strip_receipts(content, decoder):
    """Return step text with embedded receipt JSON objects removed, so
    substantiveness is judged on learner-facing prose only."""
    out = content
    for receipt_name in RECEIPT_NAMES:
        marker = f"{receipt_name}:"
        while True:
            idx = out.find(marker)
            if idx == -1:
                break
            brace_idx = out.find("{", idx + len(marker))
            if brace_idx == -1:
                break
            try:
                _obj, end_pos = decoder.raw_decode(out[brace_idx:])
            except Exception:
                break
            out = out[:idx] + out[brace_idx + end_pos:]
    return out


def is_active_subagent(steps, decoder):
    """State machine over the transcript: a set of subagent runs is 'active' at the
    END of the transcript if their invocations have not yet been closed by their
    receipts. Used to exempt a Stop event that belongs to a subagent's own turn.
    Tracks a set so parallel dispatches (Subagents=[verifier, scout]) are each
    closed by their own receipt instead of orphaning one."""
    active = set()
    for step in steps:
        for tc in step.get("tool_calls", []) or []:
            called = set()
            detect_subagents_in_call(tc.get("name", ""), tc.get("args", {}) or {}, called)
            active.update(role for role in called if role in ROLE_RECEIPT)
        content = str(step.get("content", ""))
        # A role-marked output step (re)opens that subagent's run...
        for role, receipt in ROLE_RECEIPT.items():
            if f"[SUBAGENT_ROLE:{role}]" in content:
                active.add(role)
        # ...and each role's own receipt closes exactly that role's run.
        for role, receipt in ROLE_RECEIPT.items():
            if role in active and receipt + ":" in content:
                active.discard(role)
    return active


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            emit("allow")
            return
        payload = json.loads(raw_input)
    except Exception as exc:
        emit("allow", f"hook error: {exc}")
        return

    # If background tasks or subagents are actively running, allow yielding to wait
    fully_idle = payload.get("fullyIdle") if "fullyIdle" in payload else payload.get("fully_idle", True)
    if fully_idle is False:
        emit("allow")
        return

    transcript_path = payload.get("transcriptPath") or payload.get("transcript_path") or ""
    if not transcript_path or not os.path.isfile(transcript_path):
        emit("allow")
        return

    # Parse transcript steps
    steps = []
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.strip():
                    steps.append(json.loads(line))
    except Exception:
        emit("allow")
        return

    if not steps:
        emit("allow")
        return

    decoder = json.JSONDecoder()

    # If this Stop belongs to a subagent's own turn, it is not gated. A subagent is
    # active when its invocation (or its own role-marked output) has not yet been
    # closed by its receipt.
    if is_active_subagent(steps, decoder):
        emit("allow")
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
        emit("allow")
        return

    # Locate the start of the current user turn
    last_user_idx = 0
    for idx, step in enumerate(steps):
        if step.get("source") == "USER_EXPLICIT" and step.get("type") == "USER_INPUT":
            last_user_idx = idx

    current_turn_steps = steps[last_user_idx:]

    # Aggregate tool calls and receipts in current turn
    invoked_subagents = set()
    written_files = set()
    latest_receipts = {}

    for step in current_turn_steps:
        for tc in step.get("tool_calls", []) or []:
            detect_subagents_in_call(tc.get("name", ""), tc.get("args", {}) or {}, invoked_subagents)
            name = tc.get("name", "")
            if name in ("write_to_file", "replace_file_content"):
                tf = (tc.get("args", {}) or {}).get("TargetFile", "")
                if tf:
                    written_files.add(tf)

        content = str(step.get("content", ""))
        collect_receipts(content, latest_receipts, decoder)

    # Retry accounting. Hook "continue" reasons may or may not persist as transcript
    # steps, so count BOTH explicit GATE markers and unresolved ISSUES receipts:
    # each ISSUES verifier receipt counts as a critical retry; each ISSUES auditor
    # receipt counts as a schema retry — except in /solo, where the whole close is
    # critical-tier (closed-book integrity).
    marker_critical = sum(1 for s in current_turn_steps if "GATE-CRIT:" in str(s.get("content", "")))
    marker_schema = sum(
        1 for s in current_turn_steps
        if "GATE:" in str(s.get("content", "")) and "GATE-CRIT:" not in str(s.get("content", ""))
    )
    verifier_issues = sum(
        1 for s in current_turn_steps
        if "VERIFIER_RECEIPT" in str(s.get("content", "")) and re.search(r'"verdict"\s*:\s*"ISSUES"', str(s.get("content", "")))
    )
    auditor_issues = sum(
        1 for s in current_turn_steps
        if "AUDITOR_RECEIPT" in str(s.get("content", "")) and re.search(r'"verdict"\s*:\s*"ISSUES"', str(s.get("content", "")))
    )
    critical_retries = max(marker_critical, verifier_issues + (auditor_issues if active_flow == "solo" else 0))
    schema_retries = 0 if active_flow == "solo" else max(marker_schema, auditor_issues)

    def tier_block(reason_body, is_critical):
        """Emit a retry block. The tier marker is added HERE so the emitted reason
        carries the same tier the retry counter will count on the next Stop."""
        reason = ("GATE-CRIT: " if is_critical else "GATE: ") + reason_body
        if is_critical:
            if critical_retries >= CRITICAL_CAP:
                emit(
                    "allow",
                    reason
                    + " GATE-CRIT-ESCALATION: Verification could not be completed after repeated attempts. "
                    "Proceed ONLY if you prepend a visible '⚠️ UNVERIFIED — this step failed independent verification' "
                    "banner to the learner-facing text. Never present unverified content as verified.",
                )
                return
            emit("continue", reason)
        else:
            if schema_retries >= SCHEMA_CAP:
                emit("allow", "Retry cap reached; failing open.")
                return
            emit("continue", reason)

    # Substantiveness is judged over the whole turn (receipts stripped): a substantive
    # emission cannot escape the gate by hiding behind a short closing line. No
    # procedural-phrase exemption — a status line is short, and anything long is gated.
    stripped_text = "\n".join(strip_receipts(str(step.get("content", "")), decoder) for step in current_turn_steps)
    turn_is_substantive = len(stripped_text.strip()) > 80

    # Check 1: Ingest or Review Close. In /solo these are critical (closed-book integrity).
    if active_flow in ("ingest", "review", "solo") and ("CLERK_RECEIPT" in latest_receipts or "clerk" in invoked_subagents):
        # Once clerk has persisted state, auditor must audit writes before closing
        auditor_receipt = latest_receipts.get("AUDITOR_RECEIPT")
        solo_critical = active_flow == "solo"
        if not auditor_receipt:
            tier_block(
                "State persistence complete. You must invoke the auditor subagent "
                "(review_gate or review_session_audit) to verify writes before finishing the closing summary.",
                solo_critical,
            )
            return
        if auditor_receipt.get("verdict") == "ISSUES":
            tier_block(
                "Auditor reported issues with state or wiki writes. "
                "Fix the issues with clerk and re-audit before finalizing.",
                solo_critical,
            )
            return

    # Check 2: Handoff Writes (Lessons/, Sessions/, Pending Ingest.json) via Clerk or direct
    clerk_receipt = latest_receipts.get("CLERK_RECEIPT", {})
    clerk_handoff = clerk_receipt.get("mode") in ("lesson_handoff", "pause_handoff")
    handoff_files = [f for f in written_files if any(p in f for p in ["Learning System/Lessons/", "Learning System/Sessions/", "Pending Ingest.json"])]
    if handoff_files or clerk_handoff:
        auditor_receipt = latest_receipts.get("AUDITOR_RECEIPT")
        solo_critical = active_flow == "solo"
        if not auditor_receipt or auditor_receipt.get("mode") != "tutor_audit":
            tier_block(
                "Lesson handoff writes completed. You must invoke the auditor subagent "
                "(mode: 'tutor_audit') to verify file consistency before finishing this handoff.",
                solo_critical,
            )
            return
        if auditor_receipt.get("verdict") == "ISSUES":
            tier_block(
                "Tutor audit reported issues in handoff files. "
                "Correct the handoff files with clerk and re-audit before finishing.",
                solo_critical,
            )
            return

    # Check 3: Every-Turn Verifier Check for Teaching / Review Turns
    if active_flow in ("teach", "resume", "review", "solo") and turn_is_substantive:
        verifier_receipt = latest_receipts.get("VERIFIER_RECEIPT")
        if not verifier_receipt:
            tier_block(
                "Every-turn verification required. Before presenting teaching claims, hints, "
                "quizzes, or grades to the learner, you must invoke the verifier subagent with your proposed draft.",
                True,
            )
            return

        if verifier_receipt.get("verdict") == "ISSUES" or verifier_receipt.get("agrees") is False:
            tier_block(
                "Verifier returned ISSUES or grading disagreement "
                "(this includes spoonfeeding, cue leakage, premature synthesis, and shallow passes). "
                "You must apply the corrections and re-verify until obtaining a PASS receipt.",
                True,
            )
            return

        if verifier_receipt.get("omitted_foundations"):
            tier_block(
                "Verifier reported omitted foundational theory from the sources. "
                "Integrate the missing theoretical mechanism into your draft and re-verify.",
                True,
            )
            return

    emit("allow")


if __name__ == "__main__":
    main()
