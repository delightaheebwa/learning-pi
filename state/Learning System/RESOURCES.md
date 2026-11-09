# RESOURCES.md — AI Engineering from Scratch (Rohit)

> Curated trusted sources for the current mission. The teacher draws knowledge from combined sources — Rohit's `docs/en.md` **plus** every link in its `## Further Reading` plus the entries below — never bare parametric memory. Rohit is a source, not the source. Scout gathers this synthesis; the teacher proposes new entries for user approval.

> Archive note: MIT Missing Semester / GNU Make / C-project resources remain valid as supporting refs but are not the driving curriculum. SWE Primary Colors roadmap archived 2026-09-01 — see `Archive/CURRICULUM — SWE Primary Colors — archived 2026-09-01.md`.

## Knowledge (Primary)

- [AI Engineering from Scratch — ROADMAP](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/ROADMAP.md) — 20 phases, 523 lessons, ~323h. Order + status. Lessons live at `phases/<NN>-<phase>/<NN>-<lesson>/docs/en.md` with `code/` implementations.
- [AI Engineering from Scratch — GitHub](https://github.com/rohitg00/ai-engineering-from-scratch) — `docs/en.md` per lesson (`## Further Reading` at bottom is the provenance to fetch — Scout brings all of these together, not just `docs/en.md`).
- [AI Engineering from Scratch — Website](https://aiengineeringfromscratch.com) — rendered lessons + phase sites.

### Phase-routed sources (Scout fetches the lesson's Further Reading + these as needed)

- **Phase 0 Tooling:** `uv` docs, `fnm`/`pnpm`, `rustup`, PyTorch CUDA/MPS docs (`torch.cuda.is_available()`), `verify.py --route` scripts in `phases/00-setup-and-tooling/01-dev-environment/code/`.
- **Phase 1 Math Foundations:**
  - 3Blue1Brown — linear algebra / probability intuition (linked from P1 Further Reading, e.g., CLT https://www.youtube.com/watch?v=zeJD6dqJ5lo).
  - Stanford CS229 — Probability Review (https://cs229.stanford.edu/section/cs229-prob.pdf), Linear Algebra Review.
  - Greg Gundersen — Log-Sum-Exp Trick (https://gregorygundersen.com/blog/2020/02/09/log-sum-exp/) — numerical stability for softmax/NLL.
  - (Scout adds per-lesson links: e.g., P1 L01–L06 Further Reading entries for vectors, eigen, autodiff chain rule, etc.)
- **Later phases:** add on entry — Transformers (Attention Is All You Need), Diffusion (DDPM), RL (Sutton & Barto), LLM eval harnesses, MCP/A2A specs — propose at phase start for user approval.

## Supporting (on demand)

- [MIT Missing Semester (2026)](https://missing.csail.mit.edu/2026/) — shell, git, debugging, editors — still useful for Phase 0 Terminal/Shell/Linux (Scout may fetch but not drive).
- [GNU Make Manual](https://www.gnu.org/software/make/manual/) — for Makefile-backed builds where `code/` uses Make.
- Previous lesson notes: `Knowledge Wiki/wiki/AI Engineering from Scratch — Roadmap.md` (index), `Learning System/CURRICULUM.md` (what's next), per-lesson `Lessons/` files (formed after catch-up).

## Wisdom (Communities)

- (Reserved — not started. Suggest communities when the user is ready — e.g., PyTorch forums, Hugging Face, local AI engineer meetups. Rohit's Discussions: https://github.com/rohitg00/ai-engineering-from-scratch/discussions)

## Gaps

- Fill per phase on activation: Phase 7 Transformers (original Transformer paper, RoPE/ALiBi refs), Phase 10 LLMs from Scratch (tokenizer BPE, distributed training refs), Phase 13 MCP/A2A specs, Phase 18 alignment research (MATS/Redwood/Apollo). Scout proposes new entries; user approves.

## How Scout uses this file

Scout reads `MISSION.md`, `CURRICULUM.md`, **this file**, relevant `📚 Active Concepts.md` rows, **and** the target lesson's `docs/en.md` + **every URL in its `## Further Reading`** (2–4 per lesson) via the ordered terminal-first fetch loop (direct curl → pypdf for PDFs → yt-dlp transcript for YouTube → r.jina.ai for bot-blocked HTML → Web Search snippet last; failures recorded in `failed_refs`, never aborting the digest). It writes `Learning System/.tmp/context-<chat>-<slug>.json` with `{goal, slug, rohit_source, rohit_hash, external_refs:[{url,hash,excerpt,takeaways,adds_vs_rohit}], synthesis, failed_refs:[{url,reason}], lang_recommendation, fetched_at, roadmap_sha}` — Rohit sets the agenda; every digest entry carries substance the Tutor teaches from, not just a URL and posts `SCOUT DIGEST:` (headings + 3–5 bullet synthesis of FETCHED refs vs Rohit). Tutor teaches from the combined digest; verification (`GATE:fact_check`) cites both `source_url`s.
