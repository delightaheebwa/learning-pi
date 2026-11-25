# Field guide: the learning system in pi

A practical guide to running your spaced-repetition learning system from the pi coding agent.

## 1. The setup in one picture

```
~/learning-pi/            this repo: the pi layer and the learner state
~/learning-pi/state/      Learning System/, Knowledge Wiki/, scripts/
  .pi/                    symlinks to ~/learning-pi/.pi, local only, excluded from git
```

- State lives in `state/` with its full history. The separate state repo is retired.
- The pi layer lives at the repo root. `install.sh` links `.pi/` into `state/`.
- Run pi from the state tree:

  ```bash
  cd ~/learning-pi/state && pi
  ```

  On the first run, approve trust for the project. The `.pi/` resources load only after trust.

## 2. Slash commands: the whole interface

| Command | What it does |
| --- | --- |
| `/teach <topic>` | Start a new topic. Scout gathers live sources, then the flow runs the entry gate, triage, and targeted attacks. |
| `/lesson` | Run the next curriculum lesson, in sequence within the phase. |
| `/continue` | Resume a paused lesson at its next unresolved attack. Scout gathers the resume context. |
| `/pause` | Stop cleanly. It writes a partial lesson file and banks progress through Clerk. |
| `/review` | Run a spaced-repetition review. Review Scout builds a queue of up to 5 concepts, and review-clerk persists the results. |
| `/solo` | Run a closed-book check with no AI help. Review Scout builds the queue, and the gate withholds teaching and hints. Attempts are recorded as `mode:"solo"` to feed the independence gate. |
| `/read <source>` | Run a reading session. Attach the source text, get a benchmark brief, then free recall and a quoted model diagnosis. |
| `/critique [topic-or-source]` | Bring your own-words model, or a source excerpt plus your interrogation. Get one quoted diagnosis: right, wrong, vague, missing, overreach, weak test. No rewrite, no triage, no attacks, no clone. Good turns capture both versions and ingest the concepts. |
| `/ingest <content or URL>` | Run a standalone ingest through Clerk. Also used after a lesson handoff, where you run `/ingest` with no arguments. |
| `/audit` | Run a read-only state consistency audit of MISSION, CURRICULUM, Profile, Active Concepts, and the index. It reports loudly and never writes. |

Skills load automatically, so you rarely call them by hand. To force one, run `/skill:learning-system` or `/skill:learning-teach`.

## 3. A normal teaching session

A session runs in this order.

1. Start pi and pick a lesson. Run `cd ~/learning-pi/state && pi`, then run `/lesson` for the next lesson in the curriculum. For a topic, run `/teach eigenvalue decomposition`.

2. Let Scout gather sources. For a new lesson, Scout fetches the live curriculum doc and its Further Reading pages. It hashes them, writes a digest to `Learning System/.tmp/`, and posts a digest receipt. Scout's human-readable heading is `SCOUT DIGEST:` with a space. The machine-readable receipt line that the gate parses is `SCOUT_DIGEST:` with an underscore.

   The digest has a 7-day TTL. If it is stale, Scout re-runs before teaching new material. Excerpts from a stale digest are never authoritative.

   The Tutor then dispatches one independent `scout-audit` on the digest. This is the lesson-start mirror of the ingest `review-gate`. The audit checks completeness: every Further Reading URL was fetched or explicitly failed, excerpts and `theory` lines and prerequisites are present, and raw files are on disk. It also fact-checks the synthesis against the raw sources. A missing audit withholds the first teaching turn. An `ISSUES` verdict surfaces as a banner and never blocks.

3. Pass the entry gate. The Tutor never teaches cold. It asks for your notes or material, and for a closed-book model in your own words. If you bring notes but no model, it asks for the model before reading anything. It does not preview the mechanism or name the right framing.

4. Measure your edge when needed. If your model is ambiguous or hedged, one short bracket probe locates your edge before triage. The probe uses multiple-choice questions marked `context:"probe"`. It is diagnostic and never a preview.

5. Let the Tutor triage your model. The Tutor buckets each claim as `solid`, `missing`, or `suspect`, then shows a compact table with the attack order. Off-path holes stay in the table but are not attacked this session. Prerequisites are attacked first.

