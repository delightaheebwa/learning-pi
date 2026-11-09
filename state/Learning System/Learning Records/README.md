# Learning Records

ADR-style records that capture demonstrated understanding, disclosed prior knowledge, corrected misconceptions, and mission shifts. They are the ZPD signal used by the `learning-teach` skill to pick what to teach next.

## Naming

`0001-<dash-case-name>.md`, incrementing by one (scan for the highest number first).

## When to write one (trigger)

1. **Demonstrated genuine understanding** of something non-trivial (retrieval check pass + Feynman explain-back) — sets the new floor.
2. **Disclosed prior knowledge** during the probe ("I already know X") — record it with the claimed depth.
3. **Misconception corrected** — highest value; predicts future stumbling blocks.
4. **The mission shifted** — cross-link to `../MISSION.md` and update it (confirm with user).

Not mere coverage. Not duplicate glossary terms.

## Format

```md
# <Short title>

{1–3 sentences: what was learned (or established), why it matters for future sessions.}

**Status:** active | superseded by LR-NNNN
**Evidence:** {how it was demonstrated — incl. highest Bloom level reached}
**Implications:** {what this unlocks or rules out next}
```

Optional: `Status` frontmatter (mark superseded rather than deleting), `Evidence`, `Implications` — only when they add value.