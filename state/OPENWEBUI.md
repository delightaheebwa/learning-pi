# Open WebUI Setup & Operating Guide

> **⚠️ FROZEN / LEGACY PATH.** The Open WebUI pedagogy path is **frozen and unmaintained**. The
> canonical teaching behavior is the **pi** layer in `learning-pi` (`learning-pi/.pi/skills/`,
> `learning-pi/.pi/agents/`, `learning-pi/.pi/prompts/`, `learning-pi/.pi/extensions/learning-gate/`);
> `learning-pi/README.md` and `CONTRACT.md` are its references. The `Skills/*/SKILL.md` copies in
> this repo are a frozen snapshot — do not add teaching-behavior changes to them. This guide is kept
> for historical reference only.

This file is the legacy guide for running the learning system in **Open WebUI**
using native features. The repo checkout (Open Terminal
workspace) is the source of truth for all state; Open WebUI holds the control
layer (skills, subagents, model presets, prompts, gate Pipe) that routes triggers.

> **2026-08-25 — tools → subagents:** the three gate tools (`fact_check`,
> `review_gate`, `quiz_gate`) were retired after persistent HTTP 500 failures.
> All verification now runs as **foreground subagent tasks** (`delegate_task`,
> `background:false`) with Pydantic envelope validation (`gate_schema.py`).
> The Python tool files were archived 2026-09-08 to
> `Learning System/Archive/legacy-tools-2026-08-25/`; fixed verifier prompts live in
> the global `subagents.system_prompt`
> (keyed by `GATE:`). Enforcement is via the gate **Pipe/Filter**
> `Skills/learning-review/openwebui/gate_pipe.py` (see "Gate enforcement").

## Architecture

| Concern | Open WebUI mechanism | Model — change it in ONE place |
| --- | --- | --- |
| Scout (exploration) | **Scout** preset | Workspace → Models → Scout → base model |
| Tutor (probe/plan/teach) | **Learning Tutor** preset | Workspace → Models → Learning Tutor → base model |
| Clerk (ingest + review) | **Clerk** preset — handles standalone reviews, standalone ingests, AND lesson-handoff ingests (Deputy was a legacy review preset, deleted 2026-09-08 after Clerk absorbed its role) | Workspace → Models → Clerk → base model |
| Slash-command triggers | **Prompts** (`/review`, `/ingest`, `/teach`, `/lesson`, `/continue`) — `/swe` is legacy (SWE archived; redirects to AIEFS) | — |
| Deterministic gate | **Gate Pipe** Filter (`gate_pipe.py` + `gate_schema.py`) — outlet, priority 10, bound to Tutor + Clerk | Function Valves (priority, max_retries, digest_ttl_days) |
| Fixed verifier prompts | Global **subagents.system_prompt** (keyed `GATE:fact_check` / `GATE:quiz_audit` / `GATE:review` / `GATE:review_session` / `GATE:grade_audit`) | Settings → Subagents |
| Repo + git | **Open Terminal** sandbox checkout (container) vs the WSL checkout on the host — different `$HOME`s, same repo. Docker Desktop publishes the UI on host port 3000 — reach it as `http://localhost:3000` from Windows, WSL, and browsers; only *container-to-container* traffic uses service names / `host.docker.internal` | — |
| Ephemeral Scout digest | `Learning System/.tmp/context-<chat_id>-<slug>.json` (gitignored, 7-day TTL) — now includes `rohit_hash` + `external_refs` (each with `excerpt` ~500 chars + `takeaways` + `adds_vs_rohit`) + top-level `synthesis` + `lang_recommendation` + `roadmap_sha` + `fetched_at`; adaptive re-fetch; `📦 Concept Archive.md` strictly out of scope | — |
| Web search / grounding | **Web Search** (SearXNG) — Scout uses it to fetch `docs/en.md` + Further Reading external refs live (Rohit is a source, not the source) | — |

### Models: one field per task

