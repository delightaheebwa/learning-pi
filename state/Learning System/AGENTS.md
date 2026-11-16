# Learning System: agent conventions

This folder and `Knowledge Wiki/` are the active learner state. The teaching and
review procedures are canonical in `learning-pi/.pi/skills/`, and the copy under
`Skills/` is a frozen legacy snapshot. This file holds only the local
consistency checks and the state-editing conventions.

## Repo location

The learner state lives in `~/learning-pi/state`, inside the `learning-pi` repo.
That repo's GitHub remote (https://github.com/delightaheebwa/learning-pi) is the
durable source of truth. There is no separate state repo, WSL maintenance
checkout, or Open Terminal container checkout to sync. The Open WebUI face is a
legacy runtime driven by `pi-bridge`, and it holds chat transcripts, not state.

## Multi-file consistency check

A multi-file session touches the wiki page, the index, the log, Active Concepts,
and the session note. After such a session, re-read every touched file and
verify these items:

- A wiki page was created, so `Knowledge Wiki/index.md` lists it under Concepts.
- An ingest ran, so `Knowledge Wiki/log.md` has today's entry.
- A concept was reviewed or added, so `last_reviewed` is today in
  `Core/📚 Active Concepts.md`.
- A concept was reviewed or added, so `next_review` is calculated from the
  current interval.
- A wiki link in a table points to a page that exists.
- A session note exists in `Sessions/` with today's date.

Teaching sessions also verify these items, per
`Skills/learning-teach/SKILL.md`:

- The lesson file exists in `Learning System/Lessons/` with today's date.
  On `/pause`, the partial file carries a `Status: paused at Checkpoint N/M, mini K/L`
  line and a `Resume from:` pointer to the next mini-checkpoint or the
  checkpoint practice. The curriculum row reads `in-progress (paused N/M)`, and
  the Scout digest is kept.
- The learning record is numbered `highest + 1` in
  `Learning System/Learning Records/`, with the Bloom level and the Feynman
  explain-back in Evidence. This applies to the final checkpoint only. A pause
  writes a session note and a partial ingest, with no full record.
- The curriculum lesson advanced only if practice, retrieval, and Feynman all
  passed. The status in `Learning System/CURRICULUM.md` matches reality.
- New concepts from teaching start `developing`, with `last_reviewed` today and
  `next_review` at +3d.
- Glossary additions are promoted only with your approval.

Report ✅ or ❌ for each item, then fix failures immediately.

## Git sync

The working copy is this repo at `~/learning-pi`, with remote `origin` on the
public `main` branch, and the state is `~/learning-pi/state`. There is no
container or WSL checkout to sync. Pull before a session and work from the
single checkout.

The Clerk commits the state at ingest or review close, after the final edits,
when the consistency checks pass and the writes are complete. For manual edits,
commit from the repo root with the rest of the work:

1. `git add "state/Learning System" "state/Knowledge Wiki"`
2. `git commit -m "<short summary of session changes>"`
3. `git push`

Verify with `git status` for a clean tree and `git log --oneline -1`.
`Learning System/.tmp/` and `Pending Ingest.json` are gitignored, so never
commit them.

### Git auth

Use your normal git credentials for `learning-pi`, which is an HTTPS clone. See
the root `README.md`. This layout has no container credential store and no WSL
credential-manager setup.
