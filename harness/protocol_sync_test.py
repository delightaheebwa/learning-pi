"""Pin the two copies of the stress-test protocol so neither drifts alone.

`.pi/APPEND_SYSTEM.md` owns the tutor stance and states the protocol;
`.pi/skills/learning-teach/SKILL.md` carries the same protocol as an
operational walkthrough. Both copies are load-bearing: the contract binds both
load paths, so the duplication is deliberate and stays.

The limit of this test, stated plainly: it checks that the shared vocabulary is
PRESENT in both copies. It does not check that the copies agree semantically.
A contradiction that keeps both markers in place — opposite ordering, a rule
reworded into its negation, a step that teaches something else — is invisible
here. Such a contradiction is caught only by review or by
`scripts/learn-check --e2e`.

Every marker is confirmed in both files before it is asserted on, so a copy
that legitimately drops a word shrinks the checked set instead of failing the
suite. The kept set is named in every assertion message.

Run with: python3 -m unittest discover -s harness -p '*_test.py'
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STANCE_PATH = REPO_ROOT / ".pi" / "APPEND_SYSTEM.md"
SKILL_PATH = REPO_ROOT / ".pi" / "skills" / "learning-teach" / "SKILL.md"

# Each entry is a marker, or a tuple of accepted spellings for the same marker
# (the R0 ladder uses an en-dash in both copies today).
MARKER_CANDIDATES = (
    "spine check",
    "bracket",
    "dependency tree",
    "one rung per request",
    ("R0\u2013R5", "R0-R5"),
    "repair mode",
    "fresh-surface",
    "NO_REPAIR_RECEIPT",
    "entailment check",
    "naive-student",
    "triage",
    "cross-session",
)

STEP_CANDIDATES = (
    "Step 0",
    "Step 1",
    "Step 1.5",
    "Step 2",
    "Step 3",
    "Step 3.5",
    "Step 4",
    "Step 5",
)


def read(path):
    return path.read_text(encoding="utf-8")


def label(marker):
    return marker if isinstance(marker, str) else " / ".join(marker)


def contains(text, marker):
    """Case-insensitive presence check for a marker or any accepted spelling."""
    haystack = text.lower()
    variants = marker if isinstance(marker, tuple) else (marker,)
    return any(variant.lower() in haystack for variant in variants)


class ProtocolSyncTest(unittest.TestCase):
    def test_protocol_copies_share_markers(self):
        stance = read(STANCE_PATH)
        skill = read(SKILL_PATH)
        copies = (
            ("APPEND_SYSTEM.md", stance),
            ("learning-teach/SKILL.md", skill),
        )

        for name, text in copies:
            self.assertTrue(text.strip(), f"{name} has no content")
        self.assertIn("Stress-test protocol", stance)

        # Confirm each candidate in BOTH copies first; assert only on the
        # confirmed-shared subset.
        kept = [
            marker
            for marker in MARKER_CANDIDATES
            if contains(stance, marker) and contains(skill, marker)
        ]
        self.assertTrue(
            kept,
            "no stress-test protocol marker is shared by APPEND_SYSTEM.md and "
            "learning-teach/SKILL.md",
        )
        checked = ", ".join(label(marker) for marker in kept)
        for name, text in copies:
            with self.subTest(copy=name):
                for marker in kept:
                    self.assertTrue(
                        contains(text, marker),
                        f"shared marker {label(marker)!r} missing from {name}; "
                        f"checked markers: {checked}",
                    )

        # Confirm each step heading exists as a heading first; assert only the
        # confirmed subset, in document order.
        headings = [
            heading for heading in STEP_CANDIDATES if "## " + heading in skill
        ]
        self.assertTrue(
            headings, "no `## Step ...` heading found in learning-teach/SKILL.md"
        )
        positions = [skill.index("## " + heading) for heading in headings]
        self.assertEqual(
            positions,
            sorted(positions),
            "step headings are out of order: " + ", ".join(headings),
        )


if __name__ == "__main__":
    unittest.main()
