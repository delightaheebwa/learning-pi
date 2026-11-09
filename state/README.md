# Learning System + Knowledge Wiki

> **New here?** This is a reusable local-first learning system, currently mid-migration.
> The **canonical runtime is [`learning-pi`](https://github.com/delightaheebwa/learning-pi)** (pi skills,
> subagents, prompts, verification gate). The Open WebUI layer in this repo is a **frozen legacy
> snapshot** — readable, but do not build new behavior on it. Start with the
> [pi setup](https://github.com/delightaheebwa/learning-pi#set-up-one-shot-per-platform) and the
> [Discussions front door](https://github.com/delightaheebwa/learning-system/discussions).
> Cloning this repo gives you the owner's live learning state as an example — to reuse it,
> build your own empty state with `learning-pi/init-state.sh` (Path B in Set up below) and fill it
> with your own material, rather than continuing the AIEFS schedule below.

This repo is **the notebook**: every session, concept, review, and wiki page lives
here as Markdown + JSON. The tutor program that acts on it lives in
[`learning-pi`](https://github.com/delightaheebwa/learning-pi) (self-hosted Open WebUI
support is frozen, see `OPENWEBUI.md`).

**How learning works here, in 30 seconds:** you open the notebook (`cd ~/learning-system && pi`)
and say `/lesson` (next curriculum lesson) or `/teach <topic>`. A Scout gathers live sources,
the Tutor checks what you know, teaches in small steps with questions, and a Clerk files
everything away — session notes, concept schedule, wiki pages. Later, `/review` quizzes you on
whatever is due, mistakes first. A verification gate fact-checks the tutor, so unverified
claims never reach you.

**Two ways in:** chat in your browser via **Open WebUI + pi** (`deploy/`, the face
in front of the same tutor), or terminal-only **pi** (`cd <notebook> && pi`).
Same tutor, same notebook — pick per session.

- **Repo:** https://github.com/delightaheebwa/learning-system
- **Track:** AIEFS (AI Engineering from Scratch — Rohit 20 phases; Mission 0 Catch-Up done 2026-09-05, P1 L07 done 2026-09-05, P1 L08 Optimization done 2026-09-10, P1 L09 Information Theory done 2026-09-24, P1 L10 Dimensionality Reduction in-progress — paused 5/6, CP5 mini 4 taught 2026-10-16, exit ticket unrun). SWE archived 2026-09-01 (43 concepts paused, strictly out of scope). Prior `aie` archived 2026-07-28.
- **Scheduling:** manual — `/review` reviews what's due, `/ingest` files new material away,
  `/teach` / `/lesson` / `/continue` learn. Each lesson pulls live sources (roadmap doc + Further Reading),
  in the lesson's language (Python/TS/Rust).

## Layout

```
OPENWEBUI.md              setup + operating guide (read this first)
AGENTS.md                 agent context: repo conventions, change protocol, gotchas
scripts/
  setup_openwebui.py        one-shot installer: skills, gate Pipe filter, model presets, prompts, subagent system prompt
  ops.py                    runtime sidecar (state/bundle/apply/attempt)
  learner_history.py        regenerates Core/Learner History.md (tutor context)
  audit_openwebui.py        read-only repo↔live drift audit
  ops_test.py               unittest suite
  wiki_provenance.py        wiki trust-mix report + provenance lint/stamp
  wiki_provenance_test.py   tests for wiki_provenance.py
infra/                     portability: docker-compose.yml, backup/restore, .env.example, VERSIONS.md, ACCESS.md
Learning System/          live state + history
  Core/                     💡 Learning Profile, 📚 Active Concepts (the review schedule),
                            Attempts.json, 🧯 Mistakes.md, Learner History.md (generated),
                            📦 Concept Archive, templates
  Sessions/  Reviews/ (incl. Quality Gates/, Session Audits/)  Lessons/  Learning Records/
  Concept Notes/ (archived stub — do not add)  build-artifacts/  .tmp/ (ephemeral digests)
  Archive/                  ALL legacy material, era-folded (AIE, SWE, C-project, legacy tools, plans, frozen) — do not grep
  AGENTS.md                 behavioral conventions (consistency checks, git sync)
Knowledge Wiki/           curated wiki (raw/sources, raw/assets, wiki/, index.md, log.md, AGENTS.md)
Skills/                   FROZEN Open WebUI snapshot (canonical behavior lives in learning-pi/.pi/skills/)
  learning-system/SKILL.md        review + ingest flows (Clerk runs reviews AND ingests)
  learning-teach/SKILL.md         probe → plan → teach loop (+ fact-check & quiz-audit subagent gates, lesson-end review gate)
  learning-review/SKILL.md        ingest quality gate (review-gate subagent task — standalone ingests AND lesson-end ingests)
  llm-wiki/SKILL.md               wiki building/maintenance rules
  learning-review/openwebui/      gate_pipe.py + gate_schema.py (the deterministic enforcement)
```

## Set up (one-shot per platform)

Two paths. Full prerequisites + verification live in
[`learning-pi/README.md#set-up-one-shot-per-platform`](https://github.com/delightaheebwa/learning-pi#set-up-one-shot-per-platform).

**Path A — clone this repo (owner's live data, as an example):**

```bash
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
git clone https://github.com/delightaheebwa/learning-system.git ~/learning-system
~/learning-pi/install.sh ~/learning-system
cd ~/learning-system && pi  # approve/trust once
```

Start a fresh track rather than continuing the schedule below (you have no
write access here anyway).

**Path B — your own fresh state (recommended for actual use):**

```bash
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
~/learning-pi/init-state.sh ~/my-learning  # empty scaffold, zero owner data, fresh git history
~/learning-pi/install.sh ~/my-learning
cd ~/my-learning && pi  # approve/trust once
# then: git remote add origin <your-url> && git push -u origin main;
# define your track in Learning System/MISSION.md + CURRICULUM.md; run /teach <topic> or /lesson
```

Dependency one-liners (once `git`, `python3`, and `mise` are present the minimal path above works):

- Omarchy/Arch: `sudo pacman -S --needed git openssh python base-devel curl unzip mise deno nodejs npm`
- Ubuntu/Debian/WSL: `sudo apt-get update && sudo apt-get install -y git python3 curl unzip ca-certificates nodejs npm` + `curl -fsSL https://mise.run | sh`
- macOS: `brew install git python mise deno node` (after `xcode-select --install`)
- Windows: not natively supported — use WSL2 (see `learning-pi` setup section), keep repos on the Linux filesystem.

## Daily use (once set up)

```bash
cd ~/learning-system && pi  # or ~/my-learning for your own state
```

Then `/review`, `/solo`, `/ingest`, `/teach`, `/lesson`, `/continue`, `/pause`, `/audit` (`/solo`, `/audit`, `/show` are pi-only; `/swe` below is legacy Open WebUI-only).
See [`learning-pi/README.md`](https://github.com/delightaheebwa/learning-pi#usage) for the full
usage and [`AUDIT-ROADMAP.md`](https://github.com/delightaheebwa/learning-pi/blob/main/AUDIT-ROADMAP.md)
for what is done (P0–P2, P4 foundation-beats, scout-audit gate, teach rewrite, bridge + deploy) and deferred (P3).

## Setup in Open WebUI (one time — frozen legacy)

Run the installer, then start chatting:

```bash
OPENWEBUI_API_KEY=sk-... python3 scripts/setup_openwebui.py
```

That creates/updates: the 4 Skills, the **Scout** / **Learning Tutor** / **Clerk** Model presets, the **Gate Pipe** Filter, the global subagent system prompt (keyed `GATE:`), and the 7 legacy Prompts (`/swe`, `/review`, `/ingest`, `/teach`, `/lesson`, `/continue`, `/pause` — frozen; canonical pi has 9: `/review /solo /ingest /teach /lesson /continue /pause /audit /show`, no `/swe`).
Verification gates run as **foreground** subagent tasks (`delegate_task`, `background:false`) with Pydantic envelope validation via the **Gate Pipe**; verifiers run on the **calling preset's own base model** (Open WebUI has no separate verifier-model setting — verified 2026-09-08 against `utils/subagents.py::delegate`) — enforcement rests on the deterministic Pipe checks, not model independence. (The legacy `review_gate` + `fact_check` + `quiz_gate` Tools were retired; do not bind them.)
After install, models are changed in **one place each in the Open WebUI UI** —
see `OPENWEBUI.md`. The installer only applies model values on a **first
install** (or when empty); re-running it preserves your UI-chosen models.
See `OPENWEBUI.md` for the full walkthrough, the system prompt, and the prompt texts.

The repo must also be present in the Open Terminal workspace (the model's file workspace) with git push wired —
see `OPENWEBUI.md` and `Learning System/AGENTS.md`. (Legacy Open WebUI path only — the canonical pi path uses the
current checkout + `dispatch` and needs no Open Terminal workspace.)

## Principles

- Clarity is not comprehension
- Prerequisites come first
- Retrieval beats recognition
- Open questions stay open until resolved
- Active Concepts is the persistent memory

## Community

This system is built in public, and [Discussions](https://github.com/delightaheebwa/learning-system/discussions)
is the front door:

- 💬 [Discussions](https://github.com/delightaheebwa/learning-system/discussions) — Q&A, ideas, show-and-tell, and the build log.
- 🐛 Issues — concrete bugs and tracked work. Route by layer: pi runtime / gate / skills → [`learning-pi/issues`](https://github.com/delightaheebwa/learning-pi/issues); state / wiki / Open WebUI snapshot → [learning-system issues](https://github.com/delightaheebwa/learning-system/issues). If unsure, open in learning-system and say which layer you think it is.
- 🔒 Security reports — see [SECURITY.md](.github/SECURITY.md) (do not post publicly).

The pi control layer lives in [`delightaheebwa/learning-pi`](https://github.com/delightaheebwa/learning-pi),
but its conversations happen here too. See [CONTRIBUTING.md](.github/CONTRIBUTING.md)
and the [Code of Conduct](.github/CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE) © 2026 Delight Aheebwa