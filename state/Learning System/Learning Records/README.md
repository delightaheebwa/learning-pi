# Learning Records

ADR-style records. Each one captures demonstrated understanding, disclosed prior
knowledge, corrected misconceptions, or a mission shift. The `learning-teach`
skill reads these records as its ZPD signal to pick what to teach next.

## Naming

`0001-<dash-case-name>.md`, incrementing by one. Scan for the highest number
first.

## When to write one

1. The learner demonstrates genuine understanding of something non-trivial,
   through a retrieval check pass and a Feynman explain-back. This sets the new
   floor.
2. The learner discloses prior knowledge during the probe ("I already know X").
   Record it with the claimed depth.
3. A misconception is corrected. This trigger has the highest value, because it
   predicts future stumbling blocks.
4. The mission shifts. Cross-link to `../MISSION.md` and update that file after
   you confirm the change with the user.

Coverage alone is not a trigger, and neither is a duplicate glossary term.

## Format

```md
# <Short title>

{1–3 sentences: what was learned (or established), why it matters for future sessions.}

**Status:** active | superseded by LR-NNNN
**Evidence:** {how it was demonstrated — incl. highest Bloom level reached}
**Implications:** {what this unlocks or rules out next}
```

The `Status`, `Evidence`, and `Implications` fields are optional. Add each one
only when it adds value. Mark a record superseded rather than deleting it.