6. Take one attack per turn. Attacks run in dependency order: a mechanism press, a counterexample trap, a perturbation, a source clash, a sabotage, or a synthesis clash. You predict before each attack. The Tutor exposes the hole and never fills it. Say "just tell me" and the Tutor gives the idea at once. That is logged as a dependency event, and the turn still closes with one minimal generation.

7. Enter repair mode when your repair fails. If your own repair attempt fails, or the gap is one you never learned, the Tutor switches into repair mode for that one gap. It starts from what you already hold and teaches one motivated step at a time, asking you first where you can reason it out. It checks each step. The Tutor cannot move on until you pass a fresh check on a new surface and restate the patched bit in your own words. The next attack is held back until then.

8. Patch the model. You restate the repaired model in your own words. The Tutor checks it and adds only what you missed. It never rewrites your words.

9. Graduate the concept. A naive-student clone tries to use your patched model. If the clone fails, the hole routes back to one more attack. A concept cannot reach `solid` without passing this check.

10. Pause at any point with `/pause`. The flow is student-paced. A pause banks today's progress and keeps the lesson in progress. `/continue` resumes at the next attack, and the pause pointer records `Checkpoint N/M, mini K/L`.

11. End the lesson. The end runs an entailment check and a naive-student clone, then the handoff batch and `tutor-audit`. The session then auto-ingests inline. The Tutor dispatches `clerk`, then an independent `review-gate` on the wiki pages Clerk wrote. Clerk writes the wiki and Active Concepts, reconciles the position pointers, runs the state audit, regenerates Learner History, and commits state. Clerk does not gate itself. Do not run `/ingest` at lesson end. `/pause` is the only flow that leaves ingest to you.

### Math on paper

Work on paper. Reply with only the final number or the letter, A through D. The Tutor will not ask you to type LaTeX.

The Tutor now writes its own math as LaTeX when the front end can render it. Run learning sessions in Ghostty or Kitty, where `pi-math` draws real formula images. Or use the Open WebUI face, where KaTeX renders the LaTeX. In foot or tmux, where `pi-math` cannot draw, the Tutor falls back to plain Unicode.

## 4. Review sessions with `/review`

A review runs in this order.

1. Review Scout runs first. It reads your learner state in one bundle and builds the queue.

2. The queue holds up to 2 due mistakes at priority and 3 due concepts, shuffled. It uses composite scenarios when the queue is large.

3. Answer the questions. Answers may be terse. The 3-line qualitative trace is required: cue, then mechanism, then direction or extreme. Phrases and keywords work, and length is never graded. The teach-the-clone item's explanation must carry a failure regime.

4. Every grade is verified by an independent `grade-audit` subagent before it is shown. When you answer several questions in one reply, put all answers in one batched `items[]` envelope. That is one subagent call per reply, not per answer.

5. The Reviewer writes nothing. At the close, `review-clerk` writes the Review notes and the session note. It updates `Attempts.json`, `📚 Active Concepts.md`, and `🧯 Mistakes.md`, runs the state audit, and commits. Then the Reviewer dispatches a `review-session-audit` over those writes.

The review flow mirrors the teaching flow: `review-scout`, then the Reviewer in this session, then `review-clerk`. The close is checked by `review-session-audit`, exactly like the `scout`, Tutor, and `clerk` chain with `tutor-audit`.

### Daily reminder and the bar indicator

Reviews are meant to happen daily. Two things track that, and both are driven by `bin/pi-review-status`. The script matches a `Session…Review…<date>.md` filename against the calendar date the session ran. A review finished at 1am counts as that day's, not the previous day's.

- The `local.pi-review` Omarchy bar widget shows `R` for pending, `R✓` for done, or `R✗` for missed. A missed review takes the urgent color once it is late. The widget appears only in the evening window 18:00–03:59, so the daytime bar stays clean. Left-click launches `pi` in the checkout.
- The desktop reminder sends one notification per missed day. It runs from a systemd timer at 23:00 and 00:30. The old floating terminal popup was removed.

Install or repair both with `~/learning-pi/omarchy/install.sh`.

## 4b. Critique sessions with `/critique`

