---
name: learning-viz
description: 'Show or let the learner play with a visualization during a lesson. Triggers — "show me", "visualize", "draw", "can I play with X", "what does that look like". Dispatches the viz subagent for a declarative spec, verifies it with viz-audit, and emits a standalone [[TURN:viz]] message.'
---

# Learning Viz

Visualizations are **opt-in, standalone, and verified**. A figure is its own `[[TURN:viz]]`
message — never a ` ```viz ` block inside a claims/transition turn (the gate withholds that:
`VIZ_REQUIRES_OWN_TURN`). The `viz-mode` extension renders the spec inline and, when the spec is
interactive, slides in an explorer overlay already running; the learner pokes at it and can talk
about what they saw.

## When

- The learner asks to see or play with something ("show me what that looks like", "draw the loss
  surface", "let me play with the learning rate"). This is the primary trigger for this skill.
- The Tutor may **offer** a figure in one short sentence at most once per mini-checkpoint ("want a
  picture of this?"). Generate only if the learner says yes. Never generate unprompted.
- In a `/review` session, **park it**: note the request, finish the review's grading, and offer the
  figure right after. Never interrupt grading or the due-queue flow.
- Scope is teach/resume only.

## Flow

1. **Author the spec.** `dispatch` ONE `viz` agent with a `GATE:viz` envelope. It
   returns a declarative spec (data + labels only — no code) plus what to look at:
   `{"gate":"viz","concept":"...","intent":"what the figure must make obvious","interactive":true|false,"lang":"...","sources":"source excerpts for the values shown","learner_words":"the learner's phrasing"}`.
   `dispatch({ agent: "viz", task: { ...envelope... } })` — `task` is the envelope **object**,
   never a JSON-encoded string.
2. **Assemble the turn.** Write the supporting words (1–3 sentences up front, then what to notice)
   around the spec: the message is `[[TURN:viz]]` + prose + a single ` ```viz ` fenced JSON spec
   (copy the spec **verbatim** from the viz agent) + prose. Supporting words are the Tutor's own
   voice and must be accurate — `viz-audit` checks them.
3. **Verify.** `dispatch` ONE `viz-audit` with the spec AND the full turn draft:
   `{"gate":"viz_audit","concept":"...","instructed":"...","spec":{...},"rendered_content":"the full turn draft (supporting words + fenced spec)","sources":[...]}`.
   On `ISSUES`: apply fixes and re-dispatch the **materially corrected** draft once (max 2 cycles).
   A `PASS_WITH_FLAGS` (lows only) is accepted silently. Never emit the turn without a passing,
   bound receipt.
4. **Emit.** Send the audited draft unchanged as `[[TURN:viz]]`. The `viz-mode` extension renders the
   figure and auto-opens the explorer for interactive specs. Talk **about the content** ("push the
   rate past 0.5 and watch it overshoot") — never tell the learner to run a command; the overlay is
   already open. Then pause and invite questions as usual.

## Hard rules

- The emitted fenced spec must be byte-for-byte the audited spec (the gate binds on the spec's
  canonical JSON): do not reformat numbers or reorder fields by hand — copy what `viz` returned.
- One figure per request. Keep supporting words to about one screen; the figure carries the detail.
- No picture for a concept that a sentence handles better; a figure is for a mechanism, a shape,
  a relationship the learner can vary, or a worked-example geometry.
- A `[[TURN:viz]]` turn is not separately fact-checked — `viz-audit` owns both the spec and the
  supporting words, so ground every number in the sources the `viz` agent was given.
