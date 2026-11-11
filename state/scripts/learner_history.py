#!/usr/bin/env python3
"""learner_history — regenerate Core/Learner History.md from evidence.

Reads Attempts.json (attempt history), Mistakes.md (open mistakes), Reviews/
+ Archive reviews (evidence pointers), Concept Archive.md (paused concepts),
and Active Concepts.md (live rows).
Writes a compact per-concept table with strict fuzzy/neutral/solid tags so the
Tutor gets learner context without grepping the Archive/ tree.

Tag rules (strict solid):
  solid   = consecutive_correct >= 2 AND interval_index >= 2
            AND (type in {memory, procedure} OR feynman pass)
            AND last attempt passed AND no open (active/review) mistake
            AND no failed AI-free (solo) attempt on record (P0.4); no solo
            evidence is unknown and does not block (grandfathered)
  fuzzy   = open mistake OR consecutive_wrong > 0 OR last attempt failed
  neutral = everything else

Track inference: concept in live Active Concepts rows -> aiefs; a concept whose
Attempts next_review is `paused` -> paused (outside the AIE 80/20 sprint);
else by last_reviewed date (<= 2026-07-28 -> aie, else swe).

Usage: python3 scripts/learner_history.py   (run from repo root)
"""

import datetime
import json
import os
import re
import sys
from pathlib import Path

# P0.4: reuse ops.py's dimension model for the independence gate. Imported
# defensively so a path/setup problem degrades to "unknown" (grandfather), never
# a crash or a false demotion.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import ops  # noqa: E402
except Exception:  # pragma: no cover - defensive
    ops = None

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(REPO_ROOT, "Learning System", "Core")
OUT = os.path.join(CORE, "Learner History.md")


def load_attempts():
    with open(os.path.join(CORE, "Attempts.json"), encoding="utf-8") as f:
        return json.load(f).get("concepts", {})


def _mistakes_rows_from(path):
    """Rows from one mistakes ledger, parsed by ops.py's anchor rule.

    ops.py owns the ledger layout: it anchors on the error_type enum and reads
    status/retries/next-retry as the last three cells, so literal '|' inside a
    free-text cell cannot shift the status column. The fallback only runs when
    the defensive ops import failed; it reads status from that same last-three
    position.
    """
    if ops is not None:
        return ops._mistakes_rows_from(Path(path))
    rows = []
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except FileNotFoundError:
        return rows
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 9 or cells[0].lower() == "date":
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append({"concept": cells[1], "status": cells[-3].lower()})
    return rows


def load_open_mistakes(include_archived=False):
    """Concepts with active/review mistake rows.

    Live queue by default; pass include_archived=True to also count rows in the
    Archive mistake files (SWE-era, C-project) so frozen-era tags stay accurate.
    """
    open_m = set()
    paths = [os.path.join(CORE, "🧯 Mistakes.md")]
    if include_archived:
        paths += [
            os.path.join(REPO_ROOT, "Learning System", "Archive", "SWE-2026-09-01", "mistakes.md"),
            os.path.join(REPO_ROOT, "Learning System", "Archive", "C-project", "mistakes.md"),
        ]
    for path in paths:
        for row in _mistakes_rows_from(path):
            if row["status"] in ("active", "review"):
                open_m.add(row["concept"])
    return open_m


def live_concepts():
    """Concept names with rows in the live Active Concepts tables."""
    live = set()
    path = os.path.join(CORE, "📚 Active Concepts.md")
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return live
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("Concept", "---", ""):
            continue
        if set(cells[0]) <= set("- "):
            continue
        live.add(cells[0])
    return live


def review_index():
    """Map normalized concept name -> latest review file path (repo-relative)."""
    idx = {}
    for base in ("Learning System/Reviews", "Learning System/Archive"):
        root = os.path.join(REPO_ROOT, base)
        for dirpath, _, files in os.walk(root):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                m = re.match(r"Review — (.+) — (\d{4}-\d\d-\d\d)", fn)
                if not m:
                    continue
                concept, date = m.group(1).strip(), m.group(2)
                key = concept.lower()
                rel = os.path.relpath(os.path.join(dirpath, fn), REPO_ROOT)
                if key not in idx or date > idx[key][1]:
                    idx[key] = (rel, date)
    return idx


def feynman_passed(feynman):
    if feynman is None:
        return False
    if isinstance(feynman, dict):
        return bool(feynman.get("pass"))
    return feynman == "pass"


def load_archive_concepts(known):
    """Paused concepts from Concept Archive.md not already in Attempts.

    Returns {name: {type, last, section}}. Tag is neutral (paused/stale: the
    Tutor probes first); evidence points at the archive section.
    """
    found = {}
    path = os.path.join(CORE, "📦 Concept Archive.md")
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return found
    section, era = "", "aie"
    for line in text.splitlines():
        h = re.match(r"##+\s+(.+)", line)
        if h:
            section = h.group(1).strip()
            slow = section.lower()
            if "swe" in slow or "c project" in slow:
                era = "swe"
            elif "07-28" in slow or "07-22" in slow or "aie" in slow:
                era = "aie"
            else:
                era = "aie"  # pre-split legacy (Math/ML, Robotics, PP, Compilers, NLP)
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0] in ("Concept", "") or set(cells[0]) <= set("- "):
            continue
        name = cells[0]
        if name in known:
            continue
        found[name] = {
            "type": "",
            "last": cells[3] if len(cells) > 3 else "",
            "evidence": f"📦 Concept Archive.md §{section}",
            "era": era,
        }
    return found


