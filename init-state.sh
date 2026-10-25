#!/usr/bin/env bash
# init-state.sh — scaffold a FRESH learning-system state repo (no owner data).
#
# Copies ONLY whitelisted tooling out of a learning-system clone
# (sidecar scripts, .gitignore, Core templates) and scaffolds everything else
# fresh: dirs + headers + empty tables that ops.py, audit_state.py, and
# wiki_provenance.py accept. The clone (and its history, owner data, and frozen
# Open WebUI layer) never enters TARGET — whitelist, not blacklist.
#
# This never touches your live state checkout — TARGET must be a new path
# (or pass --force to rebuild it).
#
# Usage:
#   ./init-state.sh TARGET [--source URL] [--force]
#   TARGET resolution: required arg (no default — never guess the state dir).
#
# After:
#   ~/learning-pi/install.sh TARGET
#   cd TARGET && pi   # approve/trust once, then define your track in MISSION.md

set -euo pipefail

PI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="https://github.com/delightaheebwa/learning-system.git"
FORCE=0
TARGET=""

while [ $# -gt 0 ]; do
  case "$1" in
    --source=*) SOURCE="${1#--source=}"; shift;;
    --source) [ $# -ge 2 ] || { echo "error: --source needs a URL" >&2; exit 2; }; SOURCE="$2"; shift 2;;
    --force) FORCE=1; shift;;
    -h|--help) sed -n '2,14p' "$0"; exit 0;;
    -*) echo "error: unknown flag '$1'" >&2; exit 2;;
    *) [ -z "$TARGET" ] || { echo "error: unexpected arg '$1'" >&2; exit 2; }; TARGET="$1"; shift;;
  esac
done

[ -n "$TARGET" ] || { echo "error: TARGET required (e.g. ./init-state.sh ~/my-learning)" >&2; exit 2; }
case "$TARGET" in
  .|..|./|../) echo "error: TARGET must be a named path, not '$TARGET'." >&2; exit 2;;
