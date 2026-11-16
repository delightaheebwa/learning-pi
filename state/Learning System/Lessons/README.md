# Lessons

Live teaching artifacts from the `learning-teach` skill. Each tangible-win unit
gets one markdown file, which the tutor writes after or during a teaching
walkthrough. The file is the durable record of the lesson, not the lesson's
source.

## Naming

`Lesson — <slug> — <YYYY-MM-DD>.md`

## Template

A lesson file contains these sections.

```md
# <Title>

**Track:** AIEFS · **Lesson:** <Phase X Lesson Y — Title> · **Status:** <in-progress (paused at Checkpoint N/M, mini K/L) | done> · **Language:** <Python | TypeScript | Rust>

## Core
One reasoning step per section (unconditional truth → motivated discovery; guided Socratic).
<i>Each step: what's unconditionally true, why anyone would try this, one step at a time.</i>

## Quiz
Two-tier: retrieval (Remember/Understand) + higher-order (Apply/Analyze/Evaluate). Fuzziness inferred by tutor.

## Glossary additions
→ push approved terms to `../GLOSSARY.md`

## Learning record
Link/pointer to `../Learning Records/<NNNN-slug>.md` (Feynman explain-back + Bloom level).

## Next steps
The next curriculum lesson (per CURRICULUM.md rotation).
```

Knowledge Wiki pages are written separately, never inline in lessons.
