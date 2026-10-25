#!/usr/bin/env python3
"""Learning-layer contract checks (offline, no pi).

Two jobs:
  1. Resources: the layer's own files exist and parse — APPEND_SYSTEM.md,
      .pi/settings.json, the eight prompt templates with their [[FLOW:...]]
      markers, the agent definitions, the five skills.
   2. Contract coverage: every invariant in contracts/learning-core.json has at
      least one passing test (by name substring), and every listed test name
      matches something. This keeps the contract registry and the tests from
      drifting apart.

Passing tests are collected from every test-output file given on the command
line: each `PASS <name>` line is a passing test. The deno gate suites and the
bridge unittest runner (`test/bridge/run_tests.py`) both emit that shape, so one
checker binds both corpora.

Usage:
    python3 test/contract/check_learning_layer.py LAYER_ROOT OUTPUT [OUTPUT ...]
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
    "solo": "solo",
    "audit": None,
}
EXPECTED_AGENTS = {
    "scout",
    "scout-audit",
    "clerk",
    "review-scout",
    "review-clerk",
    "fact-check",
    "quiz-audit",
    "grade-audit",
    "tutor-audit",
    "review-gate",
    "review-session-audit",
    "ui-audit",
    "naive-student",
    "graph-extract",
    "graph-audit",
}
EXPECTED_SKILLS = {"learning-system", "learning-teach", "learning-review", "llm-wiki", "openui"}

FAILURES: list[str] = []
# Every resource-level `PASS` becomes part of the contract-coverage corpus, so
# a verifier-rule invariant can bind to a resource check as well as a behavior
# suite (the resource files carry the fixed verifier prompts).
RESOURCE_PASSES: list[str] = []


def ok(msg: str) -> None:
    RESOURCE_PASSES.append(msg)
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

    # Regression guard: verifier/worker dispatches go through the `dispatch`
    # helper, whose `task` is the envelope OBJECT. pi-subagents' own `subagent`
    # tool requires `task` to be a JSON *string*; an object fails validation
    # with `task: must be string`, launches no child, and mints no receipt (the
    # 2026-09-26 and 2026-10-05 sessions dead-ended on exactly this). No
    # prompt/skill/APPEND_SYSTEM resource may spell a `subagent(` call — that
    # primes the model to emit the invalid string-escaped shape.
    import re

    dispatch_docs = [
        root / ".pi" / "APPEND_SYSTEM.md",
        *sorted((root / ".pi" / "skills").glob("*/SKILL.md")),
        *sorted((root / ".pi" / "prompts").glob("*.md")),
    ]
    subagent_call_re = re.compile(r"\bsubagent\s*\(\s*\{")
    offenders = [
        p.relative_to(root).as_posix()
        for p in dispatch_docs
        if p.is_file() and subagent_call_re.search(p.read_text(encoding="utf-8", errors="replace"))
    ]
    if offenders:
        fail(
            "resources: dispatch examples must use the `dispatch` helper (object `task`), "
            "never a `subagent(` call: " + ", ".join(offenders)
        )
    else:
        ok("resources: dispatch examples use the `dispatch` helper with an object `task`")

    # Regression guard: the model judge scores a PASS "none" (unsubstantiated)
    # when the verifier shows no evidence. Verifiers whose clean verdict is an
    # empty `issues:[]` must therefore emit a mandatory `evidence` list, or every
    # clean PASS dead-ends as *_STALE (the 2026-10-05 session looped on it).
    evidence_agents = ["quiz-audit", "tutor-audit", "review-gate", "review-session-audit", "scout-audit", "ui-audit"]
    missing_evidence = [
        name
        for name in evidence_agents
        if not re.search(r"\bevidence\b", (root / ".pi" / "agents" / f"{name}.md").read_text(encoding="utf-8", errors="replace"))
    ]
    if missing_evidence:
        fail(
            "resources: verifier agents with an empty-PASS contract must require an `evidence` "
            "list: " + ", ".join(missing_evidence)
        )
    else:
        ok(f"resources: {len(evidence_agents)} verifier agents require an `evidence` list")

    # --- Interrogation-layer resource contract -----------------------------
    # The stance and flow live in the prompt resources; the fixed verifier
    # prompts live in the agent files. These named checks bind the
    # interrogation invariants to the files that actually encode the behavior.
    agents_md = (root / ".pi" / "APPEND_SYSTEM.md").read_text(encoding="utf-8", errors="replace")
    stance_needles = (
        "sparring partner",
        "never teach a topic cold",
        "Closed-book spine check",
        "Triage",
        "Targeted attacks",
        "Predict-Before-Render",
        "naive-student",
    )
    missing_stance = [n for n in stance_needles if n.lower() not in agents_md.lower()]
    if missing_stance:
        fail(f"resources: APPEND_SYSTEM.md missing interrogation-stance rule(s): {missing_stance}")
    else:
        ok("resources: APPEND_SYSTEM.md encodes the interrogation stance (spine check, triage, attacks, clone, Predict-Before-Render)")

    teach_text = (root / ".pi" / "skills" / "learning-teach" / "SKILL.md").read_text(
        encoding="utf-8", errors="replace"
    )
    teach_needles = (
        "Entry gate",
        "Closed-book spine check",
        "Triage",
        "Targeted attacks",
        "Model patch",
        "naive-student",
    )
    missing_teach = [n for n in teach_needles if n.lower() not in teach_text.lower()]
    if missing_teach:
        fail(f"resources: learning-teach/SKILL.md missing interrogation step(s): {missing_teach}")
    else:
        ok("resources: learning-teach runs entry gate -> spine check -> triage -> attacks -> model patch/clone")

    for stale in ("probe → plan → teach", "Mini-checkpoint pause protocol", "elicit → attempt → state"):
        if stale.lower() in teach_text.lower():
            fail(f"resources: learning-teach/SKILL.md still carries the retired teacher-first flow ({stale!r})")
            break
    else:
        ok("resources: learning-teach no longer carries the retired teacher-first flow")

    fact_check_text = (root / ".pi" / "agents" / "fact-check.md").read_text(
        encoding="utf-8", errors="replace"
    )
    fact_needles = (
        "MODEL_GHOSTWRITING",
        "UNGROUNDED_HOLE",
        "LECTURE_SLIP",
        "SPOONFEEDING_DETECTED",
        "CUE_LEAKAGE",
        "VISUAL_PLAN_MISSING",
        "omitted_foundations",
    )
    missing_fact = [n for n in fact_needles if n not in fact_check_text]
    if missing_fact:
        fail(f"resources: fact-check.md missing interrogation audit rule(s): {missing_fact}")
    else:
        ok("resources: fact-check audits ghostwriting, ungrounded holes, lecture slips, spoonfeeding, cue leakage, and visual sufficiency")

    grade_text = (root / ".pi" / "agents" / "grade-audit.md").read_text(
        encoding="utf-8", errors="replace"
    )
    grade_needles = ("SHALLOW_PASS", "naive_student_receipt", "trace", "false confidence")
    missing_grade = [n for n in grade_needles if n.lower() not in grade_text.lower()]
    if missing_grade:
        fail(f"resources: grade-audit.md missing interrogation grading rule(s): {missing_grade}")
    else:
        ok("resources: grade-audit grades traces, shallow passes, false confidence, and the naive-student clone")

    quiz_text = (root / ".pi" / "agents" / "quiz-audit.md").read_text(
        encoding="utf-8", errors="replace"
    )
    quiz_needles = ("MCQ legality", "Concept-label ban", "Qualitative-trace requirement")
    missing_quiz = [n for n in quiz_needles if n.lower() not in quiz_text.lower()]
    if missing_quiz:
        fail(f"resources: quiz-audit.md missing interrogation question rule(s): {missing_quiz}")
    else:
        ok("resources: quiz-audit enforces MCQ legality, the concept-label ban, and the qualitative-trace requirement")

    naive_path = root / ".pi" / "agents" / "naive-student.md"
    if not naive_path.is_file():
        fail("resources: naive-student.md missing")
    else:
        naive_text = naive_path.read_text(encoding="utf-8", errors="replace")
        naive_needles = ("NAIVE_STUDENT_RECEIPT", "task_succeeded", "learner_transcript", "read-only")
        missing_naive = [n for n in naive_needles if n.lower() not in naive_text.lower()]
        if missing_naive:
            fail(f"resources: naive-student.md missing clone-protocol field(s): {missing_naive}")
        else:
            ok("resources: naive-student runs the clone protocol and reports task_succeeded honestly")

    review_text = (root / ".pi" / "skills" / "learning-system" / "SKILL.md").read_text(
        encoding="utf-8", errors="replace"
    )
    review_needles = ("no MCQs", "qualitative trace", "mandatory question pause", "naive-student")
    missing_review = [n for n in review_needles if n.lower() not in review_text.lower()]
    if missing_review:
        fail(f"resources: learning-system review flow missing interrogation rule(s): {missing_review}")
    else:
        ok("resources: review flow is unlabeled/trace-graded, has no MCQs, pauses for questions, and runs the clone")

    # --- Knowledge-graph resource contract --------------------------------
    # The graph's pedagogy lives in two agents (extraction + independent audit)
    # and its write discipline in the Clerk. These named checks bind the
    # G-graph-* invariants to the files that actually encode the behavior.
    extract_path = root / ".pi" / "agents" / "graph-extract.md"
    extract_needles = (
        "GRAPH_CANDIDATES",
        "subject-matter propositions only",
        "no learner state",
        "provenance",
        "entailment",
    )
    if not extract_path.is_file():
        fail("resources: graph-extract.md missing")
    else:
        extract_text = extract_path.read_text(encoding="utf-8", errors="replace")
        missing_extract = [n for n in extract_needles if n.lower() not in extract_text.lower()]
        if missing_extract:
            fail(f"resources: graph-extract.md missing graph rule(s): {missing_extract}")
        else:
            ok("resources: graph agents keep learner state out")

    audit_path = root / ".pi" / "agents" / "graph-audit.md"
    audit_needles = ("LEARNER_STATE_LEAK", "entailment", "evidence", "PASS", "ISSUES")
    if not audit_path.is_file():
        fail("resources: graph-audit.md missing")
    else:
        audit_text = audit_path.read_text(encoding="utf-8", errors="replace")
        missing_audit = [n for n in audit_needles if n.lower() not in audit_text.lower()]
        if missing_audit:
            fail(f"resources: graph-audit.md missing audit rule(s): {missing_audit}")
        else:
            ok("resources: graph extraction is independently audited")

    clerk_text = (root / ".pi" / "agents" / "clerk.md").read_text(encoding="utf-8", errors="replace")
    single_writer_needles = ("graph.py merge", "never hand-edit", "CLERK_WRITES")
    missing_writer = [n for n in single_writer_needles if n.lower() not in clerk_text.lower()]
    if missing_writer:
        fail(f"resources: clerk.md missing graph single-writer rule(s): {missing_writer}")
    else:
        ok("resources: graph ledgers have a single writer")


def check_contract(root: Path, test_outputs: list[Path]) -> None:
    contract_path = root / "contracts" / "learning-core.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("contract: contracts/learning-core.json missing")
        return
    except json.JSONDecodeError as exc:
        fail(f"contract: learning-core.json invalid: {exc}")
        return

    passed: list[str] = list(RESOURCE_PASSES)
    for output in test_outputs:
        if output.is_file():
            for line in output.read_text(encoding="utf-8", errors="replace").splitlines():
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
    if len(sys.argv) < 3:
        print(
            "usage: check_learning_layer.py LAYER_ROOT OUTPUT [OUTPUT ...]",
            file=sys.stderr,
        )
        return 2
    root = Path(sys.argv[1]).resolve()
    test_outputs = [Path(arg) for arg in sys.argv[2:]]
    check_resources(root)
    check_contract(root, test_outputs)
    if FAILURES:
        print(f"\n{len(FAILURES)} learning-layer check(s) failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
