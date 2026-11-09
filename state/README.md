# Learner state

This directory holds the learner notebook, the knowledge wiki, and the state
tooling. It came from the former `learning-system` repo in the 2026-11-09 merge.
Its full commit history is preserved in this repo's history.

| Path | Contents |
| --- | --- |
| `Learning System/` | SRS tables, sessions, reviews, lessons, learning records. |
| `Knowledge Wiki/` | Wiki pages, raw sources, and the graph ledger. |
| `scripts/` | State tooling: `ops.py`, `learner_history.py`, `wiki_provenance.py`, `audit_openwebui.py`, `setup_openwebui.py`, and their tests. |
| `infra/` | Compose file, backup and restore scripts, access and version notes. |
| `Skills/` | Frozen Open WebUI skill snapshot. `state/scripts/` reads its `gate_pipe.py`, so it stays. The canonical teaching skills are at `.pi/skills/`. |
| `AGENTS.md` | State-tree conventions from the former repo. Root `AGENTS.md` governs the whole repo. |

Run `pi` from this directory. `install.sh` links `.pi/` here. It also links
`.agents/`, the retired Antigravity layer, which is unused.
See [`docs/README.md`](../docs/README.md) for the doc map and the open
integration work.

Whitespace in the imported files is left verbatim; the root `.gitattributes`
excludes `state/` from whitespace checks.
