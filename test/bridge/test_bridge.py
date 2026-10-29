"""Unit + integration tests for pi-bridge.

The integration tests run a deterministic fake pi (`fake_pi.py`) — no models, no
network, no state — and assert the bridge's two load-bearing properties:
  1. deltas never reach the client (only the post-gate `message_end` text does);
  2. a withheld turn surfaces the gate banner, never the raw draft.
"""
import base64
import html
import json
import os
import re
import sys
import threading
import time
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bridge.stream import (  # noqa: E402
    ARGS_PREVIEW,
    Step,
    TurnStream,
    render_steps,
    text_of_content,
)
from bridge import openwebui  # noqa: E402
from bridge.rpc import PiError, PiSession  # noqa: E402
from bridge.server import (  # noqa: E402
    OPENUI_BUNDLE_VERSION,
    BridgeConfig,
    BridgeServer,
    LearningLock,
    default_bundle_base,
    is_learning_flow,
    last_user_text,
    openwebui_ids,
    payload_fragment,
    session_id_for,
    session_key,
    widget_embed_url,
)

FAKE_PI = str(ROOT / "test" / "bridge" / "fake_pi.py")
SECRET = "SECRET_DRAFT_MUST_NOT_LEAK"

_DETAILS_BLOCK_RE = re.compile(r"<details[\s\S]*?</details>\s*", re.IGNORECASE)


def prose(content: str) -> str:
    """Message text with the streamed step cards removed."""
    return _DETAILS_BLOCK_RE.sub("", content or "").strip()


def sse_content(body: str) -> str:
    """Concatenate the `delta.content` of every SSE chunk in a raw response."""
    out = []
    for line in (body or "").splitlines():
        if not line.startswith("data: "):
            continue
        payload = line[6:].strip()
        if payload == "[DONE]":
            continue
        try:
            rec = json.loads(payload)
        except ValueError:
            continue
        delta = (rec.get("choices") or [{}])[0].get("delta", {})
        out.append(delta.get("content") or "")
    return "".join(out)


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

    def test_openwebui_ids_prefer_forwarded_headers(self):
        headers = {"X-OpenWebUI-Chat-Id": "chat-1", "X-OpenWebUI-Message-Id": "msg-1"}
        body = {"metadata": {"chat_id": "stale"}}
        self.assertEqual(openwebui_ids(headers, body), ("chat-1", "msg-1"))

    def test_openwebui_ids_fall_back_to_metadata_chat(self):
        # No header (the pre-0.10 path): chat id may still arrive in metadata,
        # but without a message id there is nothing to attach a status to.
        self.assertEqual(openwebui_ids({}, {"metadata": {"chat_id": "c"}}), ("c", ""))


class TestSessionId(unittest.TestCase):
    """A chat's pi session id must be stable across bridge restarts.

    The registry is in-memory, so without `--session-id` every systemd restart
    (or pi crash) started a blank session and pi re-derived context from the
    state repo — the 2026-10-27 tensor-lesson turn answered from a review in a
    different chat that way.
    """

    def test_chat_key_maps_to_pi_session_id(self):
        self.assertEqual(
            session_id_for("chat:4f9603e9-2823-4dd9-88eb-9562d9f0ea83"),
            "chat-4f9603e9-2823-4dd9-88eb-9562d9f0ea83",
        )

    def test_fingerprint_key_maps_to_pi_session_id(self):
        self.assertEqual(session_id_for("fp:4f93b36529d5d5fc"), "fp-4f93b36529d5d5fc")

    def test_id_is_stable_and_valid(self):
        for key in ("chat:abc", "fp:abc", "a/b", "a b", "a:b", "x"):
            sid = session_id_for(key)
            self.assertEqual(sid, session_id_for(key))
            self.assertRegex(sid, r"^[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9]$")

    def test_different_keys_never_share_a_sanitised_id(self):
        self.assertNotEqual(session_id_for("a/b"), session_id_for("a b"))
        self.assertNotEqual(session_id_for("a:b"), session_id_for("a-b"))

    def test_overlong_key_collapses_to_a_short_valid_id(self):
        sid = session_id_for("chat:" + "a" * 500)
        self.assertEqual(len(sid), 26)  # "s-" + sha1[:24]
        self.assertRegex(sid, r"^[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9]$")

    def test_pi_command_resumes_the_id(self):
        session = PiSession(
            pi_bin="pi", cwd="/tmp", env={}, name="bridge-x",
            extra_args=["--bash-guard-disabled"], session_id="chat-1",
        )
        self.assertEqual(
            session.command_line(),
            ["pi", "--mode", "rpc", "--name", "bridge-x",
             "--session-id", "chat-1", "--bash-guard-disabled"],
        )

    def test_pi_command_without_id_keeps_old_shape(self):
        session = PiSession(pi_bin="pi", cwd="/tmp", env={}, name="bridge-x")
        self.assertEqual(
            session.command_line(),
            ["pi", "--mode", "rpc", "--name", "bridge-x"],
        )


