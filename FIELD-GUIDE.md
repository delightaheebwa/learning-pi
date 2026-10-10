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
| `/continue` | Resume a paused lesson at its next mini-checkpoint (no Scout needed) |
| `/pause` | Stop cleanly: exit ticket, partial lesson file, bank progress via Clerk |
| `/review` | Spaced-repetition review session (Review Scout builds the queue → up to 5 concepts → review-clerk persists) |
| `/solo` | AI-free closed-book check (Review Scout builds the queue; teaching, hints, and figures are withheld by the gate; attempts recorded `mode:"solo"` to feed the independence gate) |
| `/ingest <content or URL>` | Standalone ingest via Clerk (also used after a lesson handoff: `/ingest` with no args) |
| `/show <concept>` | Ask for a verified visualization of a concept (or to play with one). Opt-in; teach/resume only. `/viz` reopens the interactive explorer or toggles auto-open |
| `/audit` | Read-only state consistency audit (MISSION/CURRICULUM/Profile/Active Concepts/index); reports loudly, never writes |

Skills are loaded automatically; you rarely call them by hand. If you want to force one:
`/skill:learning-system`, `/skill:learning-teach`.

---

## 3. A normal teaching session

1. **Start** — `cd ~/learning-system && pi`, then run `/lesson` (next in curriculum) or
   `/teach eigenvalue decomposition` (a topic).
