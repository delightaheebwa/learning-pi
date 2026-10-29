"""Unit tests for transcript -> pi branch alignment (no pi, no HTTP)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bridge.align import (  # noqa: E402
    CONTINUATION_PREFIX,
    CONTINUATION_PROMPT,
    plan_turn,
    pi_user_messages,
)


def _pi(*texts):
    return [{"entryId": f"e{i + 1}", "text": text} for i, text in enumerate(texts)]


class TestAlignment(unittest.TestCase):
    def test_new_turn_appends_without_forking(self):
        plan = plan_turn(
            ["one", "two"], _pi("one"),
            trailing_assistant=False, answered=True, last_user_text="one",
        )
        self.assertEqual(plan.prompt, "two")
        self.assertFalse(plan.fork_entry_id or plan.fork_last)
        self.assertEqual(plan.reason, "new-turn")

    def test_regenerate_forks_the_last_user_turn(self):
        plan = plan_turn(
            ["one"], _pi("one"),
            trailing_assistant=False, answered=True, last_user_text="one",
        )
        self.assertEqual(plan.fork_entry_id, "e1")
        self.assertEqual(plan.prompt, "one")
        self.assertEqual(plan.reason, "regenerate")

    def test_edited_message_forks_the_replaced_turn(self):
        plan = plan_turn(
            ["one", "two edited"], _pi("one", "two"),
            trailing_assistant=False, answered=True, last_user_text="two",
        )
        self.assertEqual(plan.fork_entry_id, "e2")
        self.assertEqual(plan.prompt, "two edited")
        self.assertEqual(plan.reason, "edit")

    def test_edited_first_message_forks_the_first_turn(self):
        plan = plan_turn(
            ["one edited"], _pi("one", "two"),
            trailing_assistant=False, answered=True, last_user_text="two",
        )
        self.assertEqual(plan.fork_entry_id, "e1")
        self.assertEqual(plan.prompt, "one edited")

    def test_truncated_transcript_reanswers_the_last_visible_turn(self):
        plan = plan_turn(
            ["one"], _pi("one", "two"),
            trailing_assistant=False, answered=True, last_user_text="two",
        )
        self.assertEqual(plan.fork_entry_id, "e1")
        self.assertEqual(plan.prompt, "one")
        self.assertEqual(plan.reason, "truncate")

    def test_continue_prompts_without_forking(self):
        plan = plan_turn(
            ["one"], _pi("one"),
            trailing_assistant=True, answered=True, last_user_text="one",
        )
        self.assertTrue(plan.continuation)
        self.assertEqual(plan.prompt, CONTINUATION_PROMPT)
        self.assertIsNone(plan.fork_entry_id)
        self.assertEqual(plan.reason, "continue")

    def test_continue_after_deleted_turns_drops_the_extra_branch(self):
        plan = plan_turn(
            ["one"], _pi("one", "two"),
            trailing_assistant=True, answered=True, last_user_text="two",
        )
        self.assertEqual(plan.fork_entry_id, "e2")
        self.assertTrue(plan.continuation)
        self.assertEqual(plan.reason, "continue-after-delete")

    def test_continue_after_an_edit_answers_the_edited_turn(self):
        plan = plan_turn(
            ["one", "two edited"], _pi("one", "two"),
            trailing_assistant=True, answered=True, last_user_text="two",
        )
        self.assertEqual(plan.fork_entry_id, "e2")
        self.assertFalse(plan.continuation)
        self.assertEqual(plan.prompt, "two edited")

    def test_continuation_prompts_are_excluded_from_alignment(self):
        messages = _pi("one", CONTINUATION_PROMPT, "two")
        self.assertEqual(pi_user_messages(messages), [("e1", "one"), ("e3", "two")])
        plan = plan_turn(
            ["one", "two", "three"], messages,
            trailing_assistant=False, answered=True, last_user_text="two",
        )
        # Without filtering, the marker would make "two" look edited and force
        # a fork; with filtering this is a plain new turn.
        self.assertFalse(plan.fork_entry_id)
        self.assertEqual(plan.prompt, "three")
        self.assertEqual(plan.reason, "new-turn")

    def test_rag_context_matches_the_original_query_by_position(self):
        rag = "### Task:\nRespond using the context.\n\n<context><source>notes</source></context>"
        plan = plan_turn(
            ["summarise my notes", "next"], _pi(rag),
            trailing_assistant=False, answered=True, last_user_text=rag,
        )
        self.assertFalse(plan.fork_entry_id)
        self.assertEqual(plan.prompt, "next")

    def test_attached_file_tags_do_not_look_like_an_edit(self):
        pi_text = '<attached_files>\n<file name="a.pdf"/>\n</attached_files>\n\nsummarise this'
        plan = plan_turn(
            ["summarise this", "next"], _pi(pi_text),
            trailing_assistant=False, answered=True, last_user_text=pi_text,
        )
        self.assertFalse(plan.fork_entry_id)
        self.assertEqual(plan.prompt, "next")

    def test_compacted_transcript_appends_without_dropping_pi_context(self):
        plan = plan_turn(
            ["recent", "next"], _pi("old", "recent"),
            trailing_assistant=False, answered=True, last_user_text="recent",
            previous_open_users=["old", "recent"], compacted=True,
        )
        self.assertIsNone(plan.fork_entry_id)
        self.assertEqual(plan.prompt, "next")
        self.assertEqual(plan.reason, "compacted")

    def test_compacted_continue_does_not_fork(self):
        plan = plan_turn(
            ["recent"], _pi("old", "recent"),
            trailing_assistant=True, answered=True, last_user_text="recent",
            previous_open_users=["old", "recent"], compacted=True,
        )
        self.assertTrue(plan.continuation)
        self.assertIsNone(plan.fork_entry_id)

    def test_previous_visible_list_detects_a_rag_turn_edit(self):
        # pi stored a RAG envelope, but the in-memory visible list still knows
        # the learner replaced the first message (and Open WebUI truncated the
        # later turn).
        rag = "### Task:\nRespond using the context.\n\n<context><source>notes</source></context>"
        plan = plan_turn(
            ["one edited"], _pi(rag, "two"),
            trailing_assistant=False, answered=True, last_user_text=rag,
            previous_open_users=["one", "two"],
        )
        self.assertEqual(plan.fork_entry_id, "e1")
        self.assertEqual(plan.prompt, "one edited")
        self.assertEqual(plan.reason, "edit")

    def test_previous_visible_list_detects_an_extension_edit(self):
        plan = plan_turn(
            ["summarise this briefly"], _pi("summarise this"),
            trailing_assistant=False, answered=True, last_user_text="summarise this",
            previous_open_users=["summarise this"],
        )
        self.assertEqual(plan.fork_entry_id, "e1")
        self.assertEqual(plan.prompt, "summarise this briefly")

    def test_previous_visible_list_keeps_rag_new_turns_aligned(self):
        rag = "### Task:\nRespond using the context.\n\n<context><source>notes</source></context>"
        plan = plan_turn(
            ["summarise my notes", "next"], _pi(rag),
            trailing_assistant=False, answered=True, last_user_text=rag,
            previous_open_users=["summarise my notes"],
        )
        self.assertFalse(plan.fork_entry_id)
        self.assertEqual(plan.prompt, "next")
        self.assertEqual(plan.reason, "new-turn")

    def test_unknown_pi_messages_fall_back_to_last_message_heuristic(self):
        plan = plan_turn(
            ["one"], [],
            trailing_assistant=False, answered=True, last_user_text="one",
            pi_known=False,
        )
        self.assertTrue(plan.fork_last)
        self.assertEqual(plan.prompt, "one")

        continued = plan_turn(
            ["one"], [],
            trailing_assistant=True, answered=True, last_user_text="one",
            pi_known=False,
        )
        self.assertTrue(continued.continuation)
        self.assertEqual(continued.prompt, CONTINUATION_PROMPT)


if __name__ == "__main__":
    unittest.main()