class TestPromptBudgets(unittest.TestCase):
    """A turn is bounded by silence, not by wall-clock time.

    A learning turn can spend ~15 minutes inside one scout subagent with no
    record in between (2026-10-29: a fixed 900 s cap aborted exactly such a
    turn and Open WebUI showed `pi runtime error`). Idle time aborts a hung
    turn; an absolute ceiling still frees the single-writer lock.
    """

    def _session(self, scenario):
        env = dict(os.environ, FAKE_PI_SCENARIO=scenario)
        return PiSession(pi_bin=FAKE_PI, cwd=str(ROOT), env=env, name="bridge-t")

    def test_silent_turn_aborts_with_an_actionable_reason(self):
        session = self._session("silent")
        session.start()
        try:
            with self.assertRaises(PiError) as ctx:
                session.prompt("hello", lambda rec: None, timeout=0.3, max_turn=60)
        finally:
            session.close()
        self.assertIn("went quiet for 0.3s", str(ctx.exception))
        self.assertIn("PI_BRIDGE_TIMEOUT", str(ctx.exception))

    def test_activity_resets_the_idle_budget(self):
        # Records arrive every 0.15 s, so the turn outlives a 0.6 s idle budget
        # but never goes quiet for it: only an idle budget lets it finish.
        session = self._session("trickle")
        session.start()
        try:
            seen = []
            records = session.prompt(
                "hello", seen.append, timeout=0.6, max_turn=60)
        finally:
            session.close()
        self.assertTrue(seen)
        self.assertTrue(any(r.get("type") == "agent_settled" for r in records))

    def test_ceiling_aborts_an_active_runaway_turn(self):
        session = self._session("trickle_endless")
        session.start()
        try:
            with self.assertRaises(PiError) as ctx:
                session.prompt("hello", lambda rec: None, timeout=60, max_turn=0.35)
        finally:
            session.close()
        self.assertIn("ran longer than 0.35s", str(ctx.exception))
        self.assertIn("PI_BRIDGE_MAX_TURN", str(ctx.exception))

    def test_bridge_defaults_allow_a_long_learning_turn(self):
        cfg = BridgeConfig(pi_bin=FAKE_PI, state_repo=str(ROOT), api_key="k")
        self.assertEqual(cfg.timeout, 1800.0)
        self.assertEqual(cfg.max_turn, 7200.0)

    def test_cli_reads_both_budgets_from_the_environment(self):
        from bridge.__main__ import build_config
        with mock.patch.dict(os.environ, {
            "PI_BRIDGE_API_KEY": "k",
            "PI_BRIDGE_TIMEOUT": "2400",
            "PI_BRIDGE_MAX_TURN": "10800",
        }):
            cfg = build_config([])
        self.assertEqual(cfg.timeout, 2400.0)
        self.assertEqual(cfg.max_turn, 10800.0)


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


