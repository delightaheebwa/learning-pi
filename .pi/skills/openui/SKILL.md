---
name: openui
description: 'Compose a turn as text plus the right visual automatically (never opt-in): inline Mermaid diagrams, a free-form HTML artifact, or a standalone verified interactive OpenUI widget with a bound ui-audit receipt. Triggers — a concept better shown than told, a relationship the learner can vary, a table of values, a chart, or a follow-up choice.'
---

# OpenUI — automatic answer composition

Learning answers are not walls of white text. **Decide the format per turn in-prompt** — prose,
a diagram, a widget, or a code artifact — and verify it like any other gated content. This is
**automatic, never opt-in**: the learner does not ask for a widget any more than they ask for a
paragraph.

## Which format for THIS turn

| The turn is… | Emit… | Verifier |
| --- | --- | --- |
| Most teaching, definition, derivation, answer, hint, repair, plan | prose in a `[[TURN:claims]]` turn | `fact-check` |
| A shape/relationship a sentence can only describe | prose + a ` ```mermaid ` fence **inside the claims turn** (renders inline) | `fact-check` (the numbers are hard facts) |
| A small self-contained tool the learner reads as an app (calculator, mini-simulator) | prose + a ` ```html ` fence **inside the claims turn** (opens the Artifacts panel) | `fact-check` (the numbers are hard facts) |
| An interactive widget: chart, table, form, follow-up buttons, slider the learner varies | a **standalone** `[[TURN:ui]]` message with prose + ONE ` ```openui ` payload | `ui-audit` |

Rules of thumb:

- **Prefer prose** when the idea is a sentence. A figure for a sentence-concept is noise.
- **Mermaid** for structure/flow/relationships (graphs, sequence, state). It renders inline and is
  fact-checked as prose — its numbers are hard facts like any other.
- **OpenUI widget** when the learner should *interact*: vary a parameter, pick from a table, answer
  through a form, or tap a follow-up. The widget is an embed rendered **below** the prose.
- **HTML artifact** only for a genuinely free-form mini-app; it opens in the side panel.
- A ` ```openui ` fence is **its own turn** — never inside a claims/none turn (the gate withholds that:
  `UI_REQUIRES_OWN_TURN`).
- **Solo (closed-book) flows show no widget**: a `[[TURN:ui]]` turn is withheld (`SOLO_NO_AIDS`).
- In a review, park a widget until grading is done; never interrupt the due queue.

## The widget flow (standalone, verified)

1. **Author the payload.** Write OpenUI Lang: `root = Card([...])` MUST be the first line; every
   other name is defined once and reachable from `root`. Arguments are positional
   (`TextContent("Title", "large")`, never `TextContent(text: "Title")`).
2. **Assemble the turn.** `[[TURN:ui]]` + the supporting prose (1–3 sentences up front, then what to
   notice) + a single ` ```openui ` fence holding the payload + optional closing prose.
3. **Verify.** `dispatch` ONE foreground `ui-audit`:
   `{"gate":"ui_audit","concept":"…","instructed":"what the widget must make obvious","payload":"<the exact OpenUI Lang source>","rendered_content":"the full turn draft (supporting words + the fenced payload)","sources":[{"label","url?","excerpt?","file?"}],"context":"…"}`.
   On `ISSUES`: fix and re-dispatch the **materially corrected** draft until the verifier returns
   PASS — no cycle cap, any severity blocks.
4. **Emit unchanged.** Send the audited draft as `[[TURN:ui]]`. The bridge extracts the ` ```openui `
   fence, wraps it in the OpenUI HTML shell (self-hosted pinned bundle + `iframe:height` +
   `sendPrompt` bridge), and delivers it as an embed **below** the prose. Talk about **what it shows**
   ("drag the learning rate past 0.5 and watch it overshoot") — the widget is already rendered.

## OpenUI Lang (authoring rules)

Each statement is `identifier = Expression`. Expressions are strings, numbers, booleans, null,
arrays, objects, or `TypeName(arg1, arg2, …)`. The entry point is `root = Card(...)`.

Common components (the full set is in the bundle):

- Layout/containers: `Card(children[])` (the only container — no `Stack`), `CardHeader(title?, subtitle?)`,
  `Separator(orientation?, decorative?)`, `Tabs(items)`, `Accordion(items)`, `Steps(items)`,
  `SectionBlock(sections, isFoldable?)`, `Carousel(children[][])`.
