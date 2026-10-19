"""Unit + integration tests for pi-bridge.

The integration tests run a deterministic fake pi (`fake_pi.py`) — no models, no
network, no state — and assert the bridge's two load-bearing properties:
  1. deltas never reach the client (only the post-gate `message_end` text does);
  2. a withheld turn surfaces the gate banner, never the raw draft.
"""
import base64
import json
import os
import sys
import threading
import time
import unittest
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bridge.stream import TurnStream, text_of_content  # noqa: E402
from bridge import genui, openwebui  # noqa: E402
from bridge.server import (  # noqa: E402
    BridgeConfig,
    BridgeServer,
    LearningLock,
    is_learning_flow,
    last_user_text,
    session_key,
)

FAKE_PI = str(ROOT / "test" / "bridge" / "fake_pi.py")
SECRET = "SECRET_DRAFT_MUST_NOT_LEAK"


# --------------------------------------------------------------------------
# Pure units
# --------------------------------------------------------------------------
class TestHelpers(unittest.TestCase):
    def test_text_of_content(self):
        self.assertEqual(text_of_content("hi"), "hi")
        self.assertEqual(
            text_of_content([{"type": "text", "text": "a"}, {"type": "thinking", "thinking": "x"}, "b"]),
            "ab",
        )
        self.assertEqual(text_of_content(None), "")

    def test_last_user_text(self):
        msgs = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "one"},
            {"role": "assistant", "content": "two"},
            {"role": "user", "content": [{"type": "text", "text": "three"}]},
        ]
        self.assertEqual(last_user_text(msgs), "three")
        self.assertEqual(last_user_text([]), "")

    def test_only_newest_user_message_forwarded(self):
        # B-newest-message-only: pi owns the context, so the bridge forwards
        # only the newest user message of the posted transcript.
        msgs = [
            {"role": "user", "content": "oldest"},
            {"role": "assistant", "content": "reply"},
            {"role": "user", "content": "middle"},
            {"role": "assistant", "content": "reply"},
            {"role": "user", "content": [{"type": "text", "text": "newest"}]},
        ]
        self.assertEqual(last_user_text(msgs), "newest")

    def test_is_learning_flow(self):
        self.assertTrue(is_learning_flow("/review"))
        self.assertTrue(is_learning_flow("  /lesson the next one"))
        self.assertTrue(is_learning_flow("[[FLOW:teach]] go"))
        # ordinary prose must NOT be classified as a learning flow
        self.assertFalse(is_learning_flow("show me a vector"))
        self.assertFalse(is_learning_flow("continue with that"))
        self.assertFalse(is_learning_flow("what is a vector?"))
        self.assertFalse(is_learning_flow(""))

    def test_session_key_prefers_metadata_chat_id(self):
        body = {"metadata": {"chat_id": "abc"}, "model": "learning"}
        self.assertEqual(session_key(body, []), "chat:abc")

    def test_session_key_fingerprint_stable(self):
        body = {"model": "learning"}
        msgs = [{"role": "user", "content": "first"}]
        self.assertEqual(session_key(body, msgs), session_key(body, list(msgs)))


