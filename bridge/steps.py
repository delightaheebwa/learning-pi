"""Render pi turn steps as Open WebUI `<details>` blocks.

Open WebUI (>= 0.8.11) turns a top-level `<details>` block in assistant content
into a collapsible row, and consecutive `type="tool_calls"` / `type="reasoning"`
blocks into one grouped "Explored …" row (`MarkdownTokens.svelte` +
`ConsecutiveDetailsGroup.svelte`). That is the closest native equivalent of the
pi terminal's live action trace, and it survives transcript replay because it is
ordinary message content.

The parser is strict (v0.12.2 `src/lib/utils/marked/extension.ts`):

* the opening `<details …>` tag must sit at the start of a line and be followed
  by a newline;
* attributes must be `key="value"` — a raw `"` inside a value ends the value, so
  JSON is HTML-escaped (`&quot;`);
* `<summary>…</summary>` must be on its own line to be lifted out;
* the block must be complete: a half-written block renders as raw HTML.

Every block this module returns therefore ends with a blank line, so the next
block starts a fresh line and the final prose is separated from the trace.

Display policy (the learner-facing half of `B-steps-metadata-only`):

* a tool step shows its name, a truncated JSON of its `args`, its status and its
  duration — **never** its result in a learning flow;
* a thinking step shows its duration in a learning flow ("Thought for Ns") and
  its text only in a general (non-learning) chat;
* `message_update` delta text never enters a step (see `stream.py`).
"""
from __future__ import annotations

import html
import json

# A step card is a preview, not a log dump. Arguments are truncated because a
# tool call's input can incidentally carry draft prose (an editor writing the
# withheld answer); results are omitted entirely in learning flows.
ARGS_PREVIEW = 200
RESULT_PREVIEW = 800


def _escape(value: str) -> str:
    r"""Escape one attribute value for Open WebUI's `(\w+)="(.*?)"` parser."""
    return html.escape(value, quote=True)


def _json_attr(value) -> str:
    """Compact, single-line JSON of a tool's args, escaped and truncated."""
    try:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        text = str(value)
    if len(text) > ARGS_PREVIEW:
        text = text[:ARGS_PREVIEW].rstrip() + "…"
    return _escape(text)


def _neutralize(text: str) -> str:
    """Defuse nested `<details>` sequences so they cannot end our block early.

    The tokenizer counts `<details` occurrences to find the matching close, and
    Open WebUI decodes entities before lexing, so escaping would not help. A
    backslash keeps the sequence out of the tokenizer while markdown still
    renders it as the literal tag name.
    """
    if not text:
        return ""
    return text.replace("<details", "<\\/details")


def _body(text: str, limit: int = RESULT_PREVIEW) -> str:
    text = _neutralize(text or "")
    if len(text) > limit:
        text = text[:limit].rstrip() + "…"
    return text


def format_seconds(duration) -> str:
    try:
        return f"{max(0.0, float(duration)):.1f}s"
    except (TypeError, ValueError):
        return "0.0s"


def render_tool_step(step: dict, *, learning: bool = True) -> str:
    """One `type="tool_calls"` block. Body/result only outside learning flows."""
    name = str(step.get("name") or "tool")
    dur = format_seconds(step.get("duration"))
    # Open WebUI's tool row labels come from `name` (the `<summary>` is ignored
    # for this type), so the duration rides along in the label.
    label = f"{name} · {dur}"
    error = step.get("status") == "error"
    done_attr = "" if error else ' done="true"'
    status_attr = ' status="failed"' if error else ""
    body = ""
    if not learning:
        body = _body(str(step.get("result") or ""))
    args = step.get("args")
    if args is None:
        args = {}
    return (
        f'<details type="tool_calls"{done_attr}{status_attr} '
        f'id="{_escape(str(step.get("id") or name))}" '
        f'name="{_escape(label)}" '
        f'arguments="{_json_attr(args)}">\n'
        f"<summary>{html.escape(label, quote=False)}</summary>\n"
        f"{body}\n"
        f"</details>\n\n"
    )


def render_thinking_step(step: dict, *, learning: bool = True) -> str:
    """One `type="reasoning"` block; learning flows show only the duration."""
    dur = format_seconds(step.get("duration"))
    body = "" if learning else _body(str(step.get("text") or ""))
    return (
        f'<details type="reasoning" done="true" duration="{_escape(dur)}">\n'
        f"<summary>Thought for {html.escape(dur, quote=False)}</summary>\n"
        f"{body}\n"
        f"</details>\n\n"
    )


def render_step(step: dict, *, learning: bool = True) -> str:
    """Render one completed step (a no-op for transient tool/thinking starts)."""
    kind = step.get("kind")
    if kind == "tool":
        return render_tool_step(step, learning=learning)
    if kind == "thinking":
        return render_thinking_step(step, learning=learning)
    return ""


def render_steps(steps, *, learning: bool = True) -> str:
    """Render every completed step of a turn, in stream order."""
    return "".join(render_step(s, learning=learning) for s in (steps or []))