class TestChildEnv(unittest.TestCase):
    def test_forces_latex_math_for_openwebui(self):
        # Open WebUI renders KaTeX; headless pi sees no terminal image protocol,
        # so the bridge must opt into LaTeX authoring explicitly.
        with mock.patch.dict(os.environ, {}, clear=True):
            cfg = BridgeConfig(pi_bin=FAKE_PI, state_repo=str(ROOT), api_key="k")
            self.assertEqual(cfg.child_env().get("PI_MATH_MODE"), "latex")

    def test_process_env_math_mode_override_wins(self):
        # The production override: the operator sets PI_MATH_MODE in the
        # systemd EnvironmentFile, which the bridge inherits via os.environ.
        with mock.patch.dict(os.environ, {"PI_MATH_MODE": "unicode"}):
            cfg = BridgeConfig(pi_bin=FAKE_PI, state_repo=str(ROOT), api_key="k")
            self.assertEqual(cfg.child_env().get("PI_MATH_MODE"), "unicode")

    def test_child_env_extra_math_mode_override_wins(self):
        cfg = BridgeConfig(pi_bin=FAKE_PI, state_repo=str(ROOT), api_key="k",
                           child_env_extra={"PI_MATH_MODE": "unicode"})
        self.assertEqual(cfg.child_env().get("PI_MATH_MODE"), "unicode")


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
    def __init__(self, scenario="default", pi_bin=FAKE_PI, env_extra=None, **cfg):
        env = {"FAKE_PI_SCENARIO": scenario}
        env.update(env_extra or {})
        cfg.setdefault("timeout", 30)
        self.httpd = BridgeServer(BridgeConfig(
            pi_bin=pi_bin,
            state_repo=str(ROOT),
            api_key="test-key",
            host="127.0.0.1",
            port=0,
            models=["learning"],
            child_env_extra=env,
            **cfg,
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

    def request(self, payload, key="test-key", headers=None):
        merged = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        }
        merged.update(headers or {})
        return urllib.request.Request(
            self.url("/v1/chat/completions"),
            data=json.dumps(payload).encode(),
            headers=merged,
        )

    def post(self, payload, key="test-key", raw=False, headers=None):
        req = self.request(payload, key=key, headers=headers)
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
        self.assertEqual(prose(content), "VERIFIED_FINAL")
        self.assertIn('type="tool_calls"', content)  # the action trace rides along
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
        self.assertEqual(prose(data["choices"][0]["message"]["content"]), "VERIFIED_FINAL")

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
                self.assertEqual(prose(data["choices"][0]["message"]["content"]), "VERIFIED_FINAL")
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
                self.assertEqual(prose(data["choices"][0]["message"]["content"]), "VERIFIED_FINAL")
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
            self.assertEqual(prose(data["choices"][0]["message"]["content"]), "VERIFIED_FINAL")
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
            self.assertEqual(prose(content), "2 plus 2 equals 4.")
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
            self.assertEqual(prose(data["choices"][0]["message"]["content"]), "VERIFIED_FINAL")
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


class TestTurnTimeoutSurface(unittest.TestCase):
    def test_silent_turn_surfaces_the_budget_to_raise(self):
        # The learner must be able to act on an aborted turn, not see a blank
        # bubble: the reason names the env var to tune.
        h = ServerHarness("silent", timeout=0.3)
        try:
            status, data = h.post(h.body("hello"))
            self.assertEqual(status, 200)
            content = data["choices"][0]["message"]["content"]
            self.assertIn("pi runtime error", content)
            self.assertIn("went quiet for 0.3s", content)
            self.assertIn("PI_BRIDGE_TIMEOUT", content)
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
        self.session_id = k.get("session_id")
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

    def test_dead_session_is_recreated_with_the_same_pi_session_id(self):
        # pi may exit mid-chat (e.g. provider failure). The replacement must
        # resume the transcript it already wrote, not start blank.
        reg = self._reg()
        e1 = reg.get_or_create("chat:abc")
        e1.session.alive_flag = False
        e2 = reg.get_or_create("chat:abc")
        self.assertEqual(e2.session.session_id, e1.session.session_id)
        self.assertEqual(e2.session.session_id, "chat-abc")

    def test_bridge_restart_resumes_the_same_pi_session_id(self):
        # A new registry models a systemd restart: the in-memory entry is gone,
        # but the deterministic id reconnects the chat to its transcript.
        first = self._reg()
        e1 = first.get_or_create("chat:abc")
        first.close_all()
        second = self._reg()
        e2 = second.get_or_create("chat:abc")
        self.assertEqual(e2.session.session_id, e1.session.session_id)

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
        url = widget_embed_url('root = Card([])', bundle_base=self.BASE)
        self.assertTrue(url.startswith(self.BASE + "/widget.html#"))
        self.assertNotIn("data:", url)

    def test_payload_roundtrips_through_the_fragment(self):
        payload = 'root = Card([t])\nt = TextContent("Unicode — ok", "large")'
        url = widget_embed_url(payload, bundle_base=self.BASE)
        frag = url.split("#", 1)[1]
        pad = "=" * (-len(frag) % 4)
        decoded = base64.urlsafe_b64decode(frag + pad).decode("utf-8")
        self.assertEqual(decoded, payload)

    def test_fragment_is_unpadded_and_url_safe(self):
        frag = payload_fragment("a/b+c=?& d")
        self.assertNotIn("=", frag)
        self.assertNotIn("/", frag)
        self.assertNotIn("+", frag)

    def test_default_bundle_base_is_pinned_same_origin(self):
        self.assertEqual(
            default_bundle_base("http://127.0.0.1:3000/"),
            "http://127.0.0.1:3000/static/openui/" + OPENUI_BUNDLE_VERSION,
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

    def test_post_status_recipe(self):
        # The live status line/timeline: POST the per-message event route.
        client = _RecordingClient()
        self.assertTrue(client.post_status("chat-1", "msg-1", "Running bash…", False))
        method, path, body = client.calls[-1]
        self.assertEqual(method, "POST")
        self.assertEqual(path, "/api/v1/chats/chat-1/messages/msg-1/event")
        self.assertEqual(body, {"type": "status",
                                "data": {"description": "Running bash…", "done": False}})

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


class _Clock:
    """Injectable monotonic clock for deterministic step durations."""

    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestStepTrace(unittest.TestCase):
    """Steps carry action metadata; learning flows never carry draft text."""

    def test_tool_card_is_a_complete_parseable_block(self):
        clock = _Clock()
        ts = TurnStream(clock=clock)
        ts.feed({"type": "tool_execution_start", "toolCallId": "call_1",
                 "toolName": "bash", "args": {"command": "ls -la"}})
        self.assertEqual(ts.steps, [])  # nothing rendered until it finishes
        clock.t = 1.25
        ts.feed({"type": "tool_execution_end", "toolCallId": "call_1",
                 "toolName": "bash", "isError": False,
                 "result": {"content": [{"type": "text", "text": "file.txt"}]}})
        self.assertEqual(len(ts.steps), 1)
        card = ts.steps[0].render(learning=True)
        self.assertTrue(card.startswith('<details type="tool_calls" done="true"'))
        self.assertIn('name="bash · 1.2s"', card)
        self.assertIn('arguments="{&quot;command&quot;:&quot;ls -la&quot;}"', card)
        # Open WebUI's parser: opening tag + newline, summary on its own line.
        self.assertRegex(card, r"^<details[^>]*>\n<summary>[^\n]*</summary>\n")
        self.assertTrue(card.endswith("</details>\n\n"))
        self.assertNotIn("file.txt", card)  # results stay out of learning flows

    def test_general_chat_includes_the_truncated_result(self):
        ts = TurnStream(learning=False)
        ts.feed({"type": "tool_execution_start", "toolCallId": "call_1",
                 "toolName": "bash", "args": {"command": "ls"}})
        ts.feed({"type": "tool_execution_end", "toolCallId": "call_1",
                 "toolName": "bash", "isError": False,
                 "result": {"content": [{"type": "text", "text": "file.txt " * 500}]}})
        card = ts.steps[0].render(learning=False)
        self.assertIn("file.txt", card)
        self.assertIn("…", card)  # truncated preview, not a log dump

    def test_failed_tool_is_marked_failed(self):
        ts = TurnStream()
        ts.feed({"type": "tool_execution_start", "toolCallId": "c", "toolName": "bash", "args": {}})
        ts.feed({"type": "tool_execution_end", "toolCallId": "c", "toolName": "bash", "isError": True})
        card = ts.steps[0].render(learning=True)
        self.assertIn('status="failed"', card)
        self.assertNotIn('done="true"', card)

    def test_tool_args_are_truncated_and_escaped(self):
        ts = TurnStream()
        ts.feed({"type": "tool_execution_start", "toolCallId": "c", "toolName": "bash",
                 "args": {"command": 'echo "</details>" ' + "x" * 500}})
        ts.feed({"type": "tool_execution_end", "toolCallId": "c", "toolName": "bash",
                 "isError": False})
        card = ts.steps[0].render(learning=True)
        self.assertEqual(card.count("</details>"), 1)  # cannot close the block early
        attr = re.search(r'arguments="(.*?)"', card).group(1)
        self.assertLessEqual(len(html.unescape(attr)), ARGS_PREVIEW + 1)
        self.assertNotIn('"', attr)  # no raw quote ends the attribute value

    def test_opening_details_in_args_cannot_start_a_nested_block(self):
        card = Step(
            kind="tool", step_id="c", name="write_file",
            args={"path": "<details type=\"x\">"}, status="done", duration=0.1,
        ).render()
        self.assertEqual(card.count("<details"), 1)  # opening tokens are escaped too

    def test_tool_end_without_start_still_renders(self):
        ts = TurnStream()
        ts.feed({"type": "tool_execution_end", "toolName": "bash", "isError": False})
        self.assertEqual(len(ts.steps), 1)
        self.assertEqual(ts.steps[0].status, "done")

    def test_thinking_is_duration_only_in_a_learning_flow(self):
        clock = _Clock()
        ts = TurnStream(learning=True, clock=clock)
        ts.feed({"type": "message_start", "message": {"role": "assistant", "stopReason": "pending"}})
        clock.t = 0.5
        ts.feed({"type": "message_update",
                 "assistantMessageEvent": {"type": "thinking_delta", "delta": SECRET}})
        clock.t = 2.1
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "thinking", "thinking": SECRET},
                        {"type": "text", "text": "VERIFIED_FINAL"}]}})
        thought = [s for s in ts.steps if s.kind == "thinking"]
        self.assertEqual(len(thought), 1)
        self.assertEqual(thought[0].text, "")  # draft reasoning never enters the trace
        card = thought[0].render(learning=True)
        self.assertIn("<summary>Thought for 1.6s</summary>", card)
        # The attribute is bare seconds: Open WebUI feeds it to
        # `dayjs.duration(value, 'seconds')`, and "1.6s" humanizes to "a month".
        self.assertIn('duration="1.6"', card)
        self.assertNotIn('duration="1.6s"', card)
        self.assertNotIn(SECRET, card)
        self.assertNotIn(SECRET, repr(ts.steps))

    def test_thinking_duration_attribute_is_bare_seconds(self):
        card = Step(kind="thinking", duration=75.0).render()
        self.assertIn('duration="75.0"', card)
        self.assertIn("<summary>Thought for 75.0s</summary>", card)

    def test_thinking_duration_attribute_defaults_to_zero(self):
        card = Step(kind="thinking").render()
        self.assertIn('duration="0.0"', card)
        self.assertIn("<summary>Thought for 0.0s</summary>", card)

    def test_thinking_text_is_shown_in_a_general_chat(self):
        ts = TurnStream(learning=False)
        ts.feed({"type": "message_start", "message": {"role": "assistant", "stopReason": "pending"}})
        ts.feed({"type": "message_update",
                 "assistantMessageEvent": {"type": "thinking_delta", "delta": SECRET}})
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "thinking", "thinking": "pondering"},
                        {"type": "text", "text": "answer"}]}})
        thought = [s for s in ts.steps if s.kind == "thinking"][0]
        self.assertEqual(thought.text, "pondering")
        card = thought.render(learning=False)
        self.assertIn("pondering", card)

    def test_deltas_never_become_steps(self):
        ts = TurnStream()
        ts.feed({"type": "message_update",
                 "assistantMessageEvent": {"type": "text_delta", "delta": SECRET}})
        ts.feed({"type": "message_update",
                 "assistantMessageEvent": {"type": "thinking_delta", "delta": SECRET}})
        self.assertEqual(ts.steps, [])
        self.assertEqual(render_steps(ts.steps), "")

    def test_steps_keep_stream_order(self):
        ts = TurnStream()
        ts.feed({"type": "tool_execution_start", "toolCallId": "a", "toolName": "bash", "args": {}})
        ts.feed({"type": "tool_execution_end", "toolCallId": "a", "toolName": "bash"})
        ts.feed({"type": "message_start", "message": {"role": "assistant"}})
        ts.feed({"type": "message_update",
                 "assistantMessageEvent": {"type": "thinking_delta", "delta": "x"}})
        ts.feed({"type": "message_end", "message": {
            "role": "assistant", "stopReason": "stop",
            "content": [{"type": "text", "text": "done"}]}})
        ts.feed({"type": "tool_execution_start", "toolCallId": "b", "toolName": "read_file", "args": {}})
        ts.feed({"type": "tool_execution_end", "toolCallId": "b", "toolName": "read_file"})
        self.assertEqual([s.kind for s in ts.steps], ["tool", "thinking", "tool"])


