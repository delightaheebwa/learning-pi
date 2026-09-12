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

Slash commands: `/review`, `/ingest <content>`, `/teach <topic>`, `/lesson`, `/continue`, `/pause`.
The main pi session acts as the **Tutor**; `scout`, `clerk`, and the verifier subagents run as
children.

## Models

Configured in `.pi/settings.json` (project scope only):

| Role | Model |
| --- | --- |
| Tutor (main session) | `glm-5.3-flash` |
| Scout / Clerk / verifiers | `deepseek-v4.1-flash` |

Verifiers deliberately differ from the Tutor so verification is independent. Adjust in
`.pi/settings.json`; no other file needs to change.

## Verification gate

`.pi/extensions/learning-gate` tracks verification subagent calls per agent run and withholds an
assistant turn when the matching receipt is missing:

| Turn contains | Required receipt |
| --- | --- |
| Teaching claims (Tutor) | `fact-check` |
| A question batch | `quiz-audit` |
| A grade | `grade-audit` |
| A new lesson | `scout` digest (before teaching) |

Behavior: up to 2 withheld retries per run, then the turn is surfaced with an `⛔ UNVERIFIED`
banner; internal errors fail open. Classification is heuristic — it only acts in learning flows
(`/review`, `/teach`, `/lesson`, `/continue`, `/pause`, `/ingest`).

**Known limitation:** the gate observes the main session. Clerk's nested `review-gate` call for
ingests is enforced by Clerk's own instructions, not by the extension.

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