esac
[ -d "$(dirname "$TARGET")" ] || { echo "error: parent dir of '$TARGET' does not exist." >&2; exit 2; }
TARGET_ABS="$(cd "$(dirname "$TARGET")" && pwd)/$(basename "$TARGET")"
case "$TARGET_ABS" in
  "$HOME"|"$HOME/learning-system"|"$HOME/learning-system/"*)
    echo "error: refusing to touch $TARGET_ABS (live checkout or HOME). Pick a new path." >&2; exit 2;;
  "$PI_ROOT"|"$PI_ROOT"/*)
    echo "error: refusing to build inside the pi repo ($TARGET_ABS). Pick a path outside it." >&2; exit 2;;
  /) echo "error: refusing '/'. Pick a new path." >&2; exit 2;;
esac

if [ -e "$TARGET_ABS" ]; then
  if [ "$FORCE" = 1 ]; then
    echo "removing existing $TARGET_ABS (--force)"
    rm -rf "$TARGET_ABS"
  else
    echo "error: '$TARGET_ABS' exists — pass --force to rebuild it, or pick a new path." >&2; exit 2
  fi
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
echo "fetching whitelisted tooling from $SOURCE ..."
git clone -q "$SOURCE" "$WORK/src"

for d in "Learning System" "Knowledge Wiki" "scripts"; do
  [ -d "$WORK/src/$d" ] || { echo "error: source missing '$d/' — not a learning-system checkout?" >&2; exit 2; }
done
[ -f "$WORK/src/scripts/ops.py" ] || { echo "error: source missing scripts/ops.py" >&2; exit 2; }

echo "building $TARGET_ABS from whitelist ..."
mkdir -p "$TARGET_ABS"
cd "$TARGET_ABS"
mkdir -p scripts "Learning System/Core"
cp "$WORK/src/scripts/ops.py" "$WORK/src/scripts/ops_test.py" \
   "$WORK/src/scripts/learner_history.py" "$WORK/src/scripts/wiki_provenance.py" \
   "$WORK/src/scripts/wiki_provenance_test.py" scripts/
cp "$WORK/src/.gitignore" .gitignore
for t in "🔄 Review Note Template.md" "📝 Session Note Template.md"; do
  [ -f "$WORK/src/Learning System/Core/$t" ] && cp "$WORK/src/Learning System/Core/$t" "Learning System/Core/$t"
done
# Knowledge graph ledger (propositions + reasoning chains). Copied from the
# source when it carries it; otherwise scaffolded empty so graph.py works.
mkdir -p "Knowledge Wiki/graph"
if [ -d "$WORK/src/Knowledge Wiki/graph" ]; then
  cp "$WORK/src/Knowledge Wiki/graph/"* "Knowledge Wiki/graph/" 2>/dev/null || true
else
  printf '# nodes — propositions (one JSON object per line). See README.md.\n' > "Knowledge Wiki/graph/nodes.jsonl"
  printf '# chains — reasoning chains: premises jointly imply conclusion. See README.md.\n' > "Knowledge Wiki/graph/chains.jsonl"
fi
rm -rf "$WORK"
trap - EXIT

# Target holds only whitelisted tooling so far; everything else is scaffolded
# fresh below (no blacklist — nothing owner-related can survive).

echo "starting fresh git history ..."
git init -q

echo "scaffolding fresh state ..."
mkdir -p "Learning System/Core" "Learning System/Sessions" "Learning System/Reviews" \
  "Learning System/Lessons" "Learning System/Learning Records" "Learning System/Concept Notes" "Learning System/Archive" \
  "Learning System/build-artifacts" "Knowledge Wiki/wiki" "Knowledge Wiki/raw/sources" \
  "Knowledge Wiki/raw/assets"

cat > "Learning System/MISSION.md" <<'EOF'
# Mission: <your track>

## Why

TODO: one paragraph — what you are learning and why. (Example: follow the
AI Engineering from Scratch roadmap phases in order, shipping one artifact
per lesson. Scout fetches each lesson's live sources; Rohit sets the agenda.)

## Current Phase

- **Position:** not-started — define your first lesson in `CURRICULUM.md`, then run `/lesson` or `/teach <topic>`.

## Constraints

- Lessons sequential within a phase; phases in roadmap order.
- Advancement only after practice + retrieval check + Feynman explain-back.
- Local-first repo; pi is the control layer.

## Out of scope

- TODO: name what the Tutor must never pull in (e.g. archived tracks).
EOF

cat > "Learning System/CURRICULUM.md" <<'EOF'
# Curriculum: <your track>

Authoritative "what's next" map. Lessons advance only on practice + retrieval
pass + Feynman pass. Rows use status `not-started` / `in-progress (paused N/M)` / `done`.

<!-- Template (uncomment + fill per phase). Keep it prose, not a table, until
     you have real rows — line-oriented parsers treat leading-pipe lines as live.
     Example: a "Mission 1 - Phase 0" section with rows like:
     number 1, lesson "Vectors and matrices", status not-started, notes empty.
-->
EOF

cat > "Learning System/RESOURCES.md" <<'EOF'
# Resources

Curated trusted sources the Scout prefers, beyond per-lesson Further Reading.

- TODO: add your go-to sources (docs, papers, courses).
EOF

cat > "Learning System/GLOSSARY.md" <<'EOF'
# Glossary

Canonical workspace language. Add a term only when you understand it (Tutor promotes with your approval).

| Term | Meaning |
| --- | --- |
EOF

cat > "AGENTS.md" <<'EOF'
# AGENTS.md — repo conventions (pi runtime)

Canonical runtime: `learning-pi` (pi skills, subagents, prompts, verification
gate). There is no Open WebUI layer in this repo.

- **Tracked:** `Learning System/`, `Knowledge Wiki/`, `scripts/`, plus root docs
  when they change. **Never commit** secrets, `.tmp/` digests, or
  `Pending Ingest.json` (gitignored).
- After a session: `git add "Learning System" "Knowledge Wiki" scripts/ AGENTS.md README.md`
  → commit → push. Verify clean + `git log --oneline -1`.
- State edits follow the consistency check in `Learning System/AGENTS.md`.
- Verify Python changes with `python3 -m py_compile` and
  `python3 -m unittest scripts.ops_test`.
EOF

cat > "Learning System/AGENTS.md" <<'EOF'
# Learning System — Agent Conventions

This folder + `Knowledge Wiki/` are the active learning system. The operating
procedure lives in the pi skills (`learning-pi/.pi/skills/` — `learning-system`
for review/ingest flows, `learning-teach` for lessons). This file holds only
behavioral conventions.

## Multi-File Consistency Check

After any multi-file session (wiki page + index + log + Active Concepts + session note), re-read all touched files and verify:

- Wiki page created → in `Knowledge Wiki/index.md` under Concepts
- Ingest → `Knowledge Wiki/log.md` has today's entry
- Concept reviewed/added → `last_reviewed` = today in `Core/📚 Active Concepts.md`
- Concept reviewed/added → `next_review` calculated from current interval
- Wiki link in table → points to existing wiki page
- Session note → exists in `Sessions/` with today's date

Teaching sessions additionally verify:

- Lesson file → exists in `Learning System/Lessons/` (on `/pause`: partial file with `Status: paused at Checkpoint N/M, mini K/L` + `Resume from:` pointer)
- Learning record → numbered `highest + 1` in `Learning System/Learning Records/`
- Curriculum lesson advanced → only if practice + retrieval pass + Feynman pass
- New concepts from teaching → `developing` with `last_reviewed` = today, `next_review` = +3d
- Glossary additions → promoted only with user approval

Report ✅/❌ per item. Fix failures immediately.

## Git Sync

Commit state only (`Learning System/`, `Knowledge Wiki/`, `scripts/` when tooling
changes, root docs). Never commit `.tmp/` digests or `Pending Ingest.json`
(gitignored). This repo is yours — point it at your own remote and push `main`.
EOF

cat > "Learning System/README.md" <<'EOF'
# 📚 Learning System (canonical: pi)

A local-first, spaced-repetition learning system. Say `/review`, `/ingest`,
`/teach`, `/lesson`, `/continue`, or `/pause` — the pi `learning-system` skill
handles reviews, ingestion, and the writes below.

## Layout

- `Core/` — live state: `💡 Learning Profile.md`, `📚 Active Concepts.md` (review schedule),
  `Attempts.json` (mastery sidecar), `🧯 Mistakes.md`, `Learner History.md` (generated),
  `📦 Concept Archive.md`, session/review templates
- `Sessions/` — session notes
- `Reviews/` — review notes
- `Lessons/` — lesson files
- `Learning Records/` — numbered records
- `Concept Notes/` — archived stub (do not add)
- `Archive/` — reference-only historical material (do not grep)
- `Knowledge Wiki/` (sibling folder) — curated wiki pages, `index.md`, `log.md`
EOF

cat > "Knowledge Wiki/AGENTS.md" <<'EOF'
# Knowledge Wiki — Local Schema & Operating Rules

Build/maintenance rules live in the pi `llm-wiki` skill; this file is the local
contract for the files in this folder.

## Layout

```
raw/sources/   immutable raw layer — source notes and clipped text, never edited after ingest
raw/assets/    screenshots and attachments, linked from the source notes
wiki/          curated wiki pages — short, single-idea pages, aggressively cross-linked
index.md       catalog of all wiki pages (updated on every ingest)
log.md         chronological record of ingests (one entry per ingest)
```

## Rules

- **Raw sources are immutable.** Corrections land in the wiki layer or a new source note.
- **Wiki pages are short** — one main idea per page. Split, don't bloat.
- **Cross-link aggressively** with `[[wikilinks]]`.
- **Revise, don't duplicate.** Update the existing page with genuinely new material.
- **Contradictions are stated directly** on the page.
- **Keep unresolved questions visible** in `index.md` under Open questions.
- **index.md and log.md are updated on every ingest.**

## Provenance & trust order

Trust flows from evidence: raw source > verified claim > labelled AI synthesis > learner note.

Every page carries a provenance marker on its first lines:

```
<!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->
```

Lint: `python3 scripts/wiki_provenance.py [--check | --json | --stamp]`.

## Source of truth

This repo is authoritative.
EOF

cat > "Learning System/Core/📚 Active Concepts.md" <<'EOF'
# Active Concepts

The review schedule. New concepts enter as `developing` (`last_reviewed` today, `next_review` +3d).

<!-- Add one ## <Track> section per track you study. AIEFS/SWE are seeded below
     as examples (SWE archived); ops.py keys rows by section heading. -->

## AIEFS Track

| Concept | Type | Status | Prerequisites | Last Reviewed | Next Review | Source | Last Q Type | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## SWE Track (archived — see Concept Archive)

> **ARCHIVED** — no live rows. Seed concepts below to fill this slot.
> (Note: `scripts/ops_test.py` has one data-dependent SWE test that expects
> populated rows, so it fails on empty state by design — everything else passes.)

| Concept | Type | Status | Prerequisites | Last Reviewed | Next Review | Source | Last Q Type | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
EOF

cat > "Learning System/Core/Attempts.json" <<'EOF'
{
  "concepts": {},
  "meta": {
    "version": 1,
    "intervals": {
      "memory": [0, 1, 3, 7, 14, 30, 60],
      "concept": [3, 7, 14, 30],
      "procedure": [3, 7, 14],
      "design": [14, 28]
    }
  }
}
EOF

cat > "Learning System/Core/🧯 Mistakes.md" <<'EOF'
# Mistakes

Priority-1 review queue. `active` → `review` → `graduated` (2 consecutive correct).

## Active

_(none)_

## Review

_(none)_

## Graduated

_(none)_
EOF

cat > "Learning System/Core/💡 Learning Profile.md" <<'EOF'
# Learning Profile

TODO: who you are as a learner (background, pace, preferences).

- **Current Focus:** — (not started)
EOF

cat > "Learning System/Core/Learner History.md" <<'EOF'
# Learner History

Regenerated by `scripts/learner_history.py` from Attempts/Mistakes/Reviews. Do not hand-edit.
EOF

cat > "Learning System/Core/📦 Concept Archive.md" <<'EOF'
# Concept Archive

Paused/archived tracks live here, strictly out of scope for Scout/Tutor grep.
EOF

for d in Sessions Reviews Lessons "Learning Records"; do
  touch "Learning System/$d/.gitkeep"
done
touch "Learning System/build-artifacts/.gitkeep"

cat > "Learning System/Concept Notes/README.md" <<'EOF'
# Concept Notes (archived)

Atomic concept pages moved to the Knowledge Wiki. Do not add files here.
EOF

cat > "Learning System/Archive/README.md" <<'EOF'
# Archive

Legacy drops land here era-folded (`Archive/<era>-<date>/`). Models must not grep this tree.
EOF

cat > "Knowledge Wiki/index.md" <<'EOF'
# Index

## Sources

_(none yet — Scout raw material lands in `raw/sources/`)_

## Concepts

_(none yet)_

## Entities

## Open questions

_(none yet)_
EOF

cat > "Knowledge Wiki/log.md" <<'EOF'
# Log

Chronological ingest record. One entry per ingest (source → pages → concepts → position).
EOF

touch "Knowledge Wiki/wiki/.gitkeep" "Knowledge Wiki/raw/sources/.gitkeep" "Knowledge Wiki/raw/assets/.gitkeep"

cat > README.md <<'EOF'
# My Learning System

Personal spaced-repetition learning state. Scaffolding: `learning-pi/init-state.sh`.

- **Track:** TODO — name it in `Learning System/MISSION.md`.
- **Runtime:** [`learning-pi`](https://github.com/delightaheebwa/learning-pi) (`install.sh` + `pi`).

Run: `cd <this-dir> && pi`, then `/teach <topic>` or fill `CURRICULUM.md` and run `/lesson`.
Add your own LICENSE. Keep `.pi/` (git-excluded overlay) and `Pending Ingest.json` / `.tmp/` (gitignored) uncommitted.
EOF

git add -A
git commit -qm "fresh learning state scaffold (no owner data)"

cat <<EOF

Fresh state ready at: $TARGET (fresh git history, one scaffold commit)
Whitelisted tooling only: scripts/{ops,learner_history,wiki_provenance} (+ tests), .gitignore, Core templates
Never copied: owner state, git history, frozen Open WebUI layer (Skills/, OPENWEBUI.md, setup/audit scripts, infra/, .github/)
Next:
  1) $PI_ROOT/install.sh "$TARGET"
  2) ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi  # if not linked yet
  3) cd "$TARGET" && pi   # approve/trust once
  4) point it at your own remote: git remote add origin <your-url> && git push -u origin main
  5) define your track in Learning System/MISSION.md + CURRICULUM.md, then /teach or /lesson
EOF
