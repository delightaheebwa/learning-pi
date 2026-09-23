#!/usr/bin/env python3
"""Create a synthetic learning-system state fixture.

The harness never uses the real ~/learning-system as test state (CONTRACT.md
invariant S-2). This builds a minimal but structurally valid checkout instead:
the bits the learning gate, `ops.py`, and the audit scripts care about.

Usage:
    python3 test/fixtures/make_state_fixture.py DEST

Creates:
    DEST/Learning System/Core/...   (the SRS state, small)
    DEST/Knowledge Wiki/...         (index, log, wiki/, raw/sources/)
    DEST/scripts/ops.py             (copy, so sidecar root-detection works)

Idempotent: re-running rebuilds the fixture.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
LEARNING_PI = HERE.parents[2]  # test/fixtures/ -> test/ -> learning-pi/


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    core = dest / "Learning System" / "Core"
    core.mkdir(parents=True)

    _write(
        core / "📚 Active Concepts.md",
        """# Active Concepts

## AIEFS Track

| Concept | Type | Status | Prerequisites | Last Reviewed | Next Review | Source | Last Q Type | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fixture Linear Algebra | concept | developing | — | 2026-09-01 | 2026-09-04 | fixture | — | seed row |
| Fixture Shell Basics | memory | active | — | 2026-09-01 | 2026-09-02 | fixture | — | seed row |
""",
    )
    _write(
        core / "Attempts.json",
        json.dumps(
            {
                "concepts": {
                    "Fixture Linear Algebra": {
                        "type": "concept",
                        "attempts": [
                            {"date": "2026-09-01", "is_correct": True, "result": "pass", "q_type": None}
                        ],
                        "interval_index": 0,
                        "consecutive_correct": 1,
                        "consecutive_wrong": 0,
                        "last_reviewed": "2026-09-01",
                        "next_review": "2026-09-04",
                        "feynman": None,
                    }
                },
                "meta": {
                    "version": 1,
                    "intervals": {
                        "memory": [0, 1, 3, 7, 14, 30, 60],
                        "concept": [3, 7, 14, 30],
                        "procedure": [3, 7, 14],
                        "design": [14, 28],
                    },
                },
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        core / "🧯 Mistakes.md",
        "# Mistakes\n\n## Active\n\n_(none)_\n\n## Review\n\n_(none)_\n\n## Graduated\n\n_(none)_\n",
    )
    _write(
        core / "💡 Learning Profile.md",
        "# Learning Profile\n\nFixture profile. No real learner data.\n",
    )
    _write(core / "Learner History.md", "# Learner History\n\n_(fixture)_\n")
    _write(core / "📦 Concept Archive.md", "# Concept Archive\n\n_(fixture)_\n")

    _write(dest / "Learning System" / "MISSION.md", "# Mission\n\nFixture mission.\n")
    _write(dest / "Learning System" / "CURRICULUM.md", "# Curriculum\n\nFixture curriculum.\n")

    wiki = dest / "Knowledge Wiki"
    _write(wiki / "index.md", "# Index\n\n_(fixture)_\n")
    _write(wiki / "log.md", "# Log\n\n_(fixture)_\n")
    (wiki / "wiki").mkdir(parents=True, exist_ok=True)
    (wiki / "raw" / "sources").mkdir(parents=True, exist_ok=True)

    # A copy of ops.py so its root auto-detection resolves to this fixture when
    # the sidecar suite runs against it.
    src_ops = LEARNING_PI.parent / "learning-system" / "scripts" / "ops.py"
    if src_ops.is_file():
        (dest / "scripts").mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_ops, dest / "scripts" / "ops.py")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: make_state_fixture.py DEST", file=sys.stderr)
        return 2
    dest = Path(sys.argv[1]).expanduser().resolve()
    build(dest)
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