- Text/media: `TextContent(text, size?)`, `MarkDownRenderer(textMarkdown, variant?)`,
  `Callout(variant, title, description)`, `CodeBlock(language, codeString)`, `Image(alt, src?)`.
- Data: `Table(columns: Col[])`, `Col(label, data[], type?)`,
  `BarChart(labels[], series, variant?, xLabel?, yLabel?)`, `LineChart(...)`, `AreaChart(...)`,
  `PieChart(labels[], values[], variant?)`, `ScatterChart(datasets, …)`, `Series(category, values[])`,
  `Point(x, y, z?)`, `RadarChart`, `HorizontalBarChart`, `SingleStackedBarChart`.
- Input: `Form(name, buttons, fields?)`, `FormControl(label, input, hint?)`,
  `Input(name, placeholder?, type?, rules?, value?)`, `TextArea(...)`, `Select(name, items, …)`,
  `DatePicker`, `Slider(name, variant, min, max, step?, defaultValue?, label?)`,
  `CheckBoxGroup`, `RadioGroup`, `SwitchGroup`.
- Actions: `Button(label, action?, variant?)`, `Buttons(buttons, direction?)`,
  `Action([@ToAssistant("…"), @OpenUrl("…")])`, `FollowUpBlock(items)`, `FollowUpItem(text)`,
  `TagBlock(tags)`.

Hard widget rules:

- **No external assets, no network, no code.** No `Image(src:"http…")`, no remote fonts,
  no `<script>`, no data fetched at render time. Everything is inline data. `Image` takes a `data:`
  URI at most, and prefer no image at all.
- **Small.** One widget, roughly ≤ 40 components, ≤ 8 series/columns, ≤ 200 chart points. A widget is
  a glance, not a dashboard.
- **Grounded.** Every number, label, and value comes from the lesson sources. Never invent precise
  empirical figures; if a value is illustrative, say so in the prose.
- **Follow-ups carry the choice.** Clicking a `FollowUpItem` sends its text as the learner's next
  message, so it must name the selected values explicitly — `FollowUpItem("Show the derivative of
  x² at x = 3")`, never `FollowUpItem("Yes")` or `FollowUpItem("Tell me more")`.
- **Deterministic.** Same payload renders the same thing; no randomness.
- **One widget per turn.** A second figure is a second turn.

## Composition patterns

When the topic rewards exploration, compose one small surface instead of a single element:

- **Summary + chart**: a single root `Card` with a `CardHeader`, a one-line `TextContent` or
  `Callout` summary, one chart (`BarChart`/`LineChart`), and optionally a `Table` for exact values.
  Pair the chart with the one number that matters — do not stack every chart the data could support.
- **Progressive disclosure**: `Tabs` for parallel views (overview / detail / edge cases),
  `Accordion` for optional depth, `SectionBlock(sections, true)` for a long appendix. Default to the
  summary; depth on demand. Never hide the idea being taught.
- **Form → one follow-up**: put the fields in a `Form` with one submit `Button`. The shell appends
  the submitted values to the message as `Form data:` (or `Form data (<name>):` when the `Form` is
  named), so the learner answers once and the next turn receives every choice.
- **Comparison**: put the two options in one `Table`, or in two nested `Card`s inside the single root
  `Card`, below one `CardHeader`, with identical columns/units so the difference is the only variable.
- **Drill-down**: `FollowUpBlock` items that name the selected value, so each click opens a narrower
  explanation.

State does not survive a reload: tabs, sliders, and form entries reset because the payload is
re-parsed. Anything the learner must keep has to ride in the follow-up text. The iframe follows the
OS light/dark preference; do not assume a white background.

## Hard rules

- The emitted ` ```openui ` payload must be **byte-for-byte** the payload the `ui-audit` audited (the
  gate binds on the payload's canonical text): copy it verbatim, do not reformat by hand.
- A `[[TURN:ui]]` turn is **not** separately fact-checked — `ui-audit` owns both the payload and the
  supporting prose, so ground every number in the sources you pass it.
- Never surface gate/tooling internals (receipts, verifiers, gate codes) to the learner. If a turn is
  withheld, fix it silently and re-emit clean content.
