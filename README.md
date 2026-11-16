# learning-pi

This repo holds the pi control layer and the learner state for a spaced-repetition learning system. The tutor runtime is the skills, subagents, prompts, verification gate, bridge, and deploy stack. The learner notebook is under `state/`.

## What is this?

An AI tutor that teaches and remembers what you know.

- You learn real subjects. `/teach eigenvalue decomposition` starts one, and `/lesson` gives the next curriculum lesson. You read the material and bring notes plus a closed-book model. The tutor triages that model, attacks the holes one at a time, and never lectures the topic cold. When your own repair fails, it teaches that one gap one checked step at a time. It cannot move on until you pass a fresh check and restate the gap yourself.
- It cannot bluff you. An independent verifier fact-checks every claim before you see it. Anything unverified is withheld, not shown.
- It remembers. Everything you learn becomes review cards on a schedule (`/review`). Your mistakes jump the queue. Your own explanations accumulate into a personal wiki.
- Your data is files. All state is Markdown and JSON in a git repo you own: sessions, concepts, and the wiki. There is no database, no lock-in, and the history is included.

> Questions, ideas, show-and-tell, and the build log all live in the project's [Discussions](https://github.com/delightaheebwa/learning-system/discussions). That link stays at the former repo's URL because it is still the community hub. This project is built in public.

> [`docs/README.md`](docs/README.md) maps every doc and names the sources of truth. Completed audit and roadmap records live in [`docs/archive/`](docs/archive/README.md). Read `CONTRACT.md` before changing teaching behavior or the gate.

> [`docs/teaching-methodology.md`](docs/teaching-methodology.md) covers how the interrogation flow relates to LearnHarness. It names what is imported: measurement, dependency ordering, the predict, attack, then check sequence, one-step reveals, repair mode, and the entailment check. It also names what is deliberately not imported: teacher-first cold lessons, a methodology catalogue, reveal-and-move-on, Tutor-authored v2, numeric confidence, and symbolic derivations.

## One repo

```
~/learning-pi/          this repo: the tutor runtime and the learner state
~/learning-pi/state/    the notebook, the wiki, and the state scripts
```

The learner state was a separate repo until 2026-11-09. It now lives in `state/` with its full commit history. Run `install.sh ~/learning-pi/state` once to link the `.pi/` overlay. Then run `pi` from `~/learning-pi/state` so the relative paths in the skills resolve. Set `LEARNING_SYSTEM_ROOT` to the same path for the scripts that take a state root. See [`docs/README.md`](docs/README.md) for the open integration work on `install.sh` and `init-state.sh`.

## Two ways to use it

- Open WebUI with pi, so you chat in your browser. Open WebUI is the face and pi is the brain. The chat UI talks to `pi-bridge`, which drives the same tutor, gate, and skills. This suits long-form learning with images and history.
- pi only, in the terminal. Run `pi` inside `state/` and talk to the tutor directly. This is the same brain without a browser or Docker. It suits quick sessions and machines where you do not want the web stack.

Both use the same tutor and the same notebook. Pick one per session.

## Set up once per platform