A critique session is the lightest flow. You do the thinking; the Tutor diagnoses it and hands it back.

- **Explain-back.** Bring your own-words model of a topic. If you want the diagnosis checked against a source, point at a path, a pasted excerpt, or your notes. With no anchor, the Tutor tests internal consistency, mechanism gaps, and counterexamples and does not claim a source contradiction.
- **Text interrogation.** Bring a paragraph plus your own interrogation of it. The paragraph is required.

One diagnosis per presentation, always verified by the independent `fact-check` before you see it. The buckets are `right`, `wrong`, `vague`, `missing`, and `overgeneralised` in explain-back; `right`, `wrong`, `overreach`, `missing`, and `weak test` in interrogation. Every verdict quotes you, and the anchor when one is attached. The turn ends with at most two sharper questions.

The Tutor never writes the corrected model or reading. It may name a verdict, quote a single link, and pose a test; you write the next version. There is no entry gate, triage table, attack battery, hint ladder, repair mode, quiz, or naive clone.

Close with your final version. The session note keeps v1, the diagnosis, and v2 verbatim, the clerk writes the wiki pages and Active Concepts rows, and the concept rows schedule for review. A source-less session is marked `anchor: none` so review records a self-model retrieval rather than pretending to grade against a source it does not have.

## 5. What the model emits, and why you won't see it

The Tutor must start every message with a turn tag. The gate strips the tag before the message reaches you.

| Tag | Meaning | Required before it renders |
| --- | --- | --- |
| `[[TURN:claims]]` | teaching or plan | a `fact-check` whose draft matches the text |
| `[[TURN:quiz]]` | question batch | a PASS `quiz-audit` |
| `[[TURN:grade]]` | grading your answer | an agreeing `grade-audit` |
| `[[TURN:ui]]` | an interactive widget in its own turn | a passing `ui-audit` bound to the emitted `openui` payload and covering the prose |
| `[[TURN:none]]` | transitions, summaries | nothing |

A widget is delivered as a same-origin Open WebUI embed below the prose, at `/static/openui/<version>/widget.html#…`. The pinned OpenUI bundle is self-hosted and `connect-src 'none'`. Mermaid and HTML fences render natively in the client. See [`bridge/README.md`](bridge/README.md).

If the Tutor forgets the tag in any teaching or review flow, the gate won't dead-end the session on a grade or quiz turn. An untagged grade message is accepted when a `grade-audit` receipt matches that exact text. An untagged quiz message is accepted the same way with a `quiz-audit` receipt. The receipt carries the question, the answer, or the batch. A message is also accepted when exactly one gate type has a valid pending receipt. Async verifiers report through a completion notification, and that notification carries no draft, so a bound match is impossible there.

Ambiguous messages still wait. That covers a message with both gate types pending and a message with no receipt at all.

Two other cases carry an implicit `[[TURN:none]]`. An ingest summary after a clerk dispatch is verified by the clerk's `REVIEW_GATE_VERDICT`. An untagged review close is verified by the `review-session-audit` receipt once the session note is written. The gate never infers `claims`.

The Tutor writes its four handoff artifacts in one batch at a pause or at lesson end. The artifacts are the lesson file, the session note, the learning record, and `Pending Ingest.json`. An independent `tutor-audit` checks that batch once before the summary renders. Mid-lesson, the Tutor writes nothing to state. The Clerk reconciles position and state files during ingest, not the Tutor. Those files are MISSION, CURRICULUM, Learning Profile, Active Concepts, Mistakes, and Learner History.

The review flow is symmetric. `review-scout` gathers context and the due queue at the start, and the first review turn is withheld with `NO_REVIEW_CONTEXT` until it runs. The Reviewer writes nothing. `review-clerk` persists the Review notes and the session note and reconciles the touched rows at the close. `review-session-audit` checks those writes before the summary renders.

Prompt templates also carry `[[FLOW:teach|resume|review|ingest|solo]]` so the gate knows the mode deterministically. You never type these.

## 6. The gate: reading the banners

If verification is missing, the gate withholds the turn and shows a banner. The tables below list the common codes by area.