2. **Scout** runs first for a new lesson: fetches the live curriculum doc + its Further Reading,
   hashes them, writes a digest to `Learning System/.tmp/`, and posts `SCOUT DIGEST:`. The digest
   has a **7-day TTL** — if it is stale, Scout re-runs before teaching new material (a stale
   digest's source excerpts are never authoritative).
3. **Probe** — a small batch of questions, always with an "I don't know". Answer with a confidence
   tag (`sure` / `hunch` / `no idea`). Feedback is withheld until the batch ends.
4. **Plan** — a Mermaid dependency graph + what to skip/expand/reframe. You can push back.
5. **Teach** — a checkpoint is delivered as **mini-checkpoints**: one atomic idea per message,
   each followed by a pause that invites your questions and tangents. Each idea is delivered
   through **elicit → attempt → state → check-and-extend** — it asks what you predict (grounded in
   your Learner History and past learning records), nudges with at most two guiding questions if
   you're off, then asks *you* to state the idea in your own words and checks that before adding
   only what you missed. Say **"just tell me"** and it gives the idea at once (logged as a
   dependency event), still closing with one minimal one-line generation. After the last
   mini-checkpoint comes the checkpoint's single practice, then another pause after grading. It
   won't chain ahead of you or dump a whole checkpoint at once.
6. **Pause anytime** with `/pause` (student-paced). It banks today's progress and keeps the lesson
   in-progress; `/continue` resumes at the next mini-checkpoint (the pause pointer records
   `Checkpoint N/M, mini K/L`).
7. **Lesson end** — cumulative quiz + Feynman explain-back. Then run `/ingest` to finalize: Clerk
   writes the wiki + Active Concepts, reconciles the position pointers, runs the state audit,
   regenerates Learner History, and commits state; then the **Tutor** dispatches an independent
   `review-gate` on the wiki pages Clerk wrote (the Clerk does not gate itself).

**Math:** work on paper. Reply with just the final number or the letter (A–D). The Tutor won't ask
you to type LaTeX. It *will* now write its own math as LaTeX when your terminal can render it —
run learning sessions in **Ghostty** (or Kitty) and `pi-math` draws real formula images. In foot
or tmux, where pi-math can't draw, the Tutor falls back to plain Unicode.

---

## 4. Review sessions (`/review`)

- **Review Scout** runs first: it reads your learner state in one bundle and builds the queue.
- Queue: up to 2 due mistakes (priority) + 3 due concepts, shuffled.
- One question, one short answer per concept.
- Every grade is verified by an independent `grade-audit` subagent before it is shown. When several questions are answered in one reply, all answers go in ONE batched `items[]` envelope (one subagent call per reply, not per answer).
- The Reviewer writes nothing. At the close, **review-clerk** writes the Review note(s) + session note, updates `Attempts.json` / `📚 Active Concepts.md` / `🧯 Mistakes.md`, runs the state audit, and commits; then the Reviewer dispatches a `review-session-audit` over those writes.

The review flow mirrors the teaching flow: `review-scout` → Reviewer (this session) → `review-clerk`, with the close checked by `review-session-audit` — exactly like `scout` → Tutor → `clerk` with `tutor-audit`.

### Daily reminder and the bar indicator

Reviews are meant to happen daily. Two things track that, both driven by
`bin/pi-review-status` (a `Session…Review…<date>.md` filename match on the
calendar date the session ran — so a review finished at 1am is that day's, not
the previous day's):

- the **`local.pi-review` Omarchy bar widget** shows `R` (pending), `R✓` (done),
  or `R✗` (missed, urgent color once it is late) — but only in the evening
  window 18:00–03:59, so the daytime bar stays clean. Left-click launches `pi`
  in the checkout.
- the **desktop reminder** (systemd timer at 23:00 and 00:30) sends one
  notification per missed day. The old floating terminal popup was removed.

Install/repair both with `~/learning-pi/omarchy/install.sh`.

---

## Visualizations (opt-in)

Visualizations are figures the Tutor draws in the terminal for a concept that a picture explains
better than prose. They are **opt-in** and **teach/resume only** — the Tutor may offer once per
mini-checkpoint ("want a picture of this?"), and you can ask anytime ("show me…", "let me play
with…", or `/show <concept>`).

- The `viz` subagent authors a **declarative spec** (data + labels only — plots, bars, tables,
  diagrams), the `viz-audit` subagent verifies the spec *and* the words around it, and the figure is
  emitted as its own `[[TURN:viz]]` message.
- **There are two surfaces, both in the same terminal — no separate window or process:**
  1. the **inline figure** — on an image-capable terminal (Ghostty/Kitty/WezTerm/iTerm2; the
     `SUPER+SHIFT+L` launcher uses Ghostty) it is a **real image** rendered in the message, part of the
     transcript you scroll back through. On foot/tmux it falls back to Unicode/braille art; and
  2. the **explorer** — when the spec is interactive, a live panel `viz-mode` draws *centered over*
     the chat, already running, no command to type. Drive it with the keyboard *or the mouse*: drag a
     parameter slider, click the frame arrows, or click the plot to read a data point. `Esc` closes it
     and returns you to the prompt; `/viz` reopens it. (Mouse events reach the panel in fullscreen TUI
     mode, which the learning settings enable; every action also has a keyboard path.)
- A `viz` spec can carry `params` + a `formula` (an arithmetic expression in `x` and the params) for
  a relationship you can vary, `frames` for an algorithm stepped one stage at a time, and `arrows`
  for vectors (e.g. eigenvectors). A spec with neither `params`+`formula` nor `frames` is static and
  only shows the inline figure.
- The spec travels as a ` ```viz ` JSON block in the message; the raw JSON is what gets stored, the
  rendered figure is what you see. `/viz svg` exports the last figure as SVG and `/viz png` as PNG
  under `Learning System/.tmp/viz/`; `/viz open` also opens the PNG in the desktop viewer.
- In a `/review`, a visualization request is parked until the review's grading is done.

## 5. What the model emits (and why you won't see it)

The Tutor is required to start every message with a **turn tag**, which the gate strips before it
reaches you:

| Tag | Meaning | Required before it renders |
| --- | --- | --- |
| `[[TURN:claims]]` | teaching / plan | a `fact-check` whose draft matches the text |
| `[[TURN:quiz]]` | question batch | a PASS `quiz-audit` |
| `[[TURN:grade]]` | grading your answer | an agreeing `grade-audit` |
| `[[TURN:viz]]` | a visualization (a ` ```viz ` spec + supporting words) | a `viz-audit` whose spec matches the emitted block and whose draft covers the turn (missing → `NO_VIZ_AUDIT`) |
| `[[TURN:none]]` | transitions, summaries | nothing |

If the Tutor forgets the tag in **any teaching/review flow**, the gate won't dead-end the session
on a grade or quiz turn: an untagged grade/quiz message is accepted when a `grade-audit` /
`quiz-audit` receipt matches that exact text (the receipt carries the question, answer, or batch),
or when exactly one gate type has a valid pending receipt (async verifiers report via a completion
notification that carries no draft, so a bound match is impossible there). Ambiguous messages (both
gate types pending) or ones with no receipt at all are still withheld, and `claims`/`none` are never
inferred.

The Tutor writes its four handoff artifacts (lesson file, session note, learning record,
`Pending Ingest.json`) in **one batch at a pause or lesson end**, and an independent `tutor-audit`
checks that batch **once** before the summary renders. Mid-lesson it writes nothing to state.
Position/state files (MISSION, CURRICULUM, Learning Profile, Active Concepts, Mistakes, Learner
History) are reconciled by the **Clerk** at `/ingest`, not the Tutor.

The review flow is symmetric: `review-scout` gathers context + the due queue at the start (the first
review turn is withheld `NO_REVIEW_CONTEXT` until it runs), the Reviewer writes nothing, and
`review-clerk` persists the Review note(s)/session note and reconciles the touched rows at the close;
`review-session-audit` checks those writes before the summary renders.

Prompt templates also carry `[[FLOW:teach|resume|review|ingest]]` so the gate knows the mode
deterministically. You never type these.

---

## 6. The gate — reading the banners

If verification is missing, the gate withholds the turn and shows a banner. Common codes:

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_TURN_TAG` | message wasn't tagged | model self-corrects; if persistent, restart pi. **Not raised for an ingest summary after a clerk dispatch** (implicit `[[TURN:none]]`, verified by the clerk's `REVIEW_GATE_VERDICT` receipt), **for a grade/quiz turn in teach/resume/review that a `grade-audit`/`quiz-audit` receipt binds** — or when exactly one gate type has a valid pending receipt (async completion) — **or for an untagged review close once the session note is written** (implicit `[[TURN:none]]`, verified by the `review-session-audit` receipt) |
| `NO_SCOUT_CONTEXT` | new lesson without a Scout run | let it run `scout`, or resume instead |
| `NO_REVIEW_CONTEXT` | `/review` without a Review Scout run | let it run `review-scout` to build the queue |
| `NO_FACT_CHECK_MATCH` | draft wasn't verified / changed after verifying | re-draft and re-verify |
| `FACT_CHECK_MISSING_DRAFT` | fact-check passed but its envelope had no `rendered_content` | re-send the claims WITH the exact draft in `rendered_content` |
| `FACT_CHECK_MISMATCH` | verified draft covers too little of the emitted text | emit the verified draft unchanged, or re-verify the new text |
| `FACT_CHECK_ISSUES` | verifier flagged a claim | apply the correction, re-verify |
| `NO_QUIZ_AUDIT_PASS` / `QUIZ_AUDIT_ISSUES` | questions not audited / leaked | fix and re-audit |
| `QUIZ_AUDIT_STALE` / `GRADE_AUDIT_STALE` | a valid receipt exists but does not bind this message — either the emission differs from what was audited, or the dispatch envelope was the wrong shape (quiz: `items[]` instead of `questions_json`, or a questions-only envelope missing `rendered_content` = the full batch text; grade: no question/answer/verdict) so there is nothing to bind | re-emit the audited text, or re-dispatch the verifier with the correctly shaped envelope carrying the full batch in `rendered_content` (never re-audit an already-bound draft) |
| `NO_GRADE_AUDIT_PASS` / `GRADE_MISMATCH` | grade unverified / conflicts with verifier | use the verifier's `correct_verdict` |
| `NO_VIZ_AUDIT` / `VIZ_AUDIT_ISSUES` / `VIZ_AUDIT_STALE` | a viz turn's audit is missing / flagged / not bound to the emitted spec+words | dispatch ONE foreground `viz-audit` with `spec` + `rendered_content` = the full turn draft, then emit the audited draft unchanged |
| `VIZ_SPEC_INVALID` / `VIZ_REQUIRES_OWN_TURN` | a viz turn has no parseable ` ```viz ` spec, or a viz block sits in a claims/none turn | re-emit as a standalone `[[TURN:viz]]` message with one valid spec |
| `NO_REVIEW_GATE_PASS` / `REVIEW_GATE_ISSUES` | ingest review missing/flagged, or the receipt named no `target_files` | after the Clerk returns `CLERK_WRITES`, dispatch ONE independent `review-gate` with `target_files` naming the wiki pages it wrote |
| `⚠️ INGEST GATE` | the review verdict was relayed by the Clerk's own output, not an independent `review-gate` run | dispatch a `review-gate` on the Clerk's writes before trusting the summary |
| `⚠️ REVIEW GATE` / `⚠️ REVIEW SESSION GATE` | a review-family verdict carried no `evidence` list (what it read/checked) | treat the pass as unsubstantiated; re-run the gate so it names its evidence |
| `⚠️ SOURCES INCOMPLETE` | Scout could not fetch one or more sources (`failed_refs` non-empty) | teach around the gaps; consider re-scouting or adding a fallback source |
| `⚠️ SCOUT DIGEST UNVERIFIED` | Scout finished without a parseable `SCOUT_DIGEST:` receipt | verify the digest exists on disk; re-run Scout if the lesson context looks thin |
| `⚠️ REVIEW CONTEXT INCOMPLETE` | Review Scout could not read one or more state items | review around the gaps; re-run `review-scout` if the queue looks thin |
| `⚠️ REVIEW SCOUT DIGEST UNVERIFIED` | Review Scout finished without a parseable `REVIEW_SCOUT_DIGEST:` receipt | verify the digest exists on disk; re-run `review-scout` |
| `NO_TUTOR_AUDIT` / `TUTOR_AUDIT_ISSUES` | handoff writes weren't checked (or the receipt named no `files`) / verifier flagged high-or-medium issues | dispatch `tutor-audit` on the handoff batch with `files:[...]`; fix and re-audit (lows pass as `PASS_WITH_FLAGS`) |
| `NO_REVIEW_SESSION_AUDIT` | review close (review-clerk writes) wasn't audited, or the receipt named no `written_files` | dispatch `review-session-audit` with `written_files:[{path},...]` on the exact writes, then summarize |
| `⚠️ REVIEW FLAGS SURFACED` | reviewer found issues in the ingest output **or** the review-session audit returned `ISSUES` | shown with a banner, **not** withheld or re-run (review close caps at 2 passes) |
| `⚠️ STATE AUDIT` | `audit_state.py` found **warnings** still outstanding (touched ones are fixed in-flow); warnings never block | run `/audit` for details |
| `STATE_AUDIT_ERRORS` | at the ingest/review close, `audit_state.py` reported **errors** (state drift); the close summary is withheld until they are fixed | apply the `STATE_AUDIT_FIXES` hints (or `/audit` for the list), re-run the audit clean, then re-emit the summary |
| `⛔ UNVERIFIED` | retries exhausted (2); content shown unverified | review it manually |

The gate **fails open** on internal errors and **only acts in learning flows** — normal coding work
in the repo is never gated. A partial generation (the model errored, was aborted, or hit the token
cap mid-message) passes through ungated and **does not consume a receipt**, so the retried message
still binds to it — this is why an interrupted grade turn no longer dead-ends on
`NO_GRADE_AUDIT_PASS`.

A verifier/worker dispatch runs through the **`dispatch` helper**:
`dispatch({ agent, task: { ...envelope... } })` — foreground, with the envelope as an **object**. It
runs the child through pi-subagents' structured delegation bridge and returns the verdict in the tool
result, so the receipt is minted before you emit; wait for it before emitting the summary. (The
gate still mints legacy `subagent` receipts from a `subagent-notify` completion notification, but the
learning layer no longer dispatches that way.)

---

## 7. Models

Set in `~/learning-pi/.pi/settings.json` (project scope only):

| Role | Model |
| --- | --- |
| Tutor (your session) | `glm-5.3-flash` |
| Scout / Clerk / Review Scout / Review Clerk | `deepseek-v4.1-flash` |
| Gate verifiers (`fact-check` / `quiz-audit` / `grade-audit` / `tutor-audit` / `review-session-audit`) | `muse-spark-1.3-contributor` (high) |
| Ingest reviewer (`review-gate`) | `muse-spark-1.3-contributor` |

Verifiers run on preferred models for cost/availability, but this is a **default, not a guarantee** —
when the preferred model is unavailable a verifier may run on the same model as the Tutor or Clerk,
and that is acceptable. The gate records which model ran (see the per-run `model` in the subagent
artifacts) but does not enforce separation. To change a default, edit that file and restart pi.

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
Scout-digest TTL (warns when the active lesson's `.tmp/context-*.json` is older than 7 days), stale
host paths. It reports; it never writes. It now runs **automatically at ingest close (Clerk)
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
- **Withheld banner says a dispatch omitted the `agent` field** → that dispatch minted no receipt;
  the model must name the verifier (e.g. `tutor-audit`) as `dispatch({ agent: "tutor-audit", ... })`.
- **Tool result is `Validation failed for tool "subagent": - task: must be string`, or a
  `subagent` `workflow`/`args` error** → the model used the raw `subagent` tool instead of
  `dispatch`. pi-subagents requires `subagent.task` to be a JSON **string** (an object fails), which
  is exactly why the learning layer dispatches through `dispatch({ agent, task: { ...envelope... } })`
  — it takes the envelope as an object and serializes it. `dispatch` runs the child through the
  structured delegation bridge and mints the receipt; the raw `subagent` `workflow`/`args` forms are
  blocked and redirected to `dispatch`. No `subagents_enable` step is needed for `dispatch`.
- **`GRADE_AUDIT_STALE` loops on a grade + repair turn** → the grade-audit binds only the graded
  question/answer/verdict, so it cannot cover the repair prose. Dispatch a `fact-check` with
  `rendered_content` = the full emitted turn (the gate accepts the turn when the grade-audit covers
  the verdicts AND the fact-check covers the prose), or split it into a verdict-only `[[TURN:grade]]`
  and a separate `[[TURN:claims]]` repair. Never re-dispatch the grade-audit to cover repair prose.
- **`GRADE_AUDIT_STALE` on a verdict-only grade turn** → the turn presents just the graded answers
  and wants no fact-check. This is a binding bug if it persists: the grade-audit binds the graded
  question/answer/verdict, and a terse confirmation ("Correct on all three: W1 B, W2 C, W3 A") does
  not repeat the question text. Diagnostic: dispatch a `fact-check` with `rendered_content` = the
  emitted verdict text and re-emit it (or remove any teaching prose so the turn is verdict-only).
- **`QUIZ_AUDIT_STALE` on a clean PASS** (or a write-gate PASS judged unsubstantiated) → the judge
  scored the PASS unsubstantiated because the verifier emitted no evidence. The verifier's verdict
  JSON must carry a non-empty `evidence` list naming what it checked (the `quiz-audit` and
  `tutor-audit` agents require this); re-dispatch it.
- **State looks stale after Open WebUI use** → `git pull` in `~/learning-system`.

---

## 11. Provenance audit (after the fact)

`audit_gates.py` reconstructs, from a pi session transcript, which verifier runs actually backed
each claimed verdict. It is read-only and diagnostic — the live gate does not depend on it.

```bash
python3 ~/learning-pi/pi/audit_gates.py                 # newest learning-system session
python3 ~/learning-pi/pi/audit_gates.py --session <path.jsonl>
python3 ~/learning-pi/pi/audit_gates.py --json          # machine-readable
```

It correlates every `subagent` dispatch with its artifact metadata and reports: dispatches with no
artifact, runs that exited non-zero, runs the harness acceptance layer `rejected` (which the gate may
still have consumed), review verdicts with no backing run, clerk-relayed review provenance, and
`STATE_AUDIT_VERDICT` markers with no `audit_state.py` invocation. It also prints the model each run
used. Exit 1 when it finds an error-level issue.

### Judge raw dump (diagnosing a withhold the ledger can't explain)

When a block isn't obvious from `decisions.ndjson` — e.g. a `QUIZ_AUDIT_STALE` on a clean PASS — the
judge's exact input and output are the missing evidence. Export `LEARNING_GATE_JUDGE_DUMP=1` and
reproduce; each judge call appends `{at, model, user, response}` to
`~/.pi/agent/learning-gate/judge-raw.ndjson`. `user` is the serialized `JUDGE PACKAGE` (the receipts
the judge saw, their `boundText`, the emitted turn) and `response` is the model's raw JSON
(`bindings`/`substantiveness`/`reason`). Set it to a path to write elsewhere. Off by default; it
never changes gating.

---

## 12. Maintenance

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