class TestTurnStream(unittest.TestCase):
    def test_deltas_never_forwarded(self):
        # B-deltas-never-forwarded: message_update deltas carry the
        # pre-verification draft; only the completed message_end text is emitted.
        ts = TurnStream()
        ts.feed({"type": "message_start", "message": {"role": "assistant", "stopReason": "pending"}})
        ts.feed({"type": "message_update", "assistantMessageEvent": {"type": "text_delta", "delta": SECRET}})
        ts.feed({"type": "message_update", "assistantMessageEvent": {"type": "thinking_delta", "delta": SECRET}})
        self.assertEqual(ts.final_text(), "")          # nothing while the draft streams
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "text", "text": "VERIFIED_FINAL"}]}})
        self.assertEqual(ts.final_text(), "VERIFIED_FINAL")
        self.assertNotIn(SECRET, ts.final_text())

    def test_unverified_banner_forwarded(self):
        # B-withheld-banner-forwarded: at the retry cap the gate writes the
        # UNVERIFIED banner into message_end; the raw draft never reaches us.
        ts = TurnStream()
        ts.feed({"type": "message_update", "assistantMessageEvent": {"type": "text_delta", "delta": SECRET}})
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "text", "text": "⛔ UNVERIFIED (retry cap)\nA draft was withheld."}]}})
        self.assertIn("UNVERIFIED", ts.final_text())
        self.assertNotIn(SECRET, ts.final_text())

    def test_deltas_and_tooluse_never_emitted(self):
        ts = TurnStream()
        ts.feed({"type": "message_start", "message": {"role": "assistant", "stopReason": "pending"}})
        ts.feed({"type": "message_update", "assistantMessageEvent": {"type": "text_delta", "delta": SECRET}})
        ts.feed({"type": "tool_execution_start", "toolName": "bash"})
        # a tool-use assistant message (ungated) must be skipped
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "toolUse",
            "content": [{"type": "text", "text": "narration " + SECRET}]}})
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "text", "text": "VERIFIED_FINAL"}]}})
        self.assertEqual(ts.final_text(), "VERIFIED_FINAL")
        self.assertNotIn(SECRET, ts.final_text())

    def test_withheld_banner_surfaced_not_draft(self):
        ts = TurnStream()
        ts.feed({"type": "message_update", "assistantMessageEvent": {"type": "text_delta", "delta": SECRET}})
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "text", "text": "⛔ WITHHELD (NO_SCOUT_CONTEXT)\nRun scout."}]}})
        self.assertIn("WITHHELD", ts.final_text())
        self.assertNotIn(SECRET, ts.final_text())

    def test_partial_stopreason_emitted_untagged(self):
        # G-partial-ungated: the gate passes a partial through with its tag
        # stripped, so the bridge surfaces it (a later retry replaces it).
        ts = TurnStream()
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "length",
            "content": [{"type": "text", "text": "partial"}]}})
        self.assertEqual(ts.final_text(), "partial")

    def test_unknown_stopreason_not_emitted(self):
        ts = TurnStream()
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "deferred",
            "content": [{"type": "text", "text": "nope"}]}})
        self.assertEqual(ts.final_text(), "")

    def test_provider_error_with_no_content_surfaces_message(self):
        # B-provider-error-surfaced: an expired key / provider outage arrives as
        # an empty assistant message with stopReason=error. The bridge must show
        # the reason instead of streaming an empty bubble the learner cannot act
        # on (the 2026-10-19 "chat shows nothing" session).
        ts = TurnStream()
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "error", "content": [],
            "errorMessage": "401: {\"code\":\"api_key_expired\"}"}})
        self.assertIn("pi runtime error", ts.final_text())
        self.assertIn("api_key_expired", ts.final_text())

    def test_provider_error_does_not_replace_real_text(self):
        ts = TurnStream()
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "text", "text": "VERIFIED_FINAL"}]}})
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "error", "content": [],
            "errorMessage": "transient"}})
        self.assertEqual(ts.final_text(), "VERIFIED_FINAL")

    def test_later_successful_message_wins_over_earlier_error(self):
        ts = TurnStream()
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "error", "content": [],
            "errorMessage": "transient"}})
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "text", "text": "VERIFIED_FINAL"}]}})
        self.assertEqual(ts.final_text(), "VERIFIED_FINAL")

    def test_error_without_message_still_surfaces_something(self):
        for bad in (None, "", "   "):
            ts = TurnStream()
            ts.feed({"type": "message_end", "message": {
                "role": "assistant", "stopReason": "error", "content": [],
                "errorMessage": bad}})
            self.assertIn("pi runtime error", ts.final_text())
            self.assertIn("unknown provider error", ts.final_text())