### Turn tags

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_TURN_TAG` | The message carried no tag. | The model self-corrects. If the tag stays missing, restart pi. Section 5 lists the exceptions. |

### Lesson start and Scout

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_SCOUT_CONTEXT` | A new lesson started with no Scout run. | Let it run `scout`, or resume instead. |
| `NO_SCOUT_AUDIT_PASS` | Scout ran, but no independent `scout-audit` covers its digest. The receipt may also have named no `digest`. | Dispatch one independent `scout-audit` with `digest` and `raw_files` naming the lesson-start digest. On `ISSUES`, re-scout and re-audit. There is no cycle cap. |
| `⚠️ SCOUT AUDIT FLAGS SURFACED` | The scout-audit reported issues on the digest: a missing source, an invented excerpt, or a smoothed-over contradiction. | Teaching proceeds with the flags outstanding. Fix the digest with a re-scout and a re-audit. |
| `⚠️ SOURCES INCOMPLETE` | Scout could not fetch one or more sources, so `failed_refs` is non-empty. | Teach around the gaps. Consider a re-scout or a fallback source. |
| `⚠️ SCOUT DIGEST UNVERIFIED` | Scout finished without a parseable `SCOUT_DIGEST:` receipt. | Verify the digest exists on disk. Re-run Scout if the lesson context looks thin. |

### Review context

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_REVIEW_CONTEXT` | `/review` ran without a Review Scout run. | Let it run `review-scout` to build the queue. |
| `⚠️ REVIEW CONTEXT INCOMPLETE` | Review Scout could not read one or more state items. | Review around the gaps. Re-run `review-scout` if the queue looks thin. |
| `⚠️ REVIEW SCOUT DIGEST UNVERIFIED` | Review Scout finished without a parseable `REVIEW_SCOUT_DIGEST:` receipt. | Verify the digest exists on disk and re-run `review-scout`. |

### Claims fact-check

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_FACT_CHECK_MATCH` | The draft was not verified, or it changed after verification. | Re-draft and re-verify. |
| `FACT_CHECK_MISSING_DRAFT` | The fact-check passed, but its envelope carried no `rendered_content`. | Re-send the claims with the exact draft in `rendered_content`. |
| `FACT_CHECK_MISMATCH` | The verified draft covers too little of the emitted text. | Emit the verified draft unchanged, or re-verify the new text. |
| `FACT_CHECK_ISSUES` | The verifier flagged a claim. | Apply the correction and re-verify. |

### Quiz and grade audits

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_QUIZ_AUDIT_PASS` / `QUIZ_AUDIT_ISSUES` | The questions were not audited, or they leaked. | Fix and re-audit. |
| `QUIZ_AUDIT_STALE` / `GRADE_AUDIT_STALE` | A valid receipt exists, but it does not bind this message. Either the emission differs from what was audited, or the dispatch envelope had the wrong shape. A quiz envelope may send `items[]` instead of `questions_json`, or a questions-only envelope with no `rendered_content` holding the full batch text. A grade envelope may carry no question, answer, or verdict. | Re-emit the audited text. Or re-dispatch the verifier with the correct envelope and the full batch in `rendered_content`. Never re-audit an already-bound draft. |
| `NO_GRADE_AUDIT_PASS` / `GRADE_MISMATCH` | The grade is unverified, or it conflicts with the verifier. | Use the verifier's `correct_verdict`. |

### Turn shape and repair

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `FOUNDATION_INCOMPLETE` | A teach or resume claims turn omitted its shape block. Causes: unknown `turn_kind`, ungrounded triage, no single attack subtype, an autopsy without one step, or a repair without its `repair` block. | Re-dispatch the fact-check with the missing block added, then emit. |
| `NO_REPAIR_RECEIPT` | The attack battery tried to resume while a repair is still open. | Finish the repair. Start with a fresh-surface check graded `pass` with `repair_gap` naming the gap. Then send a `repair` turn with `status:"done"` that quotes that question and the learner's restatement. |
| `REPAIR_INCOMPLETE` | A `done` repair has no graded fresh-surface pass for this gap, a mismatched gap, or no learner restatement. This code also fires when a second gap was opened first. | Close the open gap first. Quote the exact question that the grade-audit passed with `repair_gap`, and the learner's own words. |

### Widgets

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_UI_AUDIT` / `UI_AUDIT_ISSUES` / `UI_AUDIT_STALE` | The widget is unverified, was flagged, or has a valid receipt that does not bind this payload. | Re-emit the audited payload and prose. Or re-dispatch `ui-audit` with the exact `payload` and `rendered_content` set to the full turn draft. |
| `UI_PAYLOAD_INVALID` | A `[[TURN:ui]]` message has no parseable `openui` fence payload. | Re-emit the payload the verifier audited. |
| `UI_REQUIRES_OWN_TURN` | An `openui` fence sat inside a claims or transition turn. | Make the widget its own `[[TURN:ui]]` message. |

