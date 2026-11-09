# REVIEW: GCC Compilation Stages — 2026-08-20

## Review Info
- **Date:** 2026-08-20
- **Concept:** GCC Compilation Stages
- **Last Reviewed:** 2026-08-17
- **Review Interval:** 3d (due)
- **Status Before Review:** developing

## Assistant's Prompt
> Definitional (alternation from last discriminative): "Walk me through GCC's four compilation stages in order — name each, the flag that runs only that stage, and the output. Then one scenario where you'd deliberately stop early."

## Your Answer
- **Confidence:** confident
- **Answer:** Preprocessing(`-r`) → Compilation proper(`-c`) → Linking(`-o`) → Execution(`-e`). Output is a binary executable. Stop at compilation when other Makefile files still need converting to object files.

## Assistant's Evaluation
- **Result:** Needs More Work
- **Feedback:** Flags attached to wrong stages. `-E` = Preprocessing (`-i` text). `-S` = Compilation proper (`.s` assembly). `-c` = Assembly (assembler → `.o` object). Linking = final no-flag pass combining `.o`s into the executable (`-o` just names output, `-e` not a stage flag). Only the link step produces the executable; earlier stages produce `.i`/`.s`/`.o`. The "stop early" scenario was correct in spirit: stop at `-c` to produce object files so Make recompiles only changed `.c` (split compilation).
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-20
- **next_review:** 2026-08-27 (held at 7d)
- **Last Q Type:** definitional
- **notes:** Held — stage→flag mapping wrong (`-E` preprocess, `-S` compile→asm, `-c` assembler→`.o`, link=final no-flag).

## Queue / Deferred Note
- **Queue position:** active

## Key Takeaway
> Each stage = one flag that stops there (`-E`, `-S`, `-c` produces the `.o`); linking is the no-flag final pass to the executable.
