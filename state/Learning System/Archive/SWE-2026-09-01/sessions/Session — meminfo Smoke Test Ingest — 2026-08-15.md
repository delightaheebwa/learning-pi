# Session — meminfo Smoke Test Ingest

- **Date:** 2026-08-15
- **Topic:** Robust `/proc/meminfo` smoke test — invariant design, sentinel values, smoke vs fixture tests, feature probing
- **Type:** Ingest (2 enrichments + 1 new concept)
- **Concepts enriched (2, SWE track):**
  - **Sentinel Values vs Presence Flags** — `{0}` default silently passing `available <= total` on missing `MemAvailable`; `ULONG_MAX` sentinel pattern; three-fact smoke assertion (`read==0 && total>0 && available<=total && available!=ULONG_MAX`); sentinel valid only when outside the legitimate domain. `last_reviewed` 2026-08-15, `next_review` 2026-08-22 (interval 3d→7d)
  - **Static Fixtures & Boundary Cases** — fixture tests (deterministic, exact asserts) vs smoke tests (live reads, range/sanity bounds); `total_kb > 0` divide-by-zero guard; `<=` is the true invariant (`<` brittle since `==` reachable on fresh/controlled systems). `last_reviewed` 2026-08-15, `next_review` 2026-08-29 (interval 7d→14d)
- **Concepts added (1 new, SWE track, `developing`):** Feature Probing vs Kernel Version Checking — runtime feature presence detection vs version checks (backports, spoofable uname); sentinel-as-feature-probe; pre-3.14 fallback `≈ MemFree + Buffers + Cached`; `MemAvailable` added in Linux 3.14. `last_reviewed` 2026-08-15, `next_review` 2026-08-18 (+3d), `Last Q Type` definitional
- **Wiki pages:** Sentinel Values vs Presence Flags (enriched), Static Fixtures & Boundary Cases (enriched), Feature Probing vs Kernel Version Checking (created)
- **Key insights ingested:**
  - `available_kb <= total_kb` is the logically complete invariant; strict `<` fails under rare boundary conditions (`==` on fresh/controlled systems)
  - `total_kb > 0` prevents downstream divide-by-zero (`100.0 * used_kb / total_kb` crashes)
  - `{0}` default + missing `MemAvailable` → `0 <= total` passes silently → green test on fake data; sentinel `ULONG_MAX` proves the key was found
  - Fixture tests assert exact values on static text; smoke tests assert sanity bounds on live data ("sanity shield")
  - Kernel version checking is fragile (backports, spoofing); multiple binaries are unmaintainable — probe feature presence at runtime, use a fallback formula (`MemFree + Buffers + Cached`) when absent
- **Verification:** learning-review gate via terminal CLI (Mimo v2.5, raw GitHub source URL). **Pass 1:** 3 medium issues — (1) `x != false` wording imprecise, (2) missing scope note on Teach C Lesson 3 section, (3) missing scope note on Static Fixtures' earlier sections → all fixed (reworded, 3 scope notes added). **Pass 2:** 3 medium flags on PRE-EXISTING Sentinel-page sections (Overview, The Fix, Key Insight — from 2026-08-07 ingest, not this session's source) → hard stop at 2 cycles per skill [2]; surfaced to user; implementer added scope notes to those sections (no third LLM pass). Factual gate (new concept only): `MemAvailable` added in Linux 3.14 (consistent with kernel history), fallback ≈ MemFree+Buffers+Cached (consistent with classic `free`) — verified against general knowledge.
- **Post-ingest follow-up (user-approved):** the pass-2 flags on pre-existing Sentinel-page sections were fixed by the implementer — Overview reworded to drop "payload value" jargon; "The Fix" scope note corrected (the 2026-08-15 Gemini source *does* name presence flags as pattern #2 — implementation details are expander-written on top); Key Insight `x != false` bullet rewritten as a precise, self-contained clarification. No third LLM pass (skill hard-stop [2]); implementer owns final wording.
- **Open questions:** none new
