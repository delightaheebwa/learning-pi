---
description: Run an AI-free (closed-book) solo check
---
[[FLOW:solo]]
Run an AI-free solo check. This is a CLOSED-BOOK test of what the learner can do unaided: no hints, no teaching, no worked steps, no visualizations. The gate withholds any `[[TURN:claims]]` or `[[TURN:viz]]` message in this flow (`SOLO_NO_TEACHING` / `SOLO_NO_AIDS`), so teaching is impossible by construction.

First `dispatch` the `review-scout` agent to build the due queue (deterministic `ops.py queue`); its `queue` is authoritative — use it verbatim, and write each question from that entry's `question_type` + `source_excerpt`. Then ask the whole queue in ONE `[[TURN:quiz]]` message, quiz-audited like any batch (`questions_json` + `rendered_content` = the exact full batch text, emitted unchanged). Say in the intro that this is a solo check: notes, hints, and AI help are not allowed; the learner answers closed-book (paper is fine) and replies with final answers only.

During the check, do NOT teach, hint, or answer questions about the material — a `[[TURN:none]]` line reminding the learner this is a solo check is all that is allowed. If the learner asks for help, decline in one line and let them answer unaided.

When the learner replies, grade with ONE batched `grade-audit` (`items[]`, one entry per answer) and present the verifier's per-item `correct_verdict`. Then hand the durable writes to ONE `review-clerk` with a `REVIEW_WRITES` envelope that includes `"mode":"solo"` (so every attempt is recorded AI-free and feeds the independence gate and the `solid` tag), then `dispatch` ONE `review-session-audit` on the exact writes and fold both verdicts. You write no state yourself.

Begin every assistant message with a turn tag on its first line — `[[TURN:quiz]]` (the closed-book batch), `[[TURN:grade]]` (grading), or `[[TURN:none]]` (transitions). Never `[[TURN:claims]]` or `[[TURN:viz]]` — they are withheld. Dispatch each verifier once with `dispatch({ agent, task: { ...envelope... } })` (foreground) and wait for its verdict; never re-dispatch the same draft.
