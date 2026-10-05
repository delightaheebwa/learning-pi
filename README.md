# learning-pi

The **pi control layer** for the `learning-system` spaced-repetition system. This repo contains
only pi-side resources (skills, subagents, prompts, a verification gate, and an audit script). It
contains **no learning state**.

State lives in the original repo, `delightaheebwa/learning-system`, which stays the single source
of truth for `Learning System/` and `Knowledge Wiki/`. Open WebUI keeps using that repo unchanged.

## Architecture

```
~/learning-system   clone of the ORIGINAL repo   -> owns state (+ Open WebUI layer)
~/learning-pi       this repo (pi layer)         -> skills/agents/prompts/gate/docs only
```

`install.sh` symlinks this repo's `.pi/` into the state checkout and adds `.pi/` to
`.git/info/exclude`, so the overlay never enters the original repo and the original repo never
receives pi-specific files.

## Install

```bash
git clone git@github.com:delightaheebwa/learning-pi.git ~/learning-pi
git clone https://github.com/delightaheebwa/learning-system.git ~/learning-system   # if not present
~/learning-pi/install.sh ~/learning-system
cd ~/learning-system && pi        # approve/trust the project once
```

## Usage

Slash commands: `/review`, `/ingest <content>`, `/teach <topic>`, `/lesson`, `/continue`, `/pause`,
`/audit`, `/show <concept>` (a verified visualization; `/viz` reopens/controls the explorer).
The main pi session acts as the **Tutor**; `scout`, `clerk`, and the verifier subagents run as
children. The Tutor writes only its four handoff artifacts (lesson file, session note, learning
record, `Pending Ingest.json`) at a pause or lesson end; the **Clerk** reconciles position/state
files (MISSION, CURRICULUM, Learning Profile, Active Concepts, Mistakes, Learner History) at
`/ingest`. The `/review` flow mirrors it: **`review-scout`** gathers context and the due queue,
the main session runs the review, and **`review-clerk`** writes the Review note(s)/session note,
syncs the touched rows, runs the state audit, and commits.

> **Editing `.pi/` takes effect only after a reload.** A running pi process keeps the extension it
> loaded at startup; changing `extensions/`, `skills/`, `agents/`, or `APPEND_SYSTEM.md` does **not**
> touch a live session. Run `/reload` in pi (or restart pi) after pulling changes, then confirm the
> new behavior. A long-lived process can otherwise keep enforcing stale gate logic indefinitely.

## Models

Configured in `.pi/settings.json` (project scope only):