The prerequisites below set up the pi layer. The learner state already lives in `state/`. To start using it, see [State](#state).

All platforms need `git` and `python3`. The setup also needs `deno` for `lpi test`, and `nodejs` plus `npm`, because `lpi update` checks extension versions via `npm view`. Install [`mise`](https://mise.jdx.dev) for the pinned `pi` binary. The Open WebUI face in `deploy/` is Linux-only and also needs Docker and Compose. The commands below are idempotent, so re-running them is safe.

### Omarchy and Arch Linux

```bash
sudo pacman -S --needed git openssh python base-devel curl unzip mise deno nodejs npm openssl
# optional, only for the Linux-only Open WebUI face in deploy/: docker and firewall
sudo pacman -S --needed docker docker-compose ufw
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: see the State section below
```

Optional Omarchy extras: the bar widget and the evening reminder.

```bash
~/learning-pi/omarchy/install.sh
```

### Ubuntu, Debian, and WSL

```bash
sudo apt-get update && sudo apt-get install -y git python3 curl unzip openssl ca-certificates nodejs npm
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"
command -v mise >/dev/null || curl -fsSL https://mise.run | sh
command -v deno >/dev/null || curl -fsSL https://deno.land/install.sh | sh
grep -qs 'mise/shims' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"' >> ~/.bashrc
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: see the State section below
```

### Windows with WSL2

Native Windows (PowerShell or `cmd.exe`) is not supported. Every entrypoint is bash: `install.sh`, `bin/pi`, and `scripts/learn-check`. The `.pi/` overlay uses Unix symlinks, and the deploy path needs systemd, `ufw`, and Linux `docker0` networking. On Windows, run everything inside WSL2.

```powershell
# PowerShell as Administrator (once): enable WSL2 and install Ubuntu. Reboot when prompted. Needs Windows 10 2004+ or 11.
wsl --install
# Then install Docker Desktop, enable "Use the WSL 2 based engine" + WSL integration for the Ubuntu distro
```

```bash
# Inside the Ubuntu/WSL2 distro: enable systemd (needed for pi-bridge.service and the audit timer), then restart the distro
sudo sh -c 'printf "[boot]\nsystemd=true\n" > /etc/wsl.conf'
exit
```

```powershell
wsl --shutdown
```

```bash
# Re-enter the distro and verify systemd + docker, then follow the Ubuntu/Debian block above
systemd-detect-virt >/dev/null; docker run --rm hello-world
sudo apt-get update && sudo apt-get install -y git python3 curl unzip openssl ca-certificates nodejs npm
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"
command -v mise >/dev/null || curl -fsSL https://mise.run | sh
command -v deno >/dev/null || curl -fsSL https://deno.land/install.sh | sh
grep -qs 'mise/shims' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"' >> ~/.bashrc
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: see the State section below
```

Docker Desktop runs on the Windows side. The checkout in WSL is the single working copy. The current Open WebUI face publishes on `http://127.0.0.1:3000`, as described in `deploy/README.md`. Keep the repo on the Linux filesystem (`~/...`, not `/mnt/c/...`) so symlinks work and performance holds.

### macOS with Homebrew

```bash
command -v brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git python mise deno node
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: see the State section below
```

## State

The learner notebook is `state/`. It holds:

- `Learning System/`: SRS tables, sessions, reviews, and lessons.
- `Knowledge Wiki/`: wiki pages and raw sources.
- `scripts/`: state tooling.
- `infra/` and the frozen `Skills/` snapshot.

Its history came across in the merge.

To start using it:

```bash
~/learning-pi/install.sh ~/learning-pi/state
cd ~/learning-pi/state && pi   # approve/trust once, then /review /lesson /teach
```

Define your track in `state/Learning System/MISSION.md` and `state/Learning System/CURRICULUM.md`. Then run `/teach <topic>` or `/lesson`.

`init-state.sh` still builds a separate scaffold repo from a clone. Rewriting it for the single-repo layout is open work, listed in `docs/README.md`.

Notes:

- `pi --version` triggers `mise` to fetch the pinned version from `versions.lock.json` on first run. `learn-check --no-load` verifies the gate without a live `pi` binary or network models.
- If `~/.local/bin` is not on your `PATH`, persist the full export from your platform's block in your shell rc (`~/.bashrc` or `~/.zshrc`). That export covers `~/.local/bin`, the mise shims, and `~/.deno/bin`.
- macOS: Homebrew needs the Xcode Command Line Tools. Run `xcode-select --install`. That also provides `/usr/bin/git` and the system `python3`. macOS ships LibreSSL, whose `openssl` covers the one base-flow use, `openssl rand -hex` for deploy keys.
- The Open WebUI face is optional and Linux-only. It needs systemd, `ufw`, and the `docker0` `172.17.0.1` bridge, which Docker Desktop for Mac or Windows does not provide. After the base setup above, follow the Apply steps in [`deploy/README.md`](deploy/README.md). macOS and Windows users run the pi CLI path instead.
- Clones use HTTPS, not SSH. The repo is public, so you need no key and no GitHub account. On a network that blocks outbound SSH, the old `git@github.com:` form fails with `ssh: connect to host github.com port 22: Connection timed out` plus git's misleading "Please make sure you have the correct access rights". The blocked port is the cause, not permissions. To push over SSH anyway, register a key and run `git remote set-url origin git@github.com:delightaheebwa/learning-pi.git`. If port 22 is blocked, map `github.com` to `ssh.github.com:443` in `~/.ssh/config`.

## Manual install

```bash
git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
~/learning-pi/install.sh ~/learning-pi/state
cd ~/learning-pi/state && pi      # approve/trust the project once
```

## Usage

Slash commands: `/review`, `/solo`, `/ingest <content>`, `/teach <topic>`, `/lesson`, `/continue`, `/pause`, and `/audit`. `/solo` is an AI-free closed-book check with no teaching and no hints.

The main pi session is the Tutor. The `scout`, `clerk`, and `naive-student` agents run as children, and so do the verifier subagents. `naive-student` is the graduation clone.

The Tutor writes only its four handoff artifacts at a pause or lesson end: the lesson file, the session note, the learning record, and `Pending Ingest.json`. The Clerk reconciles the position and state files during ingest: MISSION, CURRICULUM, Learning Profile, Active Concepts, Mistakes, and Learner History.

The `/review` flow mirrors that split. `review-scout` gathers context and the due queue. The main session runs the review. `review-clerk` writes the Review notes and session note, syncs the touched rows, runs the state audit, and commits.

> Editing `.pi/` takes effect only after a reload. A running pi process keeps the extension it loaded at startup. Changing `extensions/`, `skills/`, `agents/`, or `APPEND_SYSTEM.md` does not touch a live session. Run `/reload` in pi, or restart pi, after pulling changes, then confirm the new behavior. A long-lived process can otherwise keep enforcing stale gate logic indefinitely.

## Models

The models are configured in `.pi/settings.json` at project scope only.

| Role | Model |
| --- | --- |
| Tutor, main session | `glm-5.3-flash` (high) |
| Scout, Clerk, review-scout, review-clerk | `deepseek-v4.1-flash` |
| Graduation clone (`naive-student`) | `deepseek-v4.1-flash` |
| Gate verifiers: `fact-check`, `quiz-audit`, `grade-audit`, `tutor-audit`, `review-session-audit`, `ui-audit`, `graph-audit` | `muse-spark-1.3-contributor` (high) |
| Ingest reviewer (`review-gate`), dispatched by the Tutor on the Clerk's writes | `muse-spark-1.3-contributor` |
| Lesson-start context auditor (`scout-audit`), dispatched by the Tutor on the Scout digest | `muse-spark-1.3-contributor` |
| Graph extractor (`graph-extract`) | `deepseek-v4.1-flash` |

These models run the verifiers by default for cost and availability. Separation is a preference, not a guarantee. When the preferred model is unavailable, a verifier may run on the same model as the Tutor or Clerk, and that is acceptable. The gate does not enforce model identity. It records the model each run used in the subagent artifacts. Adjust the assignment in `.pi/settings.json`, and no other file needs to change.

## Verification gate

`.pi/extensions/learning-gate` tracks verification subagent calls per agent run. It withholds an assistant turn unless the matching, passing receipt is present.

### Teaching turns

- Teaching claims need a `fact-check` whose `rendered_content` covers the emitted text and has no `ISSUES`. With a judge configured, the rule is 100% span coverage, so the judge checks every sentence. The legacy path approximates that with ≥85% token coverage plus a length guard.
- A `claims` turn during teach or resume needs a `fact-check` envelope with a valid `turn_kind`. The values are `plan`, `triage`, `attack`, `hint`, `autopsy`, `answer`, `repair`, `grade_feedback`, and `idea`.
- A `triage` turn ships a grounded `triage[]`: a learner quote for every `suspect`, and a source citation for every `missing`.
- An `attack` turn ships exactly one subtype: `mechanism`, `counterexample`, `perturbation`, `source_clash`, `sabotage`, or `synthesis`.
- A `repair` turn ships its `repair` block.
- Only an `idea` turn ships the four-beat `foundation` block (`problem`, `where_from`, `conditions`, `contrast`), and its prose must be in the draft.
- The gate withholds (`FOUNDATION_INCOMPLETE`) any turn with a missing or unknown `turn_kind`, an ungrounded triage table, an attack with no single subtype, or a repair without its block. A fluent what-only lecture cannot render as if complete. Neither can a chain of ungrounded attacks. The verifier also returns `omitted_foundations[]`, which lists load-bearing conceptual theory with no trace in the draft. That list is an `ISSUES` verdict. Missing derivations are not omissions.
- A `repair` turn in teaching mode needs a `repair` block bound to one `gap`. The block names the `miss_class` and the tactic it selects, and ships exactly one checked `step`.

  A `teaching` turn opens the repair. The attack battery stays withheld (`NO_REPAIR_RECEIPT`) until a `done` turn names the fresh-surface check that a `grade-audit` already passed. That check must be bound to the graded item with `repair_gap` equal to this repair's gap. It is never prose, and never a check graded for another gap. The `done` turn also carries the learner's own-words restatement. A second gap cannot open first (`REPAIR_INCOMPLETE`).

  Three verifiers enforce the rest. `fact-check` enforces the trigger (`REPAIR_MODE_SKIPPED`), the method (Socratic-first, one motivated step), and the scope (`REPAIR_SCOPE_DRIFT`). `quiz-audit` enforces that the closing check is a new surface. `grade-audit` treats a recital as `SHALLOW_PASS`.

### Quiz and grade turns

- A question batch needs a `quiz-audit` that returns `PASS` with zero issues. Any issue at any severity blocks until fixed. There is no cap, so re-check until zero issues. The envelope carries `questions_json` and `rendered_content`. `rendered_content` is the full batch text: the intro and instructions, every question, and its options. It binds the whole emitted turn.
- A grade needs a `grade-audit` with `agrees === true` or `PASS`. The gate rejects a disagreement and surfaces the verifier's `correct_verdict`. One batched `items[]` envelope grades every answer from a single learner reply, never one subagent per answer. Items may carry `targets[]`, the graph `n_…` and `arg_…` ids, as additive record-keeping. The gate copies them from the scout digest, the verdict ignores them, and liveness is checked against the graph ledger when they are recorded on the attempt. `ops.py` rejects a missing or retracted id.

### Handoff writes

- A `Learning System/` handoff write during teach or resume needs a `tutor-audit` reading back one of four files: the lesson file, the session note, the learning record, or `Pending Ingest.json`. The audit runs once per handoff batch. Every issue blocks at any severity. Out-of-scope observations go to `context_notes`.

### Ingest

- A knowledge-graph write is gated when `CLERK_WRITES.graph` lists any created or linked id. The close stays withheld (`NO_GRAPH_AUDIT_PASS`) until an independent `graph-audit` returns `PASS` over every written id. `ISSUES` withholds (`GRAPH_AUDIT_ISSUES`) until the Clerk records a fix by retracting or correcting, then re-merging, and a fresh audit passes. There is no cycle cap. The audit fact-checks each proposition, each chain entailment, and each link identity against the material.
- An ingest waits for the Clerk to return a `CLERK_WRITES` receipt. The Tutor then dispatches an independent `review-gate` on the wiki pages written. `PASS` renders clean. `ISSUES` renders with a `⚠️ REVIEW FLAGS SURFACED` banner, never an endless re-run. A verdict the Clerk relays instead of a real review-gate run gets a `⚠️ INGEST GATE` banner. A review verdict with no `evidence` list gets a `⚠️ REVIEW GATE` banner.

### Review close

- A standalone `/review` closes after the delegated `review-clerk` run writes the Review notes, the session note, and the touched Active Concepts and Mistakes rows. The close needs a `review-session-audit` that reads those writes back against the transcript and the per-concept grade verdicts. `PASS` releases the summary. `ISSUES` withholds it (`REVIEW_SESSION_AUDIT_ISSUES`) until the writes are fixed and re-audited to zero issues. There is no cycle cap.

### Scout and review context

- A new lesson needs a `scout` run before teaching, plus one independent `scout-audit` on its digest. The audit checks completeness: every Further Reading URL was fetched or explicitly failed, excerpts, `theory` lines, and prereqs are present, and raw files are on disk. It also fact-checks: synthesis is grounded in the raw files, no synthesis comes from failed refs, and contradictions are surfaced. A missing audit withholds (`NO_SCOUT_AUDIT_PASS`). `ISSUES` renders with a `⚠️ SCOUT AUDIT FLAGS SURFACED` banner, never a withhold. No `evidence` gets a `⚠️ SCOUT AUDIT` banner. A partial or missing `SCOUT_DIGEST` receipt surfaces as a `⚠️ SOURCES INCOMPLETE` or `⚠️ SCOUT DIGEST UNVERIFIED` banner, never a withhold.
- A `/review` session needs a `review-scout` run before the first claims or quiz turn (`NO_REVIEW_CONTEXT` until then). A partial or missing `REVIEW_SCOUT_DIGEST` receipt surfaces as a `⚠️ REVIEW CONTEXT INCOMPLETE` or `⚠️ REVIEW SCOUT DIGEST UNVERIFIED` banner, never a withhold.

### Dispatch and receipt binding

Verifier and worker dispatches use the `dispatch` helper tool: `dispatch({ agent, task: { ...envelope } })`. It takes the envelope as an object, so the model never escapes JSON by hand. It runs the child through pi-subagents' structured delegation bridge and mints the gate receipt itself. The pi-subagents `subagent` tool requires a JSON-string `task` and is `exposure: "model-only"`. The gate blocks its `workflow` and `args` forms and redirects them to `dispatch`.

A grade turn that also teaches needs two receipts. The `grade-audit` covers the graded question, answer, and verdict. A `fact-check` covers the repair prose, with `rendered_content` set to the full emitted turn. A clean verifier `PASS` must carry a non-empty `evidence` list. The judge treats an evidence-less PASS as unsubstantiated (`*_STALE`).

The reviewer's scope is the ingest's own output only: its wiki pages and its Active Concepts rows. `audit_state.py` reports state drift separately. It runs automatically at ingest and review close, and on demand via `/audit`. The automatic runs fix the error or warning findings they touched, using the script's `STATE_AUDIT_FIXES` hints. They then surface whatever remains.

Receipts are consumed per emitted message. Every teaching step needs its own fresh, content-matched verification. The gate checks generation to emission, so "verify A, emit B" is blocked.

### Turn type is explicit

- Prompt templates carry a flow marker `[[FLOW:teach|resume|review|ingest|solo]]` that the gate reads directly. Flow detection is explicit-only. Keyword heuristics were removed because verifier subagent envelopes such as `"flow":"teach"` and "Pending Ingest.json" were being misread as learning flows.
- Every assistant message must begin with a turn tag. The gate strips the tag before the learner sees it.
  - `[[TURN:claims]]` requires a content-matched, passing `fact-check`.
  - `[[TURN:quiz]]` requires a `PASS` `quiz-audit` with zero issues. Any severity blocks.
  - `[[TURN:grade]]` requires an agreeing `grade-audit`.
  - `[[TURN:ui]]` requires a passing `ui-audit` bound to the emitted OpenUI payload and covering the prose.
  - `[[TURN:none]]` needs no verifier.
- A missing tag is withheld (`NO_TURN_TAG`) on the legacy path. Three cases are exempt. The gate infers a grade or quiz turn from a `grade-audit` or `quiz-audit` receipt. The match is either bound, or the single valid pending receipt when an async verifier's completion notification carries no draft. An ingest summary after a clerk dispatch, and an untagged review close once the session note is written, both carry an implicit `[[TURN:none]]`, verified by the clerk's `REVIEW_GATE_VERDICT` or the `review-session-audit` receipt. With a judge configured, a tag is a hint and the judge classifies the turn from the content, so an untagged claims turn whose fact-check covers it renders. The gate also withholds a `none` tag over text that matches an unused verification draft (`TURN_TAG_MISMATCH`).

The gate allows up to 2 withheld retries per turn, and the counter resets on each clean pass. After that it surfaces the turn with an `⛔ UNVERIFIED` banner. Internal errors fail open. Non-learning sessions are never gated.

### The judge

The gate can run a judge, a model that answers the semantic questions the deterministic code cannot: what type of turn this is, whether a verifier's verified draft covers 100% of the emitted text, whether a `PASS` is substantive, and what exact remedy is needed. The judge only sees and writes text. It runs no tool, writes no file, and changes no state. The engine performs every action. Receipts remain the verifier's own statement, and the judge never authors them.

- The judge model is Gemini `gemini-3.5-flash-lite`, free tier about 15 RPM and 500 RPD. Configure it under the `gemini` provider in `~/.pi/agent/models.json`, which uses Google's OpenAI-compatible endpoint. Set `GEMINI_API_KEY` in the environment. Override the model with `LEARNING_GATE_JUDGE_MODEL`.
- A hard case escalates to `gemini-3.5-flash`. A hard case is a valid receipt that does not fully cover, no best receipt, or thin substantiveness. The overrides are `LEARNING_GATE_JUDGE_ESCALATION_MODEL` and `LEARNING_GATE_JUDGE_ESCALATION_MAX_PER_DAY`, which defaults to 20. A primary outage also escalates before falling back to the legacy path.
- Turn tags become hints. The judge reads the turn type from the content, so an untagged claims turn whose fact-check covers it renders. Verifier and notification channels are never gated.
- The full-draft rule is 100%. The Tutor must put all text it will emit into the verifier envelope and emit that draft unchanged. Any uncovered span blocks, and the remedy names the span.
- A `PASS` the judge scores as unsubstantiated verifies nothing, and the receipt is treated as absent. Unsubstantiated means no evidence or unchecked items.
- While any issue remains, the gate keeps blocking and never dumps the turn as `⛔ UNVERIFIED`. The cap applies to every other reason. Severity labels no longer gate, so a `low` blocks exactly like a `high` or a `medium`.
- When the same issue blocks three times, the judge adjudicates. If the issue no longer applies, the engine releases the turn with `⚠️ VERIFIER DISPUTED`.
- Every decision and receipt is appended to `~/.pi/agent/learning-gate/` in `receipts.ndjson` and `decisions.ndjson` for provenance and review.
- With no judge configured, no auth, a rate limit, or invalid output, the gate runs the deterministic legacy path unchanged. A learning turn never dead-ends on a judge fault.

## Skills

> The skills in `learning-pi/.pi/skills/` are the canonical teaching behavior. The copies under `state/Skills/` and `state/OPENWEBUI.md` are a frozen, unmaintained legacy path. The two diverged, and pi is now the single source of truth for teaching behavior, verification, and the flows. Add teaching-behavior changes here only. A behavior-contract change updates `CONTRACT.md` and `contracts/learning-core.json` in the same commit. The frozen copies are not deleted yet, so the legacy Open WebUI path stays readable.

Four of the skills in `.pi/skills/` are stripped of Open WebUI plumbing, host-specific paths, and volatile state: lesson positions, dates, statuses, and archive logic. The four are `learning-system`, `learning-teach`, `learning-review`, and `llm-wiki`. The copies under `state/Skills/` are frozen and unmaintained. Treat `.pi/skills/` as canonical.

They are derived, not symlinked, so re-derive and diff them if the canonical skills change:

```bash
diff -u ~/learning-pi/state/Skills/learning-system/SKILL.md ~/learning-pi/.pi/skills/learning-system/SKILL.md
```

## State audit

```bash
python3 ~/learning-pi/pi/audit_state.py --root ~/learning-pi/state
```

The audit reports five things:

- Contradictions among MISSION, CURRICULUM, Profile, Active Concepts, and the wiki index.
- Position-pointer drift between the position files and the active lesson's `Checkpoint N/M`.
- Active Concepts `Next Review` against `Attempts.json`.
- Scout-digest TTL.
- Stale host paths.

It never writes. It prints a `STATE_AUDIT_FIXES:` JSON array of remediation hints for mechanically fixable findings. The automatic ingest and review runs apply the hints for the errors and warnings they touched, re-run once, and surface anything ambiguous or unrelated. `/audit` stays report-only. Known findings in the current state include outstanding Active Concepts and `Attempts.json` schedule drift.

## Gate provenance audit

```bash
python3 ~/learning-pi/pi/audit_gates.py --session <session.jsonl>
```

This audit reconstructs which verifier runs backed each claimed verdict in a pi session. It is read-only. It looks for these problems:

- A dispatch with no artifact.
- A non-zero exit.
- A harness-`rejected` run that the gate may still have consumed.
- A review verdict with no backing run.
- Clerk-relayed review provenance.
- An unbound `STATE_AUDIT_VERDICT` marker.

It prints the model each run used, and it exits 1 on error-level findings.

## Sync discipline

The pi layer and the learner state are one repo. `state/` is the notebook. The optional Open WebUI face in `deploy/` holds chat transcripts only and drives the same pi runtime through `pi-bridge`. Pull before a session. Avoid running two state-writing sessions at once. There is no separate state repo and no container checkout to sync.

## Updating safely

pi is hard-pinned to the version in `versions.lock.json`. The `bin/pi` launcher runs that exact version and never updates anything. It only reports, at most daily, when a newer candidate exists. Extension packages are pinned too, so `pi update --extensions` skips them. See `versions.lock.json`.

The behavior the learning system requires is declared in [`CONTRACT.md`](CONTRACT.md) and [`contracts/learning-core.json`](contracts/learning-core.json). `scripts/learn-check` enforces it. Nothing is promoted unless every invariant still passes.

One-time wiring, already done on this machine:

```bash
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
install -m644 ~/learning-pi/harness/man/lpi.1 ~/.local/share/man/man1/
install -m644 ~/learning-pi/harness/systemd/learning-pi-audit.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now learning-pi-audit.timer

# Omarchy review integration: `local.pi-review` bar widget + desktop reminder
~/learning-pi/omarchy/install.sh
```

The `local.pi-review` bar widget shows `R` for pending, `R✓` for done, or `R✗` for missed, only in the evening window from 18:00 to 03:59. Left-click launches `pi` in the checkout. The desktop reminder at 23:00 and 00:30 stays, but its old floating terminal popup is gone. Both read the same `bin/pi-review-status` helper, which matches the calendar date review-clerk stamps on the note, so they cannot disagree.

The `lpi` command is `harness/pi-safe-update`. The retired `lpi` OpenCode skill stub is archived at [`docs/archive/opencode-lpi-skill/`](docs/archive/opencode-lpi-skill/SKILL.md). It is not on OpenCode's discovery path and is not loaded.

Commands, with one umbrella:

```bash
lpi                   # what's newer, read-only. Same as `lpi check`.
lpi update            # stage pi + packages, gate, then promote or stay with a diagnosis. Alias: `lpi up`.
lpi update --dry-run  # gate without changing anything
lpi test              # the test suite: gate behavior, golden, resources, load probe
lpi e2e               # replay short learner journeys in a sandbox, with real models
lpi e2e --tier full   # run each journey to its natural settle (slower)
lpi e2e --diff        # only the flows touched by the git diff
lpi e2e --list        # list the journey scenarios
lpi doctor            # re-run the suite against the current pins
lpi rollback          # rollback the last promotion (pi + packages). Alias: `lpi rb`.
man lpi               # full reference
```

`lpi update` resolves newer pi and extension-package versions. It stages them side by side in an isolated sandbox and never touches `~/.pi/agent` until promotion. It runs `lpi test` and promotes the whole set only if every invariant passes. Add `--dry-run` to see the result without changing anything, or `--pi-only` to ignore package updates.

On a failed update the conductor does not patch code. It stays pinned and writes a diagnosis report to `~/.cache/learning-pi/diagnosis-*.md`. The report lists the failing invariant IDs and the relevant changelog watchlist hits. Then run the `lpi` opencode skill. It drives `lpi update --e2e`, reads the report, and classifies the break as adapter drift, behavior drift, or package breakage. It fixes the break under the contract and re-runs `lpi test`. It also covers read-only e2e testing of a change that is not an update. Changing expected behavior is the revise door. The skill gets your explicit agreement before it edits `CONTRACT.md`, the tests, and the implementation together. See `CONTRACT.md`.

A weekly `learning-pi-audit.timer` runs `pi/audit_gates.py` over the last 7 days of real sessions. The run is read-only and acts as a standing net for whatever the tests miss.

### Open WebUI face with pi-bridge and deploy

The face shipped on 2026-10-15/16. `bridge/` is an OpenAI-compatible endpoint in front of the pinned pi runtime, so Open WebUI can be the face while pi stays the brain. The gate, subagents, and skills run unchanged, and Open WebUI holds only chat transcripts. `deploy/` runs Open WebUI in Docker in front of a host `pi-bridge` systemd service. A verified `[[TURN:ui]]` turn rides out as a self-hosted OpenUI widget embed below the prose. The code is `bridge/server.py` and `deploy/openui/`, served by the installer. The behavior contract is the `B-*` invariants in `CONTRACT.md` and `contracts/learning-core.json`, and the JSON is the authoritative set. Details are in [`bridge/README.md`](bridge/README.md), [`deploy/README.md`](deploy/README.md), and [`deploy/SECURITY.md`](deploy/SECURITY.md).

### Repo layout for the gate

```
CONTRACT.md                  declared behavior (the thing updates must not break. See contracts/learning-core.json)
contracts/learning-core.json machine-readable invariants mapped to test names
bridge/                      OpenAI-compatible pi-bridge (B-* invariants) + README
deploy/                      Docker Open WebUI + pi-bridge.service + searxng + README/SECURITY
.pi/agents/                  15 subagents (incl. scout-audit, ui-audit, graph-extract + graph-audit). Details in .pi/
.pi/prompts/                 8 slash prompts (review/solo/ingest/teach/lesson/continue/pause/audit)
.pi/skills/                  5 skills
bin/pi                       pinned launcher (never updates)
bin/notify-if-outdated       debounced availability check (never updates)
bin/pi-review-status         daily /review status helper (JSON, shared by widget and reminder)
bin/lpi                      the umbrella control command (update, test, doctor, rollback, and `lpi e2e --list` or `--diff`)
harness/pi-safe-update       update conductor (backing `lpi update`)
harness/locktool.py          versions.lock.json and journal helper
harness/mk-sandbox.sh         isolated duplicate harness builder
harness/e2e-runner.py        e2e runner (--tier smoke|full)
harness/man/                 lpi(1) man page
harness/audit-recent-sessions.sh + systemd/  weekly provenance audit
scripts/learn-check          the single test entrypoint (7 deno suites + graph suite + bridge + contract checks + load probe + sidecar py_compile)
test/gate_test.mjs           core gate behavior (mocked pi)
test/golden/                 write-gate, scout, review-delegation, retry, and demotion scenarios
test/judge_*.mjs + live_judge_test.mjs  judge suites (live variants opt-in, need models)
test/redteam/                adversarial suites
test/bridge/                 bridge suite (fake_pi + run_tests.py give B-* coverage)
test/contract/               resource checks, load probe
test/e2e/scenarios/          7 e2e scenarios (smoke + full, incl. openui-smoke)
test/fixtures/               synthetic learner state (never real data)
.pi/extensions/learning-gate/gate-core/   pure, pi-independent decision logic
.pi/extensions/learning-gate/pi-adapter/  the ONLY pi-version-aware file
omarchy/                     Omarchy review integration: local.pi-review bar widget,
                             desktop reminder + systemd timer, installer
test/pi_review_status_test.sh  status-helper boundary tests (standalone)
```

## Uninstall

```bash
rm -rf ~/learning-pi/state/.pi
```