To change the model for any task, edit exactly one field in the Open WebUI UI
(table above). It takes effect on the next message. Nothing in this repo needs
to change — skills and prompts refer to models by role ("the subagent default
model"), never by ID.

Rules:

- Each preset's base model is whatever its preset's `base_model_id` is set to.
- The gate Pipe is bound only to Tutor and Clerk; Scout is exempt.
- Verifier model reality (verified 2026-09-08 against backend `utils/subagents.py::delegate`): verifiers run on the **calling preset's own base model** — Open WebUI has no separate "subagent default model" setting (its `subagents` config holds only enable/limits/system-prompt keys). So the Tutor's verifier is the Tutor's model. Enforcement therefore rests on the deterministic Pipe checks (`claims[] ⊆ rendered_content ⊆ emitted`, quiz parity, file grounding) plus the fixed `GATE:` prompts — not on model independence. Pick Tutor/Clerk base models with strong instruction-following so the envelope protocol is actually obeyed (observed failure mode: right envelope, wrong turn type).

### Gate enforcement (Pipe)

The gate Pipe (`gate_pipe.py`, outlet) blocks before render — bound to Tutor + Clerk; Scout exempt:

> **Fail-open paths (deliberate, made visible 2026-09-09):** on DB/lookup/internal errors the Pipe passes the draft through rather than bricking the learner (unsaved chats, DB history fetch failure, child-receipt lookup failure, unexpected outlet exceptions). Each such path now logs at WARNING (`gate_pipe DB history fetch failed (fail open)` / `gate_pipe child lookup failed (fail open)`) — grep `docker logs open-webui` for `gate_pipe` if you suspect enforcement is off. A missing block does NOT prove the gate approved anything.

- **Scout digest for new lessons:** a Tutor turn responding to a new `/teach`/`/lesson` (no `Lessons/Lesson — <slug> — *.md` yet) requires a `.tmp/context-<chat>-<slug>.json` digest and a prior `Scout` message in the same chat (7-day TTL, slug must match trigger). Resume of an existing lesson grounds in `Lessons/` + `Sessions/` and bypasses this check, so stale/missing digests don't confuse Tutor.
- **Receipts:** every non-trivial Tutor (claims) and Clerk (wiki or grade) message requires a foreground `GATE:*` envelope dispatched via `delegate_task` (`background:false`) with a child internal chat (`meta.parent_message_id == draft.id`) whose task parses as the envelope schema and whose assistant output parses as the verdict schema covering every `claims[].id`. Tutor `fact_check` is generation-to-emission: the envelope must carry the actual draft in `rendered_content`, the Pipe checks `claims[] ⊆ rendered_content ⊆ emitted message`, and plan-only verification never passes. Clerk `review` is file-grounded generation-to-emission: grounding (`source_url`/`source_file`/`lesson_ref`) is required, every concept must appear in `wiki_content`, and the written wiki files must match the reviewed content. Grade turns (Tutor **and** Clerk review flow) require a foreground `GATE:grade_audit` envelope (`concept/question/learner_answer/claimed_verdict/source_excerpt`) before the grade renders. The standalone-review **close** additionally requires a foreground `GATE:review_session` envelope (`concepts/transcript/grade_verdicts/written_files[]/state_rows`) whose `written_files[].path` must exist on disk and match its `content`; scope is fenced (non-session state drift → `context_notes`) and an `ISSUES` verdict **renders with a `⚠️ REVIEW FLAGS SURFACED` banner** rather than being withheld — a deliberate anti-dead-end choice mirroring the pi gate. Retry cap 2 per user turn (durably counted in `Chat.meta.gate_state`); after cap, `⛔ Withheld` banner (except the `review_session` ISSUES banner path). Block codes: `NO_SCOUT_CONTEXT`, `NO_DELEGATION`, `MALFORMED_ENVELOPE`, `MALFORMED_VERDICTS`.

## One-time setup

The setup script (`scripts/setup_openwebui.py`) creates everything:

1. **Workspace → Skills** — import the 4 `Skills/*/SKILL.md` files.
2. **Functions → Gate Pipe** — installs `gate_pipe` (inlined `gate_schema.py`) as Filter type, priority 10, bound to Tutor + Clerk.
3. **Subagent system prompt** — sets global `subagents.system_prompt` to the `GATE:*` templates.
4. **Workspace → Models** — creates **Scout**, **Learning Tutor**, **Clerk** presets (each with its system prompt, capabilities, and skill bindings; Tutor/Clerk have `filterIds: [gate_pipe]`).
5. **Workspace → Prompts** — creates the 7 slash commands below.
6. **Open Terminal** — repo checkout present; git push is wired.

*(Legacy, dormant: the `fact_check` / `review_gate` / `quiz_gate` Tools and their setup. Do not bind them.)*

### Preset system prompts (summary)

- **Scout:** gather MISSION/CURRICULUM/RESOURCES + relevant Active Concepts rows (do not grep SWE archive) + live `phases/<phase>/<lesson>/docs/en.md` **plus every URL in its `## Further Reading`** (Rohit sets the agenda, not the whole lesson; pack per-source `excerpt` + `takeaways` + `adds_vs_rohit` plus top-level `synthesis` into the digest); hash and surface drift (`SCOUT DIGEST: ⚠️ Upstream changed`), capture `lang_recommendation` (Python/TS/Rust per header); write `.tmp/context-<chat>-<slug>.json` + post `SCOUT DIGEST:` in chat. Special: Mission 0 Catch-Up (P0+P1.01–06, 80/20) synthesizes 5 strands. No phase cache (live fetch).
- **Learning Tutor:** assume Scout digest (now includes per-source `excerpt`/`takeaways`/`adds_vs_rohit` + `synthesis` + `rohit_hash`+`external_refs`+`lang`+`roadmap_sha`) / session context or existing `Lessons/` file; do not gather context or write wiki pages; deliver every checkpoint as a sequence of mini-checkpoints (one atomic idea per message, pausing after each to invite questions/tangents, then the checkpoint's single practice), making the Rohit framing → external angle → synthesis moves across them; verify claims via foreground `GATE:fact_check` (`source_urls`: Rohit + external refs, with `reference_excerpt`) before presenting; respect per-lesson language (Python/TS/Rust); handoff to Clerk via `Pending Ingest.json` at lesson end. Order: Mission 0 Catch-Up (in-progress) → Phase 1 L07.
- **Clerk:** reads `Pending Ingest.json`, writes wiki/Active Concepts, dispatches `GATE:review`, applies fixes, cleans digest and marker, commits.

**Environment note (Docker Desktop Windows-side, separate from WSL):** the UI is at `http://localhost:3000` from Windows and WSL alike (verified: the audit script and chat pulls run from WSL over localhost). Container-to-container calls use `host.docker.internal` / bridge IPs (see `infra/ACCESS.md`); workspace repo checkout in-container vs the WSL checkout on the host. See `Learning System/MISSION.md`.

### Prompts

`/swe` — **Legacy** (SWE archived 2026-09-01) — redirects to AIEFS review. Use `/review` instead.
`/review` — Run a review session on the **AIEFS** track (SWE `swe` is archived). Load `learning-system`, follow Review flow. Grades are verified via foreground `GATE:grade_audit`, and the end-of-review writes are audited via foreground `GATE:review_session` — do not bypass either.
`/ingest` — `Ingest the following content: {{content}} — Switch to Clerk, load learning-system, follow Ingest flow, then commit and push.`
`/teach` — `Teach me about: {{topic}} — Switch to Scout to gather context, then to Learning Tutor, load learning-teach, run probe → plan → teach. Gate enforces foreground GATE envelopes.`
`/lesson` — `Run the next curriculum lesson. Switch to Scout to gather context for the next lesson, then to Learning Tutor, load learning-teach.`
`/continue` — `Continue the current lesson where we left off. Load learning-teach. If the lesson file exists, it is the source of truth — no Scout digest needed.`
`/pause` — `Pause the current lesson where we are. Switch to the Learning Tutor preset, load learning-teach, run the pause protocol (exit ticket for today's mini-checkpoints only, partial lesson file with Status + Resume-from pointer — Checkpoint N/M, mini K/L — partial Pending Ingest.json), then hand to Clerk with /ingest to bank today's progress. Partial ingests keep the lesson in-progress and the Scout digest alive; curriculum row becomes in-progress (paused N/M).`

## Operating notes

- Skills are lazy-loaded via `view_skill`; keep each `description` crisp.
- Verification is synchronous per step: one foreground `delegate_task` per gate **of the matching type for the turn** (grade→`grade_audit` only; claims→`fact_check`; questions→`quiz_audit`; mixed claims+questions→both — no substitutions), fold verdicts in before presenting. Fixed prompts live in global `subagents.system_prompt`; do not weaken them.
- Scout digests are ephemeral (`.tmp/`, gitignored). `Clerk` deletes the consumed digest and clears `Pending Ingest.json` on success. Orphans older than 7 days are swept on the next Tutor/Clerk inlet (the Filter runs only on those presets; Scout is exempt).
- Routine consistency (prerequisites, self-contradiction, coverage) is the tutor's own responsibility.

## Intelligent-UI widget assets

The canonical **(frozen) legacy** Open WebUI path predates the pi-layer widgets, but the
installer still hosts their static assets so the canonical pi deployment (learning-pi) can
serve them: `scripts/setup_openwebui.py` writes the pinned, MIT `@openuidev/browser-bundle@0.2.1`
plus the shell `widget.html`/`widget.js` into `~/learning-pi/deploy/openui/0.2.1/` (override with
`--openui-static-dir` / `OPENWEBUI_OPENUI_STATIC_DIR`). `learning-pi/deploy/docker-compose.yml`
mounts that directory read-only at `/app/backend/open_webui/static/openui` and sets `IFRAME_CSP`
with `connect-src 'none'`. `scripts/audit_openwebui.py` verifies the served bundle sha256 and the
shell. The shell is opaque-origin (Same Origin stays OFF), so it follows the OS
`prefers-color-scheme` rather than Open WebUI's in-app theme; it also re-measures height on
resize/fonts/disclosure, falls back to `execCommand` when the Clipboard API is denied, and ships
keyboard-focus and invalid-input styles. The gate Pipe's `_normalize_for_binding` ignores
` ```openui `/` ```mermaid `/` ```html ` fences so a visual payload never satisfies a prose claim.

## Maintenance

- **Model changes:** UI only (see table). No repo edits, no installer flags.
- **Gate tuning:** Function Valves for `gate_pipe` (priority, max_retries, digest_ttl_days) + global `subagents.system_prompt`.
- The repo is canonical. After editing any `Skills/*/SKILL.md`, re-import the changed skill in Open WebUI (or re-run the setup script) — skills do not auto-sync. Re-running preserves UI-chosen models.
- Re-run the setup script after adding/removing prompts or changing system prompts. It is idempotent.
