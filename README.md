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
`/audit`.
The main pi session acts as the **Tutor**; `scout`, `clerk`, and the verifier subagents run as
children. The Tutor writes only its four handoff artifacts (lesson file, session note, learning
record, `Pending Ingest.json`) at a pause or lesson end; the **Clerk** reconciles position/state
files (MISSION, CURRICULUM, Learning Profile, Active Concepts, Mistakes, Learner History) at
`/ingest`.

> **Editing `.pi/` takes effect only after a reload.** A running pi process keeps the extension it
> loaded at startup; changing `extensions/`, `skills/`, `agents/`, or `APPEND_SYSTEM.md` does **not**
> touch a live session. Run `/reload` in pi (or restart pi) after pulling changes, then confirm the
> new behavior. A long-lived process can otherwise keep enforcing stale gate logic indefinitely.

## Models

Configured in `.pi/settings.json` (project scope only):

| Role | Model |
| --- | --- |
| Tutor (main session) | `glm-5.3-flash` |
| Scout / Clerk | `deepseek-v4.1-flash` |
| Gate verifiers (`fact-check` / `quiz-audit` / `grade-audit` / `tutor-audit` / `review-session-audit`) | `muse-spark-1.3-contributor` (high) |
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
| Teaching claims (Tutor) | `fact-check` whose `rendered_content` matches the emitted text (≥85% token coverage) and has no `ISSUES` |
| A question batch | `quiz-audit` returning `PASS` (or `PASS_WITH_FLAGS` for lows-only, accepted silently with no banner to the learner, max 2 cycles) |
| A grade | `grade-audit` with `agrees === true`/`PASS`; disagreement is rejected and the verifier's `correct_verdict` is surfaced. One batched `items[]` envelope grades every answer from a single learner reply (never one subagent per answer) |
| A `Learning System/` handoff write during teach/resume | `tutor-audit` reading back the lesson file / session note / learning record / `Pending Ingest.json` (once per handoff batch; high/medium block, lows pass as `PASS_WITH_FLAGS`) |
| An ingest | after the Clerk returns a `CLERK_WRITES` receipt, the Tutor dispatches an independent `review-gate` on the wiki pages written; `PASS` renders clean, `ISSUES`/`PASS_WITH_FLAGS` render with a `⚠️ REVIEW FLAGS SURFACED` banner (never an endless re-run). A verdict relayed by the Clerk instead of a real review-gate run gets a `⚠️ INGEST GATE` banner; a review verdict with no `evidence` list gets a `⚠️ REVIEW GATE` banner |
| The **close** of a standalone `/review` (Review notes, session note, touched Active Concepts / Mistakes rows written) | `review-session-audit` reading the exact writes back against the transcript + per-concept grade verdicts; `PASS`/`PASS_WITH_FLAGS` render clean, `ISSUES` renders with a `⚠️ REVIEW FLAGS SURFACED` banner — never withheld, never a re-run (cap 2 passes per flow) |
| A new lesson | a `scout` run before teaching; a partial/missing `SCOUT_DIGEST` receipt surfaces as a `⚠️ SOURCES INCOMPLETE` / `⚠️ SCOUT DIGEST UNVERIFIED` banner (never a withhold) |

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
- A missing tag is withheld (`NO_TURN_TAG`) — **except** a grade/quiz turn, which the gate infers
  from a `grade-audit`/`quiz-audit` receipt (a bound match, or the single valid pending receipt when
  an async verifier's completion notification carries no draft) so a dropped tag cannot dead-end the
  session. `claims`/`none` are never inferred. A `none` tag over text that matches an unused
  verification draft is withheld too (`TURN_TAG_MISMATCH`).

Behavior: up to 2 withheld retries per turn (counter resets on each clean pass), then the turn is surfaced with an `⛔ UNVERIFIED`
banner; internal errors fail open. Non-learning sessions are never gated.

## Skills

The four skills in `.pi/skills/` are **sanitized, vendored copies** of the originals — stripped of
Open WebUI plumbing, host-specific paths, and all volatile state (lesson positions, dates,
statuses, archive logic). The originals under the state repo's `Skills/` are untouched.

They are derived, not symlinked, so re-derive and diff them if the canonical skills change:

```bash
diff -u ~/learning-system/Skills/learning-system/SKILL.md ~/learning-pi/.pi/skills/learning-system/SKILL.md
```

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
```

The `pi-diagnosis-fix` opencode skill is registered by `skills.paths` in
`~/.config/opencode/opencode.json` pointing at `~/learning-pi/opencode`.

Commands (one umbrella):

```bash
lpi                   # what's newer (read-only); same as `lpi check`
lpi update            # stage pi + packages, gate, promote (or stay + diagnosis)  (alias: `lpi up`)
lpi update --dry-run  # gate without changing anything
lpi test              # the test suite (gate behavior, golden, resources, load probe)
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
`~/.cache/learning-pi/diagnosis-*.md`. Then run the **`pi-diagnosis-fix`** opencode skill: it reads
the report, classifies the break (adapter drift vs behavior drift vs package breakage), fixes it
under the contract, and re-runs `lpi test`. Changing expected behavior is the *revise door* — the
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
bin/lpi                      the umbrella control command (update / test / doctor / rollback)
harness/pi-safe-update       update conductor (backing `lpi update`)
harness/locktool.py          versions.lock.json / journal helper
harness/mk-sandbox.sh         isolated duplicate harness builder
harness/man/                 lpi(1) man page
harness/audit-recent-sessions.sh + systemd/  weekly provenance audit
scripts/learn-check          the single test entrypoint
test/gate_test.mjs           core gate behavior (mocked pi)
test/golden/golden_test.mjs  write-gate / scout / retry / demotion scenarios
test/contract/               resource checks, load probe
test/fixtures/               synthetic learning-system state (never real data)
opencode/skills/pi-diagnosis-fix/  opencode skill to repair a failed update
.pi/extensions/learning-gate/gate-core/   pure, pi-independent decision logic
.pi/extensions/learning-gate/pi-adapter/  the ONLY pi-version-aware file
```

## Uninstall

```bash
rm -rf ~/learning-system/.pi
# optionally remove the ".pi/" line from ~/learning-system/.git/info/exclude
```
