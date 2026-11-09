#!/usr/bin/env python3
"""wiki_provenance — provenance lint/stamp for Knowledge Wiki pages (P0.6).

Every page in Knowledge Wiki/wiki/*.md must carry a provenance marker on its
first lines:

    <!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->

Trust order (see Knowledge Wiki/AGENTS.md and AGENTS.md): a raw source outranks
a verified claim, which outranks labelled AI synthesis, which outranks learner
notes. An **unstamped page is treated as `unverified`** — the wiki is AI
synthesis derived from sources, not a source itself.

Usage (run from the repo root):
  python3 scripts/wiki_provenance.py            report status counts + offenders
  python3 scripts/wiki_provenance.py --check    exit 1 if any page lacks a marker
  python3 scripts/wiki_provenance.py --json     machine-readable report
  python3 scripts/wiki_provenance.py --stamp [--status unverified] [--date YYYY-MM-DD]
                                                add a default marker to unstamped
                                                pages (idempotent; never rewrites
                                                an existing marker)
"""

from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = REPO_ROOT / "Knowledge Wiki" / "wiki"
MARKER_RE = re.compile(r"<!--\s*provenance:\s*(.*?)-->", re.IGNORECASE | re.DOTALL)
STATUS_RE = re.compile(r"status\s*=\s*([a-z][a-z-]*)", re.IGNORECASE)
SOURCE_RE = re.compile(r"source\s*=\s*([^|]*)", re.IGNORECASE)
VERIFIED_BY_RE = re.compile(r"verified-by\s*=\s*([^|]*)", re.IGNORECASE)
DATE_RE = re.compile(r"date\s*=\s*(\d{4}-\d{2}-\d{2})")
VALID_STATUS = {"verified", "synthesis", "learner-note", "unverified"}
# The marker must be at the top of the page (it is a header, not a footnote).
MARKER_LINE_WINDOW = 5


def _pages() -> list[Path]:
    if not WIKI_DIR.is_dir():
        return []
    return sorted(p for p in WIKI_DIR.glob("*.md") if p.is_file())


def _marker_match(text: str):
    """The provenance marker, but only in the first `MARKER_LINE_WINDOW` lines.

    A marker buried mid-file is not a page header and must not validate the page
    (a stray comment in prose should never count as provenance)."""
    head = "\n".join((text or "").splitlines()[:MARKER_LINE_WINDOW])
    return MARKER_RE.search(head)


def read_status(text: str) -> str | None:
    """The raw `status=` value, or None when the marker/status is absent.

    Unknown status values are returned verbatim (never silently coerced to
    `unverified`), so `marker_problem` can reject them as malformed."""
    m = _marker_match(text)
    if not m:
        return None
    s = STATUS_RE.search(m.group(1))
    if not s:
        return None
    return s.group(1).lower()


def marker_problem(text: str) -> str | None:
    """Human-readable reason a page's provenance marker is invalid, or None.

    A missing marker, an unknown status, or a `verified` claim with no source /
    verifier / date is a problem. This is what makes `--check` able to fail on
    content, not only on absent markers."""
    m = _marker_match(text)
    if not m:
        return "missing marker"
    body = m.group(1)
    s = STATUS_RE.search(body)
    if not s:
        return "marker has no status="
    status = s.group(1).lower()
    if status not in VALID_STATUS:
        return f"unknown status={status}"
    if status == "verified":
        src = (SOURCE_RE.search(body).group(1).strip() if SOURCE_RE.search(body) else "")
        vb = (VERIFIED_BY_RE.search(body).group(1).strip() if VERIFIED_BY_RE.search(body) else "")
        if not src or src in ("—", "-"):
            return "status=verified requires a source"
        if not vb or vb in ("—", "-"):
            return "status=verified requires verified-by"
        if not DATE_RE.search(body):
            return "status=verified requires a valid date=YYYY-MM-DD"
    return None


def marker(status: str, source: str, verified_by: str, date: str) -> str:
    return (
        f"<!-- provenance: status={status} | source={source} | "
        f"verified-by={verified_by} | date={date} -->\n\n"
    )


def scan() -> dict:
    counts: dict[str, int] = {s: 0 for s in VALID_STATUS}
    missing: list[str] = []
    invalid: list[dict] = []
    for p in _pages():
        text = p.read_text(encoding="utf-8", errors="replace")
        m = _marker_match(text)
        if m is None:
            missing.append(p.name)
            continue
        problem = marker_problem(text)
        if problem is not None:
            invalid.append({"file": p.name, "reason": problem})
            continue
        status = read_status(text)
        counts[status] = counts.get(status, 0) + 1
    return {
        "total": len(_pages()),
        "counts": counts,
        "missing": missing,
        "invalid": invalid,
    }


def do_report(report: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    c = report["counts"]
    print(f"wiki pages: {report['total']}")
    for s in ("verified", "synthesis", "learner-note", "unverified"):
        print(f"  {s:12} {c.get(s, 0)}")
    print(f"  missing      {len(report['missing'])}")
    if report["missing"]:
        print("unstamped (treated as unverified):")
        for name in report["missing"][:30]:
            print(f"  - {name}")
        if len(report["missing"]) > 30:
            print(f"  … and {len(report['missing']) - 30} more")
    if report["invalid"]:
        print("malformed markers:")
        for item in report["invalid"][:30]:
            print(f"  - {item['file']}: {item['reason']}")
        if len(report["invalid"]) > 30:
            print(f"  … and {len(report['invalid']) - 30} more")


def do_stamp(status: str, date: str) -> int:
    if status not in VALID_STATUS:
        print(f"bad --status {status!r}; want one of {sorted(VALID_STATUS)}")
        return 2
    stamped = 0
    for p in _pages():
        text = p.read_text(encoding="utf-8", errors="replace")
        if _marker_match(text):
            continue
        line = marker(status, source="legacy", verified_by="—", date=date)
        p.write_text(line + text, encoding="utf-8")
        stamped += 1
    print(f"stamped {stamped} page(s) status={status}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    check = "--check" in args
    if "--stamp" in args:
        status = "unverified"
        if "--status" in args:
            status = args[args.index("--status") + 1]
        date = args[args.index("--date") + 1] if "--date" in args else datetime.date.today().isoformat()
        return do_stamp(status, date)
    report = scan()
    do_report(report, as_json)
    if check and (report["missing"] or report["invalid"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
