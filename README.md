# learning-pi

The **pi control layer** for the `learning-system` spaced-repetition system. This repo contains
only pi-side resources (skills, subagents, prompts, a verification gate, and an audit script). It
contains **no learning state**.

## What is this?

An AI tutor that actually teaches you things — and remembers what you know.

- **You learn real subjects** (`/teach eigenvalue decomposition`, or `/lesson`
  for the next curriculum lesson). The tutor first checks what you already
  know, shows you a plan, then teaches in small steps with questions along
  the way.
- **It can't bluff you.** Every claim the tutor makes is fact-checked by an
  independent verifier before you see it. Anything unverified is withheld,
  not shown.
- **It remembers.** Everything you learn becomes review cards on a schedule
  (`/review`), your mistakes jump the queue, and your own explanations
  accumulate into a personal wiki.
- **Your data is just files.** All state is Markdown + JSON in a git repo you
  own — sessions, concepts, wiki. No database, no lock-in, history included.

> **Community:** questions, ideas, show-and-tell, and the build log all live in
> [`learning-system` Discussions](https://github.com/delightaheebwa/learning-system/discussions).
> This project is built in public.

> **Roadmap:** see [`AUDIT-ROADMAP.md`](AUDIT-ROADMAP.md) for the audit verdict and the staged
> improvement plan (P0–P2 done, P3 deferred, plus post-cascade P4 foundation-beats, scout-audit gate,
> teach rewrite, and bridge + deploy). Read it before changing teaching behavior, the gate, learner state, or
> the Knowledge Wiki, and update it when a stage lands.

## The two repos

```
~/learning-pi       this repo: the tutor program (skills, gate, prompts)
~/my-learning       your notebook: everything you learn — or ~/learning-system,
                    the owner's example notebook, full of real data
```

`install.sh` plugs this repo's `.pi/` into the notebook checkout (and git-ignores
it there), so `pi` runs the tutor inside your data. The tutor's code never enters
your notebook repo, and your data never enters this repo.

## Two ways to use it

- **Open WebUI + pi (chat in your browser).** Open WebUI is the face, pi is the
  brain: the chat UI talks to `pi-bridge`, which drives the same tutor, gate,
  and skills. Best for long-form learning with images and history.
- **pi only (terminal).** Run `pi` inside your notebook checkout and talk to the
  tutor directly. Same brain, no browser, no Docker. Best for quick sessions
  and for machines where you don't want the web stack.

Both hit the same tutor and the same notebook — pick per session, or use just one.

## Set up (one-shot per platform)

Two paths share the same prerequisites below. **Path A — clone the example:**
the owner's live `learning-system` (real data, useful as a reference implementation).
**Path B — your own fresh state (recommended for actual use):** an empty
scaffold with the same structure and zero owner data, built by
`init-state.sh`, ready for your own material.

