# Generative UI Reference

How the Tutor specs a widget, `ui-generator` builds it, and the Tutor audits and embeds it in
Antigravity Desktop. Read this before authoring any widget. The pedagogy rules live in
[pedagogy.md](./pedagogy.md) §7 and `AGENTS.md` §6; this file is the mechanics.

---

## 1. Mechanism (there is no `generative_ui()` tool)

Antigravity's built-in `generative_ui` skill is **instructions, not a callable tool**. The
Tutor does not author the widget. It writes a **spec**; `ui-generator` turns that spec into an
artifact; the Tutor audits and embeds it:

1. The Tutor dispatches `ui-generator` with the spec (§3), including the conversation's
   artifact directory and a stable slug.
2. `ui-generator` writes **one self-contained `.html` file** into that directory, marks it
   user-facing, and returns `UI_GENERATOR_RECEIPT` with the absolute path and SHA-256.
3. The Tutor dispatches `verifier` (`mode: "ui_audit"`) on that exact file and the exact prose,
   then emits a raw `<agent-embed src="file:///...">` tag in the reply.

Writing the file without the embed renders nothing; the embed without a valid, audited file
renders a broken frame. Do both in the same turn. The Tutor never writes the HTML itself.

## 2. Artifact directory

The artifact directory is the current conversation's Antigravity brain folder — **not** the
learning-system repository, not `Learning System/`, not `Knowledge Wiki/`:

- App: `~/.gemini/antigravity/brain/<conversation-id>/`
- CLI: `~/.gemini/antigravity-cli/brain/<conversation-id>/`

Resolve it from the live session (or from the path the environment reports). Never hardcode a
conversation id into a file or a lesson note. If the artifact directory cannot be resolved, do
not guess: fall back to a Mermaid diagram (see §9).

`ui-generator` writes it with the `write_to_file` tool and:

```
ArtifactMetadata: { UserFacing: true, Summary: "<one line describing the widget>" }
```

One widget = one file. The Tutor picks a stable, descriptive slug (for example
`pca-variance-knob.html`) and passes it in the spec. Never write widget source into the
learning repository.

## 3. Tutor → ui-generator spec

The Tutor owns the pedagogy; the generator only implements. Dispatch `ui-generator` with:

```
mode: 'widget'
artifact_dir: '/home/<user>/.gemini/antigravity/brain/<conversation-id>'
slug: 'pca-variance-knob'
stage: 'triage | attack-mechanism | attack-counterexample | attack-perturbation | attack-source_clash | attack-sabotage | attack-synthesis | graduation-synthesis | review_repair'
spec: {
  "idea": "<the one thing the widget makes visible>",
  "mechanism": "<what moves when each control changes, and in which direction>",
  "controls": [{"id": "...", "kind": "slider|select|input", "range": "...", "default": "..."}],
  "prediction": {"prompt": "<exact learner-facing wording>", "accepts": "number|choice|coordinates"},
  "reveal": "<what is drawn after commitment, overlaid against the prediction>",
  "values": ["<every grounded number, unit, and label, or 'illustrative'>"],
  "constraints": "<anything the widget must not show or name>"
}
```

A vague spec ("make it interactive") is a defect: the generator must not guess the mechanism,
the prediction wording, or the values. If the spec is incomplete, the generator returns
`UI_GENERATOR_RECEIPT` with `status: "NEEDS_SPEC"` and the Tutor fills the gap or degrades to
Mermaid.

```json
UI_GENERATOR_RECEIPT: {
  "status": "OK",
  "widget_file": "/absolute/path/widget.html",
  "sha256": "<sha256 of the written file>",
  "prediction_gate": "commit-before-reveal",
  "summary": "one line",
  "missing": []
}
```

## 4. Embed syntax

```
<agent-embed src="file:///home/<user>/.gemini/antigravity/brain/<conversation-id>/<slug>.html"></agent-embed>
```

Hard rules:

- Raw text, never inside a code fence.
- Exactly one attribute: `src`.
- Absolute `file:///` URL (three slashes) pointing at the audited file.
- Never set `height` (it is ignored); do not wrap the tag in HTML you author.
- One short sentence of context before the tag, then the learner-facing instruction. The prose
  is part of the audited draft.
- The inline viewport is about 500px tall. Keep the widget compact enough to fit without the
  learner scrolling the frame.

## 5. HTML contract

- `<!DOCTYPE html>`, one file, everything inline.
- The **only** allowed external resource is the Antigravity Tailwind build:
  `<script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>`.
- Inline `<style>` and `<script>` are allowed; no other CDN, remote font, remote image, or
  network fetch. Inline SVG or `data:` URIs only.
- `body` is transparent and theme-aware: `class="bg-transparent text-[var(--foreground)] antialiased p-5"`.
- Wrap content in a card:
  `bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-xl p-5 shadow-sm`.
