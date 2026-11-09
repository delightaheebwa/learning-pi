# Review — Git commit message conventions — 2026-08-04

**Concept:** Git commit message conventions
**Status:** developing → developing (no interval bump — initial review)
**Source:** MIT Missing Semester
**Question type:** definitional
**Interval:** 3d → next review 2026-08-11

**Question:** What's the conventional structure of a well-formed git commit message, and what does each part communicate to someone reviewing the history?

**Answer (user):** `git commit <change> <description>`

**Feedback:** Partial — the user identified the two-part structure (change + description) but missed the key detail of type prefixes (`feat`, `fix`, `docs`, `refactor`, `chore`) and the imperative mood convention. The type communicates *what kind* of change, the scope narrows it, and the subject should be written as if giving a command. Body explains *why*, footer references issues.

**Insight refinement:** `<type>(<scope>): <subject>` — type categorizes (feat/fix/docs/refactor/chore), scope narrows, subject is imperative ≤50 chars. Body explains why. Footer references issues and breaking changes.
