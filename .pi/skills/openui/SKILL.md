---
name: openui
description: 'Compose a turn as text plus the right visual automatically (never opt-in): inline Mermaid diagrams, a free-form HTML artifact, or a standalone verified interactive OpenUI widget with a bound ui-audit receipt. Triggers: a concept better shown than told, a relationship the learner can vary, a table of values, a chart, or a follow-up choice.'
---

# OpenUI: automatic answer composition

Choose the format for each turn inside the prompt: prose, a diagram, a widget, or a code artifact. Verify it like any other gated content. This is automatic, never opt-in.

## Choose the format for this turn

| The turn carries | Emit | Verifier |
| :--- | :--- | :--- |
| Most teaching, definitions, derivations, answers, hints, repairs, and plans | prose in a `[[TURN:claims]]` turn | `fact-check` |
| A shape or relationship a sentence can only describe | prose plus a ` ```mermaid ` fence inside the claims turn; it renders inline | `fact-check` for the hard facts |
| A small self-contained tool the learner reads as an app, such as a calculator or mini-simulator | prose plus a ` ```html ` fence inside the claims turn; it opens the Artifacts panel | `fact-check` for the hard facts |
| An interactive widget: chart, table, form, follow-up buttons, or a slider the learner varies | a standalone `[[TURN:ui]]` message with prose and one ` ```openui ` payload | `ui-audit` |

Use these rules of thumb:

- Prefer prose when the idea is a sentence. A figure for a sentence-concept is noise.
- Use Mermaid for structures, flows, and relationships such as graphs, sequences, and state machines. It renders inline and is fact-checked as prose. Its numbers are hard facts.
- Use an OpenUI widget when the learner should interact: vary a parameter, pick from a table, answer through a form, or tap a follow-up. The widget renders below the prose.
- Use an HTML artifact only for a genuinely free-form mini-app. It opens in the side panel.
- A ` ```openui ` fence is its own turn. Never put it inside a claims or none turn. The gate withholds that with `UI_REQUIRES_OWN_TURN`.
- Solo flows show no widget. The gate withholds `[[TURN:ui]]` with `SOLO_NO_AIDS`.
- In a review, park a widget until grading is done. Never interrupt the due queue.

## The widget flow

1. **Author the payload.** Write OpenUI Lang. The line `root = Card([...])` must come first. Define every other name once and make it reachable from `root`. Arguments are positional. Write `TextContent("Title", "large")`, not `TextContent(text: "Title")`.
2. **Predict before render.** Render the setup, but lock or hide the output canvas: the curve, the result, and the final state. Require a committed prediction, such as typed input, a selection, or coordinates, before anything runs. Only then render the true behaviour overlaid against the prediction, labelled Predicted versus Actual. A widget that renders its output on load, or whose reveal can run without a prediction, gets `ISSUES`. If the prediction was wrong, the next turn explains the delta between the learner's mental renderer and reality. Ask for the prediction in the prose before directing attention to the reveal.
3. **Assemble the turn.** Send `[[TURN:ui]]`, then supporting prose of 1 to 3 sentences, then one ` ```openui ` fence with the payload, then optional closing prose.
4. **Verify.** Dispatch one foreground `ui-audit` with this envelope:

   `{"gate":"ui_audit","concept":"…","instructed":"what the widget must make obvious","payload":"<the exact OpenUI Lang source>","rendered_content":"the full turn draft, supporting words plus the fenced payload","sources":[{"label","url?","excerpt?","file?"}],"context":"…"}`

   On `ISSUES`, fix the draft and re-dispatch the materially corrected version until the verifier returns `PASS`. Any severity blocks. There is no cycle cap.
5. **Emit unchanged.** Send the audited draft as `[[TURN:ui]]`. The bridge extracts the ` ```openui ` fence, wraps it in the OpenUI HTML shell with the self-hosted pinned bundle, `iframe:height`, and the `sendPrompt` bridge, then delivers it as an embed below the prose. Talk about what the widget shows, such as "drag the learning rate past 0.5 and watch it overshoot". The widget is already rendered.

## Visual plan on every substantive turn

Include `visual_plan` in every substantive `fact-check` dispatch:

`{"kind":"prose|mermaid|widget|html|none","why":"<why this is the smallest format that carries the idea>","widget_file":"<path when kind is widget or html>"}`

The verifier flags `VISUAL_PLAN_MISSING` when no plan is declared. It flags `VISUAL_MISSED` when the draft carries a shape, a relationship, a parameter-to-outcome relation, or a multi-value comparison that prose cannot carry. Declaring `none` with a real reason is legal. Prose for a dynamic relationship is not.

No visual may preview the mechanism, the patched rule, or the qualitative outcome the learner is about to be asked for. Do not show a roadmap before triage.

