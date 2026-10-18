#!/usr/bin/env python3
"""Phase 0 live spike for the intelligent-ui plan.

Verifies, against a running Open WebUI, the two claims the plan depends on:

  1. A second assistant message can be appended to an existing chat over REST
     (`POST /api/v1/chats/{id}`), and an `embeds` event attached to *that*
     message (`POST /api/v1/chats/{id}/messages/{message_id}/event`) persists
     and renders BELOW the prose message.
  2. A follow-up button inside the embedded document reaches Open WebUI's
     `input:prompt:submit` handler and shows the "Confirm Prompt from Embed"
     dialog.

Auth: an Open WebUI API key (Settings -> Account -> API Keys), read from
`~/.openwebui_key` or `$OPENWEBUI_API_KEY` (or --key/--key-file). The key's
user must own the created chat.

Usage:
    python3 scripts/spike_embeds_live.py \
        --base-url http://127.0.0.1:3000 [--model learning] [--dry-run]

This is a throwaway diagnostic; it creates one chat and prints its URL. Nothing
else is written.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

WIDGET_HTML = """<!doctype html>
<html>
  <head><meta charset="utf-8"><title>openui spike widget</title></head>
  <body style="font:14px system-ui;padding:16px">
    <p id="status">Phase 0 spike widget.</p>
    <button id="go" style="padding:6px 12px">Ask a follow-up</button>
    <script>
      const report = () => {
        const h = document.documentElement.scrollHeight;
        try { parent.postMessage({ type: 'iframe:height', height: h }, '*'); } catch (e) {}
      };
      document.getElementById('go').addEventListener('click', () => {
        parent.postMessage(
          { type: 'input:prompt:submit', text: 'spike: follow-up from embed' },
          '*'
        );
      });
      new ResizeObserver(report).observe(document.documentElement);
      report();
    </script>
  </body>
</html>
"""


def data_url(html: str) -> str:
    b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
    return "data:text/html;base64," + b64


class Client:
    def __init__(self, base_url: str, key: str):
        self.base = base_url.rstrip("/")
        self.key = key

    def call(self, method: str, path: str, body: dict | None = None):
        url = self.base + path
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", "Bearer " + self.key)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = raw.decode("utf-8", "replace")
            return e.code, parsed


def now() -> int:
    return int(time.time())


def assistant_node(mid: str, parent: str, model: str, content: str) -> dict:
    return {
        "id": mid,
        "parentId": parent,
        "childrenIds": [],
        "role": "assistant",
        "content": content,
        "model": model,
        "modelName": model,
        "modelIdx": 0,
        "done": True,
        "timestamp": now(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default=os.environ.get("OPENWEBUI_BASE_URL", "http://127.0.0.1:3000"))
    ap.add_argument("--key", default=os.environ.get("OPENWEBUI_API_KEY", ""))
    ap.add_argument("--key-file", default=os.path.expanduser("~/.openwebui_key"))
    ap.add_argument("--model", default="learning")
    ap.add_argument("--widget-url", default="", help="hosted wrapper URL; default is an inline data: URL")
    ap.add_argument("--dry-run", action="store_true", help="print the payloads without calling the API")
    args = ap.parse_args()

    key = args.key
    if not key:
        try:
            with open(args.key_file) as fh:
                key = fh.read().strip()
        except OSError:
            key = ""
    if not key and not args.dry_run:
        print(f"ERROR: no API key (set OPENWEBUI_API_KEY or write {args.key_file})", file=sys.stderr)
        return 2

    uid, prose, widget = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    widget_url = args.widget_url or data_url(WIDGET_HTML)

    chat_body = {
        "chat": {
            "title": "intelligent-ui Phase 0 spike",
            "models": [args.model],
            "history": {
                "messages": {
                    uid: {
                        "id": uid, "parentId": None, "childrenIds": [prose],
                        "role": "user", "content": "Phase 0 spike seed", "timestamp": now(),
                    },
                    prose: assistant_node(prose, uid, args.model, "Prose message (the widget should render below this)."),
                    widget: assistant_node(widget, prose, args.model, ""),
                },
                "currentId": widget,
            },
            "messages": [],
            "params": {},
            "files": [],
        }
    }
    embed_event = {"type": "embeds", "data": {"embeds": [widget_url]}}

    if args.dry_run:
        print("POST /api/v1/chats/new\n" + json.dumps({"chat": {}}, indent=2))
        print("\nPOST /api/v1/chats/{id}\n" + json.dumps(chat_body, indent=2))
        print("\nPOST /api/v1/chats/{id}/messages/%s/event\n%s" % (widget, json.dumps(embed_event, indent=2)))
        return 0

    c = Client(args.base_url, key)

    status, new_chat = c.call("POST", "/api/v1/chats/new", {"chat": {}})
    if status != 200 or not isinstance(new_chat, dict) or not new_chat.get("id"):
        print(f"FAIL create chat: HTTP {status}: {new_chat}", file=sys.stderr)
        return 1
    chat_id = new_chat["id"]
    print(f"created chat: {chat_id}")

    status, updated = c.call("POST", f"/api/v1/chats/{chat_id}", chat_body)
    if status != 200:
        print(f"FAIL append messages: HTTP {status}: {updated}", file=sys.stderr)
        return 1

    status, ok = c.call("POST", f"/api/v1/chats/{chat_id}/messages/{widget}/event", embed_event)
    if status != 200 or ok is not True:
        print(f"FAIL attach embed: HTTP {status}: {ok}", file=sys.stderr)
        return 1

    status, fetched = c.call("GET", f"/api/v1/chats/{chat_id}")
    msgs = ((fetched or {}).get("chat") or {}).get("history", {}).get("messages", {}) if status == 200 else {}
    embeds = (msgs.get(widget) or {}).get("embeds") if isinstance(msgs, dict) else None
    if not embeds:
        print("FAIL persistence: no embeds on the widget message after GET", file=sys.stderr)
        print(json.dumps((fetched or {}).get("chat"), indent=2)[:2000], file=sys.stderr)
        return 1

    print("PASS persistence: embeds attached to the second assistant message")
    print()
    print("Now open this URL in a browser and check manually:")
    print(f"  {args.base_url}/c/{chat_id}")
    print("  1. the widget renders BELOW the prose message;")
    print("  2. reload the page — the widget is still there;")
    print('  3. click "Ask a follow-up" -> a "Confirm Prompt from Embed" dialog appears.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
