---
name: pi-e2e
description: End-to-end test the pi learning system by acting like a learner in a sandbox. Use when the user asks to e2e/end-to-end test the learning system, to test whether an update or code change would work, to try the flows (/lesson, /review, /ingest, /show) without touching real state, or to triage a failed lpi e2e run.
---

# pi-e2e

Test the pi learning system end to end — act like a learner, in a sandbox, with real
models — without ever touching the real `~/learning-system` or `~/.pi/agent`.

This is the agent layer on top of the scripted runner. The scripted journeys
(`lpi e2e`) are the fast default; use this skill to explore, improvise, or triage
when the scripted tier is not enough.

## Model

Run this skill under a free model, in this order of preference:

1. longcat
2. mimo
3. big pickle

The pi sessions inside the sandbox still use pi's own flash models
(`glm-5.3-flash`, `deepseek-v4.1-flash`, `muse-spark-1.3-contributor`). Those are
the system under test; do not override them. Only this exploratory/judging layer
runs on a free model.

## 1. Start with the scripted tier

```bash
~/learning-pi/bin/lpi e2e --list                 # the journeys
~/learning-pi/bin/lpi e2e --diff                 # only flows touched by the git diff
~/learning-pi/bin/lpi e2e --flows lesson,review  # explicit flows
```

Read `~/.cache/learning-pi/e2e-*/summary.json` and the per-scenario `<id>.json`.
Pass means: the expected subagents ran clean, receipts appeared, no terminal
withhold.

## 2. Improvise when needed

For a bigger change, or when the scripted tier passes but you want a real pass:

1. Build a sandbox with model access (never the real agent dir):
   `S=$(~/learning-pi/harness/mk-sandbox.sh --layer ~/learning-pi --model-access | tail -1)`
2. Drive pi headless against it (RPC mode), exactly as `harness/e2e-runner.py`
   does: env `PI_CODING_AGENT_DIR=$S/agent`, `PI_CODING_AGENT_SESSION_DIR=$S/sessions`,
   cwd `$S/state`, argv `pi --mode rpc --name e2e-<tag>`.
3. Send real learner turns: `/lesson`, `/teach <topic>`, `/review`, `/ingest <text>`,
   `/show <concept>`, `/pause`, `/continue`. Wait for `agent_settled`.
4. Judge the session `.jsonl`: every gated turn must carry a real verifier receipt;
   no `⛔ WITHHELD`, `NO_REVIEW_CONTEXT`, or `NO_GRADE_AUDIT_PASS` should reach the
   learner as the final turn. Check subagent runs with
   `python3 ~/learning-pi/pi/audit_gates.py --session <file>`.
5. Remove the sandbox when done.

## 3. Report

Write a short report: what you ran, what passed, what failed, the exact banner or
receipt that failed, and whether the cause is a layer change or model turn-hygiene.
Keep failing session transcripts as evidence.

## Rules

- Never read or write `~/learning-system` or `~/.pi/agent` state. Sandbox only.
- Never edit `test/`, `contracts/`, or `CONTRACT.md` to make a journey pass — that
  is the revise door and needs the user's explicit agreement.
- A withhold is a finding, not a nuisance: report the code and the turn.
