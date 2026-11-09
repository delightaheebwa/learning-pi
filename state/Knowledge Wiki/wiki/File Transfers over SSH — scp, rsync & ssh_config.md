<!-- provenance: status=verified | source=https://missing.csail.mit.edu/2020/command-line/ ; https://man7.org/linux/man-pages/man1/scp.1.html ; https://man7.org/linux/man-pages/man1/rsync.1.html ; https://man7.org/linux/man-pages/man5/ssh_config.5.html | verified-by=fact-check-agent | date=2026-10-26 -->

# File Transfers over SSH — scp, rsync & ssh_config

> Source: Lecture 2 written notes (website, Fri 2026-08-21), cross-checked against MIT Missing Semester (Command-line Environment). Ingested 2026-08-24.

## scp — the simple copy

`scp src dest`, where either side may be `user@host:path`. A straightforward copy of files/directories over SSH; no awareness of what already exists.

*(Correction to the notes: they say “rsync builds on scp”. Inaccurate — rsync is an independent tool that **improves on** scp’s job; MIT phrases it “rsync improves upon scp”.)*

## rsync — delta-aware, resumable copying

Improvements over scp:

- **Skips identical files** — detects what already matches between source and destination and avoids re-copying (delta-transfer under the hood). Ideal for repeated syncs/backups.
- **Fine-grained control** over symlinks (copy the link or dereference to the real file) and permissions/owners kept intact.
- **Resumable:** the notes cite `-P`, which equals `--partial --progress` — keep partially transferred files and show progress, so an interrupted copy continues instead of restarting. (MIT’s page cites `--partial`; `-P` bundles it with the progress meter.)
- Syntax closely mirrors scp.

## ~/.ssh/config — declare hosts once

```ssh-config
Host myserver
    HostName remote.server.com
    User foobar
    IdentityFile ~/.ssh/id_ed25519
    Port 2222
```

Now `ssh myserver` — or `rsync file.txt myserver:` — expands to all those flags. Key advantage over shell aliases: this file is **not only read by `ssh`** — `scp`, `rsync`, `mosh`, etc. read it too and translate the settings into their corresponding flags.

Related: [[SSH — Public-Key Auth & Remote Commands]] · [[MIT Missing Semester — Shell Configuration & Dotfiles]]

## Sources

- https://missing.csail.mit.edu/2020/command-line/
- https://man7.org/linux/man-pages/man1/scp.1.html
- https://man7.org/linux/man-pages/man1/rsync.1.html
- https://man7.org/linux/man-pages/man5/ssh_config.5.html
