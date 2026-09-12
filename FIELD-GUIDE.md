# Field Guide — the Learning System in pi

A practical guide to running your spaced-repetition learning system from the pi coding agent.

---

## 1. The setup in one picture

```
~/learning-system     clone of delightaheebwa/learning-system   <- STATE (source of truth)
                        Learning System/ , Knowledge Wiki/
  .pi/                symlinks -> ~/learning-pi/.pi             <- local-only, git-excluded (!! )

~/learning-pi         the pi control layer (this repo)          <- skills, agents, prompts, gate
```

- **State** lives in the original repo and is shared with Open WebUI. Only state is committed there.
- **The pi layer** lives here; `install.sh` symlinks it into the checkout. It never touches state.
- **You run pi from the state checkout:**
  ```bash
  cd ~/learning-system && pi
  ```
  First run only: approve/trust the project (`.pi/` resources load only after trust).

---

## 2. Slash commands (the whole interface)

| Command | What it does |
| --- | --- |
| `/teach <topic>` | New topic: Scout gathers live sources → probe → plan → teach |
| `/lesson` | Next curriculum lesson (sequential within the phase) |
| `/continue` | Resume a paused lesson at its checkpoint (no Scout needed) |
| `/pause` | Stop cleanly: exit ticket, partial lesson file, bank progress via Clerk |
| `/review` | Spaced-repetition review session (up to 5 concepts) |
| `/ingest <content or URL>` | Standalone ingest via Clerk (also used after a lesson handoff: `/ingest` with no args) |

Skills are loaded automatically; you rarely call them by hand. If you want to force one:
`/skill:learning-system`, `/skill:learning-teach`.

---

## 3. A normal teaching session

1. **Start** — `cd ~/learning-system && pi`, then run `/lesson` (next in curriculum) or
   `/teach eigenvalue decomposition` (a topic).
2. **Scout** runs first for a new lesson: fetches the live curriculum doc + its Further Reading,
   hashes them, writes a digest to `Learning System/.tmp/`, and posts `SCOUT DIGEST:`.
3. **Probe** — a small batch of questions, always with an "I don't know". Answer with a confidence
   tag (`sure` / `hunch` / `no idea`). Feedback is withheld until the batch ends.
4. **Plan** — a Mermaid dependency graph + what to skip/expand/reframe. You can push back.
5. **Teach** — checkpoints, one idea + one practice each, always stoppable.
6. **Pause anytime** with `/pause` (student-paced). It banks today's progress and keeps the lesson
   in-progress; `/continue` resumes at the next checkpoint.
7. **Lesson end** — cumulative quiz + Feynman explain-back. Then run `/ingest` to finalize (Clerk
   writes the wiki + Active Concepts and commits state).

**Math:** work on paper. Reply with just the final number or the letter (A–D). The Tutor won't ask
you to type LaTeX.

---

## 4. Review sessions (`/review`)

- Queue: up to 2 due mistakes (priority) + 3 due concepts, shuffled.
- One question, one short answer per concept.
- Every grade is verified by an independent `grade-audit` subagent before it is shown.
- Grades update `Attempts.json` (advisory mastery), `📚 Active Concepts.md`, and `🧯 Mistakes.md`.

---

## 5. What the model emits (and why you won't see it)

The Tutor is required to start every message with a **turn tag**, which the gate strips before it
reaches you:

| Tag | Meaning | Required before it renders |
| --- | --- | --- |
| `[[TURN:claims]]` | teaching / plan | a `fact-check` whose draft matches the text |
| `[[TURN:quiz]]` | question batch | a PASS `quiz-audit` |
| `[[TURN:grade]]` | grading your answer | an agreeing `grade-audit` |
| `[[TURN:none]]` | transitions, summaries | nothing |

Prompt templates also carry `[[FLOW:teach|resume|review|ingest]]` so the gate knows the mode
deterministically. You never type these.

