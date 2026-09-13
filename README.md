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
children.

## Models

Configured in `.pi/settings.json` (project scope only):

| Role | Model |
| --- | --- |
| Tutor (main session) | `glm-5.3-flash` |
| Scout / Clerk / verifiers | `deepseek-v4.1-flash` |
| Ingest reviewer (`review-gate`) | `muse-spark-1.3-contributor` (independent of the deepseek Clerk) |
| Tutor-write verifier (`tutor-audit`) | `deepseek-v4.1-flash` |

Verifiers deliberately differ from the Tutor so verification is independent, and the ingest reviewer
deliberately differs from the Clerk so it never reviews its own model. Adjust in
`.pi/settings.json`; no other file needs to change.

## Verification gate

`.pi/extensions/learning-gate` tracks verification subagent calls per agent run and withholds an
assistant turn unless the matching, **passing** receipt is present:

| Turn contains | Required receipt |
| --- | --- |
| Teaching claims (Tutor) | `fact-check` whose `rendered_content` matches the emitted text (≥85% token coverage) and has no `ISSUES` |
| A question batch | `quiz-audit` returning `PASS` (or `PASS_WITH_FLAGS` for lows-only, accepted silently with no banner to the learner, max 2 cycles) |
| A grade | `grade-audit` with `agrees === true`/`PASS`; disagreement is rejected and the verifier's `correct_verdict` is surfaced |
| A `Learning System/` write during teach/resume | `tutor-audit` reading back the lesson file / session note / learning record / `Pending Ingest.json` |
| An ingest | Clerk's result must carry a `REVIEW_GATE_VERDICT` marker; `PASS` renders clean, `ISSUES`/`PASS_WITH_FLAGS` render with a `⚠️ REVIEW FLAGS SURFACED` banner (never an endless re-run) |
| A new lesson | a `scout` run before teaching |

The reviewer's scope is the ingest's own output only (its wiki page(s) + Active Concepts row(s)).
State drift is reported separately by `audit_state.py`, which runs automatically at ingest and
review close (and on demand via `/audit`).

Receipts are **consumed per emitted message**, so every teaching step needs its own fresh,
content-matched verification (generation-to-emission — "verify A, emit B" is blocked).

### Turn type is explicit (not guessed)

- Prompt templates carry a flow marker (`[[FLOW:teach|resume|review|ingest]]`) that the gate reads
  directly; the string heuristics are only a fallback for untemplated triggers.
- Every assistant message must begin with a turn tag the gate strips before the learner sees it:
  - `[[TURN:claims]]` → requires a content-matched, passing `fact-check`
  - `[[TURN:quiz]]` → requires a PASS (or flagged PASS_WITH_FLAGS) `quiz-audit`
  - `[[TURN:grade]]` → requires an agreeing `grade-audit`
  - `[[TURN:none]]` → no verifier required
- A missing tag is withheld (`NO_TURN_TAG`); a `none` tag over text that matches an unused
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

Reports contradiction classes (MISSION vs CURRICULUM vs Profile vs Active Concepts vs wiki index)
and stale host paths. It never writes. Known findings in the current state include a real
`L08` status contradiction and a stale Learning Profile focus.

## Sync discipline

Both the Open WebUI container and this local checkout push to the **original** repo. Pull before a
session and avoid running both writers concurrently. This repo never touches state.

## Uninstall

```bash
rm -rf ~/learning-system/.pi
# optionally remove the ".pi/" line from ~/learning-system/.git/info/exclude
```