### Ingest and close

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `NO_REVIEW_GATE_PASS` / `REVIEW_GATE_ISSUES` | The ingest review is missing or flagged, or the receipt named no `target_files`. | After Clerk returns `CLERK_WRITES`, dispatch one independent `review-gate` with `target_files` naming the wiki pages it wrote. |
| `⚠️ INGEST GATE` | Clerk's own output relayed the review verdict, not an independent `review-gate` run. | Dispatch a `review-gate` on Clerk's writes before you trust the summary. |
| `⚠️ REVIEW GATE` / `⚠️ REVIEW SESSION GATE` / `⚠️ SCOUT AUDIT` | A review-family verdict carried no `evidence` list. That list names what the verifier read or checked. | Treat the pass as unsubstantiated. Re-run the gate so it names its evidence. |
| `NO_TUTOR_AUDIT` / `TUTOR_AUDIT_ISSUES` | The handoff writes were not checked, or the receipt named no `files`. This code also covers any issue the verifier flagged, at any severity. | Dispatch `tutor-audit` on the handoff batch with `files:[...]`. Fix every issue and re-audit. Out-of-scope observations go in `context_notes` and never block. |
| `NO_REVIEW_SESSION_AUDIT` / `REVIEW_SESSION_AUDIT_ISSUES` | The review close was not audited, or the receipt named no `written_files`. This code also covers any issue the audit flagged, at any severity. | Dispatch `review-session-audit` with `written_files:[{path},...]` on the exact writes. Fix the writes and re-audit until `PASS`. There is no cycle cap. |
| `⚠️ REVIEW FLAGS SURFACED` | The reviewer found out-of-scope bookkeeping flags in the ingest output. | The banner shows, and the turn is not withheld or re-run. |

### State audit

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `⚠️ STATE AUDIT` | `audit_state.py` found warnings still outstanding. The flow fixes the warnings it touched, and warnings never block. | Run `/audit` for details. |
| `STATE_AUDIT_ERRORS` | At the ingest or review close, `audit_state.py` reported errors, which means state drift. The close summary is withheld until they are fixed. | Apply the `STATE_AUDIT_FIXES` hints, or run `/audit` for the list. Re-run the audit clean, then re-emit the summary. |

### Retries

| Banner code | Meaning | Fix |
| --- | --- | --- |
| `⛔ UNVERIFIED` | Retries ran out after 2 attempts, and the content is shown unverified. | Review it manually. |

The gate fails open on internal errors, and it acts only in learning flows. Normal coding work in the repo is never gated. A partial generation passes through ungated and does not consume a receipt. That covers a model error, an abort, or the token cap hit mid-message. The retried message still binds to that receipt. This is why an interrupted grade turn no longer dead-ends on `NO_GRADE_AUDIT_PASS`.

A verifier or worker dispatch runs through the `dispatch` helper: `dispatch({ agent, task: { ...envelope... } })`. The call is foreground, and the envelope is an object. It runs the child through pi-subagents' structured delegation bridge and returns the verdict in the tool result. The receipt is minted before you emit, so wait for it before emitting the summary. The gate still mints legacy `subagent` receipts from a `subagent-notify` completion notification. The learning layer no longer dispatches that way.

## 7. Models

Set these in `~/learning-pi/.pi/settings.json`. The scope is project only.

