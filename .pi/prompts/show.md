---
description: Show me a visualization for a concept (or let me play with one)
argument-hint: "<concept or question>"
---
[[FLOW:resume]]
The learner wants to see or play with: $ARGUMENTS

Load the `learning-viz` skill and run its visualization flow in this session: dispatch ONE foreground `viz` subagent with a `GATE:viz` envelope to author a declarative spec for this concept grounded in the current lesson context (its `sources` should quote the relevant source excerpts), then dispatch ONE foreground `viz-audit` with the spec AND `rendered_content` = the full turn draft (supporting words + the fenced spec), then emit ONE `[[TURN:viz]]` message containing that exact spec. Tag every message; write no `Learning System/` files. Discuss what the figure shows in the learner's own frame — never tell them to run a command; an interactive figure opens its own explorer.
