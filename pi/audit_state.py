#!/usr/bin/env python3
"""
audit_state.py — read-only consistency audit for the learning-system repository.

Reports known classes of drift/inconsistency. It never writes or fixes anything.

Usage:
    python3 audit_state.py [--root /path/to/learning-system]
Root resolution: --root, else $LEARNING_SYSTEM_ROOT, else ~/learning-system.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

LESSON_RE = re.compile(r"\bL(\d{1,2})\b")
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
DONE_RE = re.compile(r"\b(done|complete[d]?|passed)\b", re.I)
INPROG_RE = re.compile(r"\b(in-?progress|paused|resume|not-started|not started)\b", re.I)
STALE_PATH_RE = re.compile(r"/home/(user|delinux)/learning-system")

findings: list[str] = []


def add(kind: str, msg: str) -> None:
    icon = {"error": "❌", "warn": "⚠️ ", "ok": "✅"}.get(kind, "•")
    findings.append(f"{icon} {msg}")


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def check_position_drift(root: Path) -> None:
    mission = read(root / "Learning System/MISSION.md")
    curriculum = read(root / "Learning System/CURRICULUM.md")
    if not mission or not curriculum:
        add("warn", "could not read MISSION.md and/or CURRICULUM.md")
        return

    def statuses(text: str) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for line in text.splitlines():
            if not re.search(r"\b(Position|Current Phase|Phase note)\b", line, re.I):
                continue
            for seg in re.split(r"[.;]", line):
                ids = LESSON_RE.findall(seg)
                if not ids:
                    continue
                flags: set[str] = set()
                if DONE_RE.search(seg):
                    flags.add("done")
                if INPROG_RE.search(seg):
                    flags.add("in-progress")
                if flags:
                    for i in ids:
                        out.setdefault(f"L{int(i):02d}", set()).update(flags)
        return out

    ms, cs = statuses(mission), statuses(curriculum)
    conflict = False
    for lesson in sorted(set(ms) | set(cs)):
        both = sorted(ms.get(lesson, set()) | cs.get(lesson, set()))
        if "done" in ms.get(lesson, set()) and "in-progress" in cs.get(lesson, set()):
            add("error", f"{lesson}: MISSION says done, CURRICULUM says in-progress")
            conflict = True
        if "done" in cs.get(lesson, set()) and "in-progress" in ms.get(lesson, set()):
            add("error", f"{lesson}: CURRICULUM says done, MISSION says in-progress")
            conflict = True
    if not conflict:
        add("ok", "MISSION/CURRICULUM lesson statuses agree")


def check_lessons_vs_curriculum(root: Path) -> None:
    """A lesson file that is active/done must not sit on a plain `not-started` row."""
    curriculum = read(root / "Learning System/CURRICULUM.md")
    lessons_dir = root / "Learning System/Lessons"
    if not curriculum or not lessons_dir.is_dir():
        add("warn", "could not read CURRICULUM.md or Lessons/")
        return
    missions: list[dict] = []
    cur: dict | None = None
    for line in curriculum.splitlines():
        m = re.match(r"## Mission \d+ — Phase (\d+)", line)
        if m:
            cur = {"phase": int(m.group(1)), "rows": {}}
            missions.append(cur)
            continue
        if cur is not None and re.match(r"\|\s*\d+\s*\|", line.strip()):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 6 and cells[5] in ("not-started", "not-started*", "in-progress", "done"):
                cur["rows"][int(cells[0])] = cells[5]

    def row_status(phase: int, lesson: int) -> str | None:
        for m in missions:
            if m["phase"] == phase:
                return m["rows"].get(lesson)
        return None

    flagged = 0
    for p in sorted(lessons_dir.glob("Lesson — *.md")):
        content = read(p)
        pm = re.search(r"Phase\s+(\d+)\s*[,\s]+\s*(?:Lesson\s+)?L?(\d{1,2})", content, re.I)
        if not pm:
            continue
        phase, lesson = int(pm.group(1)), int(pm.group(2))
        status = row_status(phase, lesson)
        if status != "not-started":
            continue  # only flag the plain, unambiguous stale case
        active = "DONE" in content or bool(re.search(r"Status:\s*\*\*[^*]*(paused|in-progress|done)", content, re.I))
        if active:
            flagged += 1
            add("error", f"Lessons/{p.name} is active/done but CURRICULUM Phase {phase} L{lesson} row says 'not-started'")
    if flagged == 0:
        add("ok", "lesson files and CURRICULUM rows agree")


def check_profile_focus(root: Path) -> None:
    profile = read(root / "Learning System/Core/💡 Learning Profile.md")
    curriculum = read(root / "Learning System/CURRICULUM.md")
    m = re.search(r"Current Focus:\*{0,2}\s*(.+)", profile)
    if not m:
        return
    focus = m.group(1).strip().lower()
    if "catch-up" in focus or "catch up" in focus:
        if "Mission 0" in curriculum and re.search(r"Mission 0.*?\bdone\b", curriculum, re.I | re.S):
            add("error", "Learning Profile 'Current Focus' still says Mission 0 catch-up, but CURRICULUM marks it done")
        else:
            add("warn", "Learning Profile 'Current Focus' mentions Mission 0 catch-up (verify against CURRICULUM)")


def check_active_concept_dates(root: Path) -> None:
    path = root / "Learning System/Core/📚 Active Concepts.md"
    text = read(path)
    if not text:
        add("warn", "could not read Active Concepts.md")
        return
    today = dt.date.today()
    header: list[str] = []
    rows = 0
    bad = 0
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        if not header:
            header = [c.lower() for c in cells]
            continue
        if len(cells) < 6:
            continue
        rows += 1
        try:
            col = next(i for i, h in enumerate(header) if "last" in h and "review" in h)
        except StopIteration:
            col = 4
        if col < len(cells):
            for d in DATE_RE.findall(cells[col]):
                try:
                    day = dt.date.fromisoformat(d)
                except ValueError:
                    continue
                if day > today:
                    bad += 1
                    add("warn", f"Active Concepts row '{cells[0]}' has a future Last Reviewed date {d}")
                    break
    if rows == 0:
        add("warn", "Active Concepts.md has no parseable rows")
    elif bad == 0:
        add("ok", f"Active Concepts dates look sane ({rows} rows)")


def _index_links(text: str) -> set[str]:
    out: set[str] = set()
    for m in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text):
        out.add(m.group(1).strip())
    for _, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text):
        out.add(Path(target).stem.strip())
    return out


def _index_section(index: str, heading: str) -> str:
    lines = index.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i + 1
            break
    if start is None:
        return ""
    body = []
    for line in lines[start:]:
        if line.strip().startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def check_wiki_index(root: Path) -> None:
    index = read(root / "Knowledge Wiki/index.md")
    wiki_dir = root / "Knowledge Wiki/wiki"
    src_dir = root / "Knowledge Wiki/raw/sources"
    if not wiki_dir.is_dir() or not index:
        add("warn", "could not read Knowledge Wiki/wiki or index.md")
        return
    wiki_files = {p.stem for p in wiki_dir.glob("*.md")} - {"README"}
    concept_links = _index_links(_index_section(index, "## Concepts"))
    missing_in_index = sorted(wiki_files - concept_links)
    missing_wiki = sorted(concept_links - wiki_files)
    if missing_in_index:
        add("warn", f"{len(missing_in_index)} wiki page(s) not listed in index.md Concepts (e.g. {', '.join(missing_in_index[:5])})")
    if missing_wiki:
        add("warn", f"{len(missing_wiki)} index.md Concept link(s) have no wiki file (e.g. {', '.join(missing_wiki[:5])})")
    if not missing_in_index and not missing_wiki:
        add("ok", f"wiki/index.md Concepts consistent ({len(wiki_files)} pages)")

    if src_dir.is_dir():
        source_files = {p.stem for p in src_dir.glob("*.md")}
        source_links = _index_links(_index_section(index, "## Sources"))
        missing_sources = sorted(source_links - source_files)
        if missing_sources:
            add("warn", f"{len(missing_sources)} index.md Source link(s) have no file in raw/sources (e.g. {', '.join(missing_sources[:5])})")
        else:
            add("ok", f"wiki/index.md Sources consistent ({len(source_links)} links)")


def check_pending_ingest(root: Path) -> None:
    if (root / "Learning System/Core/Pending Ingest.json").exists():
        add("warn", "stale Pending Ingest.json present (unfinished lesson handoff)")
    if list((root / "Learning System/.tmp").glob("context-*.json")):
        add("warn", "Scout digest(s) present in Learning System/.tmp/ (verify TTL / consumed)")


def check_stale_paths(root: Path) -> None:
    hits = 0
    for sub in ("Skills",):
        for p in (root / sub).rglob("*.md"):
            if STALE_PATH_RE.search(read(p)):
                hits += 1
                add("warn", f"stale host path in {p.relative_to(root)}")
    for name in ("OPENWEBUI.md", "README.md", "AGENTS.md"):
        p = root / name
        if p.exists() and STALE_PATH_RE.search(read(p)):
            hits += 1
            add("warn", f"stale host path in {name}")
    if hits == 0:
        add("ok", "no stale /home/user or /home/delinux paths in skills/docs")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("LEARNING_SYSTEM_ROOT") or str(Path.home() / "learning-system"))
    args = ap.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not (root / "Learning System").is_dir():
        print(f"not a learning-system root: {root}", file=sys.stderr)
        return 2

    print(f"audit_state — root: {root}\n")
    check_position_drift(root)
    check_lessons_vs_curriculum(root)
    check_profile_focus(root)
    check_active_concept_dates(root)
    check_wiki_index(root)
    check_pending_ingest(root)
    check_stale_paths(root)

    errors = sum(1 for f in findings if f.startswith("❌"))
    warns = sum(1 for f in findings if f.startswith("⚠"))
    print("\n".join(findings))
    print(f"\n{errors} error(s), {warns} warning(s). Read-only: nothing was modified.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