Contract note: the gate binds on the inline `payload` and `rendered_content` fields of the `ui-audit` envelope. `visual_plan.widget_file` is an advisory routing hint for file-backed artifacts only. No gate code reads it.

## Authoring OpenUI Lang

Each statement is `identifier = Expression`. An expression is a string, number, boolean, null, array, object, or `TypeName(arg1, arg2, …)`. The entry point is `root = Card(...)`.

Common components:

- Layout and containers: `Card(children[])`, the only container, plus `CardHeader(title?, subtitle?)`, `Separator(orientation?, decorative?)`, `Tabs(items)`, `Accordion(items)`, `Steps(items)`, `SectionBlock(sections, isFoldable?)`, and `Carousel(children[][])`. There is no `Stack`.
- Text and media: `TextContent(text, size?)`, `MarkDownRenderer(textMarkdown, variant?)`, `Callout(variant, title, description)`, `CodeBlock(language, codeString)`, and `Image(alt, src?)`.
- Data: `Table(columns: Col[])`, `Col(label, data[], type?)`, `BarChart(labels[], series, variant?, xLabel?, yLabel?)`, `LineChart(...)`, `AreaChart(...)`, `PieChart(labels[], values[], variant?)`, `ScatterChart(datasets, …)`, `Series(category, values[])`, `Point(x, y, z?)`, `RadarChart`, `HorizontalBarChart`, and `SingleStackedBarChart`. The full set is in the bundle.
- Input: `Form(name, buttons, fields?)`, `FormControl(label, input, hint?)`, `Input(name, placeholder?, type?, rules?, value?)`, `TextArea(...)`, `Select(name, items, …)`, `DatePicker`, `Slider(name, variant, min, max, step?, defaultValue?, label?)`, `CheckBoxGroup`, `RadioGroup`, and `SwitchGroup`.
- Actions: `Button(label, action?, variant?)`, `Buttons(buttons, direction?)`, `Action([@ToAssistant("…"), @OpenUrl("…")])`, `FollowUpBlock(items)`, `FollowUpItem(text)`, and `TagBlock(tags)`.

Hard widget rules:

- Use no external assets, no network, and no code. No `Image(src:"http…")`, no remote fonts, no `<script>`, and no data fetched at render time. Keep everything inline. `Image` takes a `data:` URI at most, and preferably no image at all.
- Keep it small. One widget, roughly 40 components or fewer, 8 series or columns or fewer, and 200 chart points or fewer. A widget is a glance, not a dashboard.
- Keep it grounded. Take every number, label, and value from the lesson sources. Never invent precise empirical figures. If a value is illustrative, say so in the prose.
- Make follow-ups carry the choice. Clicking a `FollowUpItem` sends its text as the learner's next message, so it must name the selected values. Write `FollowUpItem("Show the derivative of x² at x = 3")`, not `FollowUpItem("Yes")` or `FollowUpItem("Tell me more")`.
- Keep it deterministic. The same payload renders the same thing. No randomness.
- Use one widget per turn. A second figure is a second turn.

## Composition patterns

When the topic rewards exploration, compose one small surface instead of a single element:

- **Summary and chart.** Use one root `Card` with a `CardHeader`, a one-line `TextContent` or `Callout`, one chart such as `BarChart` or `LineChart`, and optionally a `Table` for exact values. Pair the chart with the one number that matters. Do not stack every chart the data could support.
- **Progressive disclosure.** Use `Tabs` for parallel views such as overview, detail, and edge cases. Use `Accordion` for optional depth and `SectionBlock(sections, true)` for a long appendix. Default to the summary. Put depth on demand. Never hide the idea being taught.
- **Form to one follow-up.** Put the fields in a `Form` with one submit `Button`. The shell appends the submitted values to the message as `Form data:`, or as `Form data (<name>):` when the `Form` is named. The learner answers once and the next turn receives every choice.
- **Comparison.** Put the two options in one `Table`, or in two nested `Card`s inside the single root `Card` below one `CardHeader`. Keep columns and units identical so the difference is the only variable.
- **Drill-down.** Use `FollowUpBlock` items that name the selected value, so each click opens a narrower explanation.

State does not survive a reload. The payload is re-parsed, so tabs, sliders, and form entries reset. Anything the learner must keep has to ride in the follow-up text. The iframe follows the OS light and dark preference. Do not assume a white background.

## Hard rules

- The emitted ` ```openui ` payload must be byte for byte the payload the `ui-audit` audited. The gate binds on the payload's canonical text. Copy it verbatim and do not reformat by hand.
- The gate does not separately fact-check a `[[TURN:ui]]` turn. `ui-audit` owns both the payload and the supporting prose, so ground every number in the sources you pass it.
- Never show gate internals to the learner. That includes receipts, verifiers, and gate codes. If a turn is withheld, fix it silently and re-emit clean content.
