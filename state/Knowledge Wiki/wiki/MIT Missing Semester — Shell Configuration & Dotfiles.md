<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# MIT Missing Semester — Shell Configuration & Dotfiles

**Source:** [Command-line Environment](https://missing.csail.mit.edu/2026/command-line-environment/) · MIT Missing Semester (Lecture 2, second half)
**Track:** SWE (Software Engineering Fundamentals)
**Ingested:** 2026-08-19

> **Scope / provenance note:** this page distils **MIT Missing Semester Lecture 2 (second half)** — the shell-configuration / dotfiles section of the lecture — as captured in the learner's notes, cross-referenced against the textbook page. What comes from the **static text page** (verified in the page body): dotfiles hide from `ls`, editing `~/.bashrc`/`~/.bash_profile`, collecting configs in one repo, publishing on GitHub, an install script using `ln -s`, and the `$PS1` prompt exercise, plus `prezto`/`oh-my-zsh` frameworks and plugins (zsh-syntax-highlighting, zsh-autosuggestions, zsh-completions). What comes from the **lecture video narration** (in the learner's notes, not the static text): the `source` builtin's line-by-line behavior, the "config resets after logout" motivator, "add one plugin at a time" guidance, the `~/.dotfiles` + symlink install-script workflow, and the SSH-passphrase reasoning (a passphrase encrypts the private key file; without one the key is plain text anyone with file access can copy). All such additions are standard, well-established shell facts; none contradict the textbook.

## Why shell configs need to persist

Shell settings you type at the prompt **do not survive** — after you log out of an SSH session (or close the shell), anything set by hand is gone. To make a configuration stick, you add it to the shell's **configuration file**, which the shell reads on startup.

For **bash** that is `~/.bashrc` or `~/.bash_profile` (editing either works on most systems). Reading a config file on startup is why every new shell "remembers" the aliases, `$PATH` additions, and prompt settings you've written there.

Other tools use the same dotfile convention:

| Tool | Config file |
|---|---|
| bash | `~/.bashrc`, `~/.bash_profile` |
| git | `~/.gitconfig` |
| vim | `~/.vimrc` (and `~/.vim/`) |
| ssh | `~/.ssh/config` |
| tmux | `~/.tmux.conf` |

## `source`: apply a config without re-logging-in

`source ~/.bashrc` (or `~/.bash_profile`) **evaluates the file line by line** in the current shell — like running each command in it yourself. After you edit a config file, `source` reloads it so the new settings take effect *in the running shell*, without needing to start a new one.

## `PS1`: the left prompt

`PS1` is the shell variable that **tells the shell how to render the left prompt** (the `user@host:~/path$` that appears waiting for input). Customizing `PS1` is the classic first dotfile customization — the MIT exercise suggests *"customizing your shell prompt by setting `$PS1`"* as a simple starting point.

## Dotfiles: the convention

Many command-line programs are configured with **plain-text files whose names start with a dot** (e.g. `~/.vimrc`, `~/.bashrc`) — the leading dot *hides* them from the default `ls` listing. These are called **dotfiles**, and people document their setups online (search for `.dotfiles` patterns / "dotfiles" configs).

### Put the scattered configs in one folder + version them

Rather than leaving configs scattered across `~`, collect them in a single folder (e.g. `~/.dotfiles`) and put that folder under **version control (git)**. Publish it on GitHub.

### Symlink them into place

Because each program looks for its config in a *standard* location (`~/.bashrc`, `~/.gitconfig`, …), you write a small **install script that creates symbolic links** (`ln -s`) from the standard locations to files inside your dotfiles folder — e.g. a symlink at `~/.bashrc` pointing at `~/.dotfiles/.bashrc`.

Now when you set up a *new* computer, instead of re-typing every setting you run the script, which re-creates the symlinks and instantly restores the environment you're used to. The dotfiles repo + symlink script is the standard "portable environment" setup.

### Utilities

A symlink script is the simplest installer, but specialized dotfile managers exist too. The MIT page suggests testing the install script on a fresh virtual machine before trusting it.

## Plugin frameworks: a caution

Frameworks exist that load many plugins at once — e.g. **Oh My Zsh**. They're convenient but can **bloat your shell experience**: when the shell tries to do a lot of things for you, startup can slow down noticeably. **Install one plugin at a time** and only keep it if it's actually useful to *you*.

## Related links

- `command-not-found.com` — how to install different packages (which package provides a given command).
- Example recursive-path pattern from the textbook: `export PATH="$PATH:/path/to/program/bin"` — adding new locations the shell searches for programs.

## Key Takeaways

1. Hand-typed shell settings don't survive logout — persist them in the shell config file (`~/.bashrc` / `~/.bash_profile`), which the shell reads on startup.
2. `source ~/.bashrc` evaluates the file line by line in the current shell, applying changes without re-logging-in.
3. `PS1` renders the left prompt — the classic first dotfile tweak.
4. Dotfiles are hidden plain-text config files; collect them in one version-controlled folder and `ln -s` them into standard locations via an install script for portable setups.
5. Load-everything plugin frameworks bloat and slow the shell — add plugins one at a time.

---

## Startup modes: which configs actually run

Config files run in different orders — or get skipped entirely — depending on how the session started. Two axes decide:

| Axis | Options | Effect |
|---|---|---|
| **Login vs non-login** | Login (SSH session, console login) | runs the *profile* flow: `/etc/profile`, then `~/.bash_profile` (fallbacks `~/.bash_login`, `~/.profile`) |
| **Interactive vs non-interactive** | Interactive (human typing) vs scripted | interactive shells read `~/.bashrc`; **non-interactive shells skip user startup files** entirely — speed and clean, predictable runs |

Practical consequence: cron jobs and non-interactive scripts don't load your `.bashrc` — aliases vanish and `$PATH` can differ from your terminal. (The lecture notes loosely claimed non-login shells “load the profile flow” — inverted for bash; the table above is the accurate model.)

*(Enriched 2026-08-24 from Lecture 2 notes.)*
