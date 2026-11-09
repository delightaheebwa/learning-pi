# Learning System — Agent Conventions

This folder + `Knowledge Wiki/` are the active learning system. The operating procedure lives in `Skills/learning-system/SKILL.md` (frozen legacy snapshot — canonical behavior in `learning-pi/.pi/skills/`) — that skill is the authority for review/ingest flows and file layout. This file holds only behavioral conventions.

## Repo location

The runtime working copy lives at **`/home/user/learning-system`** inside the Open WebUI **Open Terminal** workspace (a persistent container volume, legacy path). A second checkout lives at **`/home/delightaheebwa/learning-system`** (WSL, this host) for maintenance refactors — both track the same GitHub remote; GitHub (https://github.com/delightaheebwa/learning-system) is the durable source of truth. The runtime model reads and writes the Open Terminal copy; keep the two in sync only via git push/pull, never by editing both directly in one session. The canonical pi runtime uses the local checkout directly (no Open Terminal needed).

## Multi-File Consistency Check

After any multi-file session (wiki page + index + log + Active Concepts + session note), re-read all touched files and verify:

- Wiki page created → in `Knowledge Wiki/index.md` under Concepts
- Ingest → `Knowledge Wiki/log.md` has today's entry
- Concept reviewed/added → `last_reviewed` = today in `Core/📚 Active Concepts.md`
- Concept reviewed/added → `next_review` calculated from current interval
- Wiki link in table → points to existing wiki page
- Session note → exists in `Sessions/` with today's date

Teaching sessions additionally verify (per `Skills/learning-teach/SKILL.md`):

- Lesson file → exists in `Learning System/Lessons/` with today's date (on `/pause`: partial file with `Status: paused at Checkpoint N/M, mini K/L` + `Resume from:` pointer to the next mini-checkpoint or the checkpoint practice; curriculum row `in-progress (paused N/M)`, Scout digest kept)
- Learning record → numbered `highest + 1` in `Learning System/Learning Records/`, with Bloom level + Feynman explain-back in Evidence (final checkpoint only; pauses write session note + partial ingest, no full record)
- Curriculum lesson advanced → only if practice + retrieval pass + Feynman pass; status in `Learning System/CURRICULUM.md` matches reality
- New concepts from teaching → `developing` with `last_reviewed` = today, `next_review` = +3d
- Glossary additions → promoted only with user approval

Report ✅/❌ per item. Fix failures immediately.

## Git Sync

The working copy is the Git repo at `/home/user/learning-system` (container) or `/home/delightaheebwa/learning-system` (this WSL host), tracked against GitHub remote `origin` (public, branch `main`). Repo covers `Learning System/`, `Knowledge Wiki/`, and `Skills/` (the Open WebUI-tuned operating rules, with all verification gates running as subagent tasks via `delegate_task` — fact-check, quiz-audit, review-gate), plus root docs (`AGENTS.md`, `README.md`, `OPENWEBUI.md`), `scripts/`, and `infra/`.

After final edits in a session (consistency checks pass, writes complete), ALWAYS commit and push:

1. `git add "Learning System" "Knowledge Wiki" "Skills" OPENWEBUI.md AGENTS.md README.md scripts/ infra/`
2. `git commit -m "<short summary of session changes>"`
3. `git push`

Verify with `git status` (clean) and `git log --oneline -1`. Never commit `Learning System/.tmp/` or `Pending Ingest.json` (gitignored).

### Git auth (automated)

- **Open Terminal container:** credentials at `~/.git-credentials` (0600) with `credential.helper store` — `git push` works without interactive auth.
- **WSL checkout (`/home/delightaheebwa/learning-system`):** auth via Windows **Git Credential Manager** (`credential.helper=.../git-credential-manager.exe` through WSL interop) — no `~/.git-credentials` here. If push fails, refresh the credential in Windows (Credential Manager → GitHub).