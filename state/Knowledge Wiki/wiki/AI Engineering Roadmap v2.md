<!-- provenance: status=verified | source=multiple | verified-by=fact-check-agent | date=2026-10-26 -->

# AI Engineering — Primary Colors Roadmap

**Learn the primitives (the "primary colors") so you can confidently build anything by mixing and remixing them.**

5 core strands. 2 optional depth picks. A resource layer for theory gaps.
**Core total: ~130–190h.** With one depth pick + selective resources: ~220–295h.

All projects run on free/cheap hardware (laptop, Colab, Kaggle T4, <$25 API credits). All are community-verified (no 0-star repos in the critical path). All are license-safe (MIT/Apache-2.0).

---

## Design Principles

1. **Primary colors, not recipes.** Every core strand teaches a *primitive* — a concept you'll remix in every future project. Autodiff, the transformer, post-training objectives, inference arithmetic, retrieval/eval/agents.
2. **Community-verified.** The critical path uses repos with real community signals (stars, forks, active maintenance). No 0-star bus-factor risks.
3. **Runs on free hardware.** Laptop, Colab, or Kaggle T4. No "rent 8×H100" requirements in core.
4. **License-safe.** MIT or Apache-2.0 only. No PolyForm Noncommercial.
5. **Honest coverage.** Each strand says what it does NOT cover. Every gap has a named resource patch.

---

# The 5 Core Strands

---

## C1 — Spine: Foundations → LLM (Primary Colors: Autodiff, Backprop, Transformers, Training)

