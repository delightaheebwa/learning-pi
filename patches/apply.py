#!/usr/bin/env python3
"""Reapply the local modifications to the vendored agent-skills pack.

Run from the repository root, or via scripts/skills-sync.sh after a re-vendor.
Each replacement is exact so upstream drift fails loudly instead of being
silently ignored.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

SPEC_OLD = (
    "Execute tasks one at a time following `skills/incremental-implementation/SKILL.md` "
    "(`incremental-implementation`) and `skills/test-driven-development/SKILL.md` "
    "(`test-driven-development`). Use `skills/context-engineering/SKILL.md` "
    "(`context-engineering`) to load the right spec sections and source files at each step "
    "rather than flooding the agent with the entire spec."
)
SPEC_NEW = (
    "Execute tasks one at a time following `../incremental-implementation/SKILL.md` "
    "(`incremental-implementation`) and `../test-driven-development/SKILL.md` "
    "(`test-driven-development`). Use `../context-engineering/SKILL.md` "
    "(`context-engineering`) to load the right spec sections and source files at each step "
    "rather than flooding the agent with the entire spec."
)

SETUP_OLD = (
    "> **Note:** The root `AGENTS.md` inside the `addyosmani/agent-skills` repository is "
    "intended for contributors working on this repository and should not be copied into other "
    "projects. See [CONTRIBUTING.md](../CONTRIBUTING.md#repo-scoped-files)."
)
SETUP_NEW = (
    "> **Note:** The root `AGENTS.md` inside the `addyosmani/agent-skills` repository is "
    "intended for contributors working on this repository and should not be copied into other "
    "projects. Its `CONTRIBUTING.md` has the `repo-scoped files` guidance."
)

DOCS_NOTE = (
    "> **Project note:** This is the upstream document, kept for reference. "
    "The lifecycle slash commands it mentions (`/ship`, `/review`, `/test`, "
    "`/webperf`) are Claude Code commands this project did not adopt; the "
    "personas here are composed by the parent agent with `Task` calls.\n\n"
)

REPLACEMENTS = (
    ("skills/spec-driven-development/SKILL.md", SPEC_OLD, SPEC_NEW),
    ("docs/opencode-setup.md", SETUP_OLD, SETUP_NEW),
)

failed = False
for relative, old, new in REPLACEMENTS:
    path = ROOT / ".opencode" / relative
    if not path.is_file():
        print(f"FAIL {path.relative_to(ROOT)}: missing", file=sys.stderr)
        failed = True
        continue
    text = path.read_text()
    if old in text:
        path.write_text(text.replace(old, new))
        print(f"patched {path.relative_to(ROOT)}")
    elif new in text:
        print(f"already applied {path.relative_to(ROOT)}")
    else:
        print(
            f"FAIL {path.relative_to(ROOT)}: patch target not found; "
            "upstream text moved, reconcile patches/apply.py",
            file=sys.stderr,
        )
        failed = True

docs_agents = ROOT / ".opencode" / "docs" / "agents.md"
if docs_agents.is_file():
    text = docs_agents.read_text()
    if text.startswith(DOCS_NOTE):
        print("already applied .opencode/docs/agents.md")
    else:
        docs_agents.write_text(DOCS_NOTE + text)
        print("patched .opencode/docs/agents.md")
else:
    print("FAIL .opencode/docs/agents.md: missing", file=sys.stderr)
    failed = True

sys.exit(1 if failed else 0)