class TestTurnTagCleanup(unittest.TestCase):
    """B-clean-turn-tag: the bridge strips one leading turn tag from its output.

    The gate strips the tag for gated flows, but a non-learning message (no
    [[FLOW:…]] marker) passes through untouched, so the bridge cleans its own
    learner-facing text rather than leaking the internal protocol.
    """

    def _emit(self, text):
        ts = TurnStream()
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "text", "text": text}]}})
        return ts.final_text()

    def test_leading_tag_stripped(self):
        self.assertEqual(self._emit("[[TURN:none]] 2 plus 2 equals 4."), "2 plus 2 equals 4.")

    def test_leading_tag_with_whitespace_newline_stripped(self):
        self.assertEqual(self._emit("  \n[[TURN:claims]]\n\nHello."), "Hello.")

    def test_each_tag_vocabulary_stripped_case_insensitively(self):
        for tag in ("claims", "quiz", "grade", "ui", "none"):
            self.assertEqual(self._emit(f"[[TURN:{tag}]] body"), "body")
        self.assertEqual(self._emit("[[turn:NONE]] body"), "body")

    def test_inline_tag_later_in_body_preserved(self):
        text = "Intro.\n[[TURN:claims]] still part of the body"
        self.assertEqual(self._emit(text), text)

    def test_withheld_banner_untouched(self):
        text = "⛔ WITHHELD (NO_SCOUT_CONTEXT)\nRun the `scout` subagent first."
        self.assertEqual(self._emit(text), text)

    def test_text_without_tag_unchanged(self):
        text = "plain answer with no protocol tag"
        self.assertEqual(self._emit(text), text)

    def test_only_one_leading_tag_stripped(self):
        self.assertEqual(self._emit("[[TURN:none]][[TURN:none]] x"), "[[TURN:none]] x")


class TestLearningLock(unittest.TestCase):
    def test_single_learning_writer(self):
        # B-single-learning-writer: at most one chat holds the state-repo write
        # lock; a same-owner re-entry renews, a different chat is refused.
        lock = LearningLock()
        self.assertTrue(lock.acquire("chat A"))
        self.assertFalse(lock.acquire("chat B"))
        self.assertEqual(lock.owner(), "chat A")
        lock.release("chat A")
        self.assertTrue(lock.acquire("chat B"))
        self.assertEqual(lock.owner(), "chat B")
        lock.release("chat B")

    def test_one_owner_at_a_time(self):
        lock = LearningLock()
        self.assertTrue(lock.acquire("A"))
        self.assertTrue(lock.acquire("A"))       # same owner renews (refcount)
        self.assertFalse(lock.acquire("B"))       # different chat refused
        lock.release("A")                          # one holder left
        self.assertEqual(lock.owner(), "A")
        self.assertFalse(lock.acquire("B"))       # still held
        lock.release("A")                          # last holder released
        self.assertIsNone(lock.owner())
        self.assertTrue(lock.acquire("B"))
        lock.release("B")
        self.assertIsNone(lock.owner())


class TestSessionArgs(unittest.TestCase):
    def test_bash_guard_flag_only_when_present(self):
        cfg = BridgeConfig(pi_bin=FAKE_PI, state_repo=str(ROOT), api_key="k",
                           agent_dir=str(ROOT / "test" / "bridge" / "no-such-agent"))
        self.assertEqual(cfg.session_args(), [])            # no bash-guard here

    def test_bash_guard_flag_added_when_present(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "extensions" / "bash-guard").mkdir(parents=True)
            cfg = BridgeConfig(pi_bin=FAKE_PI, state_repo=str(ROOT), api_key="k", agent_dir=d)
            self.assertEqual(cfg.session_args(), ["--bash-guard-disabled"])

    def test_allow_bash_guard_overrides(self):
        real = str(Path.home() / ".pi" / "agent")
        cfg = BridgeConfig(pi_bin=FAKE_PI, state_repo=str(ROOT), api_key="k",
                           agent_dir=real, disable_bash_guard=False)
        self.assertEqual(cfg.session_args(), [])


