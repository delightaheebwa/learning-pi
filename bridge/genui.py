"""Build the embed URL for a verified OpenUI Lang widget.

Open WebUI Rich UI `embeds` are iframe URLs, and its ``FullHeightIframe`` only
treats an ``http(s)://`` (or protocol-relative) string as a URL — a ``data:``
URL is treated as raw HTML and rendered as literal text. So the widget cannot be
a self-contained ``data:`` document. Instead:

  * the shell document, the pinned OpenUI bundle, and its stylesheet are all
    self-hosted same-origin as Open WebUI static assets (written by
    ``learning-system/scripts/setup_openwebui.py``); and
  * this module builds the embed URL ``{bundle_base}/widget.html#<payload>``. The
    verified payload rides in the URL fragment (not an HTTP request body; it is
    persisted as chat embed metadata alongside the transcript). The shell decodes
    it, renders it with ``window.__OpenUI``, reports its height
    (``iframe:height``) and forwards widget actions / follow-ups as
    ``input:prompt:submit`` (Open WebUI shows a confirm dialog, then starts a new
    gated learner turn).

The payload is declarative OpenUI Lang (no script, no network), so a data-only
fragment is safe. See ``docs/plans/intelligent-ui/`` for the design.
"""
from __future__ import annotations

import base64

# Pinned per docs/plans/intelligent-ui/PHASE0-FINDINGS.md (bundle 0.2.1, MIT).
OPENUI_BUNDLE_VERSION = "0.2.1"
# Open WebUI static mount the installer writes the pinned bundle into.
OPENUI_STATIC_PATH = "/static/openui"
# The self-hosted shell document (installer-written) that the embed points at.
OPENUI_WIDGET_FILE = "widget.html"


def default_bundle_base(openwebui_base_url: str) -> str:
    """Absolute same-origin URL of the self-hosted pinned bundle + shell."""
    return f"{openwebui_base_url.rstrip('/')}{OPENUI_STATIC_PATH}/{OPENUI_BUNDLE_VERSION}"


def payload_fragment(payload: str) -> str:
    """URL-safe (unpadded) base64 of the payload — safe to place in a fragment."""
    encoded = base64.urlsafe_b64encode((payload or "").encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def widget_embed_url(payload: str, *, bundle_base: str) -> str:
    """Deliverable embed URL for a verified OpenUI payload."""
    return f"{bundle_base.rstrip('/')}/{OPENUI_WIDGET_FILE}#" + payload_fragment(payload)
