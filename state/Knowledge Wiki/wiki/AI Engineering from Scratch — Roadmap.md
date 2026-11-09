<!-- provenance: status=verified | source=https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/ROADMAP.md | verified-by=fact-check-agent | date=2026-10-26 -->

# AI Engineering from Scratch — Roadmap (Rohit)

> **Active roadmap** (2026-09-01 — switched from SWE Primary Colors). Source: **AI Engineering from Scratch** by Rohit Ghumare — https://github.com/rohitg00/ai-engineering-from-scratch — `ROADMAP.md` (~1,081h total, 20 phases, 523 lessons, each ships an artifact `outputs/`). Canonical order: `Learning System/CURRICULUM.md` (Mission 0 Catch-Up + Missions 1–21 = Phases 0–19). Mission docs: `Learning System/MISSION.md`. Curated readings: `Learning System/RESOURCES.md`.

> **How it is used:** Rohit's `phases/<phase>/<lesson>/docs/en.md` is **a source, not the source**. Before each new lesson, Scout fetches that `docs/en.md` **plus every URL in its `## Further Reading`** (2–4 external refs per lesson) and `RESOURCES.md`, hashes, surfaces drift (`SCOUT DIGEST: ⚠️ Upstream changed`), and synthesizes. Tutor teaches from the combined digest and cites both. **Adaptive:** returning after 2–3 lessons for the 4th re-fetches live and compares hash — no rigid frozen model. **Language:** per-lesson `Languages:` header (Python / TypeScript / Rust; Julia optional). **Cache:** ignored per decision 2026-09-01 (live fetch each lesson).

## 0) Mission 0 — Catch-Up: Foundations Reactivation (special · 80/20)

*Up to and including Phase 1 Lesson 06 — Probability & Distributions.* You did Phase 0 + P1.01–06 before with exercises; this is 80/20 reactivation (`~90 min`, Python), 6–8 MCQs + 2 free-recall probe then gap-targeted teach. After pass → jump to **Phase 1 L07 Bayes' Theorem** (decision 2026-09-01). See `CURRICULUM.md` Mission 0 `80/20 map` (4-layer stack · vectors/matrices `W@x+b` · transforms/eigen · calculus/chain rule · probability PMF/PDF/CLT/softmax/log-sum-exp/cross-entropy).

## 1) The 20 Phases

| Phase | Name | Est. | Lang (default) | Lessons | Role |
|-------|------|------|----------------|---------|------|
| 0 | Setup & Tooling | ~16h | Python / Node / Rust | 13 | 4-layer stack, uv/venv, GPU/MPS, verify.py |
| 1 | Math Foundations | ~23h | Python (Julia opt) | 22 | Linear algebra → calculus → probability → optimization |
| 2 | ML Fundamentals | ~26h | Python | 18 | Classical ML backbone |
| 3 | Deep Learning Core | ~15h | Python | 13 | Perceptron → backprop → optimizers → own mini-framework |
| 4 | Computer Vision | ~27h | Python | 28 | Convolutions → diffusion → vision transformers |
| 5 | NLP — Foundations to Advanced | ~30h | Python | 29 | Tokenization → attention → retrieval → eval |
| 6 | Speech & Audio | ~18h | Python | 17 | Waveforms → Whisper → TTS/voice |
| 7 | Transformers Deep Dive | ~14h | Python | 16 | Self-attention → MoE → KV cache → scaling laws |
| 8 | Generative AI | ~14h | Python | 15 | VAE/GAN → diffusion → ControlNet/LoRA |
| 9 | Reinforcement Learning | ~13h | Python | 12 | MDP → DQN → PPO → RLHF |
| 10 | LLMs from Scratch | ~26h | Python | 24 | Tokenizers → pretrain → RLHF/DPO → quantization |
| 11 | LLM Engineering | ~19h | Python / TS | 15 | Prompt → RAG → fine-tune → MCP |
| 12 | Multimodal AI | ~65h | Python / TS / Rust | 25 | ViT → CLIP → VLMs → video |
| 13 | Tools & Protocols | ~76h | TS / Python | 31 | Tool calling → MCP → A2A → registries |
| 14 | Agent Engineering | ~55h | Python / TS | 54 | Loops → memory → harnesses → workbenches |
| 15 | Autonomous Systems | ~20h | Python | 22 | Long-horizon → self-improve → guardrails |
| 16 | Multi-Agent & Swarms | ~28h | Python / TS | 25 | Protocols → consensus → scaling |
| 17 | Infrastructure & Production | ~34h | Python / TS / Rust | 28 | Serving → batch → chaos → FinOps |
| 18 | Ethics, Safety & Alignment | ~31h | Python | 30 | Reward hacking → red-teaming → regulation |
| 19 | Capstone Projects | ~620h | Python / TS / Rust | 85 | Terminal agent → RAG → video → eval → harness |

Total ~1,081h (core Phases 0–18 ~550h + 620h Capstones). **Full map is navigational, not contractual** — after each phase, decide to go deeper / branch / build a learning system.

## 2) Per-lesson shape (Rohit)

`phases/<NN>-<phase>/<NN>-<lesson>/` → `code/` (Python/TS/Rust/Julia) · `docs/en.md` · `outputs/` (artifact). Six beats: Motto → Problem → Concept → **Build It** (raw math, no frameworks) → **Use It** (PyTorch/sklearn) → **Ship It** (prompt/skill/agent/MCP). Language per `docs/en.md` header — Scout captures as `lang_recommendation`.

## 3) Provenance & Archiving

- **Upstream:** https://github.com/rohitg00/ai-engineering-from-scratch — MIT. Rohit's order is direction; teaching synthesizes `docs/en.md` + Further Reading + `RESOURCES.md`.
- **Switch date:** 2026-09-01. Previous SWE roadmap archived: `Learning System/Archive/CURRICULUM — SWE Primary Colors — archived 2026-09-01.md`, `Learning System/Archive/MISSION — SWE Stage 0 — archived 2026-09-01.md`, 43 SWE concepts → `Learning System/Core/📦 Concept Archive.md` section `Paused Concepts — SWE (Archived 2026-09-01)` (visibility strictly out of scope). Prior AI roadmap v2 remains paused (`AI Engineering Roadmap v2.md`).
- **Next real lesson after catch-up:** Phase 1 L07 — see `CURRICULUM.md` Mission 2.

## Sources

- Upstream ROADMAP.md: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/ROADMAP.md

## 4) Operating notes

- Scout → Tutor → Clerk pipeline (same chat, switch presets). Scout writes `.tmp/context-<chat>-<slug>.json` with `rohit_hash` + `external_refs` + `lang` + `roadmap_sha`; gate Pipe enforces digest for new lessons. Tutor `GATE:fact_check` cites both sources. OpenWebUI in Docker Desktop Windows-side (separate from WSL) — base URL `http://host.docker.internal:3000` from WSL.
- Related: [[SWE Primary Colors & Roadmap]] (archived) · [[AI Engineering Roadmap v2]] (paused)