# --------------------------------------------------------------------------
# Integration (fake pi + real HTTP server)
# --------------------------------------------------------------------------
class ServerHarness:
    def __init__(self, scenario="default", pi_bin=FAKE_PI, env_extra=None):
        env = {"FAKE_PI_SCENARIO": scenario}
        env.update(env_extra or {})
        self.httpd = BridgeServer(BridgeConfig(
            pi_bin=pi_bin,
            state_repo=str(ROOT),
            api_key="test-key",
            host="127.0.0.1",
            port=0,
            timeout=30,
            models=["learning"],
            child_env_extra=env,
        ))
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.registry.close_all()
        self.httpd.server_close()

    def url(self, path):
        return f"http://127.0.0.1:{self.port}{path}"

    def post(self, payload, key="test-key", raw=False):
        data = json.dumps(payload).encode()
        req = urllib.request.Request(self.url("/v1/chat/completions"), data=data,
                                     headers={"Content-Type": "application/json",
                                              "Authorization": f"Bearer {key}"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode()
                return resp.status, (body if raw else json.loads(body))
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()

    def body(self, text, chat_id="c1", stream=False):
        return {
            "model": "learning",
            "stream": stream,
            "metadata": {"chat_id": chat_id},
            "messages": [{"role": "user", "content": text}],
        }


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.h = ServerHarness("default")

    def tearDown(self):
        self.h.stop()

    def test_healthz_no_auth(self):
        with urllib.request.urlopen(self.h.url("/healthz"), timeout=10) as r:
            self.assertEqual(r.status, 200)

    def test_models(self):
        req = urllib.request.Request(self.h.url("/v1/models"),
                                     headers={"Authorization": "Bearer test-key"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        self.assertEqual(data["data"][0]["id"], "learning")

    def test_auth_required(self):
        status, _ = self.h.post(self.h.body("hello"), key="wrong")
        self.assertEqual(status, 401)

    def test_non_ascii_auth_header_is_rejected_not_crashing(self):
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", self.h.port, timeout=10)
        try:
            conn.request("GET", "/v1/models", headers={"Authorization": "Bearer \u0080"})
            resp = conn.getresponse()
            self.assertEqual(resp.status, 401)
            resp.read()
        finally:
            conn.close()

    def test_nonstream_returns_final_without_draft(self):
        status, data = self.h.post(self.h.body("hello"))
        self.assertEqual(status, 200)
        content = data["choices"][0]["message"]["content"]
        self.assertEqual(content, "VERIFIED_FINAL")
        self.assertNotIn(SECRET, json.dumps(data))

    def test_stream_returns_final_without_draft(self):
        status, body = self.h.post(self.h.body("hello", stream=True), raw=True)
        self.assertEqual(status, 200)
        self.assertIn("VERIFIED_FINAL", body)
        self.assertIn("[DONE]", body)
        self.assertNotIn(SECRET, body)

    def test_stream_client_never_receives_deltas(self):
        # B-deltas-never-forwarded, end to end: the SSE stream carries the
        # post-gate text only; no delta (raw draft) is written to the client.
        status, body = self.h.post(self.h.body("hello", stream=True), raw=True)
        self.assertEqual(status, 200)
        self.assertNotIn(SECRET, body)
        self.assertNotIn("more draft text", body)
        self.assertIn("VERIFIED_FINAL", body)

    def test_regenerate_same_message(self):
        self.h.post(self.h.body("hello"))
        status, data = self.h.post(self.h.body("hello"))  # same text -> fork path
        self.assertEqual(status, 200)
        self.assertEqual(data["choices"][0]["message"]["content"], "VERIFIED_FINAL")

    def test_resend_forks(self):
        # B-newest-message-only: a resend of the same user message is a
        # regenerate, so the bridge forks the session back before re-prompting.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            fork_log = Path(d) / "fork.log"
            h = ServerHarness("default", env_extra={"FAKE_PI_FORK_LOG": str(fork_log)})
            try:
                h.post(h.body("hello"))
                status, data = h.post(h.body("hello"))
                self.assertEqual(status, 200)
                self.assertEqual(data["choices"][0]["message"]["content"], "VERIFIED_FINAL")
                self.assertTrue(fork_log.exists(), "resend did not fork the session")
                self.assertIn("e1", fork_log.read_text())
            finally:
                h.stop()

    def test_only_newest_user_message_reaches_pi(self):
        # B-newest-message-only, server level: with a full transcript posted,
        # only the newest user message is forwarded to the pi runtime.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            prompt_log = Path(d) / "prompt.log"
            h = ServerHarness("default", env_extra={"FAKE_PI_PROMPT_LOG": str(prompt_log)})
            try:
                body = h.body("newest")
                body["messages"] = [
                    {"role": "user", "content": "oldest"},
                    {"role": "assistant", "content": "reply"},
                    {"role": "user", "content": "newest"},
                ]
                status, data = h.post(body)
                self.assertEqual(status, 200)
                self.assertEqual(data["choices"][0]["message"]["content"], "VERIFIED_FINAL")
                forwarded = prompt_log.read_text()
                self.assertIn("newest", forwarded)
                self.assertNotIn("oldest", forwarded)
            finally:
                h.stop()

    def test_empty_body_rejected(self):
        status, _ = self.h.post({"model": "learning", "messages": []})
        self.assertEqual(status, 400)


class TestHandledDisposition(unittest.TestCase):
    def test_handled_returns_without_waiting(self):
        # An extension-consumed prompt starts no run; the bridge must not block.
        h = ServerHarness("handled")
        try:
            start = time.time()
            status, data = h.post(h.body("/viz"))
            elapsed = time.time() - start
            self.assertEqual(status, 200)
            self.assertLess(elapsed, 2.0)  # must not pay the old 2s drain stall
        finally:
            h.stop()


class TestLearningLockConcurrent(unittest.TestCase):
    def test_two_chats_cannot_run_learning_turns_at_once(self):
        h = ServerHarness("slow")
        try:
            results = {}

            def first():
                results["a"] = h.post(h.body("/review now", chat_id="A"))

            t = threading.Thread(target=first)
            t.start()
            time.sleep(0.4)  # let the first turn acquire the lock
            status, data = h.post(h.body("/lesson next", chat_id="B"))
            self.assertEqual(status, 200)
            self.assertIn("Another learning session", data["choices"][0]["message"]["content"])
            t.join(timeout=15)
            self.assertEqual(results["a"][0], 200)
        finally:
            h.stop()

    def test_general_chat_exempt_from_learning_lock(self):
        # B-single-learning-writer: general (non-learning) chats are exempt —
        # one may run while another chat holds the learning lock.
        h = ServerHarness("slow")
        try:
            results = {}

            def learning():
                results["a"] = h.post(h.body("/review now", chat_id="A"))

            t = threading.Thread(target=learning)
            t.start()
            time.sleep(0.4)  # let the learning turn acquire the lock
            status, data = h.post(h.body("hello", chat_id="B"))
            self.assertEqual(status, 200)
            self.assertEqual(data["choices"][0]["message"]["content"], "VERIFIED_FINAL")
            t.join(timeout=15)
            self.assertEqual(results["a"][0], 200)
        finally:
            h.stop()


class TestWithholdScenario(unittest.TestCase):
    def test_withhold_banner_no_leak(self):
        h = ServerHarness("withhold")
        try:
            status, body = h.post(h.body("/lesson next", stream=True), raw=True)
            self.assertEqual(status, 200)
            self.assertIn("WITHHELD", body)
            self.assertNotIn(SECRET, body)
        finally:
            h.stop()

    def test_withheld_banner_forwarded(self):
        # B-withheld-banner-forwarded: the learner sees the gate's own WITHHELD
        # banner from message_end; the pre-verification draft never leaks.
        h = ServerHarness("withhold")
        try:
            status, data = h.post(h.body("/lesson next"))
            self.assertEqual(status, 200)
            content = data["choices"][0]["message"]["content"]
            self.assertIn("⛔ WITHHELD", content)
            self.assertNotIn(SECRET, content)
            self.assertNotIn("more draft text", content)
        finally:
            h.stop()


class TestTurnTagIntegration(unittest.TestCase):
    def test_completion_cleans_leading_turn_tag(self):
        h = ServerHarness("turn_tag")
        try:
            status, data = h.post(h.body("2 plus 2?"))
            self.assertEqual(status, 200)
            content = data["choices"][0]["message"]["content"]
            self.assertEqual(content, "2 plus 2 equals 4.")
            self.assertNotIn("[[TURN:", json.dumps(data))
        finally:
            h.stop()

    def test_stream_cleans_leading_turn_tag(self):
        h = ServerHarness("turn_tag")
        try:
            status, body = h.post(h.body("2 plus 2?", stream=True), raw=True)
            self.assertEqual(status, 200)
            self.assertIn("2 plus 2 equals 4.", body)
            self.assertNotIn("[[TURN:", body)
        finally:
            h.stop()


class TestForkFallback(unittest.TestCase):
    def test_fork_failure_falls_back_to_append(self):
        h = ServerHarness("forkfail")
        try:
            h.post(h.body("hello"))
            status, data = h.post(h.body("hello"))  # same text -> fork, which fails
            self.assertEqual(status, 200)
            self.assertEqual(data["choices"][0]["message"]["content"], "VERIFIED_FINAL")
        finally:
            h.stop()


class TestProviderError(unittest.TestCase):
    def test_provider_error_returns_actionable_text_not_empty_bubble(self):
        h = ServerHarness("provider_error")
        try:
            status, data = h.post(h.body("hello"))
            self.assertEqual(status, 200)
            content = data["choices"][0]["message"]["content"]
            self.assertIn("pi runtime error", content)
            self.assertIn("api_key_expired", content)
            self.assertNotIn(SECRET, content)
        finally:
            h.stop()

    def test_provider_error_stream_carries_the_message(self):
        h = ServerHarness("provider_error")
        try:
            status, body = h.post(h.body("hello", stream=True), raw=True)
            self.assertEqual(status, 200)
            self.assertIn("pi runtime error", body)
            self.assertIn("[DONE]", body)
            self.assertNotIn(SECRET, body)
        finally:
            h.stop()


class TestStartFailure(unittest.TestCase):
    def test_bad_pi_bin_returns_error_not_crash(self):
        h = ServerHarness("default", pi_bin="/nonexistent/pi-binary")
        try:
            status, data = h.post(h.body("hello"))
            self.assertEqual(status, 200)
            self.assertIn("pi runtime error", data["choices"][0]["message"]["content"])
        finally:
            h.stop()


class FakeSession:
    def __init__(self, *a, **k):
        self.started = False
        self.closed = False
        self.alive_flag = True

    def start(self):
        self.started = True

    def alive(self):
        return self.alive_flag and not self.closed

    def close(self):
        self.closed = True

    def prompt(self, *a, **k):
        return []


class TestRegistry(unittest.TestCase):
    def setUp(self):
        import bridge.server as S
        self.S = S
        self.orig = S.PiSession
        S.PiSession = FakeSession

    def tearDown(self):
        self.S.PiSession = self.orig

    def _reg(self, cap=4):
        return self.S.SessionRegistry(self.S.BridgeConfig(
            pi_bin="x", state_repo=str(ROOT), api_key="k", max_sessions=cap))

    def test_one_session_per_chat(self):
        # B-newest-message-only: one pi RPC session per chat, reused across turns.
        reg = self._reg()
        e1 = reg.get_or_create("chat")
        e2 = reg.get_or_create("chat")
        self.assertIs(e1, e2)
        self.assertEqual(len(reg._entries), 1)

    def test_dead_session_is_replaced_and_removed(self):
        reg = self._reg()
        e1 = reg.get_or_create("a")
        e1.session.alive_flag = False
        e2 = reg.get_or_create("a")
        self.assertTrue(e1.session.closed)
        self.assertEqual(len(reg._entries), 1)
        self.assertIsNot(e1, e2)

    def test_get_or_create_marks_inflight(self):
        reg = self._reg()
        self.assertTrue(reg.get_or_create("a").inflight)

    def test_lru_eviction_at_cap(self):
        reg = self._reg(cap=1)
        a = reg.get_or_create("a")
        a.inflight = False            # simulate a completed turn (idle again)
        reg.get_or_create("b")
        self.assertTrue(a.session.closed)
        self.assertNotIn("a", reg._entries)

    def test_inflight_session_not_evicted(self):
        reg = self._reg(cap=1)
        a = reg.get_or_create("a")    # returned inflight
        reg.get_or_create("b")
        self.assertFalse(a.session.closed)   # overshoot rather than kill live work
        self.assertIn("a", reg._entries)


class TestOpenUiFences(unittest.TestCase):
    """The bridge lifts a verified ```openui payload out of the prose and keeps
    Mermaid/HTML fences intact for Open WebUI's native rendering."""

    def _turn(self, text):
        ts = TurnStream()
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "text", "text": text}]}})
        return ts

    def test_openui_fence_extracted_and_stripped_from_prose(self):
        payload = "root = Card([title])\ntitle = TextContent(\"Hi\", \"large\")"
        ts = self._turn(f"Here.\n```openui\n{payload}\n```\nDone.")
        self.assertEqual(ts.openui_payloads(), [payload])
        self.assertEqual(ts.final_text(), "Here.\n\nDone.")

    def test_multiple_fences_extracted_in_order(self):
        ts = self._turn("a\n```openui\nroot = Card([])\n```\nb\n```openui\nroot = Card([x])\n```\nc")
        self.assertEqual(ts.openui_payloads(), ["root = Card([])", "root = Card([x])"])
        self.assertNotIn("```openui", ts.final_text())

    def test_mermaid_and_html_fences_left_intact(self):
        text = "A\n```mermaid\ngraph TD\n```\nB\n```html\n<p>hi</p>\n```\nC"
        ts = self._turn(text)
        self.assertEqual(ts.openui_payloads(), [])
        self.assertEqual(ts.final_text(), text)

    def test_no_fence_leaves_text_unchanged(self):
        ts = self._turn("[[TURN:none]] plain")
        self.assertEqual(ts.final_text(), "plain")
        self.assertEqual(ts.openui_payloads(), [])


