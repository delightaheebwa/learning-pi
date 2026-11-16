# Open WebUI: legacy setup guide (frozen)

This guide is frozen and legacy. It came from the pre-merge standalone
`learning-system` checkout. Its former body held commands, prompts, model
presets, WSL and container paths, and a repo remote for a retired two-repo
setup. Do not follow them. The old text stays in git history.

Current references:

- Canonical teaching behavior: `learning-pi/.pi/skills/`, `.pi/agents/`,
  `.pi/prompts/`, `.pi/APPEND_SYSTEM.md`, and
  `.pi/extensions/learning-gate/`. Behavior contract: `CONTRACT.md` and
  `contracts/learning-core.json`.
- Running the system: the root `README.md` and `FIELD-GUIDE.md`.
- The optional Open WebUI face is `deploy/`, Linux only, with `pi-bridge`. See
  `deploy/README.md` and `deploy/SECURITY.md`. That face holds chat
  transcripts, not teaching behavior.
- `state/Skills/`, `state/scripts/setup_openwebui.py`, and `state/infra/` are a
  frozen legacy snapshot kept for historical reference.
