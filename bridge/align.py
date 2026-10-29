"""Map one Open WebUI transcript turn onto pi's active session branch.

Open WebUI only posts the current transcript and (with the headers configured)
the chat id. It does not say whether the user typed a new message, edited an
older one, deleted messages, clicked Regenerate, or clicked Continue. Those
actions differ in the transcript's shape, and getting them wrong makes pi answer
with context the learner no longer sees.

This module is pure: it compares the Open WebUI user messages with pi's own user
messages (from `get_fork_messages`) and returns the prompt to send plus the pi
entry to fork from, if any. The HTTP layer executes the plan.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

# A Continue click has no new user message. The bridge sends a marked prompt so
# the model knows to extend the previous turn; alignment filters the marker out
# so it is never mistaken for a user message the learner can see or edit.
CONTINUATION_PREFIX = "[[BRIDGE:CONTINUE]]"
CONTINUATION_PROMPT = CONTINUATION_PREFIX + " Continue from where you left off."


@dataclass(frozen=True)
class TurnPlan:
    """What to send to pi, and which branch to fork first (if any)."""

    prompt: str
    fork_entry_id: Optional[str] = None
    fork_last: bool = False
    continuation: bool = False
    reason: str = ""


def _same_user(open_text: str, pi_text: str) -> bool:
    """Whether an Open WebUI user message is the one pi actually received.

    Open WebUI may replace the user message with a RAG context envelope (the
    default template does not keep the original query verbatim) or prefix
    `<attached_files>` tags. Treat those envelopes as the same turn by position;
    the length-based cases below still fork correctly when an earlier message
    was edited.
    """
    left = (open_text or "").strip()
    right = (pi_text or "").strip()
    if left == right:
        return True
    if not left or not right:
        return False
    if any(marker in right for marker in ("<context>", "### Task:", "<source", "<attached_files>")):
        return True
    if min(len(left), len(right)) >= 4 and (left in right or right in left):
        return True
    return False


def _common_prefix(open_users: Sequence[str], pi_users: Sequence[str]) -> int:
    limit = min(len(open_users), len(pi_users))
    index = 0
    while index < limit and _same_user(open_users[index], pi_users[index]):
        index += 1
    return index


def pi_user_messages(pi_messages) -> list[tuple[str, str]]:
    """`(entryId, text)` for real user messages, dropping Continue markers."""
    out = []
    for message in pi_messages or []:
        if not isinstance(message, dict):
            continue
        text = message.get("text")
        entry = message.get("entryId")
        if not isinstance(text, str) or not isinstance(entry, str) or not entry:
            continue
        if text.startswith(CONTINUATION_PREFIX):
            continue
        out.append((entry, text))
    return out


def plan_turn(
    open_users: Sequence[str],
    pi_messages,
    *,
    trailing_assistant: bool,
    answered: bool = False,
    last_user_text: str = "",
    pi_known: bool = True,
) -> TurnPlan:
    """Decide the next prompt and optional fork for one posted transcript.

    `open_users` is the transcript's user-message text in order;
    `trailing_assistant` is true for Open WebUI's Continue request (the posted
    conversation ends with the assistant message being extended). `pi_known`
    is false when `get_fork_messages` failed; the caller then falls back to the
    old last-message heuristic.
    """
    users = list(open_users)
    last = users[-1] if users else ""

    if not pi_known:
        if trailing_assistant:
            return TurnPlan(CONTINUATION_PROMPT, continuation=True, reason="continue-unverified")
        return TurnPlan(
            last,
            fork_last=bool(answered and last and last == last_user_text),
            reason="fallback",
        )

    pi_users = pi_user_messages(pi_messages)
    pi_texts = [text for _, text in pi_users]
    common = _common_prefix(users, pi_texts)

    if trailing_assistant:
        if common < len(users):
            # The learner edited/added a user message and then continued; answer
            # that message instead of extending a turn pi does not have.
            fork = pi_users[common][0] if common < len(pi_users) else None
            return TurnPlan(last, fork_entry_id=fork, reason="continue-after-change")
        if len(users) < len(pi_users):
            # Open WebUI no longer has pi's later turns; drop them before
            # extending the visible assistant message.
            return TurnPlan(
                CONTINUATION_PROMPT,
                fork_entry_id=pi_users[len(users)][0],
                continuation=True,
                reason="continue-after-delete",
            )
        return TurnPlan(CONTINUATION_PROMPT, continuation=True, reason="continue")

    if common == len(users) == len(pi_users):
        # Regenerate: the same user messages, posted again with the answer gone.
        return TurnPlan(
            last,
            fork_entry_id=pi_users[-1][0] if pi_users else None,
            reason="regenerate",
        )
    if common == len(pi_users) and common == len(users) - 1:
        # A normal new user message after the previous turn.
        return TurnPlan(last, reason="new-turn")
    if common < len(users):
        # An edited/replaced message (or a new message after a deletion) at
        # `common`; fork off the pi turn it replaces.
        fork = pi_users[common][0] if common < len(pi_users) else None
        return TurnPlan(last, fork_entry_id=fork, reason="edit")
    if common == len(users) < len(pi_users):
        # Open WebUI truncated after a user message; re-answer that message.
        return TurnPlan(
            last,
            fork_entry_id=pi_users[common - 1][0] if common > 0 else None,
            reason="truncate",
        )
    return TurnPlan(last, reason="fallback")
