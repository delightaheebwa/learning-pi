#!/usr/bin/env python3
"""audit_openwebui — read-only drift audit: repo (source of truth) vs live Open WebUI.

Verifies that every installer-managed object in the live instance matches what
`scripts/setup_openwebui.py` would install right now:

  - 4 Skills (content sha)
  - 3 model presets (system prompt + filterIds/skillIds)
  - 7 Prompts (content sha)
  - gate_pipe Function (content sha vs repo recomputation) + valves
  - subagents.system_prompt (sha)
  - OpenUI widget assets (served from Open WebUI's /static/openui; bundle sha)
  - orphan report (live objects the installer does not manage)

Exit code 0 = in sync, 1 = drift detected. Never mutates anything.

Usage:
  OPENWEBUI_API_KEY=sk-... python3 scripts/audit_openwebui.py [--base-url http://localhost:3000] [--orphans-only]
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from scripts.setup_openwebui import (  # noqa: E402
    Client,
    GATE_FILTER_ID,
    OPENUI_BUNDLE_SHA256,
    OPENUI_BUNDLE_VERSION,
    PRESETS,
    PROMPTS,
    SKILLS,
    SUBAGENT_SYSTEM_PROMPT,
    build_function_source,
    parse_skill_md,
    REPO_ROOT as _,
)

MANAGED_PROMPTS = {p["command"] for p in PROMPTS}
MANAGED_SKILLS = {parse_skill_md(os.path.join(REPO_ROOT, rel))[0] for rel in SKILLS}
MANAGED_MODELS = {p["id"] for p in PRESETS}


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:12]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:3000"))
    ap.add_argument("--api-key", default=os.environ.get("OPENWEBUI_API_KEY", ""))
    ap.add_argument("--orphans-only", action="store_true", help="only report unmanaged objects")
    args = ap.parse_args()

    if not args.api_key and os.path.isfile(os.path.expanduser("~/.openwebui_key")):
        args.api_key = open(os.path.expanduser("~/.openwebui_key")).read().strip()
    if not args.api_key:
        print("ERROR: no API key (OPENWEBUI_API_KEY or ~/.openwebui_key)", file=sys.stderr)
        return 2
    c = Client(args.base_url, args.api_key)

    drift: list[str] = []

    def check(label: str, want: str, got: str):
        if want != got:
            drift.append(label)
            print(f"  DRIFT {label}: repo {want} != live {got}")
        else:
            print(f"  ok    {label}: {got}")

    # Skills
    print("== Skills ==")
    status, live_skills = c.get("/api/v1/skills/list")
    by_id = {s.get("id"): s for s in (live_skills.get("items") if isinstance(live_skills, dict) else live_skills) or []}
    for rel in SKILLS:
        sid, _, _, content = parse_skill_md(os.path.join(REPO_ROOT, rel))
        # The list endpoint omits `content` (v0.12.2); read the skill itself.
        sstatus, live = c.get(f"/api/v1/skills/id/{sid}")
        live_content = live.get("content") if sstatus == 200 and isinstance(live, dict) else None
        check(f"skill {sid}", sha(content), sha(live_content) if live_content else "MISSING")

    # Gate function
    print("== Gate Function ==")
    status, fn = c.get(f"/api/v1/functions/id/{GATE_FILTER_ID}")
    if status == 200 and fn:
        with open(os.path.join(REPO_ROOT, "Skills/learning-review/openwebui/gate_schema.py")) as f:
            schema_src = f.read()
        with open(os.path.join(REPO_ROOT, "Skills/learning-review/openwebui/gate_pipe.py")) as f:
            pipe_src = f.read()
        expected = build_function_source(schema_src, pipe_src)
        check("function gate_pipe", sha(expected), sha(fn.get("content") or ""))
        vstatus, valves = c.get(f"/api/v1/functions/id/{GATE_FILTER_ID}/valves")
        if vstatus == 200:
            want = {"priority": 10, "max_retries": 2, "digest_ttl_days": 7}
            got = {k: valves.get(k) for k in want}
            if got != want:
                drift.append("gate valves")
                print(f"  DRIFT valves: want {want} got {got}")
            else:
                print(f"  ok    valves: {got}")
    else:
        drift.append("function gate_pipe")
        print("  DRIFT function gate_pipe: MISSING")

    # Subagent prompt
    print("== Subagent prompt ==")
    status, sub = c.get("/api/v1/configs/subagents")
    if status == 200 and sub:
        check("subagents.system_prompt", sha(SUBAGENT_SYSTEM_PROMPT), sha(sub.get("SUBAGENTS_SYSTEM_PROMPT") or ""))
    else:
        drift.append("subagents.system_prompt")
        print("  DRIFT subagents config unreadable")

    # Presets
    print("== Presets ==")
    for p in PRESETS:
        status, m = c.get(f"/api/v1/models/model?id={p['id']}")
        if status != 200 or not m:
            drift.append(f"model {p['id']}")
            print(f"  DRIFT model {p['id']}: MISSING")
            continue
        check(f"model {p['id']} system", sha(p["system"]), sha((m.get("params") or {}).get("system") or ""))
        meta = m.get("meta") or {}
        want_filters = [GATE_FILTER_ID] if p["id"] in ("learning-tutor", "clerk") else []
        if (meta.get("filterIds") or []) != want_filters:
            drift.append(f"model {p['id']} filterIds")
            print(f"  DRIFT filterIds: want {want_filters} got {meta.get('filterIds')}")
        else:
            print(f"  ok    filterIds: {want_filters}")

    # Prompts
    print("== Prompts ==")
    status, prompts = c.get("/api/v1/prompts/list")
    items = (prompts.get("items") if isinstance(prompts, dict) else prompts) or []
    by_cmd = {p.get("command"): p for p in items}
    for p in PROMPTS:
        live = by_cmd.get(p["command"])
        check(f"prompt /{p['command']}", sha(p["content"]), sha(live.get("content") or "") if live else "MISSING")

    # OpenUI widget assets (served same-origin from Open WebUI's /static mount)
    print("== OpenUI widget assets ==")
    base = args.base_url.rstrip("/")
    for rel, want in OPENUI_BUNDLE_SHA256.items():
        url = f"{base}/static/openui/{OPENUI_BUNDLE_VERSION}/{rel}"
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                got = hashlib.sha256(resp.read()).hexdigest()
        except Exception as e:  # noqa: BLE001 - any failure is drift for the audit
            got = f"UNREACHABLE-{e.__class__.__name__}"
        check(f"openui {rel}", want[:12], got[:12])
    shell_url = f"{base}/static/openui/{OPENUI_BUNDLE_VERSION}/widget.html"
    try:
        with urllib.request.urlopen(shell_url, timeout=20) as resp:
            shell = resp.read().decode("utf-8", "replace")
        if "widget.js" in shell and "connect-src 'none'" in shell:
            print("  ok    openui widget.html")
        else:
            drift.append("openui widget.html")
            print("  DRIFT openui widget.html: shell missing widget.js / connect-src 'none'")
    except Exception as e:  # noqa: BLE001
        drift.append("openui widget.html")
        print(f"  DRIFT openui widget.html: UNREACHABLE-{e.__class__.__name__}")

    # Orphans
    print("== Orphans (live but unmanaged) ==")
    orphans: list[str] = []
    live_cmds = set(by_cmd)
    for extra in sorted(live_cmds - MANAGED_PROMPTS):
        orphans.append(f"prompt /{extra}")
    for extra in sorted(set(by_id) - MANAGED_SKILLS):
        orphans.append(f"skill {extra}")
    status, models = c.get("/api/v1/models")
    if status == 200 and models:
        for m in models.get("data", []):
            info = m.get("info") or {}
            # Provider/connection models carry no `info` object — only custom
            # presets (managed or not) do. deputy (legacy) shows up here.
            if info.get("base_model_id") is not None and m.get("id") not in MANAGED_MODELS:
                orphans.append(f"model {m.get('id')}")
    for o in orphans:
        print(f"  orphan {o}")
    if orphans:
        print("  (orphans are informational — prune by hand or extend the installer)")

    print()
    if drift:
        print(f"RESULT: DRIFT — {len(drift)} item(s): {', '.join(drift)}")
        print("Fix: re-run scripts/setup_openwebui.py (idempotent), then audit again.")
        return 1
    print("RESULT: in sync (managed objects match repo).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
