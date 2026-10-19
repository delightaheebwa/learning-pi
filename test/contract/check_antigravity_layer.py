#!/usr/bin/env python3
"""check_antigravity_layer.py — Resource and behavioral verification for the Antigravity learning layer.

Validates:
1. Resource completeness, YAML frontmatter, and size constraints.
2. Subagent tool name validity (preventing subagent hangs) and read-only invariants.
3. Skill discovery and [[FLOW:...]] markers.
4. Behavioral unit tests for pre_tool_gate.py and stop_gate.py hooks.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FAILURES: list[str] = []


def ok(msg: str) -> None:
    print(f"PASS {msg}")


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"FAIL {msg}")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw_yaml = parts[1]
    body = parts[2]
    meta = {}
    for line in raw_yaml.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                meta[key] = items
            elif val.lower() in ("true", "false"):
                meta[key] = val.lower() == "true"
            else:
                meta[key] = val.strip("'\"")
    return meta, body


def check_resources(root: Path) -> None:
    agy = root / "antigravity"
    if not agy.is_dir():
        fail("resources: antigravity/ directory missing")
        return

    # 1. AGENTS.md
    agents_md = agy / "AGENTS.md"
    if not agents_md.is_file():
        fail("resources: antigravity/AGENTS.md missing")
    else:
        sz = agents_md.stat().st_size
        if sz > 24000:
            fail(f"resources: AGENTS.md size {sz} exceeds 24,000 bytes cap")
        else:
            ok(f"resources: AGENTS.md present ({sz} bytes <= 24,000)")

    # 2. hooks.json
    hooks_json = agy / "hooks.json"
    if not hooks_json.is_file():
        fail("resources: antigravity/hooks.json missing")
    else:
        try:
            data = json.loads(hooks_json.read_text(encoding="utf-8"))
            if "learning-write-guard" in data and "learning-turn-gate" in data:
                ok("resources: antigravity/hooks.json parses with write-guard and turn-gate")
            else:
                fail("resources: antigravity/hooks.json missing required hook entries")
        except Exception as exc:
            fail(f"resources: antigravity/hooks.json invalid JSON: {exc}")

    # 3. Subagents
    expected_agents = {"scout", "verifier", "clerk", "auditor"}
    valid_tool_names = {
        "view_file",
        "grep_search",
        "find_by_name",
        "list_dir",
        "run_command",
        "write_to_file",
        "replace_file_content",
        "read_url_content",
        "search_web",
    }
    agents_dir = agy / "agents"
    found_agents = {p.stem: p for p in agents_dir.glob("*.md")}
    missing = expected_agents - set(found_agents.keys())
    if missing:
        fail(f"resources: subagents missing: {missing}")
    else:
        ok(f"resources: all 4 subagents present: {', '.join(sorted(expected_agents))}")

    for name, path in found_agents.items():
        text = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        if meta.get("name") != name:
            fail(f"resources: subagent {name}.md frontmatter name '{meta.get('name')}' != '{name}'")
        if meta.get("subagent") is not True:
            fail(f"resources: subagent {name}.md must have 'subagent: true'")
        if meta.get("mainAgent") is not False:
            fail(f"resources: subagent {name}.md must have 'mainAgent: false'")
        if meta.get("model") != "flash":
            fail(f"resources: subagent {name}.md must specify model: flash, got '{meta.get('model')}'")
        else:
            ok(f"resources: subagent {name}.md specifies model: flash")

        # Extract tools list
        tools = []
        in_tools = False
        for line in text.split("---")[1].splitlines():
            line_s = line.strip()
            if line_s.startswith("tools:"):
                in_tools = True
                continue
            if in_tools:
                if line_s.startswith("- "):
                    tools.append(line_s[2:].strip())
                elif line_s and not line_s.startswith("#") and ":" in line_s:
                    in_tools = False

        invalid_tools = set(tools) - valid_tool_names
        if invalid_tools:
            fail(f"resources: subagent {name}.md specifies unmapped tool names: {invalid_tools}")
        else:
            ok(f"resources: subagent {name}.md tools valid ({', '.join(tools)})")

        if name in ("verifier", "auditor"):
            if "write_to_file" in tools or "replace_file_content" in tools:
                fail(f"resources: read-only subagent {name}.md must not include write tools")
            else:
                ok(f"resources: read-only subagent {name}.md has no write tools")

    # 4. Skills
    expected_skills = {
        "teach": "teach",
        "lesson": "teach",
        "continue": "resume",
        "pause": "resume",
        "review": "review",
        "solo": "solo",
        "ingest": "ingest",
        "audit": None,
        "llm-wiki": None,
    }
    skills_dir = agy / "skills"
    for name, flow in expected_skills.items():
        skill_file = skills_dir / name / "SKILL.md"
        if not skill_file.is_file():
            fail(f"resources: skill {name}/SKILL.md missing")
            continue
        text = skill_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        if meta.get("name") != name:
            fail(f"resources: skill {name} frontmatter name '{meta.get('name')}' != '{name}'")
        if not meta.get("description"):
            fail(f"resources: skill {name} missing description in frontmatter")
        if flow:
            if f"[[FLOW:{flow}]]" not in text:
                fail(f"resources: skill {name} missing [[FLOW:{flow}]] marker")
            else:
                ok(f"resources: skill {name} carries [[FLOW:{flow}]]")
        else:
            ok(f"resources: skill {name} present")

    # Pedagogy reference
    pedagogy_ref = skills_dir / "teach" / "references" / "pedagogy.md"
    if not pedagogy_ref.is_file():
        fail("resources: teach/references/pedagogy.md missing")
    else:
        ok("resources: teach/references/pedagogy.md present")

    # 5. Scripts compile
    for script_name in ("pre_tool_gate.py", "stop_gate.py"):
        sp = agy / "scripts" / script_name
        if not sp.is_file():
            fail(f"resources: scripts/{script_name} missing")
        else:
            res = subprocess.run([sys.executable, "-m", "py_compile", str(sp)], capture_output=True, text=True)
            if res.returncode != 0:
                fail(f"resources: py_compile failed for {script_name}: {res.stderr}")
            else:
                ok(f"resources: {script_name} compiles cleanly")


def run_hook(script_path: Path, payload: dict) -> dict:
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Hook exited {proc.returncode}: {proc.stderr}")
    return json.loads(proc.stdout)


def test_hook_behaviors(root: Path) -> None:
    agy = root / "antigravity"
    pre_tool_script = agy / "scripts" / "pre_tool_gate.py"
    stop_script = agy / "scripts" / "stop_gate.py"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # --- Test 1: pre_tool_gate denies write by read-only verifier ---
        transcript_verifier = tmp_path / "trans_verifier.jsonl"
        with open(transcript_verifier, "w") as f:
            f.write(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "verify"}) + "\n")
            f.write(json.dumps({"source": "MODEL", "type": "PLANNER_RESPONSE", "content": "[SUBAGENT_ROLE:verifier] start"}) + "\n")

        res = run_hook(
            pre_tool_script,
            {
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": "some/path.md"}},
                "transcriptPath": str(transcript_verifier),
            },
        )
        if res.get("decision") == "deny":
            ok("behavior: pre_tool_gate denies write_to_file for verifier subagent")
        else:
            fail(f"behavior: pre_tool_gate should deny verifier write, got {res}")

        # --- Test 2: pre_tool_gate denies Tutor writing to Learning System (pure teaching stance) ---
        transcript_tutor = tmp_path / "trans_tutor.jsonl"
        with open(transcript_tutor, "w") as f:
            f.write(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "/teach eigen"}) + "\n")
            f.write(json.dumps({"source": "MODEL", "type": "PLANNER_RESPONSE", "content": "[[FLOW:teach]] Teaching step"}) + "\n")

        res = run_hook(
            pre_tool_script,
            {
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": "/repo/Learning System/Lessons/Lesson — 1.md"}},
                "transcriptPath": str(transcript_tutor),
            },
        )
        if res.get("decision") == "deny" and "TUTOR_PURE_TEACHING" in res.get("reason", ""):
            ok("behavior: pre_tool_gate denies Tutor writing to Learning System (TUTOR_PURE_TEACHING)")
        else:
            fail(f"behavior: pre_tool_gate should deny Tutor writing lesson file, got {res}")

        # --- Test 2b: pre_tool_gate denies Tutor running ops.py attempt ---
        res = run_hook(
            pre_tool_script,
            {
                "toolCall": {"name": "run_command", "args": {"CommandLine": "python3 scripts/ops.py attempt 'concept' pass"}},
                "transcriptPath": str(transcript_tutor),
            },
        )
        if res.get("decision") == "deny" and "TUTOR_PURE_TEACHING" in res.get("reason", ""):
            ok("behavior: pre_tool_gate denies Tutor running ops.py attempt (TUTOR_PURE_TEACHING)")
        else:
            fail(f"behavior: pre_tool_gate should deny Tutor running attempt logging, got {res}")

        # --- Test 3: pre_tool_gate denies HTML widgets during solo flow ---
        transcript_solo = tmp_path / "trans_solo.jsonl"
        with open(transcript_solo, "w") as f:
            f.write(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "/solo"}) + "\n")
            f.write(json.dumps({"source": "MODEL", "type": "PLANNER_RESPONSE", "content": "[[FLOW:solo]] Review session"}) + "\n")

        res = run_hook(
            pre_tool_script,
            {
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": "/repo/artifact/widget.html"}},
                "transcriptPath": str(transcript_solo),
            },
        )
        if res.get("decision") == "deny":
            ok("behavior: pre_tool_gate denies HTML widget artifacts in /solo mode (SOLO_NO_AIDS)")
        else:
            fail(f"behavior: pre_tool_gate should deny widgets in solo mode, got {res}")

        # --- Test 4: stop_gate allows when fullyIdle=false (awaiting subagent) ---
        res = run_hook(stop_script, {"fullyIdle": False, "transcriptPath": str(transcript_tutor)})
        if res.get("decision") == "allow":
            ok("behavior: stop_gate allows yielding turn when fullyIdle=false (subagent in flight)")
        else:
            fail(f"behavior: stop_gate should allow when fullyIdle=false, got {res}")

        # --- Test 5: stop_gate blocks unverified substantive teaching turn ---
        transcript_unverified = tmp_path / "trans_unverified.jsonl"
        with open(transcript_unverified, "w") as f:
            f.write(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "next"}) + "\n")
            f.write(json.dumps({
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "[[FLOW:teach]] Here is the full derivation of eigenvalues and eigenvectors: Av = lambda v where lambda is a scalar.",
                "tool_calls": [],
            }) + "\n")

        res = run_hook(stop_script, {"fullyIdle": True, "transcriptPath": str(transcript_unverified)})
        if res.get("decision") == "continue":
            ok("behavior: stop_gate requires verifier subagent before substantive teaching turn")
        else:
            fail(f"behavior: stop_gate should continue when unverified, got {res}")

        # --- Test 6: stop_gate blocks turn with ISSUES in VERIFIER_RECEIPT ---
        transcript_issues = tmp_path / "trans_issues.jsonl"
        with open(transcript_issues, "w") as f:
            f.write(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "next"}) + "\n")
            f.write(json.dumps({
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": (
                    "[[FLOW:teach]] VERIFIER_RECEIPT: {\"mode\": \"fact_check\", \"verdict\": \"ISSUES\", \"issues\": [{\"id\": 1, \"issue\": \"Wrong sign\"}]}\n"
                    "Now presenting the updated step to the learner with complete derivations."
                ),
                "tool_calls": [],
            }) + "\n")

        res = run_hook(stop_script, {"fullyIdle": True, "transcriptPath": str(transcript_issues)})
        if res.get("decision") == "continue":
            ok("behavior: stop_gate blocks turn when verifier returns ISSUES")
        else:
            fail(f"behavior: stop_gate should continue on ISSUES, got {res}")

        # --- Test 7: stop_gate allows turn with PASS in VERIFIER_RECEIPT ---
        transcript_pass = tmp_path / "trans_pass.jsonl"
        with open(transcript_pass, "w") as f:
            f.write(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "next"}) + "\n")
            f.write(json.dumps({
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": (
                    "[[FLOW:teach]] VERIFIER_RECEIPT: {\"mode\": \"fact_check\", \"verdict\": \"PASS\", \"evidence\": [\"raw source p.12\"], \"issues\": [], \"omitted_foundations\": []}\n"
                    "Av = lambda v represents the characteristic equation. Notice how the vector direction remains invariant under transformation."
                ),
                "tool_calls": [],
            }) + "\n")

        res = run_hook(stop_script, {"fullyIdle": True, "transcriptPath": str(transcript_pass)})
        if res.get("decision") == "allow":
            ok("behavior: stop_gate allows turn when verifier returns PASS")
        else:
            fail(f"behavior: stop_gate should allow on PASS, got {res}")

        # --- Test 8: stop_gate requires tutor_audit when handoff files are written ---
        transcript_handoff = tmp_path / "trans_handoff.jsonl"
        with open(transcript_handoff, "w") as f:
            f.write(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "/pause"}) + "\n")
            f.write(json.dumps({
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "[[FLOW:resume]] Banking lesson progress...",
                "tool_calls": [{"name": "write_to_file", "args": {"TargetFile": "/repo/Learning System/Lessons/Lesson — 1.md"}}],
            }) + "\n")

        res = run_hook(stop_script, {"fullyIdle": True, "transcriptPath": str(transcript_handoff)})
        if res.get("decision") == "continue":
            ok("behavior: stop_gate requires auditor (tutor_audit) after handoff writes")
        else:
            fail(f"behavior: stop_gate should require tutor_audit on handoff writes, got {res}")

        # --- Test 8b: stop_gate requires tutor_audit when clerk completes lesson_handoff ---
        transcript_clerk_handoff = tmp_path / "trans_clerk_handoff.jsonl"
        with open(transcript_clerk_handoff, "w") as f:
            f.write(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "finish lesson"}) + "\n")
            f.write(json.dumps({
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": (
                    "[[FLOW:teach]] CLERK_RECEIPT: {\"mode\": \"lesson_handoff\", \"written_files\": [\"Learning System/Lessons/Lesson — 1.md\"], \"status\": \"done\"}\n"
                    "Lesson completed and progress saved."
                ),
                "tool_calls": [],
            }) + "\n")

        res = run_hook(stop_script, {"fullyIdle": True, "transcriptPath": str(transcript_clerk_handoff)})
        if res.get("decision") == "continue":
            ok("behavior: stop_gate requires auditor (tutor_audit) after clerk lesson_handoff receipt")
        else:
            fail(f"behavior: stop_gate should require tutor_audit on clerk handoff, got {res}")

        # --- Test 9: pre_tool_gate denies replace_file_content HTML widgets during solo flow ---
        res = run_hook(
            pre_tool_script,
            {
                "tool_call": {"name": "replace_file_content", "args": {"TargetFile": "/repo/artifact/widget.html"}},
                "transcript_path": str(transcript_solo),
            },
        )
        if res.get("decision") == "deny":
            ok("behavior: pre_tool_gate denies replace_file_content HTML widget in /solo mode (snake_case payload)")
        else:
            fail(f"behavior: pre_tool_gate should deny replace_file_content widgets in solo mode, got {res}")

        # --- Test 10: stop_gate allows when fully_idle=false (snake_case payload) ---
        res = run_hook(stop_script, {"fully_idle": False, "transcript_path": str(transcript_tutor)})
        if res.get("decision") == "allow":
            ok("behavior: stop_gate allows yielding turn when fully_idle=false (snake_case payload)")
        else:
            fail(f"behavior: stop_gate should allow when fully_idle=false, got {res}")


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(f"check_antigravity_layer: root={root}")
    check_resources(root)
    test_hook_behaviors(root)

    print()
    if FAILURES:
        print(f"check_antigravity_layer: {len(FAILURES)} FAILURE(S)")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("check_antigravity_layer: ALL CHECKS PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