- Use Antigravity's semantic tokens instead of hardcoded colors: `--background`, `--content`,
  `--card`, `--sidebar`, `--border`, `--foreground`, `--muted-foreground`, `--placeholder`,
  `--primary`, `--primary-foreground`, `--secondary`, `--secondary-foreground`, `--accent`.
  Do **not** define `:root` fallbacks or hardcode `bg-slate-900` / `text-white`.
- Minimum text size is 12px (`text-xs`). No `text-[10px]` / `text-[11px]`.
- No `h-screen`, `min-h-screen`, `100vh`, or `height: 100%` on top-level containers — the frame
  is sized from content and collapses otherwise.
- For `<canvas>`, branch on `document.documentElement.classList.contains('light')` for colors.
- No random values: the same widget always renders the same initial state.
- KaTeX is available in the chat message, not guaranteed inside the widget frame. Render formulas
  in a widget as styled inline HTML/SVG (or a clear monospace expression), never by loading a
  KaTeX CDN.

## 6. Predict-Before-Render pattern

Every widget is a two-state machine:

1. **Setup state** — render the scenario, the controls, and the prediction input. The output
   canvas is hidden or visibly locked. Show a short instruction: *"Commit your prediction first."*
2. **Prediction committed** — validate the input, store it, then run the model and reveal the
   output.
3. **Reveal** — draw the true behavior and the learner's prediction in the same chart/space.
   Label both explicitly ("Predicted" / "Actual"). Show the delta when it is meaningful.
4. **Reset** — allow a new prediction without a page reload (reset the locked state and clear
   the output, not the setup).

Minimal skeleton:

```html
<button id="commit" class="rounded-md bg-[var(--primary)] text-[var(--primary-foreground)] px-3 py-2">
  Commit prediction
</button>
<canvas id="out" class="hidden mt-4"></canvas>
<script>
  let predicted = null;
  document.getElementById('commit').addEventListener('click', () => {
    predicted = Number(document.getElementById('prediction').value);
    document.getElementById('out').classList.remove('hidden');
    render(predicted); // draws Predicted vs Actual
  });
</script>
```

The gate is satisfied only when the reveal code cannot run before a committed prediction.
A slider that recomputes the output live, or a chart drawn on load, is `ISSUES`.

## 7. Grounding and size

- Every number, label, axis, unit, and table row comes from the lesson's sources or is an
  explicitly illustrative value that the prose flags as illustrative.
- One idea per widget: roughly ≤ 40 components, ≤ 8 series/columns, ≤ 200 chart points. A widget
  is a glance, not a dashboard.
- The widget must make the *instructed* idea obvious. Do not smuggle in a second concept.
- Never expose the answer the learner is about to be asked for. The prediction gate exists so
  they commit first; the prose must ask for the prediction before directing attention to the
  reveal.

## 8. Audit and gate binding

`ui-generator` writes the file **first** (the verifier run holds a read-only write lock). When
its `UI_GENERATOR_RECEIPT` returns `status: "OK"`, dispatch exactly one `verifier` with:

```
mode: 'ui_audit', widget_file: '<absolute path>', prose_draft: '<the exact turn: prose + <agent-embed> call>'
```

The verifier reads the file, checks the prediction gate, math, CSP, theme, sizing, and the
prose↔widget match, and returns:

```json
VERIFIER_RECEIPT: {
  "mode": "ui_audit",
  "verdict": "PASS",
  "widget_file": "/absolute/path/widget.html",
  "widget_sha256": "<sha256 of the audited file>",
  "issues": []
}
```

The turn gate binds the embed to that receipt: same absolute file path and the file's current
SHA-256. A modified file, a different path, a missing hash, a non-`ui_audit` receipt, or an
`ISSUES` verdict all block the turn. The hash binds the **file**; the verifier binds the **prose
it read**. If either the file or the surrounding prose changes, re-run `ui_audit` and re-embed
the audited version. Apply fixes silently.

## 9. Fallback chain

**widget → Mermaid → prose.**

- A static structure, flow, state, or causal chain is better as an inline Mermaid diagram.
- If a widget fails `ui_audit` twice, `ui-generator` returns `NEEDS_SPEC`/`ERROR`, or the
  artifact directory cannot be resolved, degrade to Mermaid and say what the diagram shows.
  Never ship an unaudited widget.
- In `review`, park the widget until the batch is graded. In `/solo`, never build or embed one.

## 10. Do not

- Do not create a workspace skill named `generative_ui` (it would shadow the builtin).
- Do not write widget HTML in the Tutor session: only `ui-generator` writes artifacts.
- Do not write widgets into `Learning System/`, `Knowledge Wiki/`, or `.tmp/`.
- Do not describe a widget you did not verify, and never expose audit mechanics to the learner.
- Do not use a widget to decorate a sentence or to restate a formula the prose already carries.
