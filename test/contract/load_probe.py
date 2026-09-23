#!/usr/bin/env python3
"""Load probe — does the learning layer load under the candidate pi?

Starts pi in RPC mode against a sandbox (see harness/mk-sandbox.sh), asks for
the command list (which loads project prompts and skills), and checks that:
  - pi starts and answers,
  - the seven learning prompt templates loaded from the project overlay,
  - the `lp-load-probe` sentinel command loaded (its factory imports the real
    learning-gate and math-mode entry modules, so a broken module graph fails
    the factory and is reported on stderr),
  - no extension failed to load.

No model is called, so this is offline and fast.

Usage:
    python3 test/contract/load_probe.py --sandbox DIR --pi BIN
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

EXPECTED_PROMPTS = {"teach", "lesson", "continue", "pause", "review", "ingest", "audit"}
SENTINEL = "lp-load-probe"


def _fail(msg: str) -> None:
    print(f"FAIL load-probe: {msg}")


def run(sandbox: str, pi_bin: str, timeout: float = 40.0) -> int:
    state = os.path.join(sandbox, "state")
    agent = os.path.join(sandbox, "agent")
    sessions = os.path.join(sandbox, "sessions")
    env = dict(os.environ)
    env["PI_CODING_AGENT_DIR"] = agent
    env["PI_CODING_AGENT_SESSION_DIR"] = sessions
    env["PI_OFFLINE"] = "1"

    cmd = [pi_bin, "--mode", "rpc", "--no-session"]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=state,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    except OSError as exc:
        _fail(f"could not start pi ({pi_bin}): {exc}")
        return 1

    try:
        assert proc.stdin is not None
        proc.stdin.write(json.dumps({"id": "1", "type": "get_commands"}) + "\n")
        proc.stdin.flush()
    except (BrokenPipeError, ValueError):
        # pi exited before reading stdin — capture stderr below.
        pass

    response = None
    deadline = time.time() + timeout
    try:
        assert proc.stdout is not None
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") == "response" and obj.get("id") == "1":
                response = obj
                break
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    stderr = ""
    try:
        assert proc.stderr is not None
        stderr = proc.stderr.read()
    except Exception:
        pass

    failed = False

    if response is None:
        _fail("pi did not answer get_commands (startup failure?)")
        if stderr.strip():
            print("--- pi stderr ---")
            print(stderr.strip()[:2000])
            print("-----------------")
        return 1

    if not response.get("success"):
        _fail(f"get_commands failed: {response}")
        failed = True

    if "Failed to load extension" in stderr:
        _fail("an extension failed to load:")
        for ln in stderr.splitlines():
            if "Failed to load extension" in ln or ln.strip().startswith("Error:"):
                print(f"    {ln.strip()}")
        failed = True

    commands = (response.get("data") or {}).get("commands") or []
    by_name = {}
    for c in commands:
        if isinstance(c, dict) and isinstance(c.get("name"), str):
            by_name.setdefault(c["name"], c)

    missing_prompts = sorted(EXPECTED_PROMPTS - set(by_name))
    non_prompt = sorted(
        n for n in EXPECTED_PROMPTS if n in by_name and by_name[n].get("source") != "prompt"
    )
    if missing_prompts:
        _fail(f"prompt templates not loaded: {', '.join(missing_prompts)}")
        failed = True
    if non_prompt:
        _fail(f"expected source=prompt for: {', '.join(non_prompt)}")
        failed = True
    if SENTINEL not in by_name:
        _fail(f"sentinel command '{SENTINEL}' missing (module graph failed to load)")
        failed = True

    if not failed:
        print(f"PASS load-probe: pi answered; {len(EXPECTED_PROMPTS)} prompts + sentinel loaded; no load errors")
        return 0
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("--pi", required=True)
    args = ap.parse_args()
    return run(args.sandbox, args.pi)


if __name__ == "__main__":
    raise SystemExit(main())
