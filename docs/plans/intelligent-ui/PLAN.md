# Plan: Intelligent-UI-style learning in Open WebUI (OpenUI Lang + native fallbacks)

Status: **Phase 0 spikes done** (source-confirmed against Open WebUI v0.12.2,
commit `6a18585`) — see [`PHASE0-FINDINGS.md`](./PHASE0-FINDINGS.md). Phases 1-3
not started (plan-mode output, 2026-10-18).
Goal: GPT-6 "Intelligent UI"-like answers inside the existing learning system —
text + visuals + interactive elements composed automatically per turn, so learning
is not a wall of white text.

## Decisions locked (2026-10-18)

| Decision | Choice |
|---|---|
| Host / chat face | Open WebUI (v0.12.2, `pi-webui` docker project, 127.0.0.1:3000) |
| Opt-in viz flow | **Removed entirely** — no `[[TURN:viz]]`, no `/show` opt-in, no viz-audit ceremony |
| Rendering stack | **OpenUI Lang inline embeds** + native fallbacks (Mermaid inline, Artifacts side panel, Python Run button) |
| Format decision | **pi decides in-prompt** (GPT-6-style). No external decision router for now |
| Widget verification | **`ui-audit` verifier** (replaces `viz-audit`); OpenUI Lang is declarative so binding/fact-check is cheap |
| Widget placement | **Below the prose** via two-message arrangement (embeds render above a message's own text by design) |
| Viz teardown scope | Full, including TUI features (explorer overlay, `/viz`, SVG/PNG exports) |
| Tools / MCP / tool-calling | Not used. pi-bridge has **no tool-calling support** (no `tools`/`tool_calls` in `bridge/*.py`) |
| Deferred | Mercury→Clef decision router; progressive UI streaming; Open Terminal for Python workloads |

## What the user gets vs GPT-6 Intelligent UI

- Format chosen **automatically per turn** by pi (like GPT-6 composing text/visuals/interaction). No opt-in.
- **Inline interactive widgets** (charts, forms, tables, follow-up buttons) — the OpenUI Lang route.
- **Inline diagrams** via native Mermaid; **free-form HTML apps** via native Artifacts side panel;
  **Python code blocks** runnable via the native "Run" button.
- Accepted gap: **no progressive UI streaming** — pi-bridge forwards only completed `message_end`
  (`bridge/stream.py:60-89`, invariant `B-deltas-never-forwarded`). Widgets appear fully formed.

## Architecture

```
learner turn → bridge → pi (learning lock)
  └─ pi decides in-prompt (new `openui` skill): text | mermaid | widget | html-artifact
       • diagrams  → ```mermaid block in prose (renders inline natively)
       • widgets   → ```openui fenced OpenUI Lang payload (40+ components)
       • free-form → ```html block (native Artifacts side panel)
       • ui-audit  → binds payload + verifies load-bearing facts ⊆ evidence
                     (GATE:ui_audit receipt; withhold on fail)
message_end → bridge:
  ├─ forwards clean prose (+ mermaid/html fences intact — native rendering)
  ├─ extracts ```openui fence, wraps it with our own OpenUI HTML shell
  │   (self-hosted bundle + iframe:height + sendPrompt; see Phase 0)
  └─ delivers widget via Rich UI `embeds` on its own 2nd assistant message
     → widget renders BELOW the prose
follow-up button → sendPrompt/input:prompt:submit (confirm dialog) → new gated turn
```

### Why this shape (key research findings)

- **Open WebUI Rich UI embeds** (`embeds` event) render HTML in a sandboxed iframe, persist in chat.
  Message-level/Action embeds render **above** the message text (docs, "Rendering Position") —
  hence the two-message arrangement for "below".
- **Native Artifacts** detect model-emitted HTML/SVG (no tool-calling) and show them in a side panel
  with versioning; `IFRAME_CSP` + Settings>Interface sandbox toggles control isolation.
- **Mermaid** renders inline for ` ```mermaid ` fences.
- **thesysdev/openwebui-plugin** (`render_openui(openui_lang_code, title)`) proves the inline path,
  but as a Tool it needs OpenAI `tool_calls` — **pi-bridge cannot produce them**, so it would never
  fire on `learning*` models. We **cannot vendor its code** (no license, Phase 0), so we write our own
  rendering wrapper and deliver via `embeds` instead.
- `input:prompt:submit` from cross-origin embeds shows a confirm dialog (works without same-origin).
  Closed bug #26912 (`input:prompt:submit` silently dropped) applied to **tool-result srcdoc iframes**;
  Phase 0 confirmed the own-embed trust path is present in v0.12.2 and message-level embeds reach the
  dialog (live click-through still pending an API key).
- The bridge keeps `chat_id` in scope at turn end (`bridge/server.py:344,377`; `session_key()` `:66-84`)
  but has **no Open WebUI REST client today** (only installer scripts in `learning-system/scripts/`).

## Phase 0 — Spikes (do first; they unblock design)

1. **Artifacts trigger**: confirm a ` ```html ` fence inside a longer pi-style message opens the
   Artifacts panel on v0.12.2 (docs only say "generate a block of HTML code").
2. **Embeds delivery + placement**:
   - Filter `outlet` `__event_emitter__({"type":"embeds",...})` vs REST
     `POST /api/v1/chats/{chat_id}/messages/{message_id}/event`.
   - Implement **two-message**: append a minimal assistant message via the chat-save API, then attach
     the embed to it → renders below the prose message. Verify persistence across reload.
   - Verify `input:prompt:submit` confirm dialog + submit works from message-level embeds.
3. **Bundle loading**: pin `@openuidev/browser-bundle` (not `@latest`); decide jsDelivr allowlist in
   `IFRAME_CSP` vs self-hosting via the plugin's `cdn_base_url` valve (self-host preferred for the
   repo's network posture: `deploy/SECURITY.md` — loopback-only, no 0.0.0.0).
4. **License check** on `thesysdev/openwebui-plugin` `tool.py` (repo shows no LICENSE; the OpenUI
   standard repo is MIT). If unclear, write our own thin wrapper against the OpenUI Lang spec.

**Phase 0 results** (full evidence in [`PHASE0-FINDINGS.md`](./PHASE0-FINDINGS.md)):

- **1 — CONFIRMED:** ` ```html ` auto-opens Artifacts (as do `svg`, `xml`+`<svg`); `mermaid`
  renders inline, not as an artifact; no size threshold and surrounding prose is irrelevant.
- **2 — CONFIRMED:** embeds render **above** a message's own text; the **two-message** recipe
  (append a 2nd assistant message via `POST /api/v1/chats/{id}`, then `POST
  .../messages/{id}/event`) is feasible over REST. pi-bridge is not a Filter, so the REST route is
  the path. `input:prompt:submit` from a message-level embed reaches the confirm dialog (own-embed
  trust path; bug #26912 fixed in v0.12.2). Only the live click-test is pending an API key.
- **3 — DECIDED:** pin **and self-host** `@openuidev/browser-bundle@0.2.1` (MIT; ~873 KB gzip JS +
  ~38 KB gzip CSS), not the plugin's `@latest` CDN default. No CDN allowlist needed.
- **4 — BLOCKER RESOLVED:** the plugin repo has **no license** → do **not** vendor `tool.py`. Write
  our own wrapper against the MIT OpenUI Lang spec/bundle.
- **New open question for Phase 2/3:** embeds are **URLs**, so the wrapper HTML must be served —
  recommendation: an Open WebUI static asset written by `setup_openwebui.py` (same-origin, no new
  port).

## Phase 1 — Viz teardown (revise-door commit #1, `learning-pi`)

One reviewed commit. The update door may never touch `contracts/`, `CONTRACT.md`, `test/`
(`CONTRACT.md:12-24`); behavior lives in contract + tagged tests (`S-1`, `CONTRACT.md:323`).

- **`CONTRACT.md`**: delete the 5 `G-viz-*` invariants (`:224-239`); edit `G-solo-no-teaching`
  (`:123-129`) to drop the viz / `SOLO_NO_AIDS` clause; audit `G-pass-substantive` and
  `G-receipt-shape-binds` statements for viz mentions.
- **`contracts/learning-core.json`**: delete the 5 `G-viz-*` entries + their test names; fix
  `G-solo-no-teaching` (test `solo flow withholds a visualization`).
- **Tests**:
  - delete `test/viz_test.mjs` + remove from the `scripts/learn-check` deno suite loop;
  - `test/golden/golden_test.mjs:308-371` — delete the 9 viz assertions;
  - `test/gate_test.mjs:926-928` — delete solo-viz test;
  - `test/bridge/test_bridge.py:177` — drop `"viz"` from the tag-strip vocabulary loop
    (line ~408 `/viz` is a Regenerate test, not viz — keep);
  - `test/contract/check_learning_layer.py:51-54,152` — remove viz/viz-audit/learning-viz expectations;
  - delete `test/e2e/scenarios/viz-{smoke,full}.json`; `test/e2e/impact-map.json:33-34` — delete rules.
- **Impl/resources in the same commit**:
  - `.pi/skills/learning-viz/` (SKILL.md),
  - `.pi/extensions/viz-mode/` (10 files; explorer/render-svg/asii/raster/image-patch/spec/expr/wire),
  - `.pi/agents/viz.md` + `viz-audit.md`, `~/.pi/settings.json` `:18-19` overrides,
  - `.pi/prompts/show.md`, viz vocabulary in `teach.md`/`lesson.md`/`continue.md`/`review.md`/`solo.md`,
    `.pi/APPEND_SYSTEM.md` (`:19,:34,:154,:213-217`),
  - gate branches: `gate-core/engine.ts` (~12 sites: `:497-519,610-637,683-714,929-961,978,1102,...`),
    `gate-core/primitives.ts` (`:22,:49,:87-89,:762-769,:797-811,:1146-1147,:1393`),
    `gate-core/judge/{types,model,prompts}.ts`, `learning-gate/index.ts` docblock,
    `pi-adapter/index.ts:60` dispatch vocabulary,
  - `FIELD-GUIDE.md` / `README.md` counts (13 agents, 5 skills, 9 prompts, 8 deno suites).
- `learning-system` has **zero code refs** — do not touch historical session/lesson prose.

## Phase 2 — OpenUI Lang pipeline (revise-door commit #2 + infra)

- **`openui` skill** — `learning-pi/.pi/skills/openui/SKILL.md`:
  when text vs mermaid vs widget vs artifact; OpenUI Lang authoring rules (port snippets from
  thesysdev/openui docs, MIT); payload caps; no external assets in widgets; follow-up buttons must
  carry selected values explicitly.
- **Wrapper module** — `learning-pi/bridge/genui.py`: our own HTML shell (no code from the
  unlicensed plugin) + `iframe:height` reporting script + `sendPrompt` bridge; self-hosted pinned
  bundle (Phase 0 decision).
- **Bridge changes**:
  - `bridge/stream.py` — extract ` ```openui ` fences alongside `strip_turn_tag()` (`:24-33`); drop
    `viz` from `_TURN_TAG_RE` (`:24-26`);
  - new small Open WebUI REST client using `~/.openwebui_key` for the post-turn two-message embed;
  - extend `test/bridge/test_bridge.py` (fence extraction + tag vocabulary).
- **`ui-audit` agent** — `.pi/agents/ui-audit.md`, envelope `GATE:ui_audit`, evidence-mandated
  (clone the `viz-audit.md` structure) + `~/.pi/settings.json` model override.
- **Contract invariants** (same commit + tagged tests): `G-ui-turn-requires-audit`,
  `G-ui-audit-binds-payload-and-prose` (canonical OpenUI Lang JSON equality),
  `G-ui-payload-valid`; `G-solo-no-teaching` keeps `SOLO_NO_AIDS` for widgets.
  Mermaid / html-artifact numbers stay under the existing claims rules.
- **Prompts** — `teach.md` / `lesson.md` / `continue.md`: auto composition; delete opt-in language.

## Phase 3 — Hardening & docs

- `deploy/docker-compose.yml`: `IFRAME_CSP=default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:;
  connect-src 'none'` (self-hosted bundle → `'self'` suffices; **no CDN origin**). Keep **iframe Sandbox Allow Same Origin
  OFF**.
- `gate_pipe.py` defensive carve-out: ignore ` ```openui `/` ```mermaid `/` ```html ` fences in
  `_normalize_for_binding` (bridge normally strips `openui` first). Edit via `setup_openwebui.py` +
  `audit_openwebui.py` (installer-only writes; `infra/VERSIONS.md` entry).
- Golden tests: wrapper HTML, ui-audit binding pos/neg, bridge fence extraction; e2e
  `openui-smoke` (teach turn with widget + a follow-up turn).
- Docs: `learning-system/OPENWEBUI.md`, `learning-system/infra/VERSIONS.md`, `learning-pi/FIELD-GUIDE.md`,
  `learning-pi/README.md`, `learning-pi/bridge/README.md`, `learning-pi/deploy/SECURITY.md`.

## Deferred / optional (documented, not built now)

- **Mercury Decide → Cloudflare Clef-flash** presentation router (System One API schema shared).
  Keys: Inception `mercury-decide` (free tier) primary, `@cf/cloudflare/clef-flash` (smallest Clef)
  fallback. Config in `~/.config/genui.env` (600). Not needed while pi decides in-prompt.
- **Progressive UI streaming** — needs same-origin DOM tailing (community Inline Visualizer pattern)
  or a bridge rewrite; out of scope.
- **Python workloads** — native manual Run button works; Open Terminal is the real backend if needed
  (was in the frozen legacy stack `learning-system/infra/docker-compose.yml`).
- **Standalone OpenIntelligentUI MCP server** as a pi-net service (skill docs only) — not needed.

## Constraints honored

| Invariant | How |
|---|---|
| `B-deltas-never-forwarded` | widget payload rides in final `message_end`; prose forwarded clean |
| Gate/claims on prose | unchanged; `ui-audit` receipt covers widget facts |
| `B-single-learning-writer` | follow-ups are ordinary learner turns |
| No tool-calling assumption | fence + `embeds` path; native Tool import only for non-pi models |
| Revise door | teardown + new invariants each in one reviewed commit with tests |
| Installer-only writes | all Open WebUI objects via `learning-system/scripts/setup_openwebui.py` |
| Network posture | bundle pinned/self-hostable; `connect-src 'none'`; no new published ports |

## Risks / watch-items

- ~~Two-message placement may be infeasible via the public REST API~~ **Resolved in Phase 0** — it is
  feasible; see PHASE0-FINDINGS.md §2c.
- ~~Artifact trigger heuristic may not fire on a fence inside a longer message~~ **Resolved in
  Phase 0** — `html`/`svg` fences trigger regardless of surrounding prose, with no size threshold.
- OpenUI bundle is ~873KB gzipped JS + ~38KB gzipped CSS on first load at 0.2.1
  (browser-cached); self-host to avoid CDN dependency (Phase 0).
- **Phase 2/3:** embeds are URLs — decide where the wrapper HTML is served (recommend an Open WebUI
  static asset via `setup_openwebui.py`); see PHASE0-FINDINGS.md open question.
- `ui-audit` adds a verifier turn per widget — watch latency; keep it single-shot with a fix loop like
  the old viz-audit.

## Verification (done criteria)

- Phase 0 spikes pass (placement below, persistence, follow-up submit, artifact trigger).
- `python3 scripts/audit_openwebui.py` prints `in sync`.
- `scripts/learn-check` green with the new tagged tests; no active invariant lacks a passing test.
- Manual: a teach turn renders an inline OpenUI widget below the prose; a follow-up button starts a
  gated turn; a widget with an uncovered number is withheld (ui-audit negative test).
