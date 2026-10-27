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
| `/teach <topic>` | New topic: Scout gathers live sources → entry gate → triage → targeted attacks |
| `/lesson` | Next curriculum lesson (sequential within the phase) |
| `/continue` | Resume a paused lesson at its next mini-checkpoint (no Scout needed) |
| `/pause` | Stop cleanly: exit ticket, partial lesson file, bank progress via Clerk |
| `/review` | Spaced-repetition review session (Review Scout builds the queue → up to 5 concepts → review-clerk persists) |
| `/solo` | AI-free closed-book check (Review Scout builds the queue; teaching and hints are withheld by the gate; attempts recorded `mode:"solo"` to feed the independence gate) |
| `/ingest <content or URL>` | Standalone ingest via Clerk (also used after a lesson handoff: `/ingest` with no args) |
| `/audit` | Read-only state consistency audit (MISSION/CURRICULUM/Profile/Active Concepts/index); reports loudly, never writes |

Skills are loaded automatically; you rarely call them by hand. If you want to force one:
`/skill:learning-system`, `/skill:learning-teach`.

---

## 3. A normal teaching session

1. **Start** — `cd ~/learning-system && pi`, then run `/lesson` (next in curriculum) or
   `/teach eigenvalue decomposition` (a topic).
2. **Scout** runs first for a new lesson: fetches the live curriculum doc + its Further Reading,
   hashes them, writes a digest to `Learning System/.tmp/`, and posts `SCOUT_DIGEST:`. (Scout's
   human-readable heading is `SCOUT DIGEST:` with a space; the machine-readable receipt line
   the gate parses is `SCOUT_DIGEST:` with an underscore.) The digest
   has a **7-day TTL** — if it is stale, Scout re-runs before teaching new material (a stale
   digest's source excerpts are never authoritative). The Tutor then dispatches ONE independent
   `scout-audit` on the digest — the lesson-start mirror of the ingest `review-gate`: it checks
   completeness (every Further Reading URL fetched or explicitly failed, excerpts + `theory`
   lines + prereqs present, raw files on disk) and fact-checks the synthesis against the raw
   sources. A missing audit withholds the first teaching turn; `ISSUES` surfaces as a banner
   and never blocks.
3. **Entry gate** — the Tutor never teaches cold. It asks for your notes/material and a **closed-book
   model in your own words** first; if you bring notes but no model, it asks for the model before
   reading anything. It will not preview the mechanism or name the right framing.
4. **Measure (optional)** — if your model is ambiguous or hedged, one short bracket probe (MCQs,
   marked `context:"probe"`) locates your edge before triage. It is diagnostic, never a preview.
5. **Triage** — the Tutor buckets each claim in your model as `solid` / `missing` / `suspect` and
   shows a compact table with the attack order. Off-path holes stay in the table but are not
   attacked this session; prerequisites are attacked first.
6. **Attack** — one targeted attack per turn, in dependency order: mechanism press, counterexample
   trap, perturbation, source clash, sabotage, or synthesis clash. You predict before each attack;
   the Tutor exposes the hole and never fills it. Say **"just tell me"** and it gives the idea at
   once (logged as a dependency event), still closing with one minimal generation.
6a. **Repair** — if your own repair attempt fails (or the gap is one you never learned), the Tutor
   switches into **repair mode** for that one gap: it starts from what you already hold and teaches
   one motivated step at a time (asking you first where you can reason it out), checking each step.
   It cannot move on until you pass a fresh check on a new surface and restate the patched bit in
   your own words. The next attack is held back until then.
7. **Patch (v2)** — you restate the repaired model in your own words; the Tutor checks it and adds
   only what you missed, never rewriting your words.
8. **Graduate** — a naive-student clone tries to use your patched model; if it fails, the hole
   routes back to one more attack. A concept cannot reach `solid` without passing.
9. **Pause anytime** with `/pause` (student-paced). It banks today's progress and keeps the lesson
   in-progress; `/continue` resumes at the next attack (the pause pointer records
   `Checkpoint N/M, mini K/L`).
10. **Lesson end** — cumulative quiz + Feynman explain-back. Then run `/ingest` to finalize: Clerk
   writes the wiki + Active Concepts, reconciles the position pointers, runs the state audit,
   regenerates Learner History, and commits state; then the **Tutor** dispatches an independent
   `review-gate` on the wiki pages Clerk wrote (the Clerk does not gate itself).

**Math:** work on paper. Reply with just the final number or the letter (A–D). The Tutor won't ask
you to type LaTeX. It *will* now write its own math as LaTeX when the front-end can render it —
run learning sessions in **Ghostty** (or Kitty) and `pi-math` draws real formula images, or use
the **Open WebUI** face, where KaTeX renders the LaTeX. In foot or tmux, where pi-math can't draw,
the Tutor falls back to plain Unicode.

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

## 5. What the model emits (and why you won't see it)

The Tutor is required to start every message with a **turn tag**, which the gate strips before it
reaches you:

| Tag | Meaning | Required before it renders |
| --- | --- | --- |
| `[[TURN:claims]]` | teaching / plan | a `fact-check` whose draft matches the text |
| `[[TURN:quiz]]` | question batch | a PASS `quiz-audit` |
| `[[TURN:grade]]` | grading your answer | an agreeing `grade-audit` |
| `[[TURN:ui]]` | an interactive widget (its own turn) | a passing `ui-audit` bound to the emitted ```openui payload and covering the prose |
| `[[TURN:none]]` | transitions, summaries | nothing |

A widget is delivered as a same-origin Open WebUI embed below the prose
(`/static/openui/<version>/widget.html#…`, with the pinned OpenUI bundle self-hosted and
`connect-src 'none'`); Mermaid and HTML fences render natively in the client. See
[`bridge/README.md`](bridge/README.md).

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
| `NO_SCOUT_AUDIT_PASS` | Scout ran but no independent `scout-audit` covers its digest, or the receipt named no `digest` | dispatch ONE independent `scout-audit` with `digest` + `raw_files` naming the lesson-start digest; fix via re-scout + re-audit on ISSUES (no cycle cap) |
| `⚠️ SCOUT AUDIT FLAGS SURFACED` | the scout-audit reported issues on the digest (missing source, invented excerpt, smoothed-over contradiction) | teaching proceeds with flags outstanding; fix the digest via re-scout and re-audit |
| `NO_REVIEW_CONTEXT` | `/review` without a Review Scout run | let it run `review-scout` to build the queue |
| `NO_FACT_CHECK_MATCH` | draft wasn't verified / changed after verifying | re-draft and re-verify |
| `FACT_CHECK_MISSING_DRAFT` | fact-check passed but its envelope had no `rendered_content` | re-send the claims WITH the exact draft in `rendered_content` |
| `FACT_CHECK_MISMATCH` | verified draft covers too little of the emitted text | emit the verified draft unchanged, or re-verify the new text |
| `FACT_CHECK_ISSUES` | verifier flagged a claim | apply the correction, re-verify |
| `NO_QUIZ_AUDIT_PASS` / `QUIZ_AUDIT_ISSUES` | questions not audited / leaked | fix and re-audit |
| `QUIZ_AUDIT_STALE` / `GRADE_AUDIT_STALE` | a valid receipt exists but does not bind this message — either the emission differs from what was audited, or the dispatch envelope was the wrong shape (quiz: `items[]` instead of `questions_json`, or a questions-only envelope missing `rendered_content` = the full batch text; grade: no question/answer/verdict) so there is nothing to bind | re-emit the audited text, or re-dispatch the verifier with the correctly shaped envelope carrying the full batch in `rendered_content` (never re-audit an already-bound draft) |
| `NO_GRADE_AUDIT_PASS` / `GRADE_MISMATCH` | grade unverified / conflicts with verifier | use the verifier's `correct_verdict` |
| `FOUNDATION_INCOMPLETE` | a teach/resume claims turn omitted its shape block (unknown `turn_kind`, ungrounded triage, no single attack subtype, an autopsy without one step, or a repair without its `repair` block) | re-dispatch the fact-check with the missing block added, then emit |
| `NO_REPAIR_RECEIPT` | the attack battery tried to resume while a repair is still open | finish the repair: fresh-surface check graded `pass`, then a `repair` turn with `status:"done"` quoting that question and the learner's restatement |
| `REPAIR_INCOMPLETE` | a `done` repair has no graded fresh-surface pass, a mismatched gap, or no learner restatement (or a second gap was opened first) | close the open gap first; quote the exact question the grade-audit passed and the learner's own words |
| `NO_UI_AUDIT` / `UI_AUDIT_ISSUES` / `UI_AUDIT_STALE` | widget unverified / flagged / a valid receipt that does not bind this payload | re-emit the audited payload+prose, or re-dispatch `ui-audit` with the exact `payload` and `rendered_content` = the full turn draft |
| `UI_PAYLOAD_INVALID` | a `[[TURN:ui]]` message with no parseable ```openui payload | re-emit the payload the verifier audited |
| `UI_REQUIRES_OWN_TURN` | a ```openui fence inside a claims/transition turn | make the widget its own `[[TURN:ui]]` message |
| `NO_REVIEW_GATE_PASS` / `REVIEW_GATE_ISSUES` | ingest review missing/flagged, or the receipt named no `target_files` | after the Clerk returns `CLERK_WRITES`, dispatch ONE independent `review-gate` with `target_files` naming the wiki pages it wrote |
| `⚠️ INGEST GATE` | the review verdict was relayed by the Clerk's own output, not an independent `review-gate` run | dispatch a `review-gate` on the Clerk's writes before trusting the summary |
| `⚠️ REVIEW GATE` / `⚠️ REVIEW SESSION GATE` / `⚠️ SCOUT AUDIT` | a review-family verdict carried no `evidence` list (what it read/checked) | treat the pass as unsubstantiated; re-run the gate so it names its evidence |
| `⚠️ SOURCES INCOMPLETE` | Scout could not fetch one or more sources (`failed_refs` non-empty) | teach around the gaps; consider re-scouting or adding a fallback source |
| `⚠️ SCOUT DIGEST UNVERIFIED` | Scout finished without a parseable `SCOUT_DIGEST:` receipt | verify the digest exists on disk; re-run Scout if the lesson context looks thin |
| `⚠️ REVIEW CONTEXT INCOMPLETE` | Review Scout could not read one or more state items | review around the gaps; re-run `review-scout` if the queue looks thin |
| `⚠️ REVIEW SCOUT DIGEST UNVERIFIED` | Review Scout finished without a parseable `REVIEW_SCOUT_DIGEST:` receipt | verify the digest exists on disk; re-run `review-scout` |
| `NO_TUTOR_AUDIT` / `TUTOR_AUDIT_ISSUES` | handoff writes weren't checked (or the receipt named no `files`) / verifier flagged an issue (any severity) | dispatch `tutor-audit` on the handoff batch with `files:[...]`; fix every issue and re-audit (out-of-scope observations are `context_notes`, never blocking) |
| `NO_REVIEW_SESSION_AUDIT` / `REVIEW_SESSION_AUDIT_ISSUES` | review close (review-clerk writes) wasn't audited, or the receipt named no `written_files` / the audit flagged an issue (any severity) | dispatch `review-session-audit` with `written_files:[{path},...]` on the exact writes; fix the writes and re-audit until `PASS` (no cycle cap) |
| `⚠️ REVIEW FLAGS SURFACED` | reviewer found out-of-scope bookkeeping flags in the ingest output | shown with a banner, **not** withheld or re-run |
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
| Gate verifiers (`fact-check` / `quiz-audit` / `grade-audit` / `tutor-audit` / `review-session-audit` / `ui-audit` / `graph-audit`) | `muse-spark-1.3-contributor` (high) |
| Ingest reviewer (`review-gate`) / lesson-start context auditor (`scout-audit`) | `muse-spark-1.3-contributor` |
| Graph extractor (`graph-extract`) | `deepseek-v4.1-flash` |

