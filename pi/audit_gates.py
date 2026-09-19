#!/usr/bin/env python3
"""
audit_gates.py — read-only provenance audit for the learning-system verification gates.

The learning-gate extension decides, live, whether a turn's verdict marker came from a
real verifier run. This script reconstructs that from the session artifacts *after the
fact*: it correlates every `subagent` dispatch in a pi session transcript with the
subagent artifact metadata (`subagent-artifacts/<runId>_<agent>_meta.json`) that the
pi-subagents runtime wrote, and reports where a claimed verdict has no backing run, where
a run failed, or where the harness acceptance layer disagreed with the gate.

It never writes. It is a diagnostic, not an enforcement layer.

Usage:
    python3 audit_gates.py [--session PATH] [--root DIR] [--json]

Resolution:
    --session  explicit pi session .jsonl file
    --root     session directory to scan (default: the learning-system session dir,
               else ~/.pi/agent/sessions/--home-delight-learning-system--)
    default session = the newest top-level *.jsonl in the session directory.

Exit status: 0 when no findings, 1 when any finding is reported.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_SESSION_DIRS = [
    "~/.pi/agent/sessions/--home-delight-learning-system--",
    "~/.pi/agent/sessions/--home-delight-learning--",
]

# Verifier agents whose receipt must map to a real subagent run.
VERIFIER_AGENTS = {
    "fact-check",
    "quiz-audit",
    "grade-audit",
    "review-gate",
    "tutor-audit",
    "review-session-audit",
}
# Agents that write/act rather than verify; tracked for provenance but not "verifiers".
WORKER_AGENTS = {"scout", "clerk"}

RUNID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
REVIEW_MARKER_RE = re.compile(r"REVIEW_GATE_VERDICT\s*:\s*(\{.*?\})", re.S)
STATE_MARKER_RE = re.compile(r'STATE_AUDIT_VERDICT\s*:\s*\{\s*"errors"\s*:\s*\d+\s*,\s*"warnings"\s*:\s*\d+')
AUDIT_CMD_RE = re.compile(r"audit_state\.py")

findings: list[dict] = []
runs: list[dict] = []


def finding(level: str, code: str, message: str, **extra) -> None:
    findings.append({"level": level, "code": code, "message": message, **extra})


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def text_of_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                if isinstance(p.get("text"), str):
                    parts.append(p["text"])
                elif p.get("type") == "toolCall" or p.get("type") == "tool_use":
                    parts.append(json.dumps(p.get("arguments", p.get("input", {}))))
        return "\n".join(parts)
    return ""


def load_session(path: Path):
    """Return (records, tool_calls_by_id, tool_results, all_text, model_changes)."""
    records = []
    tool_calls: dict[str, dict] = {}
    tool_results: list[dict] = []
    model_changes: list[dict] = []
    texts: list[str] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            records.append(rec)
            t = rec.get("type")
            if t == "model_change":
                model_changes.append(rec)
            if t == "message":
                m = rec.get("message", {})
                role = m.get("role")
                if role == "assistant":
                    for b in m.get("content", []) or []:
                        if isinstance(b, dict) and b.get("type") in ("toolCall", "tool_use"):
                            cid = b.get("id")
                            if cid:
                                tool_calls[cid] = {
                                    "name": b.get("name"),
                                    "arguments": b.get("arguments", b.get("input", {})),
                                }
                    texts.append(text_of_content(m.get("content")))
                elif role == "toolResult":
                    tool_results.append(m)
                elif role == "user":
                    texts.append(text_of_content(m.get("content")))
            elif t == "custom_message":
                texts.append(text_of_content(rec.get("content", rec.get("message", ""))))
    return records, tool_calls, tool_results, "\n".join(texts), model_changes


def discover_artifacts(session_dir: Path) -> dict[str, dict]:
    """Map runId -> merged meta across every *_meta.json under the session dir."""
    artifacts: dict[str, dict] = {}
    for p in session_dir.rglob("*_meta.json"):
        d = read_json(p)
        if not isinstance(d, dict):
            continue
        rid = d.get("runId")
        if not rid:
            continue
        d["_path"] = str(p)
        artifacts[rid] = d
    return artifacts


def dispatched_runs(tool_calls: dict, tool_results: list) -> list[dict]:
    """Correlate subagent tool calls with their results to enumerate dispatched runs."""
    out: list[dict] = []
    for res in tool_results:
        if res.get("toolName") != "subagent":
            continue
        cid = res.get("toolCallId")
        call = tool_calls.get(cid, {})
        args = call.get("arguments", {}) if isinstance(call.get("arguments"), dict) else {}
        details = res.get("details") if isinstance(res.get("details"), dict) else {}
        mode = details.get("mode")
        agents: list[str] = []
        if isinstance(args.get("agent"), str):
            agents.append(args["agent"])
        for t in (args.get("tasks") or []):
            if isinstance(t, dict) and isinstance(t.get("agent"), str):
                agents.append(t["agent"])
        # workflow script agents
        script = args.get("workflowScript") if isinstance(args.get("workflowScript"), str) else ""
        if script:
            for m in re.finditer(r"\bagent\s*:\s*[\"']([\w.-]+)[\"']", script):
                agents.append(m.group(1))

        rid = details.get("runId")
        if not rid:
            # async result text may carry `Async: agent [runid]` in content
            ctext = text_of_content(res.get("content"))
            mm = re.search(r"Async:\s*[\w-]+\s*\[([0-9a-f-]{36})\]", ctext)
            if mm:
                rid = mm.group(1)
        if not rid:
            for m in RUNID_RE.findall(text_of_content(res.get("content"))):
                rid = m
                break
        results = details.get("results") if isinstance(details.get("results"), list) else []
        for r in results:
            if isinstance(r, dict) and r.get("agent"):
                agents.append(r["agent"])
                if r.get("runId"):
                    rid = r["runId"]
        is_launch = bool(
            args.get("task")
            or args.get("prompt")
            or args.get("workflowScript")
            or args.get("tasks")
        )
        out.append({
            "toolCallId": cid,
            "mode": mode,
            "agents": sorted(set(a for a in agents if a)),
            "runId": rid,
            "isError": bool(res.get("isError")),
            "isLaunch": is_launch,
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Provenance audit for learning-system verifier runs.")
    ap.add_argument("--session", help="explicit pi session .jsonl")
    ap.add_argument("--root", help="session directory to scan")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args()

    root = Path(args.root).expanduser() if args.root else None
    session = Path(args.session).expanduser() if args.session else None

    if session is None:
        if root is None:
            for cand in DEFAULT_SESSION_DIRS:
                p = Path(cand).expanduser()
                if p.is_dir():
                    root = p
                    break
        if root is None or not root.is_dir():
            print("error: no session directory found (pass --root or --session)", file=sys.stderr)
            return 2
        candidates = sorted(
            (p for p in root.glob("*.jsonl")),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            print(f"error: no session .jsonl in {root}", file=sys.stderr)
            return 2
        session = candidates[0]
    else:
        root = session.parent

    artifacts = discover_artifacts(root)
    records, tool_calls, tool_results, all_text, model_changes = load_session(session)
    dispatches = dispatched_runs(tool_calls, tool_results)

    parent_models = [rec.get("modelId") for rec in model_changes if rec.get("modelId")]
    parent_model = parent_models[-1] if parent_models else None

    # ---- per-run provenance ----
    for d in dispatches:
        agents = d["agents"]
        if not agents:
            if d.get("isLaunch") and d.get("toolCallId"):
                finding("warn", "dispatch-no-agent",
                        "a subagent launch carried no string `agent` field (mints no receipt)")
            continue
        rid = d.get("runId")
        meta = artifacts.get(rid) if rid else None
        for agent in agents:
            if agent in VERIFIER_AGENTS or agent in WORKER_AGENTS:
                runs.append({
                    "agent": agent,
                    "runId": rid,
                    "model": (meta or {}).get("model"),
                    "requestedModel": (meta or {}).get("requestedModel"),
                    "exitCode": (meta or {}).get("exitCode"),
                    "acceptance": ((meta or {}).get("acceptance") or {}).get("status"),
                    "runError": d.get("isError"),
                })
        if not rid:
            finding("warn", "dispatch-runid-unresolved",
                    f"could not resolve a runId for dispatch of {agents}",
                    agents=agents)
            continue
        if meta is None:
            finding("error", "dispatch-without-artifact",
                    f"dispatch of {agents} (run {rid}) has no artifact meta under {root}",
                    runId=rid, agents=agents)
            continue
        if meta.get("exitCode") not in (0, None):
            finding("error", "run-failed",
                    f"{meta.get('agent')} run {rid} exited {meta.get('exitCode')}",
                    runId=rid, agent=meta.get("agent"))
        acc = ((meta.get("acceptance") or {}).get("status"))
        if acc == "rejected":
            finding("warn", "harness-acceptance-rejected",
                    f"{meta.get('agent')} run {rid} was REJECTED by the harness acceptance layer "
                    f"(gate may still have consumed its verdict)",
                    runId=rid, agent=meta.get("agent"))

    # ---- verdict-marker provenance ----
    review_markers = REVIEW_MARKER_RE.findall(all_text)
    if review_markers:
        review_gate_runs = [r for r in runs if r["agent"] == "review-gate"]
        clerk_runs = [r for r in runs if r["agent"] == "clerk"]
        # Nested review-gates (clerk self-dispatch) live only in artifacts, not this
        # session; scope them to this session's own run directory (session.stem).
        stem = session.stem
        nested_review = [
            a for a in artifacts.values()
            if a.get("agent") == "review-gate" and stem in a.get("_path", "")
        ]
        if not review_gate_runs and not nested_review and not clerk_runs:
            finding("error", "review-verdict-unbacked",
                    f"{len(review_markers)} REVIEW_GATE_VERDICT marker(s) present but no review-gate "
                    "run is recorded in this session tree")
        elif not review_gate_runs and nested_review:
            finding("info", "review-verdict-clerk-nested",
                    f"{len(review_markers)} REVIEW_GATE_VERDICT marker(s) backed by a clerk-nested "
                    f"review-gate ({len(nested_review)} run(s)) — provenance is clerk-relayed")
        elif not review_gate_runs and clerk_runs:
            finding("warn", "review-verdict-clerk-only",
                    f"{len(review_markers)} REVIEW_GATE_VERDICT marker(s) but the only related runs "
                    "are clerk runs — possible self-attestation")

    if STATE_MARKER_RE.search(all_text):
        bash_results = [r for r in tool_results if r.get("toolName") == "bash"]
        ran_audit = any(AUDIT_CMD_RE.search(text_of_content(r.get("content"))) for r in bash_results)
        # also check subagent transcripts for the audit command
        if not ran_audit:
            for meta in artifacts.values():
                tp = meta.get("transcriptPath")
                if tp and Path(tp).exists():
                    try:
                        if AUDIT_CMD_RE.search(Path(tp).read_text(encoding="utf-8", errors="ignore")):
                            ran_audit = True
                            break
                    except Exception:
                        pass
        if not ran_audit:
            finding("warn", "state-verdict-unbound",
                    "STATE_AUDIT_VERDICT marker present but no audit_state.py invocation found "
                    "in this session tree")

    # ---- report ----
    if args.json:
        print(json.dumps({
            "session": str(session),
            "parentModel": parent_model,
            "runs": runs,
            "findings": findings,
        }, indent=2))
    else:
        print(f"audit_gates — session: {session.name}")
        print(f"parent model: {parent_model}\n")
        if runs:
            print("verifier/worker runs:")
            for r in runs:
                rid = (r["runId"] or "?")[:8]
                acc = r["acceptance"] or "-"
                print(f"  {r['agent']:20} {rid}  model={r['model'] or '?':42} "
                      f"exit={r['exitCode']} accept={acc}")
        else:
            print("verifier/worker runs: (none)")
        print()
        errors = [f for f in findings if f["level"] == "error"]
        warns = [f for f in findings if f["level"] == "warn"]
        infos = [f for f in findings if f["level"] == "info"]
        for f in findings:
            icon = {"error": "❌", "warn": "⚠️ ", "info": "ℹ️ "}.get(f["level"], "•")
            print(f"{icon} [{f['code']}] {f['message']}")
        if not findings:
            print("✅ no provenance findings")
        print(f"\n{len(errors)} error(s), {len(warns)} warning(s), {len(infos)} info")

    return 1 if any(f["level"] == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
