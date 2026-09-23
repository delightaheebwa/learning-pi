#!/usr/bin/env python3
"""Learning-layer contract checks (offline, no pi).

Two jobs:
  1. Resources: the layer's own files exist and parse — APPEND_SYSTEM.md,
     .pi/settings.json, the seven prompt templates with their [[FLOW:...]]
     markers, the eight agent definitions, the four skills.
  2. Contract coverage: every invariant in contracts/learning-core.json has at
     least one passing test (by name substring), and every listed test name
     matches something. This keeps the contract registry and the tests from
     drifting apart.

Usage:
    python3 test/contract/check_learning_layer.py LAYER_ROOT GATE_TEST_OUTPUT
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# prompt template -> expected [[FLOW:...]] marker (None = not a gated flow)
EXPECTED_PROMPTS = {
    "teach": "teach",
    "lesson": "teach",
    "continue": "resume",
    "pause": "resume",
    "review": "review",
    "ingest": "ingest",
    "audit": None,
}
EXPECTED_AGENTS = {
    "scout",
    "clerk",
    "fact-check",
    "quiz-audit",
    "grade-audit",
    "tutor-audit",
    "review-gate",
    "review-session-audit",
}
EXPECTED_SKILLS = {"learning-system", "learning-teach", "learning-review", "llm-wiki"}

FAILURES: list[str] = []


def ok(msg: str) -> None:
    print(f"PASS {msg}")


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"FAIL {msg}")


def check_resources(root: Path) -> None:
    if (root / ".pi" / "APPEND_SYSTEM.md").is_file():
        ok("resources: APPEND_SYSTEM.md present")
    else:
        fail("resources: .pi/APPEND_SYSTEM.md missing")

    settings_path = root / ".pi" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        ok("resources: .pi/settings.json parses")
        if "defaultModel" in settings and not isinstance(settings["defaultModel"], str):
            fail("resources: settings.defaultModel must be a string")
        if "subagents" in settings and not isinstance(settings["subagents"], dict):
            fail("resources: settings.subagents must be an object")
    except FileNotFoundError:
        fail("resources: .pi/settings.json missing")
    except json.JSONDecodeError as exc:
        fail(f"resources: .pi/settings.json invalid JSON: {exc}")

    for name, flow in EXPECTED_PROMPTS.items():
        p = root / ".pi" / "prompts" / f"{name}.md"
        if not p.is_file():
            fail(f"resources: prompt {name}.md missing")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if flow is None:
            ok(f"resources: prompt {name}.md present")
            continue
        import re

        m = re.search(r"\[\[FLOW:([a-z]+)\]\]", text)
        if not m:
            fail(f"resources: prompt {name}.md has no [[FLOW:...]] marker")
        elif m.group(1) != flow:
            fail(f"resources: prompt {name}.md FLOW is '{m.group(1)}', expected '{flow}'")
        else:
            ok(f"resources: prompt {name}.md carries [[FLOW:{flow}]]")

    agents = {p.stem for p in (root / ".pi" / "agents").glob("*.md")}
    missing = EXPECTED_AGENTS - agents
    if missing:
        fail(f"resources: agent definitions missing: {', '.join(sorted(missing))}")
    else:
        ok(f"resources: {len(EXPECTED_AGENTS)} agent definitions present")

    skills = {p.parent.name for p in (root / ".pi" / "skills").glob("*/SKILL.md")}
    missing = EXPECTED_SKILLS - skills
    if missing:
        fail(f"resources: skill files missing: {', '.join(sorted(missing))}")
    else:
        ok(f"resources: {len(EXPECTED_SKILLS)} skills present")


def check_contract(root: Path, gate_output: Path) -> None:
    contract_path = root / "contracts" / "learning-core.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("contract: contracts/learning-core.json missing")
        return
    except json.JSONDecodeError as exc:
        fail(f"contract: learning-core.json invalid: {exc}")
        return

    passed: list[str] = []
    if gate_output.is_file():
        for line in gate_output.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("PASS "):
                passed.append(line[len("PASS ") :].strip())

    invariants = contract.get("invariants") or []
    for inv in invariants:
        iid = inv.get("id", "?")
        tests = inv.get("tests") or []
        matched = [t for t in tests if any(t in name for name in passed)]
        if not matched:
            fail(f"contract: {iid} has no passing test (expected one of: {tests})")
        else:
            ok(f"contract: {iid} covered by {len(matched)} test(s)")

        for t in tests:
            if not any(t in name for name in passed):
                fail(f"contract: {iid} lists test '{t}' but no PASS matched it")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_learning_layer.py LAYER_ROOT GATE_TEST_OUTPUT", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    gate_output = Path(sys.argv[2])
    check_resources(root)
    check_contract(root, gate_output)
    if FAILURES:
        print(f"\n{len(FAILURES)} learning-layer check(s) failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