Verifiers run on preferred models for cost/availability, but this is a **default, not a guarantee** —
when the preferred model is unavailable a verifier may run on the same model as the Tutor or Clerk,
and that is acceptable. The gate records which model ran (see the per-run `model` in the subagent
artifacts) but does not enforce separation. To change a default, edit that file and restart pi.

---

## 8. State, git, and sync

- The Clerk commits and pushes **state only** (`Learning System/`, `Knowledge Wiki/`) to the
  original repo, per `Learning System/AGENTS.md`.
- The pi layer is its own repo; update it with `cd ~/learning-pi && git pull`, then
  `/reload` (or `systemctl --user restart pi-bridge` + `docker compose` restart if you run the bridge/deploy path).
- **Open WebUI also writes this state** (via pi-bridge). Pull before a session and don't run both writers at once:
  ```bash
  cd ~/learning-system && git pull
  ```
  See `bridge/README.md` + `deploy/README.md` for the Open WebUI → pi-bridge → pi path.
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
**or warning** findings it touched using those hints, re-runs once, and surfaces the rest. Errors
surface as `STATE_AUDIT_ERRORS` (withhold); warnings-only surface as `⚠️ STATE AUDIT`.

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
- **`GRADE_AUDIT_STALE` on a verdict-only grade turn** → fixed by `G-grade-verdict-only-binds`
  (`CONTRACT.md`): a verdict-only `[[TURN:grade]]` binds via a full-sentence grade envelope + deterministic
  fallback ("every graded answer restated, turn ≤ half question text"). If it still fires, check the turn is
  grade-only (no teaching prose — move repair to a separate `[[TURN:claims]]` with its own `fact-check`).
- **`NO_REPAIR_RECEIPT` / `REPAIR_INCOMPLETE` loops** → repair mode is bound to one gap and closes only
  on evidence. The check that closes it must be a **new surface** (not a re-ask of the repair turn),
  graded `pass` with `qtype:"micro-check"`; the `done` turn must quote that exact question in
  `fresh_surface_check` and the learner's own words in `learner_restate`. A `done` turn for a
  different gap, or before the grade receipt exists, is rejected — finish the open gap first.
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