class TestGenUiEmbedUrl(unittest.TestCase):
    """The widget is delivered as a same-origin static-shell URL. Open WebUI's
    FullHeightIframe treats a `data:` embed as raw HTML, so the payload rides in
    the URL fragment and the shell (installer-written) decodes it."""

    BASE = "http://127.0.0.1:3000/static/openui/0.2.1"

    def test_embed_url_targets_the_self_hosted_shell(self):
        url = genui.widget_embed_url('root = Card([])', bundle_base=self.BASE)
        self.assertTrue(url.startswith(self.BASE + "/widget.html#"))
        self.assertNotIn("data:", url)

    def test_payload_roundtrips_through_the_fragment(self):
        payload = 'root = Card([t])\nt = TextContent("Unicode — ok", "large")'
        url = genui.widget_embed_url(payload, bundle_base=self.BASE)
        frag = url.split("#", 1)[1]
        pad = "=" * (-len(frag) % 4)
        decoded = base64.urlsafe_b64decode(frag + pad).decode("utf-8")
        self.assertEqual(decoded, payload)

    def test_fragment_is_unpadded_and_url_safe(self):
        frag = genui.payload_fragment("a/b+c=?& d")
        self.assertNotIn("=", frag)
        self.assertNotIn("/", frag)
        self.assertNotIn("+", frag)

    def test_default_bundle_base_is_pinned_same_origin(self):
        self.assertEqual(
            genui.default_bundle_base("http://127.0.0.1:3000/"),
            "http://127.0.0.1:3000/static/openui/" + genui.OPENUI_BUNDLE_VERSION,
        )