| Role | Model |
| --- | --- |
| Tutor (your session) | `glm-5.3` (high) |
| Scout / Clerk / Review Scout / Review Clerk | `deepseek-v4.1-flash` |
| Gate verifiers (`fact-check` / `quiz-audit` / `grade-audit` / `tutor-audit` / `review-session-audit` / `ui-audit` / `graph-audit`) | `muse-spark-1.3-contributor` (high) |
| Ingest reviewer (`review-gate`) / lesson-start context auditor (`scout-audit`) | `muse-spark-1.3-contributor` |
| Graph extractor (`graph-extract`) | `deepseek-v4.1-flash` |

Verifiers run on preferred models for cost and availability. That is a default, not a guarantee. When the preferred model is unavailable, a verifier may run on the same model as the Tutor or the Clerk, and that is acceptable. The gate records which model ran, and you can read it as the per-run `model` in the subagent artifacts. The gate does not enforce separation. To change a default, edit that file and restart pi.

## 8. State, git, and sync

- State lives in this repo under `state/`. The Clerk commits it at ingest or review close, per `state/Learning System/AGENTS.md`. There is no separate state repo to push to.
- Update the pi layer with `cd ~/learning-pi && git pull`, then run `/reload`. If you run the bridge or the deploy path, also run `systemctl --user restart pi-bridge` and restart the `deploy/` compose stack.
- Open WebUI is optional, and it fronts the same pi runtime through `pi-bridge`. Open WebUI holds chat transcripts, while the Clerk writes state. Do not run two state-writing sessions at once. Pull before a session:

  ```bash
  cd ~/learning-pi && git pull
  ```

  See `bridge/README.md` and `deploy/README.md` for the Open WebUI, `pi-bridge`, and pi path.
- Never commit `.pi/`, which is in `.git/info/exclude`. Never commit `Pending Ingest.json` or `.tmp/`, which are gitignored.

## 9. The consistency audit

```bash
python3 ~/learning-pi/pi/audit_state.py --root ~/learning-pi/state
```

The audit checks these items:

- MISSION positions against CURRICULUM positions.
- Lesson files against curriculum rows.
- Active Concepts dates.
- Position pointers. The MISSION, Learning Profile, and Active Concepts track header each point at a position. The audit compares each one with the active lesson's `Checkpoint N/M`.
- Active Concepts `Next Review` against `Attempts.json`.
- The wiki index against the wiki files and the source files.
- Scout-digest TTL. The audit warns when the active lesson's `.tmp/context-*.json` is older than 7 days.
- Stale host paths.

The audit reports and never writes. It runs automatically at ingest close under the Clerk and at review close under the Tutor. It also runs on demand through `/audit`. For findings it can fix mechanically, it prints a `STATE_AUDIT_FIXES:` JSON array of remediation hints. The automatic flow fixes the error or warning findings it touched with those hints, re-runs once, and surfaces the rest. Errors surface as `STATE_AUDIT_ERRORS`, and the gate withholds. Warnings alone surface as `⚠️ STATE AUDIT`.

## 10. Troubleshooting

