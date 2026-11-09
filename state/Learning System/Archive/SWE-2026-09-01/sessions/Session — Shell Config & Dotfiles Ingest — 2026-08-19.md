# Session — Shell Config & Dotfiles Ingest — 2026-08-19

- **Date:** 2026-08-19
- **Topic:** Shell configuration persistence (bashrc/bash_profile, `source`), `PS1` prompt, dotfile convention + symlink setup, plugin-framework caution, SSH-key passphrase
- **Type:** Ingest (1 new concept + 1 enrichment) — from MIT Missing Semester Lecture 2, second half
- **Source:** https://missing.csail.mit.edu/2026/command-line-environment/
- **Concepts added (1 new, SWE track, `developing`):**
  - **Shell Config & Dotfiles** — hand-typed shell settings don't survive logout; persist them in the shell config file (`~/.bashrc` / `~/.bash_profile`), which the shell reads on startup. `source ~/.bashrc` evaluates the file line-by-line in the current shell (no re-login needed). `PS1` renders the left prompt. Dotfiles are hidden plain-text config files (names start with `.`); collect them in one version-controlled folder (`~/.dotfiles`) and `ln -s` them into the standard locations via an install script → portable environment on any new machine. Plugin frameworks (Oh My Zsh) can bloat/slow the shell — install one plugin at a time. `command-not-found.com` shows which package provides a command. `last_reviewed` 2026-08-19, `next_review` 2026-08-22 (+3d), `Last Q Type` definitional
- **Concept enriched (1, SWE track):**
  - **SSH: Public-Key Auth & Remote Commands** — passphrase point: a passphrase **encrypts the private key file**; without one the key is plain text, so anyone with filesystem access can copy it and immediately use it to log into your remote servers (no password needed). Generate with `ssh-keygen -a 100 -t ed25519 -f ~/.ssh/id_ed25519`; validate with `ssh-keygen -y -f /path/to/key`. `last_reviewed` 2026-08-19, `next_review` 2026-08-22
- **Wiki pages (1 created, 1 enriched):** [[MIT Missing Semester — Shell Configuration & Dotfiles]] (new); enriched [[SSH — Public-Key Auth & Remote Commands]] (passphrase section + 5th takeaway). index.md + log.md updated.
- **Key insights ingested:**
  - Persistence lives in the config file the shell reads on startup, not in what you type at the prompt.
  - `source` is how you apply a config change to the *running* shell without logging out/in.
  - `PS1` is the variable that draws the left prompt — the classic first dotfile edit.
  - The dotfile payoff: one version-controlled folder + a symlink script = reproduce your whole environment on a fresh machine.
  - Plugin frameworks trade convenience for startup bloat — add plugins deliberately, one at a time.
  - A passphrase on your SSH key is not about hiding the key from the network; it's about protecting the private key *file* if someone steals/copies it.
- **Verification:** learning-review gate **PASS on pass 2** (verdict JSONs saved to `Reviews/Quality Gates/`; model `minimax-m3`). Pass 1 raised source-attribution flags ($PS1/`ln -s`/`source`/Oh My Zsh/passphrase) — most such material is genuinely in the static page; the rest is lecture-video narration from the learner's notes, so both wiki pages gained a precise scope/provenance note distinguishing textbook-page vs lecture-video content. Pass 2 returned PASS, 0 issues. **Factual gate passed** — bash config-file persistence, `source` semantics, `PS1`, the dotfile/symlink convention, and SSH-key passphrase encryption are standard, well-established shell facts.
- **Open questions:** none new