---

## 6. The gate — reading the banners

If verification is missing, the gate withholds the turn and shows a banner. Common codes:

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_TURN_TAG` | message wasn't tagged | model self-corrects; if persistent, restart pi |
| `NO_SCOUT_CONTEXT` | new lesson without a Scout run | let it run `scout`, or resume instead |
| `NO_FACT_CHECK_MATCH` | draft wasn't verified / text changed after verifying | re-draft and re-verify |
| `FACT_CHECK_ISSUES` | verifier flagged a claim | apply the correction, re-verify |
| `NO_QUIZ_AUDIT_PASS` / `QUIZ_AUDIT_ISSUES` | questions not audited / leaked | fix and re-audit |
| `NO_GRADE_AUDIT_PASS` / `GRADE_MISMATCH` | grade unverified / conflicts with verifier | use the verifier's `correct_verdict` |
| `NO_REVIEW_GATE_PASS` / `REVIEW_GATE_ISSUES` | ingest review missing/flagged | Clerk must return a PASS marker |
| `⛔ UNVERIFIED` | retries exhausted (2); content shown unverified | review it manually |

The gate **fails open** on internal errors and **only acts in learning flows** — normal coding work
in the repo is never gated.

---

## 7. Models

Set in `~/learning-pi/.pi/settings.json` (project scope only):

| Role | Model |
| --- | --- |
| Tutor (your session) | `glm-5.3-flash` |
| Scout / Clerk / verifiers | `deepseek-v4.1-flash` |

Verifiers deliberately differ from the Tutor so verification is independent. To change one, edit
that file and restart pi — nothing else needs to change.

---

## 8. State, git, and sync

- The Tutor/Clerk commit and push **state only** (`Learning System/`, `Knowledge Wiki/`) to the
  original repo, per `Learning System/AGENTS.md`.
- The pi layer is its own repo; update it with `cd ~/learning-pi && git pull`.
- **Open WebUI also writes this state.** Pull before a session and don't run both writers at once:
  ```bash
  cd ~/learning-system && git pull
  ```
- Never commit `.pi/` (it's in `.git/info/exclude`) or `Pending Ingest.json` / `.tmp/` (gitignored).

---

## 9. The consistency audit (read-only)

```bash
python3 ~/learning-pi/pi/audit_state.py --root ~/learning-system
```

Checks: MISSION vs CURRICULUM positions, lesson files vs curriculum rows, Active Concepts dates,
wiki index vs wiki/source files, stale host paths. It reports; it never writes. Run it if something
feels off.

---

## 10. Troubleshooting

- **Gate never blocks / tags visible in output** → the project isn't trusted or the extension didn't
  load. `cd ~/learning-system && pi`, approve trust, then `/reload`.
- **`/skill:...` or slashes missing** → start pi from `~/learning-system`; project `.pi/` loads only
  there (after trust).
- **Scout/verifier web fetches fail** → the agents load `pi-web-access` via an absolute path in their
  frontmatter; verify `~/.pi/agent/npm/node_modules/pi-web-access/index.ts` exists.
- **Verifier can't read the repo** → the Tutor's cwd must be `~/learning-system`.
- **Model keeps forgetting turn tags** → consider a stronger Tutor model in `.pi/settings.json`.
- **State looks stale after Open WebUI use** → `git pull` in `~/learning-system`.

---

## 11. Maintenance

```bash
# update the pi layer
cd ~/learning-pi && git pull && ./install.sh ~/learning-system

# update state
cd ~/learning-system && git pull

# if the canonical Skills/ change, re-derive the sanitized pi copies and diff
diff -u ~/learning-system/Skills/learning-system/SKILL.md \
        ~/learning-pi/.pi/skills/learning-system/SKILL.md
```

The pi skills are **sanitized vendored copies** — no Open WebUI plumbing, no host paths, no stale
state. The originals stay untouched for Open WebUI.