- The gate never blocks, or tags show in the output. The project is not trusted, or the extension did not load. Run `cd ~/learning-pi/state && pi`, approve trust, then run `/reload`.
- `/skill:...` or slashes are missing. Start pi from `~/learning-pi/state`. The project `.pi/` loads only there, and only after trust.
- Scout or verifier web fetches fail. The agents load `pi-web-access` through a home-relative path in their frontmatter. Verify that `~/.pi/agent/npm/node_modules/pi-web-access/index.ts` exists.
- The verifier cannot read the repo. The Tutor's working directory must be `~/learning-pi/state`.
- The model keeps forgetting turn tags. Consider a stronger Tutor model in `.pi/settings.json`.
- A withheld banner says a dispatch omitted the `agent` field. That dispatch minted no receipt. The model must name the verifier as `dispatch({ agent: "tutor-audit", ... })`, for example.
- A tool result says `Validation failed for tool "subagent": - task: must be string`, or a `subagent` `workflow` or `args` error appears. The model used the raw `subagent` tool instead of `dispatch`. pi-subagents requires `subagent.task` to be a JSON string, and an object fails. That is why the learning layer dispatches through `dispatch({ agent, task: { ...envelope... } })`, which takes the envelope as an object and serializes it. `dispatch` runs the child through the structured delegation bridge and mints the receipt. The raw `subagent` `workflow` and `args` forms are blocked and redirected to `dispatch`. No `subagents_enable` step is needed for `dispatch`.
- `GRADE_AUDIT_STALE` loops on a grade and repair turn. The grade-audit binds only the graded question, answer, and verdict, so it cannot cover the repair prose. Dispatch a `fact-check` with `rendered_content` set to the full emitted turn. The gate accepts the turn when the grade-audit covers the verdicts and the fact-check covers the prose. Or split the turn into a verdict-only `[[TURN:grade]]` and a separate `[[TURN:claims]]` repair. Never re-dispatch the grade-audit to cover repair prose.
- `GRADE_AUDIT_STALE` fires on a verdict-only grade turn. This is fixed by `G-grade-verdict-only-binds` in `CONTRACT.md`. A verdict-only `[[TURN:grade]]` binds through a full-sentence grade envelope and a deterministic fallback: every graded answer restated, and the turn is at most half the question text. If it still fires, check that the turn is grade-only with no teaching prose. Move repair to a separate `[[TURN:claims]]` with its own `fact-check`.
- `NO_REPAIR_RECEIPT` or `REPAIR_INCOMPLETE` loops. Repair mode is bound to one gap, and it closes only on evidence. The check that closes it must use a new surface, not a re-ask of the repair turn. That check must be graded `pass` with `qtype:"micro-check"` and `repair_gap` equal to the repair's gap. The `done` turn must quote that exact question in `fresh_surface_check` and the learner's own words in `learner_restate`. A `done` turn for a different gap, or one sent before the grade receipt exists, is rejected. Finish the open gap first.
- `QUIZ_AUDIT_STALE` on a clean PASS, or a write-gate PASS judged unsubstantiated. The judge scored the PASS unsubstantiated because the verifier emitted no evidence. The verifier's verdict JSON must carry a non-empty `evidence` list naming what it checked. The `quiz-audit` and `tutor-audit` agents require this. Re-dispatch it.
- State looks stale after Open WebUI use. Run `git pull` in `~/learning-pi/state`.

## 11. Provenance audit, after the fact

`audit_gates.py` reconstructs, from a pi session transcript, which verifier runs actually backed each claimed verdict. It is read-only and diagnostic. The live gate does not depend on it.

```bash
python3 ~/learning-pi/pi/audit_gates.py                 # newest learning session
python3 ~/learning-pi/pi/audit_gates.py --session <path.jsonl>
python3 ~/learning-pi/pi/audit_gates.py --json          # machine-readable
```

The script correlates every `subagent` dispatch with its artifact metadata. It reports these cases:

- Dispatches with no artifact.
- Runs that exited non-zero.
- Runs that the harness acceptance layer marked `rejected`, which the gate may still have consumed.
- Review verdicts with no backing run.
- Clerk-relayed review provenance.
- `STATE_AUDIT_VERDICT` markers with no `audit_state.py` invocation.

It also prints the model each run used. It exits 1 when it finds an error-level issue.

### Judge raw dump for an unexplained withhold

A block is not always obvious from `decisions.ndjson`. A `QUIZ_AUDIT_STALE` on a clean PASS is one example. The judge's exact input and output are the missing evidence.

Export `LEARNING_GATE_JUDGE_DUMP=1` and reproduce the block. Each judge call then appends `{at, model, user, response}` to `~/.pi/agent/learning-gate/judge-raw.ndjson`. `user` is the serialized `JUDGE PACKAGE`: the receipts the judge saw, their `boundText`, and the emitted turn. `response` is the model's raw JSON, with `bindings`, `substantiveness`, and `reason`. Set the variable to a path to write elsewhere. The dump is off by default, and it never changes gating.

## 12. Maintenance

```bash
# update the repo (runtime and state together)
cd ~/learning-pi && git pull && ./install.sh ~/learning-pi/state

# compare the frozen Skills/ snapshot with the canonical pi skills
diff -u ~/learning-pi/state/Skills/learning-system/SKILL.md \
        ~/learning-pi/.pi/skills/learning-system/SKILL.md
```

The pi skills are canonical. They contain no Open WebUI plumbing, no host paths, and no stale state. The copies under `state/Skills/` are frozen and unmaintained.
