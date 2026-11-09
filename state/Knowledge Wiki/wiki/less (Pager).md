<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# less — The Terminal Pager

> Source: handwritten lecture notes, Monday 2026-08-24. Expanded lightly from standard Unix knowledge; pairs with the inspect-first `curl` pattern in [[MIT Missing Semester — Shell]].

**`less`** is a terminal **pager**: it displays a text file or command output one screenful ("page") at a time, so long content waits for you instead of scrolling past. Quit with `q`; navigate with arrows/PageUp/PageDown; search within the text with `/pattern`.

## Why `less` beats `more` and text editors

- Unlike the older **`more`** utility (and unlike text editors), `less` does **not load the entire file into memory** before opening it — it reads lazily, only the portion you are actually viewing.
- That makes it extremely fast and memory-efficient on massive log or configuration files: `less /var/log/huge.log` opens instantly at any file size, because the whole file is never read up front.
- Editors must slurp and parse the whole document before showing anything; `less` never does.

## Using it

```bash
less huge.log          # view a file, one page at a time
some-command | less    # paginate ANY command output
```

Typical jobs: reading long logs, browsing `man` pages (man renders through a pager), and inspecting a downloaded script before executing it:

```bash
curl -fsSL URL -o install.sh && less install.sh && bash install.sh
```

Related: [[MIT Missing Semester — Shell]] · [[MIT Missing Semester — Command-line Environment]]

## Sources

- https://en.wikipedia.org/wiki/Less_(Unix)
- https://www.greenwoodsoftware.com/less/
