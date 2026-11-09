# Session — Gemini Shell Ingest (xargs, curl, jq)

- **Date:** 2026-08-05
- **Topic:** MIT Missing Semester Exercises 13–16 via Gemini tutoring (Gemini notebook: https://gemini.google.com/app/3b1807d0dd75591c)
- **Type:** Ingest (not review)
- **Concepts added (3):** xargs, curl, jq — all `developing`, `last_reviewed` 2026-08-05, `next_review` 2026-08-08/09, `Last Q Type` definitional
- **Concepts enriched (4):** find, grep, awk, Pipes (`|`) & Pipeline Composition — insight rows updated, `last_reviewed` set to today
- **Wiki page:** MIT Missing Semester — Shell (added xargs, curl, jq sections; enriched find, grep, awk, Pipes)
- **Key insights ingested:**
  - Top-extension pipeline: `find . -type f | awk -F. '{print $NF}' | sort | uniq -c | sort -nr | head -n 5` — `uniq -c` needs a prior `sort`, `sort -nr` orders by count desc, no-dot files hit NF=1 and print their whole filename
  - xargs bridges stream text → command arguments; default whitespace splitting breaks filenames with spaces; `-print0`/`-0` use the NUL byte, the only char never legal in a filename
  - grep is line-by-line: multiline HTML defeats `<h3>.*</h3>`; greedy matching collapses same-line repeats; `-c` counts; grep regex `*` ≠ glob `*`
  - jq: `.[] | select(.version > 6) | .name` inside one quoted program; `-r` for raw output; pipes outside quotes get eaten by bash
- **Open questions:** none new
