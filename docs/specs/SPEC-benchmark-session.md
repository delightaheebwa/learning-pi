# Spec: `benchmark-session` — declare reading, get the session brief

Module of: `docs/specs/CAPABILITY-MAP-reading-mode.md` (approved 2026-11-24)

## Objective

When the learner declares what they are about to read and attaches the source
text, pi returns one **session brief** and stops. The brief tells them where to
stop reading, what they must be able to *do* with the knowledge, the benchmark
they will be measured against (Sung #16: 5 low / 5 mid / 5 high questions,
aiming 90% / 80% / 70% from memory a week later), and the plain keyword list
they will connect and group themselves.

User story: "I say 'I'm reading the introduction chapter of The Psychology of
Money', attach the text, and I get back: stop here, here's what you'll do with
it, here are my 15 benchmark questions, here are the keywords. Then I go read."

## Behavior

The brief contains exactly four parts, in this order:

1. **Session scope.** Where to stop reading and why — sized to one sitting,
   chosen from the actual attached text (chapter/section boundaries), never
   invented.
2. **Outcome definition.** What the learner will actually *do* with the
   knowledge up to that point — phrased as performance, not coverage ("predict
   how an incentive change moves behavior", not "finish pages 1–24").
3. **Benchmark.** Exactly 15 questions: 5 low (recall/understand), 5 mid
   (apply), 5 high (evaluate/judge). All free-recall format — no MCQ, no
   true/false. Mid and high questions are written at the level and cue-style
   of real use ("retrieve in the way you will use it", Sung #42/#102): real
   scenarios, real decisions, not trivia recognition. Stated targets: 90% low /
   80% mid / 70% high, answered from memory.
4. **Keyword list.** The minimal necessary set of plain keywords from the
   scoped text. No groupings, no relations, no connections — the learner does
   the grouping and connecting themselves (the user was explicit about this,
   and Sung #96: structure you did not build is not yours).

Hard rules:

- **Grounding.** Every question and every keyword must be traceable to the
  attached source text. The gate withholds the brief if any item is
  unanchored — same standard as an ungrounded hole in the teach flow.
- **No teaching in the brief.** No answers, no explanations, no summaries of
  the content. Gist-level orientation only (Sung's priming: ~5–10 min worth,
  and "if you can explain processes after priming, you did it wrong").
- **No attachment, no brief.** If the learner names a book without attaching
  or pasting the text, pi asks for the text and stops. Questions are never
  generated from general knowledge of a title.
- The brief is one turn, then pi stops and waits for the learner to read.

## Commands

- Verify: `scripts/learn-check --no-load`; doc drift: `python3 scripts/check-docs`

## Project Structure

- `.pi/skills/learning-read/SKILL.md` — brief structure and rules
- `.pi/APPEND_SYSTEM.md` + gate verifier rules — grounding enforcement
- Tagged tests in the gate suites + `test/contract/check_learning_layer.py`

## Testing Strategy

- Gate test: a brief whose question or keyword lacks a source anchor is
  withheld (grounding check).
- Gate test: a brief that answers its own questions or summarizes the content
  is withheld.
- Gate test: declaring a reading without attached text yields a request for
  the text and no questions.
- Contract: an `R-*` invariant binds brief grounding + no-teaching to these
  tests.

## Boundaries

- Always: 15 questions exactly (5/5/5); free-recall format only; brief is a
  single turn.
- Ask first: changing the 5/5/5 counts or the 90/80/70 targets.
- Never: generate questions from general knowledge of a title; reveal
  mechanisms/answers in the brief; group the keywords for the learner.

## Success Criteria

1. A declared reading with attached text returns scope + outcome + 15 grounded
   questions + plain keywords, and stops.
2. An ungrounded question or keyword withholds the brief.
3. A declaration without text produces a text request, not questions.
4. Benchmark questions are usable as-is by `benchmark-retrieval` (persisted
   at session close with their level labels).

## Open Questions

- Whether the brief also states the retrieval dates (+1d/+1w/+1m) up front —
  default yes, one line.