class _RecordingClient(openwebui.OpenWebUIClient):
    """Records the REST recipe and returns canned Open WebUI responses."""

    def __init__(self, current_role="assistant", drop_new_node=False):
        super().__init__("http://owui.test", "testkey")
        self.calls = []
        self._current = "m-user"
        self._role = current_role
        self._drop_new_node = drop_new_node

    def call(self, method, path, body=None):
        self.calls.append((method, path, body))
        if method == "GET":
            return 200, {"chat": {"models": ["learning"], "history": {
                "currentId": self._current,
                "messages": {self._current: {"id": self._current, "role": self._role}},
            }}}
        if method == "POST" and "/event" not in path:
            new_id = next(iter(body["chat"]["history"]["messages"]))
            self._current = new_id
            msgs = {} if self._drop_new_node else {new_id: {"id": new_id, "role": "assistant"}}
            return 200, {"chat": {"history": {"messages": msgs, "currentId": new_id}}}
        if method == "POST" and "/event" in path:
            return 200, True
        return 404, {}

    def _assistant_get_count(self):
        return sum(1 for c in self.calls if c[0] == "GET")


class TestOpenWebUIClient(unittest.TestCase):
    def test_read_key_prefers_env(self):
        os.environ["OPENWEBUI_API_KEY"] = "env-key"
        try:
            self.assertEqual(openwebui.read_key("/nonexistent"), "env-key")
        finally:
            os.environ.pop("OPENWEBUI_API_KEY", None)

    def test_read_key_from_file(self):
        path = ROOT / "test" / "bridge" / "_tmp_owui_key"
        path.write_text("file-key\n", encoding="utf-8")
        try:
            self.assertEqual(openwebui.read_key(str(path)), "file-key")
        finally:
            path.unlink(missing_ok=True)

    def test_append_widget_recipe(self):
        client = _RecordingClient()
        url = "http://127.0.0.1:3000/static/openui/0.2.1/widget.html#AAAA"
        ok = client.append_widget("c1", [url], model="learning")
        self.assertTrue(ok)
        self.assertEqual([c[0] for c in client.calls], ["GET", "POST", "POST"])
        self.assertEqual(client.calls[0][1], "/api/v1/chats/c1")
        self.assertEqual(client.calls[1][1], "/api/v1/chats/c1")
        new_id = next(iter(client.calls[1][2]["chat"]["history"]["messages"]))
        self.assertEqual(client.calls[2][1], f"/api/v1/chats/c1/messages/{new_id}/event")
        self.assertEqual(client.calls[2][2]["type"], "embeds")
        self.assertEqual(client.calls[2][2]["data"]["embeds"], [url])

    def test_empty_urls_is_a_noop(self):
        client = _RecordingClient()
        self.assertFalse(client.append_widget("c1", []))
        self.assertEqual(client.calls, [])

    def test_missing_new_node_in_response_raises(self):
        client = _RecordingClient(drop_new_node=True)
        with self.assertRaises(openwebui.OpenWebUIError):
            client.append_widget("c1", ["data:1"])

    def test_polls_until_the_assistant_message_is_saved(self):
        client = _RecordingClient(current_role="user")
        # The poll never sees an assistant node, so it gives up without a GET storm.
        self.assertFalse(client.append_widget("c1", ["data:1"], attempts=3, delay=0.0))
        self.assertGreaterEqual(client._assistant_get_count(), 1)


if __name__ == "__main__":
    unittest.main()