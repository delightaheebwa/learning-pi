#!/usr/bin/env python3
"""e2e-runner — replay short learner journeys against a sandboxed pi.

This is the end-to-end companion to `learn-check`. Where `learn-check` proves
the layer loads and the gate logic is sound, this runner *acts like a learner*:
it sends real slash-command flows (`/teach`, `/review`, `/ingest`, `/show`,
`/audit`) to a candidate pi in an isolated sandbox, lets the real Tutor and its
subagents run with the real models, then inspects the session transcript.

Assertions are structural, not prose: expected worker/verifier subagent runs
must exist and finish clean, certain receipts must appear, and no turn may be
withheld (`⛔ WITHHELD`, `NO_REVIEW_CONTEXT`, `NO_GRADE_AUDIT_PASS`, ...).

The sandbox never touches the real ~/learning-system or ~/.pi/agent (CONTRACT
S-2). Model access (auth, model catalog, pinned packages) is reachable read-only
through `mk-sandbox.sh --model-access`.

Usage:
    python3 harness/e2e-runner.py [options]
      --scenario ID          run only this scenario (repeatable; also comma list)
      --tier smoke|full      filter by tier (default: all)
      --flows a,b            filter by flow
      --diff [--base REF]    select flows affected by the git diff (layer + learning-system)
      --jobs N               run N scenarios concurrently (default: 1)
      --retries N            retry a failed scenario in a fresh sandbox (default: 1)
      --list                 list scenarios and exit
    Tiers: smoke (fast, early-stop) and full (run to settle). Default: all.
      --pi BIN               pi binary under test (default: <layer>/bin/pi)
      --layer DIR            learning-pi layer root (default: parent of this file)
      --sandbox DIR          reuse a pre-built sandbox (implies --keep)
      --keep                 keep the sandbox and reports for inspection
      --timeout SEC          whole-run cap per scenario (default: per scenario)
      --json                 emit a JSON result document
      --report-dir DIR       where to write artifacts (default: cache/e2e-<stamp>)

Exit: 0 all selected scenarios pass / 1 a scenario failed / 2 usage / 3 sandbox error.
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_LAYER = HERE.parents[1]
DEFAULT_CACHE = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "learning-pi"

# Terminal banners that mean a gated turn did not reach the learner.
WITHHOLD_MARKERS = ["⛔ WITHHELD", "⛔ UNVERIFIED", "NO_REVIEW_CONTEXT", "NO_GRADE_AUDIT_PASS"]


def eprint(*a) -> None:
    print(*a, file=sys.stderr)


def text_of_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict) and isinstance(p.get("text"), str):
                parts.append(p["text"])
        return "\n".join(parts)
    return ""


def subagent_runs(path: Path) -> list[dict]:
    """Dispatched subagent runs from the session, independent of audit_gates.

    Covers every agent (including viz/viz-audit, which audit_gates' fixed set
    omits). Each entry: {agent, runId, exitCode, isError}. Tool-call validation
    failures (e.g. a non-string `task`) are ignored: they never launched a run.
    """
    calls: dict[str, dict] = {}
    results: list[dict] = []
    try:
        fh = path.open(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") != "message":
                continue
            m = rec.get("message") or {}
            if m.get("role") == "assistant":
                for b in m.get("content") or []:
                    if isinstance(b, dict) and b.get("type") in ("toolCall", "tool_use") and b.get("id"):
                        calls[b["id"]] = b.get("name")
            elif m.get("role") == "toolResult" and m.get("toolName") == "subagent":
                results.append(m)
    runs: list[dict] = []
    for m in results:
        if m.get("isError"):
            continue
        details = m.get("details") if isinstance(m.get("details"), dict) else {}
        for r in details.get("results") or []:
            if isinstance(r, dict) and isinstance(r.get("agent"), str):
                runs.append({
                    "agent": r["agent"],
                    "runId": r.get("runId") or details.get("runId"),
                    "exitCode": r.get("exitCode"),
                    "acceptance": (r.get("acceptance") or {}).get("status") if isinstance(r.get("acceptance"), dict) else r.get("acceptance"),
                })
    return runs


def session_texts(path: Path) -> tuple[list[str], str]:
    """Return (assistant_messages, all_text).

    Banners from the gate land in assistant messages; receipts and verdicts from
    subagents land in toolResult messages. Keep both, separately.
    """
    assistant: list[str] = []
    everything: list[str] = []
    try:
        fh = path.open(encoding="utf-8", errors="ignore")
    except OSError:
        return assistant, ""
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") != "message":
                continue
            m = rec.get("message") or {}
            role = m.get("role")
            t = text_of_content(m.get("content"))
            if not t.strip():
                continue
            everything.append(t)
            if role == "assistant":
                assistant.append(t)
    return assistant, "\n".join(everything)


class Sandbox:
    def __init__(self, root: Path, owned: bool):
        self.root = root
        self.owned = owned
        self.agent = root / "agent"
        self.state = root / "state"
        self.sessions = root / "sessions"

    @classmethod
    def build(cls, layer: Path, pi_bin: str, model_access: bool = True) -> "Sandbox":
        cmd = ["bash", str(layer / "harness" / "mk-sandbox.sh"), "--layer", str(layer), "--pi", pi_bin]
        if model_access:
            cmd.append("--model-access")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            eprint(proc.stderr.rstrip() or proc.stdout.rstrip())
            raise RuntimeError("could not build sandbox")
        root = Path(proc.stdout.strip().splitlines()[-1])
        return cls(root, owned=True)

    def ensure_model_access(self, agent_from: Path) -> None:
        """Give a caller-provided sandbox model access.

        A sandbox built by pi-safe-update already has the candidate packages in
        its own npm dir, so only credentials and the model catalog are added.
        pi rewrites auth.json/models-store.json on startup and can leave them
        empty, so a weak file (missing or empty/`{}`) is refreshed. Files are
        copied, never symlinked: pi must not write through to the real agent dir.
        """
        def weak(path: Path) -> bool:
            try:
                return path.stat().st_size < 5
            except OSError:
                return True

        if weak(self.agent / "auth.json") and (agent_from / "auth.json").is_file():
            shutil.copy2(agent_from / "auth.json", self.agent / "auth.json")
            os.chmod(self.agent / "auth.json", 0o600)
        if weak(self.agent / "models-store.json") and (agent_from / "models-store.json").is_file():
            shutil.copy2(agent_from / "models-store.json", self.agent / "models-store.json")
        settings_path = self.agent / "settings.json"
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            settings = {}
        if "defaultProvider" not in settings:
            try:
                real = json.loads((agent_from / "settings.json").read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                real = {}
            if real.get("defaultProvider"):
                settings["defaultProvider"] = real["defaultProvider"]
                settings_path.write_text(json.dumps(settings), encoding="utf-8")

    def reset_state(self, layer: Path) -> None:
        """Rebuild fixture state and the .pi overlay, keeping the agent dir.

        Used when one sandbox serves several scenarios (update-gate mode): each
        journey starts from a clean fixture so earlier state writes cannot leak.
        """
        shutil.rmtree(self.state, ignore_errors=True)
        self.state.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["python3", str(layer / "test" / "fixtures" / "make_state_fixture.py"), str(self.state)],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        (self.state / ".pi").mkdir(exist_ok=True)
        for entry in ["APPEND_SYSTEM.md", "settings.json", "skills", "prompts", "agents", "extensions"]:
            src = layer / ".pi" / entry
            if not src.exists():
                continue
            dst = self.state / ".pi" / entry
            if dst.is_symlink() or dst.is_file():
                dst.unlink()
            elif dst.is_dir():
                shutil.rmtree(dst)
            dst.symlink_to(src)
        for child in self.sessions.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)

    def newest_session(self) -> Path | None:
        cands = sorted(
            (p for p in glob.glob(str(self.sessions / "*.jsonl"))),
            key=lambda p: os.path.getmtime(p),
            reverse=True,
        )
        return Path(cands[0]) if cands else None

    def cleanup(self) -> None:
        if self.owned:
            shutil.rmtree(self.root, ignore_errors=True)


def load_scenarios(layer: Path) -> list[dict]:
    out = []
    for path in sorted(glob.glob(str(layer / "test" / "e2e" / "scenarios" / "*.json"))):
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            eprint(f"e2e-runner: cannot load {path}: {exc}")
            continue
        data.setdefault("id", Path(path).stem)
        data["_path"] = path
        out.append(data)
    return out


def changed_paths(layer: Path, base: str) -> list[str]:
    """Paths changed in the layer repo vs `base`, including untracked files."""
    out: set[str] = set()
    for cmd in (
        ["git", "-C", str(layer), "diff", "--name-only", base],
        ["git", "-C", str(layer), "ls-files", "--others", "--exclude-standard"],
    ):
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            out.update(p for p in proc.stdout.splitlines() if p)
    return sorted(out)


def flows_from_diff(
    layer: Path, impact_map: dict, base: str, extra_repos: list[tuple[Path, list[dict]]] | None = None
) -> tuple[set[str], list[str]]:
    """Return (flows, changed_paths) selected by the impact map.

    `extra_repos` are (repo_root, rule_set) pairs (e.g. the learning-system
    checkout, whose changes map through `learning_system_paths`).
    """
    all_flows = set(impact_map.get("flows") or [])
    default = impact_map.get("default_flows", "*")
    selected: set[str] = set()
    paths: list[str] = []

    def apply(repo_paths: list[str], rules: list[dict]) -> None:
        for path in repo_paths:
            matched = False
            for rule in rules:
                if fnmatch.fnmatch(path, rule.get("match", "")):
                    matched = True
                    flows = rule.get("flows", "*")
                    selected.update(all_flows if flows == "*" else flows)
            if not matched:
                selected.update(all_flows if default == "*" else default)

    layer_paths = changed_paths(layer, base)
    paths.extend(layer_paths)
    apply(layer_paths, impact_map.get("rules") or [])
    for repo, rules in extra_repos or []:
        repo_paths = changed_paths(repo, base)
        paths.extend(f"{repo.name}/{p}" for p in repo_paths)
        apply(repo_paths, rules)
    return selected, paths


def run_scenario(scn: dict, sandbox: Sandbox, pi_bin: str, timeout: float, layer: Path) -> dict:
    """Drive one scenario; return a result dict."""
    import threading

    sid = scn["id"]
    steps = scn.get("steps") or []
    max_turns = int(scn.get("max_turns", 12))
    expect = scn.get("expect") or {}
    until_agents = scn.get("until_agents") or []
    until_min_messages = int(scn.get("until_min_messages", 0))
    until_clean_turn = bool(scn.get("until_clean_turn", False))
    until_text_any = scn.get("until_text_any") or []
    has_until = bool(until_agents or until_min_messages or until_clean_turn or until_text_any)
    result = {"id": sid, "flow": scn.get("flow"), "passed": False, "reasons": [], "steps": len(steps)}

    env = dict(os.environ)
    env["PI_CODING_AGENT_DIR"] = str(sandbox.agent)
    env["PI_CODING_AGENT_SESSION_DIR"] = str(sandbox.sessions)
    env.pop("PI_OFFLINE", None)

    proc = subprocess.Popen(
        [pi_bin, "--mode", "rpc", "--name", f"e2e-{sid}"],
        cwd=str(sandbox.state),
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    records: list[dict] = []
    stderr_lines: list[str] = []
    extension_errors: list[str] = []
    write_lock = threading.Lock()
    settled = threading.Event()
    stop_reader = threading.Event()
    turn_count = 0

    def send(obj: dict) -> None:
        with write_lock:
            try:
                assert proc.stdin is not None
                proc.stdin.write(json.dumps(obj) + "\n")
                proc.stdin.flush()
            except (BrokenPipeError, ValueError, OSError):
                pass

    def _reader() -> None:
        nonlocal turn_count
        assert proc.stdout is not None
        for line in proc.stdout:
            if stop_reader.is_set():
                break
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            records.append(rec)
            t = rec.get("type")
            if t == "extension_ui_request":
                method = rec.get("method")
                if method in ("select", "input", "editor"):
                    send({"type": "extension_ui_response", "id": rec["id"], "cancelled": True})
                elif method == "confirm":
                    send({"type": "extension_ui_response", "id": rec["id"], "confirmed": False})
            elif t == "turn_start":
                turn_count += 1
            elif t == "extension_error":
                extension_errors.append(f"{rec.get('event')}: {rec.get('error')}")
            elif t == "agent_settled":
                settled.set()

    def _drain_stderr() -> None:
        assert proc.stderr is not None
        for ln in proc.stderr:
            stderr_lines.append(ln.rstrip())

    threading.Thread(target=_reader, daemon=True).start()
    threading.Thread(target=_drain_stderr, daemon=True).start()

    deadline = time.time() + timeout

    def snapshot():
        sess = sandbox.newest_session()
        if not sess:
            return None, [], "", []
        texts, all_text = session_texts(sess)
        return sess, texts, all_text, subagent_runs(sess)

    def until_met() -> bool:
        _, texts, all_text, runs = snapshot()
        for a in until_agents:
            if not any(r["agent"] == a and r["exitCode"] in (0, None) and r.get("acceptance") != "rejected" for r in runs):
                return False
        if until_min_messages and len(texts) < until_min_messages:
            return False
        if until_clean_turn and (not texts or any(m in texts[-1] for m in WITHHOLD_MARKERS)):
            return False
        if until_text_any and not any(n in all_text for n in until_text_any):
            return False
        return True

    def wait_step() -> str:
        while time.time() < deadline:
            if turn_count > max_turns:
                return "maxturns"
            if has_until and until_met():
                return "until"
            if settled.is_set():
                return "settled"
            time.sleep(1.0)
        return "timeout"

    def missing_agents() -> list[str]:
        _, _, _, runs = snapshot()
        out = []
        for a in until_agents:
            if not any(r["agent"] == a and r["exitCode"] in (0, None) and r.get("acceptance") != "rejected" for r in runs):
                out.append(a)
        return out

    aborted = False
    stopped_early = False
    recoveries = 0
    nudges = 0
    max_nudges = int(expect.get("max_nudges", 3))
    generic_nudge = scn.get(
        "nudge_prompt",
        "Continue the flow now. Dispatch the required subagent(s) for this flow and proceed.",
    )

    def nudge_message() -> str:
        missing = missing_agents()
        if missing:
            named = ", ".join(f"`{a}`" for a in missing)
            return (
                f"The flow has not dispatched the required subagent(s): {named}. "
                "Dispatch each one now as a foreground call "
                "(subagent({ agent: \"<name>\", async: false, task: ... })) and continue the flow."
            )
        return generic_nudge

    try:
        for step in steps:
            if time.time() >= deadline:
                result["reasons"].append("scenario timeout before a step ran")
                aborted = True
                break
            prompt = step.get("prompt")
            if not prompt:
                continue
            settled.clear()
            send({"id": f"p-{len(records)}", "type": "prompt", "message": prompt})
            outcome = wait_step()
            # If the flow settled before reaching the early-stop condition (e.g. the
            # Tutor paused for input), nudge it to continue, up to max_nudges.
            while outcome == "settled" and has_until and not until_met() and nudges < max_nudges:
                nudges += 1
                settled.clear()
                send({"id": f"n-{nudges}", "type": "prompt", "message": nudge_message()})
                outcome = wait_step()
            if outcome == "timeout":
                result["reasons"].append("timed out waiting for the flow")
                aborted = True
                break
            if outcome == "maxturns":
                result["reasons"].append(f"exceeded max_turns ({max_turns})")
                aborted = True
                break
            if outcome == "until":
                stopped_early = True
                if not settled.is_set():
                    send({"type": "abort"})
                    settled.wait(timeout=20)
                break
        # Recovery only applies to settle-driven scenarios: a terminal withhold
        # from model turn-hygiene gets one nudge, as the gate banner instructs.
        if not aborted and not has_until:
            recover_on = scn.get("recover_on", WITHHOLD_MARKERS)
            max_recover = int(expect.get("max_recover", 1))
            recover_prompt = scn.get(
                "recover_prompt",
                "Your previous turn was withheld by the verification gate (see the banner above). "
                "Recover now: re-emit the verified draft as a single, correctly tagged turn.",
            )
            while time.time() < deadline and recoveries < max_recover:
                _, cur_texts, _, _ = snapshot()
                last = cur_texts[-1] if cur_texts else ""
                if not any(m in last for m in recover_on):
                    break
                recoveries += 1
                settled.clear()
                send({"id": f"r-{recoveries}", "type": "prompt", "message": recover_prompt})
                outcome = wait_step()
                if outcome in ("timeout", "maxturns"):
                    result["reasons"].append(f"recovery {outcome}")
                    aborted = True
                    break
    finally:
        stop_reader.set()
        try:
            if proc.stdin:
                proc.stdin.close()
        except OSError:
            pass
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
    result["turns"] = turn_count
    result["recoveries"] = recoveries
    result["nudges"] = nudges
    result["aborted"] = aborted
    result["stopped_early"] = stopped_early
    result["stderr_tail"] = stderr_lines[-15:]
    result["extension_errors"] = extension_errors[:5]
    if extension_errors:
        result["reasons"].append(f"extension error(s): {extension_errors[:3]}")

    session = sandbox.newest_session()
    result["session"] = str(session) if session else None
    texts, all_text = session_texts(session) if session else ([], "")
    # Fall back to stream-captured text if the session file is missing.
    if not texts:
        for rec in records:
            if rec.get("type") == "message_end":
                m = rec.get("message") or {}
                if m.get("role") == "assistant":
                    t = text_of_content(m.get("content"))
                    if t.strip():
                        texts.append(t)
                        all_text += "\n" + t
    joined = "\n".join(texts)
    result["assistant_messages"] = len(texts)

    runs = subagent_runs(session) if session else []
    result["runs"] = runs
    # audit_gates is kept in the artifact for human triage, not for pass/fail
    # (its fixed agent set omits viz/viz-audit and it flags missing meta files).
    audit = None
    if session and (layer / "pi" / "audit_gates.py").exists():
        ap = subprocess.run(
            ["python3", str(layer / "pi" / "audit_gates.py"), "--session", str(session), "--json"],
            capture_output=True,
            text=True,
        )
        try:
            audit = json.loads(ap.stdout)
        except json.JSONDecodeError:
            audit = {"error": "audit_gates produced no JSON", "stderr": ap.stderr[-500:]}
    result["audit"] = audit

    expect = scn.get("expect") or {}
    last_msg = texts[-1] if texts else ""

    for agent in expect.get("agents", []):
        match = [r for r in runs if r.get("agent") == agent]
        if not match:
            result["reasons"].append(f"expected subagent run missing: {agent}")
        else:
            clean = [r for r in match if r.get("exitCode") in (0, None) and r.get("acceptance") != "rejected"]
            if not clean:
                result["reasons"].append(f"subagent run not clean: {agent} -> {match}")

    for needle in expect.get("require_all", []):
        if needle not in all_text:
            result["reasons"].append(f"required text missing: {needle!r}")
    any_list = expect.get("require_any", [])
    if any_list and not any(n in all_text for n in any_list):
        result["reasons"].append(f"none of required-any present: {any_list!r}")
    # `forbid` guards the terminal turn: intermediate gate corrections are normal.
    for needle in expect.get("forbid", []):
        if needle in last_msg:
            result["reasons"].append(f"forbidden text in final turn: {needle!r}")
    for needle in expect.get("forbid_any", []):
        if needle in joined or needle in all_text:
            result["reasons"].append(f"forbidden text anywhere: {needle!r}")

    result["passed"] = not result["reasons"]
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenario", action="append", default=[], help="scenario id (repeatable or comma list)")
    ap.add_argument("--tier", choices=["smoke", "full"], default=None)
    ap.add_argument("--flows", default="", help="comma-separated flow filter")
    ap.add_argument("--diff", action="store_true", help="select flows affected by the git diff")
    ap.add_argument("--base", default="HEAD", help="git base for --diff (default: HEAD)")
    ap.add_argument("--diff-ls", default="", help="learning-system checkout to also diff (default: $LEARNING_SYSTEM_ROOT or ~/learning-system)")
    ap.add_argument("--no-diff-ls", action="store_true", help="do not diff the learning-system checkout")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--pi", default=os.environ.get("LEARN_CHECK_PI") or str(DEFAULT_LAYER / "bin" / "pi"))
    ap.add_argument("--layer", default=os.environ.get("LEARNING_PI_ROOT") or str(DEFAULT_LAYER))
    ap.add_argument("--sandbox", default="")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--jobs", type=int, default=1,
                    help="run scenarios concurrently (each in its own sandbox); "
                         "higher values raise model-provider contention and flakiness")
    ap.add_argument("--retries", type=int, default=1,
                    help="retry a failed scenario in a fresh sandbox this many times (default: 1)")
    ap.add_argument("--timeout", type=float, default=0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--report-dir", default="")
    args = ap.parse_args()

    layer = Path(args.layer).resolve()
    scenarios = load_scenarios(layer)
    if not scenarios:
        eprint(f"e2e-runner: no scenarios under {layer}/test/e2e/scenarios/")
        return 2

    wanted = set()
    for chunk in args.scenario:
        wanted.update(x for x in chunk.split(",") if x)
    flows = {x for x in args.flows.split(",") if x}
    if args.diff:
        try:
            impact = json.loads((layer / "test" / "e2e" / "impact-map.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            eprint(f"e2e-runner: cannot read impact map: {exc}")
            return 2
        extra_repos: list[tuple[Path, list[dict]]] = []
        if not args.no_diff_ls:
            ls = Path(args.diff_ls).expanduser() if args.diff_ls else Path(
                os.environ.get("LEARNING_SYSTEM_ROOT", str(Path.home() / "learning-system"))
            )
            if (ls / ".git").exists():
                extra_repos.append((ls, impact.get("learning_system_paths") or []))
        diff_flows, paths = flows_from_diff(layer, impact, args.base, extra_repos)
        print(f"e2e-runner: --diff {args.base}: {len(paths)} changed path(s) -> flows {sorted(diff_flows) or '(none)'}")
        if not diff_flows:
            print("e2e-runner: no affected flows; nothing to run")
            return 0
        flows |= diff_flows
    selected = [
        s
        for s in scenarios
        if (not wanted or s["id"] in wanted)
        and (not args.tier or s.get("tier") == args.tier)
        and (not flows or s.get("flow") in flows)
    ]
    if not selected:
        eprint("e2e-runner: no scenarios match the filter")
        if args.list:
            return 0
        return 2

    if args.list:
        for s in selected:
            print(f"{s['id']:20} flow={s.get('flow') or '-':10} tier={s.get('tier') or '-':6} {s.get('description','')}")
        return 0

    stamp = time.strftime("%Y%m%d-%H%M%S")
    report_dir = Path(args.report_dir) if args.report_dir else DEFAULT_CACHE / f"e2e-{stamp}"
    report_dir.mkdir(parents=True, exist_ok=True)

    print(f"e2e-runner: layer={layer}")
    print(f"e2e-runner: pi={args.pi}")
    print(f"e2e-runner: report={report_dir}")
    print()

    # Each scenario gets a fresh sandbox so one journey's state writes cannot
    # leak into the next. A caller-supplied sandbox (update-gate mode, with the
    # candidate packages staged) is reused serially, with state reset per journey.
    agent_from = Path(os.environ.get("PI_AGENT_SRC", str(Path.home() / ".pi" / "agent")))
    jobs = max(1, int(args.jobs))
    if args.sandbox and jobs > 1:
        print("e2e-runner: --sandbox shares one sandbox; forcing serial runs (ignoring --jobs)")
        jobs = 1

    def report(res: dict) -> None:
        retry = ""
        if res.get("attempts", 1) > 1:
            retry = f" after {res['attempts']} attempts" if res.get("passed") else f" ({res['attempts']} attempts)"
        if res.get("passed"):
            print(f"PASS {res['id']} ({res.get('duration_sec')}s, {res.get('turns')} turns, "
                  f"{res.get('assistant_messages')} messages){retry}", flush=True)
        else:
            print(f"FAIL {res['id']} ({res.get('duration_sec')}s){retry}", flush=True)
            for r in res["reasons"]:
                print(f"     - {r}", flush=True)

    def run_one(s: dict) -> dict:
        """Run one scenario, retrying a fresh attempt on failure.

        Model turn-hygiene is nondeterministic; one clean retry turns a flaky
        withhold into a pass without masking a real, repeatable break.
        """
        tmo = args.timeout or float(s.get("timeout_sec", 300))
        attempts: list[dict] = []
        for attempt in range(args.retries + 1):
            started = time.time()
            if args.sandbox:
                sandbox = Sandbox(Path(args.sandbox).resolve(), owned=False)
                sandbox.ensure_model_access(agent_from)
                sandbox.reset_state(layer)
            else:
                sandbox = Sandbox.build(layer, args.pi, model_access=True)
            try:
                res = run_scenario(s, sandbox, args.pi, tmo, layer)
                if res.get("session") and Path(res["session"]).exists():
                    suffix = "" if attempt == 0 else f".attempt{attempt + 1}"
                    shutil.copy2(res["session"], report_dir / f"{s['id']}{suffix}.session.jsonl")
            finally:
                sandbox.cleanup()
            res["duration_sec"] = round(time.time() - started, 1)
            res["attempt"] = attempt + 1
            attempts.append(res)
            if res["passed"]:
                break
        res = attempts[-1]
        res["attempts"] = len(attempts)
        if res["passed"] and len(attempts) > 1:
            res["passed_on_retry"] = True
        (report_dir / f"{s['id']}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
        return res

    results_by_id: dict[str, dict] = {}
    if jobs == 1:
        for s in selected:
            print(f"--- {s['id']} (flow={s.get('flow','?')}, timeout="
                  f"{args.timeout or float(s.get('timeout_sec', 300)):.0f}s) ...", flush=True)
            try:
                res = run_one(s)
            except (RuntimeError, subprocess.CalledProcessError):
                return 3
            results_by_id[s["id"]] = res
            report(res)
    else:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        print(f"e2e-runner: running {len(selected)} scenarios with jobs={jobs}", flush=True)
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            futures = {ex.submit(run_one, s): s for s in selected}
            for fut in as_completed(futures):
                s = futures[fut]
                try:
                    res = fut.result()
                except Exception as exc:  # noqa: BLE001 - report, never crash the run
                    res = {"id": s["id"], "flow": s.get("flow"), "passed": False,
                           "reasons": [f"runner error: {exc}"], "duration_sec": None}
                results_by_id[s["id"]] = res
                report(res)

    results = [results_by_id[s["id"]] for s in selected]
    ok = all(r.get("passed") for r in results)
    summary = {"stamp": stamp, "results": results, "passed": ok}
    (report_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print()
    passed = sum(1 for r in results if r["passed"])
    print(f"e2e-runner: {passed}/{len(results)} passed")
    if not ok:
        print(f"e2e-runner: FAILED — artifacts in {report_dir}")
        return 1
    print("e2e-runner: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