Base requirements (all platforms): `git`, `python3`, [`mise`](https://mise.jdx.dev)
(provides the pinned `pi` binary), `deno` for `lpi test`, and `nodejs`/`npm`
(`lpi update` checks extension versions via `npm view`). The Open WebUI face
(`deploy/`, Linux-only) additionally needs Docker + Compose. Commands below are
idempotent — re-running them is safe.

### Omarchy / Arch Linux

```bash
sudo pacman -S --needed git openssh python base-devel curl unzip mise deno nodejs npm openssl
# optional, only for the deploy/ Open WebUI face (Linux-only): docker + firewall
sudo pacman -S --needed docker docker-compose ufw
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone git@github.com:delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: pick a state path below (A example, B fresh)
```

Omarchy extras (bar widget + evening reminder — optional):

```bash
~/learning-pi/omarchy/install.sh
```

### Ubuntu / Debian / WSL

```bash
sudo apt-get update && sudo apt-get install -y git python3 curl unzip openssl ca-certificates nodejs npm
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"
command -v mise >/dev/null || curl -fsSL https://mise.run | sh
command -v deno >/dev/null || curl -fsSL https://deno.land/install.sh | sh
grep -qs 'mise/shims' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"' >> ~/.bashrc
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone git@github.com:delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: pick a state path below (A example, B fresh)
```

### Windows (via WSL2 — native Windows is not supported)

Native Windows (PowerShell/`cmd.exe`) is **not** supported: every entrypoint is
bash (`install.sh`, `bin/pi`, `scripts/learn-check`), the `.pi/` overlay uses
Unix symlinks, and the deploy path needs systemd + `ufw` + Linux `docker0`
networking. On Windows, run everything inside WSL2:

```powershell
# PowerShell as Administrator (once): enable WSL2 + install Ubuntu (reboot when prompted; needs Windows 10 2004+ or 11)
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
# Re-enter the distro and verify systemd + docker, then same as Ubuntu/Debian above
systemd-detect-virt >/dev/null; docker run --rm hello-world
sudo apt-get update && sudo apt-get install -y git python3 curl unzip openssl ca-certificates nodejs npm
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"
command -v mise >/dev/null || curl -fsSL https://mise.run | sh
command -v deno >/dev/null || curl -fsSL https://deno.land/install.sh | sh
grep -qs 'mise/shims' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"' >> ~/.bashrc
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone git@github.com:delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: pick a state path below (A example, B fresh)
```

Notes: Docker Desktop runs Windows-side — the WSL checkout is the working copy
and the UI is reached as `http://localhost:3000` from WSL/browsers (see
`learning-system/infra/ACCESS.md`). Keep the repos on the Linux filesystem
(`~/...`, not `/mnt/c/...`) for symlinks and performance.

### macOS (Homebrew)

```bash
command -v brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git python mise deno node
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone git@github.com:delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: pick a state path below (A example, B fresh)
```

## State — two paths

Prerequisites above give you the pi layer. Now pick your state:

### Path A — clone the example (owner's live data)

```bash
git clone https://github.com/delightaheebwa/learning-system.git ~/learning-system  # owner's data, as an example
~/learning-pi/install.sh ~/learning-system
cd ~/learning-system && pi  # approve/trust once, then /review /lesson /teach
```

Read-only inspiration: start your own track rather than continuing the owner's
schedule — and you have no write access to that repo anyway.

### Path B — your own fresh state (recommended for actual use)

```bash
~/learning-pi/init-state.sh ~/my-learning   # empty scaffold, zero owner data, fresh git history
~/learning-pi/install.sh ~/my-learning
cd ~/my-learning && pi  # approve/trust once
```

Then: point it at your own remote
(`git remote add origin <your-url> && git push -u origin main`), define your
track in `Learning System/MISSION.md` + `CURRICULUM.md`, and run `/teach <topic>`
or fill the curriculum and run `/lesson`. The scaffold passes the state audit
with 0 errors out of the box.

Notes:

- `pi --version` triggers `mise` to fetch the pinned version from
  `versions.lock.json` on first run; `learn-check --no-load` verifies the gate
  without needing a live `pi` binary or network models.
- If `~/.local/bin` is not on your `PATH`, persist the full export from your
  platform's block (it covers `~/.local/bin`, the mise shims, and `~/.deno/bin`)
  in your shell rc (`~/.bashrc`, `~/.zshrc`).
- macOS: Homebrew requires the Xcode Command Line Tools (`xcode-select --install`;
  also provides `/usr/bin/git` and the system `python3`). macOS ships LibreSSL,
  whose `openssl` covers the one base-flow use (`openssl rand -hex` for deploy keys).
- Open WebUI face (optional, **Linux-only**: needs systemd, `ufw`, and the
  `docker0` `172.17.0.1` bridge — not available under Docker Desktop for
  Mac/Windows): follow [`deploy/README.md`](deploy/README.md) Apply steps after
  the base setup above. macOS/Windows users run the pi CLI path instead.
- If `git clone` over SSH fails (no key), use
  `https://github.com/delightaheebwa/learning-pi.git` instead.

## Install (manual)

```bash
git clone git@github.com:delightaheebwa/learning-pi.git ~/learning-pi
git clone https://github.com/delightaheebwa/learning-system.git ~/learning-system   # if not present
~/learning-pi/install.sh ~/learning-system
cd ~/learning-system && pi        # approve/trust the project once
```

## Usage

Slash commands: `/review`, `/solo` (an AI-free closed-book check — no teaching or hints),
`/ingest <content>`, `/teach <topic>`, `/lesson`, `/continue`, `/pause`,
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
| Lesson-start context auditor (`scout-audit`) | `muse-spark-1.3-contributor` (dispatched by the Tutor on the Scout digest) |

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
| A new idea during teach/resume | the `fact-check` envelope carries `turn_kind` plus, for an `idea`, a four-beat `foundation` block (`problem`/`where_from`/`conditions`/`contrast`) whose prose is in the draft; a turn with no `turn_kind`, or an `idea` missing/unbinding a beat, is withheld (`FOUNDATION_INCOMPLETE`) — a factually correct "what"-only summary cannot render as if complete. The verifier also returns `omitted_foundations[]` (source theory with no trace in the draft), which is an `ISSUES` verdict. `answer`/`repair`/`hint`/`plan` need no foundation |
| A question batch | `quiz-audit` returning `PASS` (zero issues); any issue, at any severity, blocks until fixed (uncapped — re-check until zero issues). The envelope carries `questions_json` **and** `rendered_content` = the full batch text (intro/instructions + every question + its options), which binds the whole emitted turn |
| A grade | `grade-audit` with `agrees === true`/`PASS`; disagreement is rejected and the verifier's `correct_verdict` is surfaced. One batched `items[]` envelope grades every answer from a single learner reply (never one subagent per answer) |
| A visualization (`[[TURN:viz]]` — a ` ```viz ` spec + supporting words) | `viz-audit` whose canonical `spec` matches the emitted fenced spec and whose `rendered_content` covers the turn (missing → `NO_VIZ_AUDIT`, `ISSUES` → `VIZ_AUDIT_ISSUES`, unbound/stale → `VIZ_AUDIT_STALE`). A ` ```viz ` block in any other turn is withheld (`VIZ_REQUIRES_OWN_TURN`); a missing parseable spec is withheld (`VIZ_SPEC_INVALID`). Figures are opt-in and teach/resume-only; `viz-mode` renders them inline and opens an interactive explorer overlay |
| A `Learning System/` handoff write during teach/resume | `tutor-audit` reading back the lesson file / session note / learning record / `Pending Ingest.json` (once per handoff batch; every issue blocks at any severity; out-of-scope observations go to `context_notes`) |
| An ingest | after the Clerk returns a `CLERK_WRITES` receipt, the Tutor dispatches an independent `review-gate` on the wiki pages written; `PASS` renders clean, `ISSUES` renders with a `⚠️ REVIEW FLAGS SURFACED` banner (never an endless re-run). A verdict relayed by the Clerk instead of a real review-gate run gets a `⚠️ INGEST GATE` banner; a review verdict with no `evidence` list gets a `⚠️ REVIEW GATE` banner |
| The **close** of a standalone `/review` (the delegated `review-clerk` run wrote the Review notes, session note, and touched Active Concepts / Mistakes rows) | `review-session-audit` reading the writes back against the transcript + per-concept grade verdicts; `PASS` releases the summary, `ISSUES` withholds it (`REVIEW_SESSION_AUDIT_ISSUES`) until the writes are fixed and re-audited to zero issues (no cycle cap) |
| A new lesson | a `scout` run before teaching plus ONE independent `scout-audit` on its digest (completeness: every Further Reading URL fetched or explicitly failed, excerpts + `theory` lines + prereqs present, raw files on disk; fact-check: synthesis grounded in the raw files, no synthesis from failed refs, contradictions surfaced). Missing audit withholds (`NO_SCOUT_AUDIT_PASS`); `ISSUES` renders with a `⚠️ SCOUT AUDIT FLAGS SURFACED` banner (never a withhold); no `evidence` gets a `⚠️ SCOUT AUDIT` banner. A partial/missing `SCOUT_DIGEST` receipt surfaces as a `⚠️ SOURCES INCOMPLETE` / `⚠️ SCOUT DIGEST UNVERIFIED` banner (never a withhold) |
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
  - `[[TURN:quiz]]` → requires a `PASS` `quiz-audit` (zero issues; any severity blocks)
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
- **No cap while any issue remains:** the gate keeps blocking and never dumps the turn as
  `⛔ UNVERIFIED`; the cap applies to every other reason. Severity labels no longer gate — a `low`
  blocks exactly like a `high` or `medium`.
- **Dispute:** the same issue blocking three times is adjudicated by the judge; if it no longer
  applies the engine releases the turn with `⚠️ VERIFIER DISPUTED`.
- **Ledger:** every decision and receipt is appended to `~/.pi/agent/learning-gate/`
  (`receipts.ndjson`, `decisions.ndjson`) for provenance and review.
- **Degraded fallback:** with no judge configured, no auth, a rate-limit, or invalid output, the gate
  runs the deterministic legacy path unchanged. A learning turn never dead-ends on a judge fault.

## Skills

> **Canonical pedagogy lives here.** The skills in `learning-pi/.pi/skills/` are the **canonical**
> teaching behavior. The copies under the state repo's `Skills/` (and `OPENWEBUI.md`) are a
> **frozen, unmaintained legacy path** — the two diverged and pi is now the single source of truth
> for teaching behavior, verification, and the flows. Add teaching-behavior changes here only; a
> behavior-contract change updates `CONTRACT.md`/`contracts/learning-core.json` in the same commit.
> The frozen copies are not deleted (yet) so the Open WebUI branch stays readable.

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

### Open WebUI face: pi-bridge + deploy (shipped 2026-10-15/16)

`bridge/` is an OpenAI-compatible endpoint in front of the pinned pi runtime, so **Open WebUI
can be the face while pi stays the brain** (gate, subagents, skills run unchanged; Open WebUI
holds only chat transcripts). `deploy/` runs Open WebUI in Docker in front of a host
`pi-bridge` systemd service. Behavior contract: `B-*` invariants in `CONTRACT.md` /
`contracts/learning-core.json` (v6, 55 invariants). Details: [`bridge/README.md`](bridge/README.md),
[`deploy/README.md`](deploy/README.md), [`deploy/SECURITY.md`](deploy/SECURITY.md).

### Repo layout for the gate

```
CONTRACT.md                  declared behavior (the thing updates must not break; v6, 55 invariants 2026-10-16)
contracts/learning-core.json machine-readable invariants -> test names
bridge/                      OpenAI-compatible pi-bridge (B-* invariants) + README
deploy/                      Docker Open WebUI + pi-bridge.service + searxng + README/SECURITY
.pi/agents/                  13 subagents (incl. scout-audit, viz) — see .pi/
.pi/prompts/                 9 slash prompts (review/solo/ingest/teach/lesson/continue/pause/audit/show)
.pi/skills/                  5 skills (incl. learning-viz)
bin/pi                       pinned launcher (never updates)
bin/notify-if-outdated       debounced availability check (never updates)
bin/pi-review-status         daily /review status helper (JSON; shared by widget + reminder)
bin/lpi                      the umbrella control command (update / test / doctor / rollback; `lpi e2e --list/--diff`)
harness/pi-safe-update       update conductor (backing `lpi update`)
harness/locktool.py          versions.lock.json / journal helper
harness/mk-sandbox.sh         isolated duplicate harness builder
harness/e2e-runner.py        e2e runner (--tier smoke|full)
harness/man/                 lpi(1) man page
harness/audit-recent-sessions.sh + systemd/  weekly provenance audit
scripts/learn-check          the single test entrypoint (8 deno suites: gate/golden/redteam/viz/judge/judge_model/judge_router/judge_dump + bridge + contract checks + load probe)
scripts/agent-worktree       worktree helper (new/list/clean/land)
test/gate_test.mjs           core gate behavior (mocked pi)
test/golden/                 write-gate / scout / review-delegation / retry / demotion / viz scenarios
test/viz_test.mjs            viz-mode pure units (spec validation, expression eval, ASCII render)
test/judge_*.mjs + live_judge_test.mjs  judge suites (live variants opt-in, need models)
test/redteam/                adversarial suites
test/bridge/                 bridge suite (fake_pi + run_tests.py → B-* coverage)
test/contract/               resource checks, load probe
test/e2e/scenarios/          8 e2e scenarios (smoke + full)
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
