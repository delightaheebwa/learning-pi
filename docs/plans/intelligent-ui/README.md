# intelligent-ui — implementation workspace

Plan for bringing GPT-6 "Intelligent UI"-style answers (text + visuals + interactive widgets,
auto-composed per turn) into the Open WebUI learning system.

**Read [`PLAN.md`](./PLAN.md) first.** It has the locked decisions, architecture, phases,
file:line references, risks, and done-criteria.

## Where the code lives

- `~/learning-pi` — canonical runtime (bridge, pi skill/agents, CONTRACT, tests). **Most changes.**
- `~/learning-system` — notebook + Open WebUI installer scripts (`scripts/setup_openwebui.py`,
  `scripts/audit_openwebui.py`, `infra/VERSIONS.md`). Installer-only writes.
- `~/learning-pi/deploy/` — `docker-compose.yml`, `SECURITY.md`, `.env*`.

## Start here

```sh
cd ~/learning-pi/docs/plans/intelligent-ui   # this dir
less PLAN.md
less PHASE0-FINDINGS.md                       # Phase 0 results + plan deltas
```

Phase 0 is source-confirmed against Open WebUI v0.12.2 (commit `6a18585`). To
finish the one live click-test, put an Open WebUI API key in `~/.openwebui_key`,
then run the spike against a **served** wrapper document (`data:` embeds render
as text in v0.12.2):

```sh
python3 spike_embeds_live.py --print-html > embed.html
python3 -m http.server 8000 &          # any host the browser can reach
python3 spike_embeds_live.py --base-url http://127.0.0.1:3000 \
  --widget-url http://127.0.0.1:8000/embed.html
```

Two Phase 0 results change the plan: the plugin must **not** be vendored (no
license), and the OpenUI bundle must be **pinned + self-hosted** (0.2.1).

## Phase checklist

- [x] **Phase 0** — spikes: artifacts trigger, embeds placement (below), bundle
      loading, license — findings in [`PHASE0-FINDINGS.md`](./PHASE0-FINDINGS.md);
      source-confirmed, one live click-test pending `~/.openwebui_key` (run
      `spike_embeds_live.py`)
- [x] **Phase 1** — viz teardown (revise-door commit #1) — full removal, see PLAN.md §Phase 1
- [x] **Phase 2** — OpenUI Lang pipeline: `openui` skill, `bridge/genui.py`, bridge fence
      extraction + REST embeds, `ui-audit` agent, contract invariants (revise-door commit #2)
- [x] **Phase 3** — hardening & docs: `IFRAME_CSP`, sandbox settings (same-origin OFF),
      gate_pipe carve-out, static-asset widget shell + self-hosted bundle, golden/e2e tests,
      doc updates
- [ ] Deferred — Mercury→Clef router, progressive streaming, Open Terminal

## Non-negotiables (don't relearn these the hard way)

- pi-bridge has **no tool-calling** → Open WebUI Tools / MCP / `render_openui` never fire on `learning*`.
- pi-bridge forwards **`message_end` only** → no progressive widget streaming.
- Rich UI message embeds render **above** message text → use the **two-message** arrangement for "below".
- Contract/`learning-core.json`/tagged tests change **only through the revise door**, together, one commit.
- Open WebUI objects are written **only** by `setup_openwebui.py`; verify with `audit_openwebui.py`.
- Fix the live system via the `omarchy`/`ovm` skills' rules if a change is system-level (docker/deploy/etc.).