| Role | Model |
| --- | --- |
| Tutor (main session) | `glm-5.3-flash` |
| Scout / Clerk / review-scout / review-clerk / `viz` | `deepseek-v4.1-flash` |
| Gate verifiers (`fact-check` / `quiz-audit` / `grade-audit` / `tutor-audit` / `review-session-audit` / `viz-audit`) | `muse-spark-1.3-contributor` (high) |
| Ingest reviewer (`review-gate`) | `muse-spark-1.3-contributor` (dispatched by the Tutor on the Clerk's writes) |

Verifiers run on these models by default for cost/availability, but separation is a **preference,
not a guarantee** — when the preferred model is unavailable a verifier may run on the same model as
the Tutor or Clerk, and that is acceptable. The gate does not enforce model identity; it records the
model each run used in the subagent artifacts. Adjust in `.pi/settings.json`; no other file needs to
change.

## Verification gate

`.pi/extensions/learning-gate` tracks verification subagent calls per agent run and withholds an
assistant turn unless the matching, **passing** receipt is present:

| Turn contains | Required receipt |
| --- | --- |
| Teaching claims (Tutor) | `fact-check` whose `rendered_content` covers the emitted text and has no `ISSUES`. With a judge configured the rule is **100% span coverage** (the judge checks every sentence); the legacy path approximates it with ≥85% token coverage + a length guard |
| A question batch | `quiz-audit` returning `PASS` (or `PASS_WITH_FLAGS` for lows-only, accepted silently with no banner to the learner, max 2 cycles); the envelope carries `questions_json` **and** `rendered_content` = the full batch text (intro/instructions + every question + its options), which binds the whole emitted turn |
| A grade | `grade-audit` with `agrees === true`/`PASS`; disagreement is rejected and the verifier's `correct_verdict` is surfaced. One batched `items[]` envelope grades every answer from a single learner reply (never one subagent per answer) |
| A visualization (`[[TURN:viz]]` — a ` ```viz ` spec + supporting words) | `viz-audit` whose canonical `spec` matches the emitted fenced spec and whose `rendered_content` covers the turn (missing → `NO_VIZ_AUDIT`, `ISSUES` → `VIZ_AUDIT_ISSUES`, unbound/stale → `VIZ_AUDIT_STALE`). A ` ```viz ` block in any other turn is withheld (`VIZ_REQUIRES_OWN_TURN`); a missing parseable spec is withheld (`VIZ_SPEC_INVALID`). Figures are opt-in and teach/resume-only; `viz-mode` renders them inline and opens an interactive explorer overlay |
| A `Learning System/` handoff write during teach/resume | `tutor-audit` reading back the lesson file / session note / learning record / `Pending Ingest.json` (once per handoff batch; high/medium block, lows pass as `PASS_WITH_FLAGS`) |
| An ingest | after the Clerk returns a `CLERK_WRITES` receipt, the Tutor dispatches an independent `review-gate` on the wiki pages written; `PASS` renders clean, `ISSUES`/`PASS_WITH_FLAGS` render with a `⚠️ REVIEW FLAGS SURFACED` banner (never an endless re-run). A verdict relayed by the Clerk instead of a real review-gate run gets a `⚠️ INGEST GATE` banner; a review verdict with no `evidence` list gets a `⚠️ REVIEW GATE` banner |
| The **close** of a standalone `/review` (the delegated `review-clerk` run wrote the Review notes, session note, and touched Active Concepts / Mistakes rows) | `review-session-audit` reading the writes back against the transcript + per-concept grade verdicts; `PASS`/`PASS_WITH_FLAGS` render clean, `ISSUES` renders with a `⚠️ REVIEW FLAGS SURFACED` banner — never withheld, never a re-run (cap 2 passes per flow) |
| A new lesson | a `scout` run before teaching; a partial/missing `SCOUT_DIGEST` receipt surfaces as a `⚠️ SOURCES INCOMPLETE` / `⚠️ SCOUT DIGEST UNVERIFIED` banner (never a withhold) |
| A `/review` session | a `review-scout` run before the first claims/quiz turn (`NO_REVIEW_CONTEXT` until then); a partial/missing `REVIEW_SCOUT_DIGEST` receipt surfaces as a `⚠️ REVIEW CONTEXT INCOMPLETE` / `⚠️ REVIEW SCOUT DIGEST UNVERIFIED` banner (never a withhold) |

Verifier and worker dispatches use the `dispatch` helper tool:
`dispatch({ agent, task: { ...envelope } })`. It takes the envelope as an **object** (the model never
escapes JSON by hand), runs the child through pi-subagents' structured delegation bridge, and mints the
gate receipt itself. pi-subagents' `subagent` tool requires a JSON-*string* `task` and is
`exposure: "model-only"`; its `workflow`/`args` forms are blocked and redirected to `dispatch`.

A grade turn that also teaches (the diagnose-first repair) is covered by **two** receipts: the
`grade-audit` covers the graded question/answer/verdict and a `fact-check` covers the repair prose
(`rendered_content` = the full emitted turn). A clean verifier `PASS` must carry a non-empty
`evidence` list — the judge treats an evidence-less PASS as unsubstantiated (`*_STALE`).

The reviewer's scope is the ingest's own output only (its wiki page(s) + Active Concepts row(s)).
State drift is reported separately by `audit_state.py`, which runs automatically at ingest and
review close (and on demand via `/audit`). The automatic runs fix the error **or warning** findings
they touched (using the script's `STATE_AUDIT_FIXES` hints), then surface whatever remains.

Receipts are **consumed per emitted message**, so every teaching step needs its own fresh,
content-matched verification (generation-to-emission — "verify A, emit B" is blocked).

### Turn type is explicit (not guessed)

- Prompt templates carry a flow marker (`[[FLOW:teach|resume|review|ingest]]`) that the gate reads
  directly. Flow detection is **explicit-only** — keyword heuristics were removed because verifier
  subagent envelopes (`"flow":"teach"`, "Pending Ingest.json") were being misread as learning flows.
- Every assistant message must begin with a turn tag the gate strips before the learner sees it:
  - `[[TURN:claims]]` → requires a content-matched, passing `fact-check`
  - `[[TURN:quiz]]` → requires a PASS (or flagged PASS_WITH_FLAGS) `quiz-audit`
  - `[[TURN:grade]]` → requires an agreeing `grade-audit`
  - `[[TURN:none]]` → no verifier required
- A missing tag is withheld (`NO_TURN_TAG`) on the legacy path — **except** a grade/quiz turn, which
  the gate infers from a `grade-audit`/`quiz-audit` receipt (a bound match, or the single valid
  pending receipt when an async verifier's completion notification carries no draft). With a judge
  configured, a tag is a **hint** and the judge classifies the turn from the content, so an untagged
  claims turn whose fact-check covers it renders. A `none` tag over text that matches an unused
  verification draft is withheld too (`TURN_TAG_MISMATCH`).

Behavior: up to 2 withheld retries per turn (counter resets on each clean pass), then the turn is surfaced with an `⛔ UNVERIFIED`
banner; internal errors fail open. Non-learning sessions are never gated.

### The judge (model-based semantics)

The gate can run a **judge** — a model that answers the semantic questions the deterministic code
cannot: what type of turn this is, whether a verifier's verified draft covers **100%** of the emitted
text, whether a `PASS` is substantive, and what exact remedy is needed. The judge only **sees and
writes text**: it runs no tool, writes no file, changes no state. The engine performs every action.
Receipts are still the verifier's own statement; the judge never authors them.

- **Model:** Gemini `gemini-3.5-flash-lite` (free tier ≈15 RPM / 500 RPD), configured under the
  `gemini` provider in `~/.pi/agent/models.json` (Google's OpenAI-compatible endpoint). Set
  `GEMINI_API_KEY` in the environment. Override the model with `LEARNING_GATE_JUDGE_MODEL`.
- **Escalation:** a hard case — a valid receipt that does not fully cover, no best receipt, or thin
  substantiveness — escalates to `gemini-3.5-flash` (`LEARNING_GATE_JUDGE_ESCALATION_MODEL`,
  `LEARNING_GATE_JUDGE_ESCALATION_MAX_PER_DAY`, default 20). A primary outage also escalates before
  falling back to the legacy path.
- **Turn tags become hints:** the judge reads the turn type from the content, so an untagged claims
  turn whose fact-check covers it renders. Verifier/notification channels are never gated.
- **Full-draft rule (100%):** the Tutor must put *all* text it will emit into the verifier envelope
  and emit that draft unchanged; any uncovered span blocks, and the remedy names the span.
- **PASS-real:** a `PASS` the judge scores unsubstantiated (no evidence, items unchecked) verifies
  nothing — the receipt is treated as absent.
- **No cap while a high/medium issue remains:** the gate keeps blocking and never dumps the turn as
  `⛔ UNVERIFIED`; the cap applies to every other reason.
- **Dispute:** the same issue blocking three times is adjudicated by the judge; if it no longer
  applies the engine releases the turn with `⚠️ VERIFIER DISPUTED`.
- **Ledger:** every decision and receipt is appended to `~/.pi/agent/learning-gate/`
  (`receipts.ndjson`, `decisions.ndjson`) for provenance and review.
- **Degraded fallback:** with no judge configured, no auth, a rate-limit, or invalid output, the gate
  runs the deterministic legacy path unchanged. A learning turn never dead-ends on a judge fault.

## Skills

Four of the skills in `.pi/skills/` (`learning-system`, `learning-teach`, `learning-review`,
`llm-wiki`) are **sanitized, vendored copies** of the originals — stripped of
Open WebUI plumbing, host-specific paths, and all volatile state (lesson positions, dates,
statuses, archive logic). The originals under the state repo's `Skills/` are untouched.

They are derived, not symlinked, so re-derive and diff them if the canonical skills change:

```bash
diff -u ~/learning-system/Skills/learning-system/SKILL.md ~/learning-pi/.pi/skills/learning-system/SKILL.md
```

The fifth skill, `learning-viz`, is **pi-only** (the opt-in visualization flow: dispatch `viz` →
`viz-audit` → a standalone `[[TURN:viz]]` message, rendered inline by the `viz-mode` extension). It
has no Open WebUI counterpart and is not derived from the state repo.

## State audit (read-only)

```bash
python3 ~/learning-pi/pi/audit_state.py --root ~/learning-system
```

Reports contradiction classes (MISSION vs CURRICULUM vs Profile vs Active Concepts vs wiki index),
position-pointer drift (the position files vs the active lesson's `Checkpoint N/M`), Active Concepts
`Next Review` vs `Attempts.json`, Scout-digest TTL, and stale host paths. It never writes, but it prints a
`STATE_AUDIT_FIXES:` JSON array of remediation hints for mechanically-fixable findings. The
automatic ingest/review runs apply the hints for errors **and warnings** they touched, re-run once,
and surface anything ambiguous or unrelated; `/audit` stays report-only. Known findings in the
current state include outstanding Active Concepts/Attempts.json schedule drift.

## Gate provenance audit (read-only)

```bash
python3 ~/learning-pi/pi/audit_gates.py --session <session.jsonl>
```

Reconstructs which verifier runs actually backed each claimed verdict in a pi session: dispatches
with no artifact, non-zero exits, harness-`rejected` runs the gate may still have consumed,
review verdicts with no backing run, Clerk-relayed review provenance, and unbound
`STATE_AUDIT_VERDICT` markers. Prints the model each run used. Exit 1 on error-level findings.

## Sync discipline

Both the Open WebUI container and this local checkout push to the **original** repo. Pull before a
session and avoid running both writers concurrently. This repo never touches state.

## Updating safely (the update gate)

pi is **hard-pinned** to the version in `versions.lock.json`. The `bin/pi` launcher runs that exact
version and never updates anything; it only reports (at most daily) when a newer candidate exists.
Extension packages are pinned to exact versions in `~/.pi/agent/settings.json`, so
`pi update --extensions` skips them.

The behavior the learning system requires is declared in [`CONTRACT.md`](CONTRACT.md) and
[`contracts/learning-core.json`](contracts/learning-core.json), and enforced by `scripts/learn-check`.
Nothing is promoted unless every invariant still passes.

One-time wiring (already done on this machine):

```bash
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
install -m644 ~/learning-pi/harness/man/lpi.1 ~/.local/share/man/man1/
install -m644 ~/learning-pi/harness/systemd/learning-pi-audit.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now learning-pi-audit.timer

# Omarchy review integration: `local.pi-review` bar widget + desktop reminder
~/learning-pi/omarchy/install.sh
```

The `local.pi-review` bar widget shows `R` (pending), `R✓` (done), or `R✗`
(missed) only in the evening window (18:00–03:59); left-click launches `pi` in
the checkout. The 23:00/00:30 desktop reminder stays, but its old floating
terminal popup is gone. Both read the same `bin/pi-review-status` helper, which
matches the calendar date review-clerk stamps on the note, so they cannot
disagree.

The `lpi` opencode skill is registered by `skills.paths` in
`~/.config/opencode/opencode.json` pointing at `~/learning-pi/opencode`.

Commands (one umbrella):

```bash
lpi                   # what's newer (read-only); same as `lpi check`
lpi update            # stage pi + packages, gate, promote (or stay + diagnosis)  (alias: `lpi up`)
lpi update --dry-run  # gate without changing anything
lpi test              # the test suite (gate behavior, golden, resources, load probe)
lpi e2e               # replay short learner journeys in a sandbox (real models)
lpi e2e --tier full   # run each journey to its natural settle (slower)
lpi e2e --diff        # only the flows touched by the git diff
lpi e2e --list        # list the journey scenarios
lpi doctor            # re-run the suite against the current pins
lpi rollback          # rollback the last promotion (pi + packages)  (alias: `lpi rb`)
man lpi               # full reference
```

`lpi update` resolves newer pi **and** extension-package versions, stages them side-by-side in an
isolated sandbox (never touching `~/.pi/agent` until promotion), runs `lpi test`, and promotes the
whole set only if every invariant passes. Add `--dry-run` to see the result without changing
anything, or `--pi-only` to ignore package updates.

On a failed update the conductor **does not patch code**. It stays pinned and writes a diagnosis
report (failing invariant IDs, the relevant changelog watchlist hits) to
`~/.cache/learning-pi/diagnosis-*.md`. Then run the **`lpi`** opencode skill: it drives
`lpi update --e2e`, reads the report, classifies the break (adapter drift vs behavior drift vs
package breakage), fixes it under the contract, and re-runs `lpi test`. It also covers read-only
e2e testing of a change that is not an update. Changing expected behavior is the *revise door* — the
skill gets your explicit agreement before editing `CONTRACT.md`/tests/implementation together (see
`CONTRACT.md`).

A weekly `learning-pi-audit.timer` runs `pi/audit_gates.py` over the last 7 days of real sessions
(read-only) as a standing net for whatever tests miss.

### Repo layout for the gate

```
CONTRACT.md                  declared behavior (the thing updates must not break)
contracts/learning-core.json machine-readable invariants -> test names
bin/pi                       pinned launcher (never updates)
bin/notify-if-outdated       debounced availability check (never updates)
bin/pi-review-status         daily /review status helper (JSON; shared by widget + reminder)
bin/lpi                      the umbrella control command (update / test / doctor / rollback)
harness/pi-safe-update       update conductor (backing `lpi update`)
harness/locktool.py          versions.lock.json / journal helper
harness/mk-sandbox.sh         isolated duplicate harness builder
harness/man/                 lpi(1) man page
harness/audit-recent-sessions.sh + systemd/  weekly provenance audit
scripts/learn-check          the single test entrypoint
test/gate_test.mjs           core gate behavior (mocked pi)
test/golden/golden_test.mjs  write-gate / scout / review-delegation / retry / demotion / viz scenarios
test/viz_test.mjs            viz-mode pure units (spec validation, expression eval, ASCII render)
test/contract/               resource checks, load probe
test/fixtures/               synthetic learning-system state (never real data)
opencode/skills/lpi/         opencode skill: gated update, diagnosis/repair, and e2e
.pi/extensions/learning-gate/gate-core/   pure, pi-independent decision logic
.pi/extensions/learning-gate/pi-adapter/  the ONLY pi-version-aware file
.pi/extensions/viz-mode/     spec/render/explorer (display + interaction; no gating)
omarchy/                     Omarchy review integration: local.pi-review bar widget,
                             desktop reminder + systemd timer, installer
test/pi_review_status_test.sh  status-helper boundary tests (standalone)
```

## Uninstall

```bash
rm -rf ~/learning-system/.pi
# optionally remove the ".pi/" line from ~/learning-system/.git/info/exclude
```