def prereq_states(entry, concepts, open_mistakes):
    """Compact per-concept prerequisite state for the Learner History table
    (P1.3): `A: fuzzy, B: solid`. Empty when the concept records no prereqs."""
    out = []
    for p in entry.get("prereqs") or []:
        st = ops._prereq_state(p, concepts, open_mistakes) if ops else "unknown"
        out.append(f"{p}: {st}")
    return ", ".join(out)


def tag(concept, entry, open_mistakes):
    attempts = entry.get("attempts", [])
    last_ok = bool(attempts) and bool(attempts[-1].get("is_correct"))
    if (
        concept in open_mistakes
        or entry.get("consecutive_wrong", 0) > 0
        or (attempts and not last_ok)
    ):
        return "fuzzy"
    if (
        entry.get("consecutive_correct", 0) >= 2
        and entry.get("interval_index", 0) >= 2
        and last_ok
        # P0.4 independence gate: a concept with a failed AI-free (solo) attempt
        # on record cannot be solid. No solo evidence is unknown, so existing
        # concepts are grandfathered until /solo produces a real test.
        and (ops.independence_ok(entry) if ops else True)
        and (
            entry.get("type") in ("memory", "procedure")
            or feynman_passed(entry.get("feynman"))
        )
    ):
        return "solid"
    return "neutral"


def main():
    concepts = load_attempts()
    open_mistakes = load_open_mistakes(include_archived=True)
    live = live_concepts()
    reviews = review_index()

    rows = {"aiefs": [], "paused": [], "swe": [], "aie": []}
    for name, entry in concepts.items():
        last_rev = entry.get("last_reviewed", "")
        if name in live:
            track = "aiefs"
        elif entry.get("next_review") == "paused":
            track = "paused"
        elif last_rev <= "2026-07-28":
            track = "aie"
        else:
            track = "swe"
        ptr = reviews.get(name.lower())
        evidence = ptr[0] if ptr else f"last reviewed {last_rev or 'unknown'}"
        rows[track].append(
            {
                "concept": name,
                "type": entry.get("type", ""),
                "tag": tag(name, entry, open_mistakes),
                "prereqs": prereq_states(entry, concepts, open_mistakes),
                "last": last_rev,
                "evidence": evidence,
            }
        )
    for track in rows:
        rows[track].sort(key=lambda r: (r["tag"] != "fuzzy", r["concept"].lower()))

    # Paused concepts from the Concept Archive (no attempt history): neutral,
    # Tutor probes first. Attempts evidence wins on name overlap.
    for name, info in load_archive_concepts(set(concepts)).items():
        rows[info["era"]].append(
            {
                "concept": name,
                "type": info["type"],
                "tag": "neutral",
                "prereqs": "",
                "last": info["last"],
                "evidence": info["evidence"],
            }
        )
    for track in rows:
        rows[track].sort(key=lambda r: (r["tag"] != "fuzzy", r["concept"].lower()))

    total = sum(len(rows[t]) for t in rows)

    lines = [
        f"# Learner History — compact tutor context (generated {datetime.date.today().isoformat()})",
        "",
        "> **For models: read THIS file for learner background, not `Archive/`.**",
        "> One row per concept ever studied: strict `solid` / `neutral` / `fuzzy` tag +",
        "> a `Prereqs` column (each direct prereq's live state) + evidence pointer.",
        "> Regenerate with `python3 scripts/learner_history.py`.",
        "> Clerk updates the AIEFS section after every session (see `learning-system` skill).",
        "> Era sections are frozen at archive time.",
        "",
        "Tag rules (strict): `solid` = 2+ consecutive passes, interval_index ≥ 2,",
        "(Feynman pass for concept/design types), last attempt passed, no open mistake.",
        "`fuzzy` = open mistake OR consecutive misses OR last attempt failed.",
        "`neutral` = everything else (developing, single pass, stale).",
        "Tutor use: build directly on `solid`; probe-then-teach `neutral`;",
        "reteach-from-scratch `fuzzy` (check its mistake row / review note first).",
        "",
        f"Totals: {total} concepts ({len(concepts)} with attempt history + {total - len(concepts)} paused)"
        f" — aiefs {len(rows['aiefs'])} · paused {len(rows['paused'])} · swe {len(rows['swe'])} · aie {len(rows['aie'])} · "
        f"solid {sum(r['tag'] == 'solid' for rs in rows.values() for r in rs)} · "
        f"neutral {sum(r['tag'] == 'neutral' for rs in rows.values() for r in rs)} · "
        f"fuzzy {sum(r['tag'] == 'fuzzy' for rs in rows.values() for r in rs)}",
        "",
    ]
    titles = {
        "aiefs": "## AIEFS — living (updated by Clerk each session)",
        "paused": "## Paused — outside the AIE 80/20 sprint (archived 2026-11-11)",
        "swe": "## SWE era — frozen 2026-09-01 (see `Archive/SWE-2026-09-01/`)",
        "aie": "## AIE era — frozen 2026-07-28 (see `Archive/AIE-2026-07-28/`)",
    }
    for track in ("aiefs", "paused", "swe", "aie"):
        lines += [
            titles[track],
            "",
            "| Concept | Type | Tag | Prereqs | Last evidenced | Evidence |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for r in rows[track]:
            lines.append(
                f"| {r['concept']} | {r['type']} | {r['tag']} | {r['prereqs']} | "
                f"{r['last']} | {r['evidence']} |"
            )
        lines.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT}: " + ", ".join(f"{t}={len(rows[t])}" for t in rows))


if __name__ == "__main__":
    sys.exit(main())
