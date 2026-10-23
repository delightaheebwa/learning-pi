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
5. Widget integrity: every raw <agent-embed> in the learner-facing text must be bound
   to a passing ui_audit receipt for the same absolute file and the file's current
   SHA-256. /solo may never render one. This check is a hard block (no fail-open
   tier): an unaudited widget or a closed-book aid must never ship.
"""
import hashlib
import json
import os
import re
import sys

SCHEMA_CAP = 2
# A rendered widget is a raw <agent-embed src="file:///absolute/path"> tag.
EMBED_TAG_RE = re.compile(r"<agent-embed\b[^>]*>", re.IGNORECASE)
EMBED_SRC_RE = re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
CRITICAL_CAP = 6
# Longest-first: "REVIEW_SCOUT_RECEIPT:" contains "SCOUT_RECEIPT:" as a substring,
# so matching order matters to avoid aliasing.
RECEIPT_NAMES = [
    "UI_GENERATOR_RECEIPT",
    "NAIVE_STUDENT_RECEIPT",
    "REVIEW_SCOUT_RECEIPT",
    "VERIFIER_RECEIPT",
    "AUDITOR_RECEIPT",
    "SCOUT_RECEIPT",
    "CLERK_RECEIPT",
]
# Receipt that marks the END of a subagent run (tutor resumes on wakeup)
ROLE_RECEIPT = {
    "verifier": "VERIFIER_RECEIPT",
    "auditor": "AUDITOR_RECEIPT",
    "naive-student": "NAIVE_STUDENT_RECEIPT",
    "scout": "SCOUT_RECEIPT",
    "clerk": "CLERK_RECEIPT",
    "ui-generator": "UI_GENERATOR_RECEIPT",
}


def emit(decision, reason=None):
    payload = {"decision": decision}
    if reason:
        payload["reason"] = reason
    print(json.dumps(payload))


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


def detect_subagents_in_call(name, args, invoked_subagents):
    if name == "invoke_subagent":
        type_name = get_arg(args, "TypeName", "typeName", "type_name")
        if type_name:
            invoked_subagents.add(type_name)
        subagents = get_arg(args, "Subagents", "subagents") or []
        for sa in subagents:
            if isinstance(sa, dict):
                sa_type = get_arg(sa, "TypeName", "typeName", "type_name")
                if sa_type:
                    invoked_subagents.add(sa_type)


def collect_receipts(content, latest_receipts, all_receipts, decoder, step_index):
    """Parse receipt JSON objects out of a step's text: keep the latest per name
    for gate checks, and every occurrence (name, obj, order key) for retry
    accounting and phase ordering. The order key is (step index, text offset) so
    receipts inside one step keep their textual order."""
    for receipt_name in RECEIPT_NAMES:
        marker = f"{receipt_name}:"
        idx = content.find(marker)
        while idx != -1:
            brace_idx = content.find("{", idx + len(marker))
            if brace_idx != -1:
                try:
                    obj, end_pos = decoder.raw_decode(content[brace_idx:])
                    latest_receipts[receipt_name] = obj
                    all_receipts.append((receipt_name, obj, (step_index, brace_idx)))
                    idx = content.find(marker, brace_idx + end_pos)
                    continue
                except Exception:
                    pass
            idx = content.find(marker, idx + len(marker))


def collect_transcript_receipts(steps, decoder):
    """Collect every receipt in the transcript in textual order. Used for cross-turn
    binding: a widget audited once stays audited while its file and SHA are unchanged."""
    receipts = []
    for step_index, step in enumerate(steps):
        # Ignore tool output: a file read or grep that happens to contain receipt
        # text must not be able to bind a widget to a passing audit.
        if step.get("type") == "GENERIC":
            continue
        collect_receipts(str(step.get("content", "")), {}, receipts, decoder, step_index)
    return receipts


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
    """State machine over the transcript: subagent runs are 'active' at the END of
    the transcript if their invocations have not yet been closed by their receipts.
    Used to exempt a Stop event that belongs to a subagent's own turn. Tracked as a
    LIFO stack (pop-most-recent) so duplicate same-role parallel dispatches each
    close with their own receipt."""
    active = []
    for step in steps:
        for tc in step.get("tool_calls", []) or []:
            called = set()
            detect_subagents_in_call(tc.get("name", ""), tc.get("args", {}) or {}, called)
            active.extend(role for role in called if role in ROLE_RECEIPT)
        content = str(step.get("content", ""))
        # A role-marked output step (re)opens that subagent's run...
        for role, receipt in ROLE_RECEIPT.items():
            if f"[SUBAGENT_ROLE:{role}]" in content:
                active.append(role)
        # ...and each role's own receipt closes the most recent run of that role.
        for role, receipt in ROLE_RECEIPT.items():
            if role in active and receipt + ":" in content:
                for i in range(len(active) - 1, -1, -1):
                    if active[i] == role:
                        active.pop(i)
                        break
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

    # Identify active learning flow: LAST marker in the transcript, matched the same
    # way pre_tool_gate does (so the two hooks never disagree on solo-ness).
    active_flow = None
    for step in steps:
        if step.get("type") == "GENERIC":
            continue
        content = str(step.get("content", "") + "\n" + str(step.get("thinking", "")))
        matches = re.findall(r"\[\[FLOW:([A-Za-z]+)\]\]", content)
        if matches:
            active_flow = matches[-1].lower()

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
    all_receipts = []

    for step_index, step in enumerate(current_turn_steps):
        for tc in step.get("tool_calls", []) or []:
            detect_subagents_in_call(tc.get("name", ""), tc.get("args", {}) or {}, invoked_subagents)
            name = tc.get("name", "")
            if name in ("write_to_file", "replace_file_content"):
                tf = (tc.get("args", {}) or {}).get("TargetFile", "")
                if tf:
                    written_files.add(tf)

        # Tool output is never a receipt: file contents must not mint a PASS.
        if step.get("type") != "GENERIC":
            collect_receipts(str(step.get("content", "")), latest_receipts, all_receipts, decoder, step_index)

    # Receipts are appended per receipt name inside a step, so sort by their
    # textual position to keep phase ordering (clerk before/after auditor) honest.
    all_receipts.sort(key=lambda receipt: receipt[2])

    # Retry accounting. Hook "continue" reasons may or may not persist as transcript
    # steps, so count BOTH explicit GATE markers and unresolved ISSUES receipts
    # (parsed, so receipts split across steps still count):
    # each ISSUES verifier receipt counts as a critical retry; each ISSUES auditor
    # receipt counts as a schema retry — except in /solo, where the whole close is
    # critical-tier (closed-book integrity).
    marker_critical = sum(1 for s in current_turn_steps if "GATE-CRIT:" in str(s.get("content", "")))
    marker_schema = sum(
        1 for s in current_turn_steps
        if "GATE:" in str(s.get("content", "")) and "GATE-CRIT:" not in str(s.get("content", ""))
    )
    verifier_issues = sum(1 for name, obj, _order in all_receipts if name == "VERIFIER_RECEIPT" and obj.get("verdict") == "ISSUES")
    auditor_issues = sum(1 for name, obj, _order in all_receipts if name == "AUDITOR_RECEIPT" and obj.get("verdict") == "ISSUES")
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
    stripped_text = "\n".join(
        strip_receipts(str(step.get("content", "")), decoder)
        for step in current_turn_steps
        if step.get("type") == "PLANNER_RESPONSE"
    )
    turn_is_substantive = len(stripped_text.strip()) > 80

    # Check 0: Interactive widget integrity. Every <agent-embed> in the learner-facing
    # text must be bound to a passing ui_audit receipt for the same absolute file and
    # the file's current SHA-256. /solo may never render a widget at all. This is a
    # hard block (no retry tier): an unaudited executable widget or a closed-book aid
    # must never ship, so there is nothing safe to fail open to.
    embed_tags = EMBED_TAG_RE.findall(stripped_text)
    if embed_tags:
        if active_flow == "solo":
            emit(
                "continue",
                "SOLO_NO_AIDS: this turn renders an interactive widget, but /solo is closed-book. "
                "Remove the <agent-embed> and every interactive aid; solo turns are text-only questions.",
            )
            return

        embed_paths = []
        for tag in embed_tags:
            src_match = EMBED_SRC_RE.search(tag)
            src = src_match.group(1) if src_match else ""
            if not src.startswith("file:///") or any(c in src for c in ('"', "'", "<", ">")):
                emit(
                    "continue",
                    "UI_AUDIT_REQUIRED: <agent-embed> must use exactly one absolute "
                    'src="file:///..."> attribute pointing at an audited artifact. '
                    f"Got: {tag}",
                )
                return
            embed_paths.append(os.path.realpath(src[len("file://"):]))

        transcript_receipts = collect_transcript_receipts(steps, decoder)
        ui_audits = [
            obj
            for name, obj, _order in transcript_receipts
            if name == "VERIFIER_RECEIPT"
            and obj.get("mode") == "ui_audit"
            and obj.get("verdict") == "PASS"
        ]
        for path in embed_paths:
            try:
                with open(path, "rb") as fh:
                    digest = hashlib.sha256(fh.read()).hexdigest()
            except OSError:
                emit(
                    "continue",
                    f"UI_AUDIT_REQUIRED: <agent-embed> points at '{path}', which is not readable. "
                    "Write the widget into the conversation artifact directory, audit it, then embed the audited file.",
                )
                return

            bound = any(
                os.path.realpath(str(obj.get("widget_file", ""))) == path
                and str(obj.get("widget_sha256", "")).lower() == digest
                for obj in ui_audits
            )
            if not bound:
                emit(
                    "continue",
                    "UI_AUDIT_REQUIRED: every <agent-embed> must be bound to a passing ui_audit receipt for "
                    f"the same file and hash ({path}). Dispatch verifier (mode: 'ui_audit', widget_file: ..., "
                    "prose_draft: <the exact turn>) and emit only after PASS; re-audit if the file changed. "
                    "If the widget cannot pass, fall back to a Mermaid diagram.",
                )
                return

    # Check 1: Clerk persistence requires a matching auditor AFTER it.
    # Ingest is gated in every flow (teach/resume ingest inline at lesson end);
    # review_close is gated in ingest/review/solo. Ordering matters: an auditor
    # receipt from an earlier phase must not satisfy a later clerk write.
    clerk_receipts = [(i, obj) for i, (name, obj, _order) in enumerate(all_receipts) if name == "CLERK_RECEIPT"]
    last_clerk_idx, last_clerk = clerk_receipts[-1] if clerk_receipts else (-1, {})
    clerk_mode = last_clerk.get("mode", "")
    clerk_gated = (
        clerk_mode == "ingest"
        or (clerk_mode in ("", "review_close") and active_flow in ("ingest", "review", "solo"))
    )
    if clerk_gated:
        expected_audit_mode = "review_gate" if clerk_mode == "ingest" else "review_session_audit"
        auditor_after = [
            obj for i, (name, obj, _order) in enumerate(all_receipts)
            if i > last_clerk_idx
            and name == "AUDITOR_RECEIPT"
            and obj.get("mode") == expected_audit_mode
        ]
        solo_critical = active_flow == "solo"
        if not auditor_after:
            tier_block(
                f"State persistence via clerk ({clerk_mode}) complete. You must invoke the auditor "
                f"subagent (mode: '{expected_audit_mode}') to verify the writes before finishing the closing summary.",
                solo_critical,
            )
            return
        if auditor_after[-1].get("verdict") == "ISSUES":
            tier_block(
                "Auditor reported issues with state or wiki writes. "
                "Fix the issues with clerk and re-audit before finalizing.",
                solo_critical,
            )
            return
    elif "clerk" in invoked_subagents and not clerk_receipts:
        # Clerk was dispatched but returned no receipt (failed or hung).
        tier_block(
            "Clerk was invoked but no CLERK_RECEIPT was returned. Wait for clerk or re-dispatch it before finishing.",
            active_flow == "solo",
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
