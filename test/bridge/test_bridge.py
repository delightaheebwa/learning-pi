"""Unit + integration tests for pi-bridge.

The integration tests run a deterministic fake pi (`fake_pi.py`) — no models, no
network, no state — and assert the bridge's two load-bearing properties:
  1. deltas never reach the client (only the post-gate `message_end` text does);
  2. a withheld turn surfaces the gate banner, never the raw draft.
"""
import json
import sys
import threading
import unittest
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bridge.stream import TurnStream, text_of_content  # noqa: E402
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

    def test_is_learning_flow(self):
        self.assertTrue(is_learning_flow("/review"))
        self.assertTrue(is_learning_flow("  /lesson the next one"))
        self.assertTrue(is_learning_flow("[[FLOW:teach]] go"))
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

    def test_partial_stopreason_not_emitted(self):
        ts = TurnStream()
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "length",
            "content": [{"type": "text", "text": "partial"}]}})
        self.assertEqual(ts.final_text(), "")


class TestLearningLock(unittest.TestCase):
    def test_one_owner_at_a_time(self):
        lock = LearningLock(idle_seconds=3600)
        self.assertTrue(lock.acquire("A"))
        self.assertTrue(lock.acquire("A"))       # same owner renews
        self.assertFalse(lock.acquire("B"))      # different chat refused
        lock._owner = None                        # simulate idle release
        self.assertTrue(lock.acquire("B"))


# --------------------------------------------------------------------------
# Integration (fake pi + real HTTP server)
# --------------------------------------------------------------------------
class ServerHarness:
    def __init__(self, scenario="default"):
        self.httpd = BridgeServer(BridgeConfig(
            pi_bin=FAKE_PI,
            state_repo=str(ROOT),
            api_key="test-key",
            host="127.0.0.1",
            port=0,
            timeout=30,
            models=["learning"],
            child_env_extra={"FAKE_PI_SCENARIO": scenario},
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

    def test_regenerate_same_message(self):
        self.h.post(self.h.body("hello"))
        status, data = self.h.post(self.h.body("hello"))  # same text -> fork path
        self.assertEqual(status, 200)
        self.assertEqual(data["choices"][0]["message"]["content"], "VERIFIED_FINAL")

    def test_learning_lock_blocks_second_chat(self):
        s1, _ = self.h.post(self.h.body("/review now", chat_id="A"))
        self.assertEqual(s1, 200)
        s2, data = self.h.post(self.h.body("/lesson next", chat_id="B"))
        self.assertEqual(s2, 200)
        self.assertIn("Another learning session", data["choices"][0]["message"]["content"])


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


if __name__ == "__main__":
    unittest.main()
