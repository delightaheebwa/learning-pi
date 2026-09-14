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
| `/audit` | Read-only state consistency audit (MISSION/CURRICULUM/Profile/Active Concepts/index); reports loudly, never writes |

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
5. **Teach** — checkpoints, one idea + one practice each, always stoppable. The Tutor **pauses
   twice per checkpoint**: after the idea (invites questions before the practice) and after the
   practice grade (invites questions before the next checkpoint). It won't chain ahead of you.
6. **Pause anytime** with `/pause` (student-paced). It banks today's progress and keeps the lesson
   in-progress; `/continue` resumes at the next checkpoint.
7. **Lesson end** — cumulative quiz + Feynman explain-back. Then run `/ingest` to finalize (Clerk
   writes the wiki + Active Concepts, reconciles the position pointers, regenerates Learner History,
   and commits state).

**Math:** work on paper. Reply with just the final number or the letter (A–D). The Tutor won't ask
you to type LaTeX. It *will* now write its own math as LaTeX when your terminal can render it —
run learning sessions in **Ghostty** (or Kitty) and `pi-math` draws real formula images. In foot
or tmux, where pi-math can't draw, the Tutor falls back to plain Unicode.

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

If the Tutor forgets the tag in a **review**, the gate won't dead-end the session: an untagged
grade or quiz message is accepted when a bound `grade-audit` / `quiz-audit` receipt matches that
exact text (the receipt carries the question, answer, or batch, so it is real evidence). Ambiguous
or unbound messages are still withheld.

The Tutor writes its four handoff artifacts (lesson file, session note, learning record,
`Pending Ingest.json`) in **one batch at a pause or lesson end**, and an independent `tutor-audit`
checks that batch **once** before the summary renders. Mid-lesson it writes nothing to state.
Position/state files (MISSION, CURRICULUM, Learning Profile, Active Concepts, Mistakes, Learner
History) are reconciled by the **Clerk** at `/ingest`, not the Tutor.

Prompt templates also carry `[[FLOW:teach|resume|review|ingest]]` so the gate knows the mode
deterministically. You never type these.

---

## 6. The gate — reading the banners

If verification is missing, the gate withholds the turn and shows a banner. Common codes:

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_TURN_TAG` | message wasn't tagged | model self-corrects; if persistent, restart pi. **Not raised for an ingest summary after a clerk dispatch** (implicit `[[TURN:none]]`, verified by the clerk's `REVIEW_GATE_VERDICT` receipt), **for a review grade/quiz that a matching `grade-audit`/`quiz-audit` receipt binds**, **or for an untagged review close once the session note is written** (implicit `[[TURN:none]]`, verified by the `review-session-audit` receipt) |
| `NO_SCOUT_CONTEXT` | new lesson without a Scout run | let it run `scout`, or resume instead |
| `NO_FACT_CHECK_MATCH` | draft wasn't verified / changed after verifying | re-draft and re-verify |
| `FACT_CHECK_MISSING_DRAFT` | fact-check passed but its envelope had no `rendered_content` | re-send the claims WITH the exact draft in `rendered_content` |
| `FACT_CHECK_MISMATCH` | verified draft covers too little of the emitted text | emit the verified draft unchanged, or re-verify the new text |
| `FACT_CHECK_ISSUES` | verifier flagged a claim | apply the correction, re-verify |
| `NO_QUIZ_AUDIT_PASS` / `QUIZ_AUDIT_ISSUES` | questions not audited / leaked | fix and re-audit |
| `NO_GRADE_AUDIT_PASS` / `GRADE_MISMATCH` | grade unverified / conflicts with verifier | use the verifier's `correct_verdict` |
| `NO_REVIEW_GATE_PASS` / `REVIEW_GATE_ISSUES` | ingest review missing/flagged | Clerk must return a `REVIEW_GATE_VERDICT` marker |
| `NO_TUTOR_AUDIT` / `TUTOR_AUDIT_ISSUES` | handoff writes weren't checked / verifier flagged high-or-medium issues | dispatch `tutor-audit` on the handoff batch; fix and re-audit (lows pass as `PASS_WITH_FLAGS`) |
| `NO_REVIEW_SESSION_AUDIT` | review close wrote notes/rows but wasn't audited | dispatch `review-session-audit` on the exact writes, then summarize |
| `⚠️ REVIEW FLAGS SURFACED` | reviewer found issues in the ingest output **or** the review-session audit returned `ISSUES` | shown with a banner, **not** withheld or re-run (review close caps at 2 passes) |
| `⚠️ STATE AUDIT` | `audit_state.py` found errors or warnings still outstanding (touched ones are fixed in-flow) | run `/audit` for details |
| `⛔ UNVERIFIED` | retries exhausted (2); content shown unverified | review it manually |

The gate **fails open** on internal errors and **only acts in learning flows** — normal coding work
in the repo is never gated.

Subagent runs are async: the dispatch's tool result is only a fan-out notice, and the verdict
arrives later as a `subagent-notify` custom message. The gate mints verifier/clerk receipts from
that completion (from the dispatch result and from the custom notification), so a completed
`tutor-audit`/`review-gate`/`clerk` run is never lost — wait for it before emitting the summary.

---

## 7. Models

Set in `~/learning-pi/.pi/settings.json` (project scope only):

| Role | Model |
| --- | --- |
| Tutor (your session) | `glm-5.3-flash` |
| Scout / Clerk / verifiers | `deepseek-v4.1-flash` |
| Ingest reviewer (`review-gate`) | `muse-spark-1.3-contributor` |

Verifiers deliberately differ from the Tutor so verification is independent, and the ingest reviewer
runs on a different model from the deepseek Clerk. To change one, edit that file and restart pi —
nothing else needs to change.

---

## 8. State, git, and sync

- The Clerk commits and pushes **state only** (`Learning System/`, `Knowledge Wiki/`) to the
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
position pointers (MISSION / Learning Profile / Active Concepts track header vs the active lesson's
`Checkpoint N/M`), Active Concepts `Next Review` vs `Attempts.json`, wiki index vs wiki/source files,
stale host paths. It reports; it never writes. It now runs **automatically at ingest close (Clerk)
and review close (Tutor)**, and on demand via `/audit`. For mechanically-fixable findings it also
prints a `STATE_AUDIT_FIXES:` JSON array of remediation hints; the automatic flow fixes the error
**or warning** findings it touched using those hints, re-runs once, and surfaces the rest. A
`⚠️ STATE AUDIT` banner means errors or warnings remain outstanding.

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
- **Withheld banner says a `subagent` call omitted the `agent` field** → that dispatch minted no
  receipt; the model must pass `agent: "<name>"` (e.g. `tutor-audit`) in the subagent call.
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