**Track:** [karpathy/nn-zero-to-hero](https://github.com/karpathy/nn-zero-to-hero) → [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch)
**Verification:** 23.6k★ · 99.5k★ · actively maintained (Raschka)
**License:** MIT (both)
**Hardware:** Laptop CPU for z2h; Kaggle T4/Colab for Raschka pretraining
**Hours:** 60–85

### What you build (end-to-end)

**Karpathy (lectures 1–7):** `micrograd` (scalar autograd) → `makemore` (bigram → MLP → RNN → WaveNet → Transformer). Every lecture ends with a working model. Covers manual backprop (Lecture 5 = "Backprop Ninja"), activation statistics, BatchNorm, gradient flow diagnostics.

**Raschka (ch2–7 + bonuses):** BPE tokenizer (from scratch) → attention mechanisms (self, multi-head, causal) → full GPT model → pretraining loop → SFT for classification → SFT for instruction following → DPO (bonus notebook) → LoRA (appendix).

**Submodule bonus:** `reasoning-from-scratch` (4.8k★) adds GRPO/RLVR from scratch, eval (MATH-500 verifier, MMLU, LLM-as-judge).

### What this strand genuinely covers
- Autodiff + backprop from scratch (the foundation)
- DL core: MLP, activations, loss functions, optimizers (SGD/Adam), regularization (BatchNorm/dropout), weight init, LR schedules, debugging NNs
- NLP: tokenization (BPE), embeddings, language modeling
- Transformers: self-attention, multi-head attention, positional encoding, full encoder-decoder, GPT (causal LM), KV cache, attention variants (GQA, MLA), MoE, scaling laws
- LLM: data pipelines, pretraining 124M-scale model, SFT, DPO, GRPO, LoRA/QLoRA, open-model architecture walkthroughs (Llama 3.2, Qwen3, Gemma 4, OLMo 3 from scratch)
- Eval: loss curves, perplexity, bits-per-byte, MMLU, MATH-500 verifier, LLM-as-judge

### Does NOT cover (resource layer fills these)
- Reward modeling + PPO (see C2)
- RL fundamentals (see resource layer)
- Serving/inference systems (see C4)
- Applied RAG/agents/eval (see C5)
- Vision, speech, multimodal (see D1 + resource layer)

---

## C2 — Post-Training: Alignment from Scratch (Primary Color: How models get aligned)

**Repo:** [huggingface/trl](https://github.com/huggingface/trl)
**Verification:** ~19.6k★ · Apache-2.0 · v1.16.0 (Oct 2026) · very active
**Hardware:** Free Colab/Kaggle T4 with Qwen2.5-0.5B
**Hours:** 10–14

### What you build (end-to-end)

A complete SFT → Reward Model → PPO → DPO → GRPO sequence on Qwen2.5-0.5B using TRL's trainers. On free Colab/Kaggle T4:

1. `SFTTrainer` on `trl-lib/Capybara` (instruction tuning)
2. `RewardTrainer` on `trl-lib/ultrafeedback_binarized` (Bradley-Terry preference model)
3. `PPOTrainer` — policy from SFT checkpoint, reward model scoring, KL penalty
4. `DPOTrainer` on same preference data — compare PPO vs DPO outputs side-by-side
5. `GRPOTrainer` on `trl-lib/DeepMath-103K` (verifiable-reward RL, DeepSeek-R1 style)
6. Evaluate: RM held-out accuracy + side-by-side generations (SFT vs PPO vs DPO)

**Critical self-designed experiment (+2h):** Judge your PPO output with your RM *and* with an independent LLM-as-judge (Claude/GPT). The gap between the two scores **is** the Goodhart tax. This is the "reward hacking" lesson — and it's the most important thing in this strand.

### Why TRL, not TheYellowDuck/RLHF-pipeline
TheYellowDuck was disqualified: **0 stars** (zero community verification that it actually works for others) and **PolyForm Noncommercial** (restrictive license, unusual for a portfolio piece). TRL is the industry-standard tool — learning it IS the skill, and its community (18.9k★) means every bug you hit has been hit before.

### What it covers
- SFT, reward modeling, PPO, DPO, GRPO, KTO/ORPO (bonus)
- LoRA/QLoRA parameter-efficient fine-tuning via PEFT
- Running on free T4 hardware

### Does NOT cover
- RL internals (GAE, clipped surrogate, value-loss clipping) — TRL wraps these; you configure them, you don't implement them
- Data-quality lessons (label noise in preference data, dedup, length bias) — you must discover these yourself
- Scale engineering (FSDP/ZeRO-3, vLLM-accelerated rollouts, distributed PPO)
- Alignment breadth: Constitutional AI/RLAIF, iterative DPO, process reward models, best-of-N inference alignment

---

## C3 — Hardware: Understanding What Computation Costs (Primary Color: What the hardware actually does)

**Resources (5 items, ~19h total):**

| # | Type | Resource | Hours | What it teaches |
|---|---|---|---|---|
| 1 | READ | [Horace He — "Making Deep Learning Go Brrrr From First Principles"](https://horace.io/brrr_intro.html) | 2h | The master mental model: every DL workload is compute-bound, memory-bandwidth-bound, or overhead-bound; tensor vs CUDA cores; DRAM vs SRAM; operator fusion. **The framing that makes every later resource legible.** |
| 2 | WATCH | [GPU MODE lectures](https://github.com/gpu-mode/lectures) — **L4** (Compute & Memory Architecture), **L12** (Flash Attention), **L7** (Advanced Quantization) | 4.5h | L4: SMs, warps, HBM→L2→SRAM→registers. L12: the SRAM-tiling of FlashAttention. L7: INT8/FP8/INT4, CUDA-vs-Triton quant kernels, memory-vs-accuracy tradeoffs. |
| 3 | DO | [Triton official tutorials 01–03](https://triton-lang.org/main/getting-started/tutorials/index.html) | 4h | What a kernel is, with zero C++ boilerplate: program IDs, blocks, masked loads/stores, `tl.dot` on tensor cores. Tutorial 02 = fused softmax (Horace's fusion lesson made concrete). Runs on free Colab GPU. |
| 4 | DO | [kipply — "Transformer Inference Arithmetic"](https://kipply.github.io/blog/transformer-inference-arithmetic/) — **redo every calculation by hand** | 4h | Why decode is memory-bandwidth-bound (read all 2P bytes of weights per token → bound below the 208:1 FLOPS/bandwidth ratio). KV-cache byte counts, capacity math, tensor vs pipeline parallelism mapped to NVLink vs PCIe; latency floor equations validated against benchmarks. **Do the 12 end-of-post exercises even roughly.** |
| 5 | DO | [karpathy/llm.c](https://github.com/karpathy/llm.c) — `doc/layernorm/layernorm.md` tutorial + read `dev/cuda/` kernels + `profile_gpt2.cu` | 4h | Read real CUDA in the wild: layernorm kernel built step-by-step naive→optimized; curated kernel library from simple to complex/faster; kernel-level profiling of a full GPT-2. |

### Learning outcomes coverage

| Outcome | Horace | GPU MODE | Triton | kipply | llm.c |
|---|---|---|---|---|---|
| 1. Decode is memory-bandwidth-bound | framework | | | definitive | |
| 2. Memory hierarchy + why FlashAttention | SRAM/DRAM | definitive (L4+L12) | reinforced | | reinforced |
| 3. What a CUDA kernel is; read one | context | definitive | | graduation |
| 4. Why quantization works | | definitive (L7) | | capacity math | |
| 5. Parallelism → GPUs/interconnects | | | | definitive | |
| 6. Read vLLM/llama.cpp codebases | | | | what they fight | code practice |

### Why hardware is a core strand, not optional
Inference optimization *is* hardware reasoning. PagedAttention exists because KV cache fragmentation wastes HBM. Quantization exists because decode is memory-bound. FlashAttention exists because SRAM is small. The kipply essay sits right before C4 because mini-vllm's entire design — paged KV cache, continuous batching, speculative decoding — is just "obviously necessary responses to numbers you can now compute yourself."

### Does NOT cover
- Writing your own FlashAttention kernel (GPU MODE L12 gives the intuition; the paper adds tiling minutiae — expert tier)
- Full CUDA from scratch (Triton skips the nvcc boilerplate; the point is **reading** CUDA, not writing it from scratch)
- Full GPU MODE catalog (100+ lectures — only L4/L7/L12 are needed here)
- CUTLASS, CuTE, SASS microarchitecture, ThunderKittens (expert tier)

---

## C4 — Systems: Inference Engine from Scratch (Primary Color: How models become servable)

**Repo:** [Mihawii/mini-vllm](https://github.com/Mihawii/mini-vllm) + [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) (capstone)
**Verification:** mini-vllm 2★ but quality-verified (74 token-parity tests, committed benchmarks, candid limitations); llama.cpp 121k★
**License:** MIT (both)
**Hardware:** Laptop CPU for mini-vllm core; Kaggle T4 for GPU benchmarks
**Hours:** 12–20

### What you build (end-to-end)

**mini-vllm (8–12h core + 4–6h deep):**
- Custom autoregressive decoding loop (74 tests assert token-for-token greedy parity vs HF `model.generate()`, never calls `model.generate()`)
- KV cache on/off benchmark — **prove the 2.6× speedup yourself**
- Paged KV cache: block pool, per-request block tables, preemption, content-addressed prefix caching
- Continuous batching: iteration-level scheduler that pauses/drains/refills runs
- Chunked prefill: long prompts stop stalling the decode batch
- Speculative decoding: draft-propose + target-verify with lossless acceptance
- Dynamic INT8 quantization experiment (measure size, speed, output agreement)
- Tensor-parallelism math demo (Megatron-style sharding on simulated ranks)
- OpenAI-compatible FastAPI + SSE streaming + Prometheus metrics + scheduler dashboard
- Committed benchmarks (Qwen2.5-3B @ 197 tok/s on Kaggle T4×2)

**Capstone in llama.cpp (3–4h):**
- `llama-server` a GGUF model, quantize to Q4, `llama-bench` — operate the canonical 121k★ production engine

**Accompanying read:** [vLLM paper — "Efficient Memory Management for LLM Serving with PagedAttention"](https://arxiv.org/abs/2309.06180) (SOSP 2023). The paper you now understand because you built it.

### What it covers
- KV cache, paged attention, continuous batching, chunked prefill
- Quantization (dynamic INT8 as experiment; production Q4 via llama.cpp)
- Speculative decoding (provably lossless)
- Serving API design (OpenAI-compatible, SSE streaming)
- Inference metrics (TTFT, TPOT, ITL, goodput via Prometheus)
- Production quantization (GGUF Q4 via llama.cpp capstone)

### Does NOT cover
- Custom CUDA/Triton kernels for paged attention (mini-vllm is honest about this gap — it gathers blocks per step; vLLM's real kernel reads in place)
- Multi-device serving, K8s autoscaling, AI gateways, edge inference (see resource layer: Chip Huyen, AI Engineering — or skip for a minimal roadmap)
- AWQ/GPTQ-style weight quantization (llama.cpp capstone gives the Q4 exposure)

### Why mini-vllm despite 2★?
The quality signals are self-verifying: a 74-test suite with committed pass/fail reporting, committed benchmark JSONs with hardware configs, a candid limitations section that documents exactly what it doesn't do, and a README written by someone who understands educational inference engines. The llama.cpp capstone hedges the bus-factor risk with 121k★ behind it.

---

## C5 — Applied: Production RAG + Agents + Eval (Primary Color: How models become products)

**Core:** [DataTalksClub/llm-zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp) (6.9k★, free, laptop + $1–5 API cost, 30–50h)
**Production reference:** [jamwithai/production-agentic-rag-course](https://github.com/jamwithai/production-agentic-rag-course) (8.1k★, MIT, 7 tagged weekly builds, free blogs + $99 optional videos)
**Gap patches:** Selected notebooks from [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) (49.3k★)

### What you build (end-to-end)

**Core — llm-zoomcamp (30–50h):**
A searchable knowledge base → agentic RAG pipeline → vector/hybrid retrieval with reranking → evaluation harness (offline + online, LLM-as-judge) → monitored app with user feedback dashboards → **capstone: your own end-to-end RAG app** shipped with Streamlit/FastAPI.

Modules:
1. **Intro + knowledge base search** — keyword (BM25-style) and semantic (embeddings) search from scratch
2. **Vector search** — open-source DB (Qdrant/Pinecone), indexed retrieval
3. **Orchestration** — function calling, tool use, agent loop
4. **Evaluation** — retrieval quality (precision/recall/MRR/nDCG), answer quality (faithfulness, relevance, correctness), LLM-as-judge, Ragas metrics. **This module is why zoomcamp stays core.**
5. **Monitoring** — user feedback collection, online evaluation, dashboards, drift detection
6. **Advanced RAG** — hybrid search (BM25 + vector + RRF fusion), reranking (cross-encoder/biencoder), query rewriters, self-querying retrieval
7. **Capstone** — design, build, and ship your own RAG application

**Production reference — jamwithai weeks 4–7 (supplement, 15–20h):**
Use alongside or after llm-zoomcamp for depth on:
- Section-aware chunking with Docling PDF parsing
- BM25-first hybrid search discipline (start with keyword, add vector only when proven)
- Full LangGraph agentic layer: guardrails, document grading, query rewriting, adaptive retrieval
- Langfuse tracing end-to-end (not just the eval dashboard)
- Redis caching for cost reduction
- Telegram bot interface
- 6-service Docker stack: FastAPI + Postgres + OpenSearch + Airflow + Ollama + Redis

**Gap patches (4h total):**
- [Prompt caching notebook](https://github.com/anthropics/claude-cookbooks) — adds prompt caching that llm-zoomcamp doesn't cover
- [Moderation filter notebook](https://github.com/anthropics/claude-cookbooks) — adds guardrails that llm-zoomcamp doesn't cover
- [Building evals notebook](https://github.com/anthropics/claude-cookbooks) — complements zoomcamp's eval module with production patterns

### What it covers
- Embeddings, vector search, hybrid search, reranking, chunking strategies
- RAG from naive → advanced (multi-query, RAG-Fusion, CRAG, adaptive RAG)
- Function calling, tool use, single-agent loop, LangGraph orchestration
- Evaluation methodology: retrieval metrics, answer quality, LLM-as-judge, Ragas, online evaluation
- Observability: monitoring, user feedback dashboards, drift, tracing
- Production: Docker, Airflow, caching, 6-service stack (via jamwithai)
- MCP: indirectly via function calling patterns; no dedicated module

### Does NOT cover
- MCP theory (covered only through function calling proxies)
- A2A protocol, OpenTelemetry GenAI (read the OTel semconv docs → 2h)
- Full multi-agent systems, planning, reflexion (see optional D2 if needed)
- Deployment hardening (auth, rate limiting, CI/CD, cloud deploy)
- Voice assistants (see the ideal spec in the older roadmap files)

---

# Optional Depth Picks (choose 0–2)

Take these **only** if you target roles that specifically need the skill, or if you want to follow up the core with a month of depth.

---

## D1 — Generative Media: VAE → GAN → Diffusion → Multimodal

**Repo:** [davidADSP/Generative_Deep_Learning_2nd_Edition](https://github.com/davidADSP/Generative_Deep_Learning_2nd_Edition) — scoped to chapters 3, 4, 8, 13
**Verification:** 1.5k★, Apache-2.0, O'Reilly book code (frozen, book is the actual artifact)
**Caveat:** TensorFlow/Keras, not PyTorch. Concepts transfer cleanly.
**Hours:** ~20–25 (scoped chapters)

### What you build
- Ch 3: VAE on fashion-MNIST — autoencoding from first principles
- Ch 4: DCGAN, WGAN-GP — adversarial training hands-on
- Ch 8: DDPM from scratch + Stable Diffusion sampling — the generative-AI backbone
- Ch 13: CLIP-style image-text alignment — multimodal bridge

**Alternative (PyTorch, diffusion only, ~10–15h):** [hkproj/pytorch-stable-diffusion](https://github.com/hkproj/pytorch-stable-diffusion) — Stable Diffusion v1.5 line-by-line with YouTube series. Covers CLIP text encoder, VAE, U-Net with cross-attention, DDPM/DDIM sampler, classifier-free guidance. If GANs feel historical, swap this in for the higher-density PyTorch path.

### What it covers
- VAE: autoencoding, KL loss, latent space semantics
- GAN: generator vs discriminator, adversarial loss, conditional GANs, StyleGAN
- Diffusion: DDPM, DDIM, Latent Diffusion, Stable Diffusion, classifier-free guidance
- CLIP: contrastive vision-language pretraining, zero-shot transfer
- World Models (bonus chapter 12)

---

## D2 — Agent Depth: HF Agents Course

**Repo:** [huggingface/agents-course](https://github.com/huggingface/agents-course) — units 2–4 + Bonus Unit 2
**Verification:** 30.3k★, very actively maintained
**Hardware:** Free HF Inference API tiers
**Hours:** 15–20

### What you build
- Unit 2: Code Agents with smolagents, LlamaIndex, LangGraph — three frameworks in parallel
- Unit 3: "Alfred" agentic RAG app — tool creation, code execution, web search
- Bonus Unit 2: Langfuse + Opik tracing and evaluation pipelines
- Unit 4: Final capstone agent project scored on a public leaderboard

### What it covers
- Agent loop depth beyond llm-zoomcamp's single-agent function calling
- Three parallel frameworks for comparison
- Dedicated tracing & evaluation pipeline
- Multi-agent primitives via LangGraph subgraphs

---

# Resource Layer (theory for the gaps)

| Topic | Pick | Hours | When |
|---|---|---|---|
| Math for ML | [MML Book](https://mml-book.github.io/) (free PDF) — ch 2, 3, 4, 6 selective; [3Blue1Brown Essence of LA](https://www.3blue1brown.com/topics/linear-algebra) (~4h) for geometric intuition | 15–30 | During C1 |
| Classical ML | [StatQuest core playlist](https://statquest.org/) (trees, RF, boosting, SVM, CV, metrics) | 12–15 | After C1 wk 2 |
| Classical NLP | [Jurafsky & Martin SLP3](https://web.stanford.edu/~jurafsky/slp3/) (free PDF) — ch 2,3,4,5,11,12,13,17,20 | 15–20 | During C1 |
| RL fundamentals | [David Silver UCL RL lectures](https://www.youtube.com/playlist?list=PLqYmG7hTraZDM-OYHWgPebj2MfCFzFObQ) (10 lectures) | 15 | Before C2 |
| Agents theory | [Anthropic "Building Effective Agents"](https://www.anthropic.com/research/building-effective-agents) + [Lilian Weng agent survey](https://lilianweng.github.io/posts/2023-06-23-agent/) | 2 | Before C5 |
| AI safety | [BlueDot AI Alignment course](https://bluedot.org/courses/alignment) (free, 12 units) + Anthropic papers ([Constitutional AI](https://arxiv.org/abs/2212.08073), [Sleeper Agents](https://arxiv.org/abs/2401.05566)) | 15–30 | After C2 |
| Speech/audio | [HF Audio Course](https://huggingface.co/learn/audio-course) (8 units) | 10–12 | Optional (with D1 or standalone) |
| Multimodal/VLMs | [CLIP paper](https://arxiv.org/abs/2103.00020) + [LLaVA paper](https://arxiv.org/abs/2304.08485) | 3–4 | Before D1 or standalone |
| CV classics | [Stanford CS231n notes](https://cs231n.github.io/) (detection, segmentation, CNN architectures, transfer learning) | 20–25 | Optional (with D1) |

---

# Sequencing (~10–12 weeks)

| Week(s) | Strand | What you're doing | Milestone |
|---|---|---|---|
| 1–2 | C1 | Karpathy nn-zero-to-hero (lectures 1–7). Interleave MML math (ch2,3) + StatQuest basics. | Backprop Ninja (L5) feels easy. You can derive autodiff for any expression. |
| 3–5 | C1 | Raschka ch2–5 (tokenizer → attention → GPT → pretraining). Interleave SLP3 classical NLP. | BPE tokenizer trained; GPT-2 pretraining loop runs; you understand every line of the forward pass. |
| 6 | C2 | TRL sequence: SFT→RM→PPO→DPO→GRPO on Qwen2.5-0.5B. Do the Goodhart experiment (judge PPO with RM vs API judge, quantify the gap). | RM > 0.75 accuracy. PPO vs DPO tradeoff understood from your own results. |
| 7 | C3 | Hardware strand (19h block): Horace He (2h) → GPU MODE L4/L12/L7 (4.5h) → Triton 01–03 (4h) → kipply by hand (4h) → llm.c kernels (4h). | You can compute the memory-bandwidth-bound decode math yourself. You've written a Triton softmax kernel and read a real CUDA kernel. |
| 8 | C4 | mini-vllm: run quickstart → benchmark KV cache → simulate continuous batching → paged KV with preemption → speculative decoding → quant experiment → serve. | 74 token-parity tests pass. KV cache benchmark proves 2.6×. OpenAI endpoint streams tokens. |
| 9 | C4 | llama.cpp capstone + vLLM paper. | GGUF Q4 model running on `llama-server`. vLLM paper reads like a familiar story. |
| 10–11 | C5 | llm-zoomcamp full (10 weeks × 3–5h/week) accelerated to 2 weeks by focusing on modules 2–7. | Shipped RAG app with eval dashboard + monitoring. |
| 12 | C5 | jamwithai weeks 4–7 reference (LangGraph agentic layer, Langfuse, Redis, 6-service stack). Apply what you learn to harden your zoomcamp capstone. | Production-hardened RAG app: hybrid search, tracing/Docker. |
| 12 optional | D1/D2 | GDL2 generative media or HF agents-course. | — |

---

# What's Deliberately Not Covered (honest exclusions)

This roadmap is optimized for concept density. The following topics are real parts of the full curriculum that don't justify a project slot in a minimal design. Each has a named resource patch:

| Topic | What to do instead |
|---|---|
| **Voice assistant build** | Read the deep spec in the older `ai-engineering-projects-roadmap.md` (Appendix B) and build it if needed. ~30–40h. |
| **Nano-VLM (train a VLM from scratch)** | Same file, Appendix A. Read the LLaVA+CLIP papers (resource layer) as the reading compromise. |
| **MCP hands-on** | Read the jamwithai flagship's MCP-adjacent function calling patterns + the `modelcontextprotocol` spec. ~4h. |
| **A2A protocol** | Read the Google A2A spec repo. ~2h. |
| **OpenTelemetry GenAI** | Read the OTel semconv docs. ~2h. |
| **Full multi-agent systems** | Read Smallville paper + `reverie.py` source. ~6h. |
| **Autonomous coding agents** | Self-host OpenHands for a weekend. ~10h. |
| **K8s GPU production ops (Karpenter, KAI Scheduler)** | Read vLLM + SGLang deploy docs + one blog post. ~4h. |
| **AI gateways (LiteLLM, Portkey)** | Read LiteLLM docs + run one proxy command. ~2h. |
| **Edge inference** | Read the TensorRT-LLM edge notes. ~2h. |

---

# Prerequisites & Hardware Costs

- **Must know:** Python (including PyTorch basics, or learn PyTorch via Raschka Appendix A)
- **Highly recommended:** Docker, Git, basic CLI proficiency
- **GPU access:** Kaggle (free T4 ×2) or Google Colab (free T4) covers everything. C1 pretraining runs in ~1–2h on a T4 for the 124M model. C2 fits a T4. C4 runs on laptop CPU + optional T4 for GPU benchmarks.
- **API costs:** C2 Claude judge eval ~$5–10. C5 llm-zoomcamp ~$1–5 (mostly for eval prompts). C5 jamwithai runs locally. Total: **~$15–25** for the entire roadmap.
- No Google Cloud / AWS accounts needed.

---

# How to know you've learned it (verification checkpoints)

Rather than tracking hours, pass these gates.

| | After this strand | You can: |
|---|---|---|
| ✓ | C1 (z2h) | Write the backward pass for any expression graph by hand |
| ✓ | C1 (Raschka) | Train a GPT model from scratch; explain every layer of the Transformer diagram to a peer |
| ✓ | C2 | Run a full SFT→RM→PPO→DPO→GRPO sequence; judge if your model is actually better or just reward-hacked |
| ✓ | C3 | Compute the minimum ops required to decode a 7B model; name which bottleneck it hits; read a simple CUDA kernel |
| ✓ | C4 | Write an inference loop that beats HF's `model.generate()` on a latency benchmark; serve an OpenAI-compatible endpoint |
| ✓ | C5 | Design, build, eval, ship, and monitor a RAG application that an end user can actually use |
| ✓ | Resource layer | Explain when to use cross-encoder vs bi-encoder; argue why PPO exists if DPO is simpler; identify the safety-vs-capability tradeoff in a frontier model |

## Sources

- karpathy/nn-zero-to-hero: https://github.com/karpathy/nn-zero-to-hero
- rasbt/LLMs-from-scratch: https://github.com/rasbt/LLMs-from-scratch
- huggingface/trl: https://github.com/huggingface/trl
- Mihawii/mini-vllm: https://github.com/Mihawii/mini-vllm
- ggml-org/llama.cpp: https://github.com/ggml-org/llama.cpp
- DataTalksClub/llm-zoomcamp: https://github.com/DataTalksClub/llm-zoomcamp
- jamwithai/production-agentic-rag-course: https://github.com/jamwithai/production-agentic-rag-course
- huggingface/agents-course: https://github.com/huggingface/agents-course