class _FakeOwui:
    """Records POSTed per-message events; answers 200 `true` like Open WebUI."""

    def __init__(self):
        import http.server

        events = self.events = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                n = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(n) if n else b"{}"
                try:
                    body = json.loads(raw)
                except ValueError:
                    body = {}
                events.append((self.path, body))
                payload = b"true"
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def do_GET(self):
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def url(self):
        return f"http://127.0.0.1:{self.port}"

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    def statuses(self, message_id="msg-1"):
        suffix = f"/messages/{message_id}/event"
        return [b for p, b in self.events if p.endswith(suffix)]


class TestLiveSteps(unittest.TestCase):
    def test_learning_turn_shows_actions_not_results(self):
        h = ServerHarness("steps")
        try:
            status, body = h.post(h.body("/lesson next", stream=True), raw=True)
            self.assertEqual(status, 200)
            text = sse_content(body)
            self.assertIn('type="tool_calls"', text)
            self.assertIn("bash", text)
            self.assertIn("ls -la", text)          # the action's input is visible
            self.assertNotIn("file.txt", text)     # the tool's result is not
            self.assertNotIn("wrapping up", text)  # neither is draft reasoning
            self.assertNotIn(SECRET, body)
            self.assertIn("VERIFIED_FINAL", text)
        finally:
            h.stop()

    def test_general_chat_shows_results_and_thinking(self):
        h = ServerHarness("steps")
        try:
            status, data = h.post(h.body("hello"))
            self.assertEqual(status, 200)
            content = data["choices"][0]["message"]["content"]
            self.assertIn("file.txt", content)
            self.assertIn("wrapping up", content)
            self.assertEqual(prose(content), "VERIFIED_FINAL")
        finally:
            h.stop()

    def test_failed_tool_card_streams(self):
        h = ServerHarness("steps_error")
        try:
            status, body = h.post(h.body("/lesson next", stream=True), raw=True)
            self.assertEqual(status, 200)
            self.assertIn('status="failed"', sse_content(body))
        finally:
            h.stop()

    def test_step_card_streams_before_the_turn_settles(self):
        # B-steps-stream-before-settle: the card is on the wire while pi is
        # still running, not after agent_settled.
        h = ServerHarness("steps_slow")
        try:
            req = h.request(h.body("/lesson next", stream=True))
            first_card = final = None
            with urllib.request.urlopen(req, timeout=30) as resp:
                while True:
                    line = resp.readline()
                    if not line:
                        break
                    if not line.startswith(b"data: "):
                        continue
                    payload = line[6:].strip()
                    if payload == b"[DONE]":
                        break
                    rec = json.loads(payload)
                    delta = (rec.get("choices") or [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if "<details" in content and first_card is None:
                        first_card = time.monotonic()
                    if "VERIFIED_FINAL" in content:
                        final = time.monotonic()
            self.assertIsNotNone(first_card, "no step card reached the client")
            self.assertIsNotNone(final, "no post-gate prose reached the client")
            self.assertGreater(final - first_card, 0.4)
        finally:
            h.stop()


class TestStatusEvents(unittest.TestCase):
    def setUp(self):
        self.owui = _FakeOwui()
        self.headers = {"X-OpenWebUI-Chat-Id": "chat-1", "X-OpenWebUI-Message-Id": "msg-1"}

    def tearDown(self):
        self.owui.stop()

    def _wait_done(self, timeout=3.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            events = self.owui.statuses()
            if events and events[-1].get("data", {}).get("done") is True:
                return events
            time.sleep(0.02)
        return self.owui.statuses()

    def test_status_sequence_reports_tools_and_ends_done(self):
        h = ServerHarness("steps_slow", openwebui_base_url=self.owui.url())
        try:
            with mock.patch("bridge.openwebui.read_key", return_value="k"):
                status, _ = h.post(h.body("/lesson next", stream=True), raw=True,
                                   headers=self.headers)
            self.assertEqual(status, 200)
            events = self._wait_done()
            self.assertTrue(events, "no status events were posted")
            self.assertTrue(all(e["type"] == "status" for e in events))
            self.assertFalse(events[0]["data"]["done"])
            self.assertTrue(any("bash" in e["data"]["description"] for e in events))
            self.assertTrue(events[-1]["data"]["done"])
            self.assertNotIn(SECRET, json.dumps(events))
        finally:
            h.stop()

    def test_status_ends_done_after_provider_error(self):
        h = ServerHarness("steps_provider_error", openwebui_base_url=self.owui.url())
        try:
            with mock.patch("bridge.openwebui.read_key", return_value="k"):
                status, text = h.post(h.body("/lesson next", stream=True), raw=True,
                                      headers=self.headers)
            self.assertEqual(status, 200)
            self.assertIn("pi runtime error", text)
            events = self._wait_done()
            self.assertTrue(events)
            self.assertTrue(events[-1]["data"]["done"])
        finally:
            h.stop()

    def test_no_message_id_means_no_status_posts(self):
        h = ServerHarness("steps", openwebui_base_url=self.owui.url())
        try:
            with mock.patch("bridge.openwebui.read_key", return_value="k"):
                status, _ = h.post(h.body("hello"))
            self.assertEqual(status, 200)
            time.sleep(0.2)
            self.assertEqual(self.owui.statuses(), [])
        finally:
            h.stop()


class TestStatusReporter(unittest.TestCase):
    def test_close_always_ends_the_sequence_with_done(self):
        calls = []

        class Recording:
            def post_status(self, chat, message, description, done):
                calls.append((chat, message, description, done))

        reporter = openwebui.StatusReporter(Recording(), "c1", "m1")
        reporter.status("Running bash…")
        reporter.close()
        deadline = time.time() + 2.0
        while len(calls) < 2 and time.time() < deadline:
            time.sleep(0.01)
        self.assertEqual(calls[0][:2], ("c1", "m1"))
        self.assertIn("bash", calls[0][2])
        self.assertTrue(calls[-1][3])

    def test_close_without_any_status_posts_nothing(self):
        calls = []

        class Recording:
            def post_status(self, *a):
                calls.append(a)

        reporter = openwebui.StatusReporter(Recording(), "c1", "m1")
        reporter.close()
        time.sleep(0.1)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()