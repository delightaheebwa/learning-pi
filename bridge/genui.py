"""Render an OpenUI Lang payload as a self-contained widget document.

Open WebUI's Rich UI `embeds` are iframe **URLs**, so the bridge wraps each
verified ` ```openui ` payload in a small HTML shell and delivers it as a
`data:` URL (Phase 3 switches to a same-origin static asset). The shell:

  * loads the pinned, self-hosted `@openuidev/browser-bundle` IIFE (exposing
    `window.__OpenUI`) plus its stylesheet from `bundle_base`;
  * renders the payload with `OpenUI.Renderer` and the chat component library;
  * reports its height to Open WebUI (`iframe:height`) so the embed sizes to
    its content;
  * forwards widget actions (`onAction`) and follow-up clicks as
    `input:prompt:submit`, which Open WebUI shows as a confirm dialog before a
    new gated learner turn — the payload carries the selected values.

This is an original implementation written against the MIT OpenUI Lang spec and
bundle. It was *informed* by the rendering contract of thesysdev/openwebui-plugin
(which has no license and is therefore not vendored), but shares no code with it.
"""
from __future__ import annotations

import base64
import json
import re

# Pinned per docs/plans/intelligent-ui/PHASE0-FINDINGS.md (bundle 0.2.1, MIT).
OPENUI_BUNDLE_VERSION = "0.2.1"
# Open WebUI static mount the installer writes the pinned bundle into.
OPENUI_STATIC_PATH = "/static/openui"


def default_bundle_base(openwebui_base_url: str) -> str:
    """Absolute same-origin URL of the self-hosted pinned bundle."""
    return f"{openwebui_base_url.rstrip('/')}{OPENUI_STATIC_PATH}/{OPENUI_BUNDLE_VERSION}"


def _json_for_script(value: str) -> str:
    """JSON-encode a string for a `<script>` body without breaking out of it."""
    return (
        json.dumps(value)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _attr(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _csp_origin(bundle_base: str) -> str:
    m = re.match(r"^(https?://[^/]+)", bundle_base or "")
    return m.group(1) if m else ""


def build_widget_document(
    payload: str,
    *,
    bundle_base: str,
    title: str = "Visual",
    theme: str = "light",
) -> str:
    """Return the HTML document that renders `payload` in an iframe embed."""
    safe_title = _attr(title)
    safe_theme = "dark" if str(theme).lower() == "dark" else "light"
    bundle = _attr(bundle_base.rstrip("/"))
    origin = _csp_origin(bundle_base)
    csp = "default-src 'none'; " f"script-src 'unsafe-inline' {origin}; " f"style-src 'unsafe-inline' {origin}; " f"img-src data:; " f"font-src {origin} data:; " f"connect-src 'none'; " "base-uri 'none'; " "form-action 'none'"
    payload_json = _json_for_script(payload)
    return f"""<!doctype html>
<html lang="en" data-theme="{safe_theme}" data-openui-theme="{safe_theme}" style="color-scheme:{safe_theme}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<title>{safe_title}</title>
<link rel="stylesheet" href="{bundle}/dist/openui-styles.css">
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; background: transparent; color-scheme: {safe_theme}; }}
  body {{ padding: 4px; }}
  #openui-root {{ width: 100%; }}
  .openui-status {{ padding: 16px; font: 13px system-ui, -apple-system, sans-serif; color: #888; }}
  .openui-error {{ padding: 14px; border: 1px solid #fecaca; border-radius: 8px; background: #fef2f2; color: #b91c1c; font: 13px/1.5 system-ui, sans-serif; white-space: pre-wrap; }}
</style>
</head>
<body>
<div id="openui-root"><div class="openui-status">Loading…</div></div>
<script>
(function () {{
  var bundle = {_json_for_script(bundle_base.rstrip("/"))};
  function postToParent(message) {{
    var origin = '*';
    try {{ if (document.referrer) origin = new URL(document.referrer).origin; }} catch (e) {{}}
    try {{ parent.postMessage(message, origin); }} catch (e) {{}}
  }}
  var last = 0, raf = 0;
  function reportHeight() {{
    var h = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
    if (h === last) return;
    last = h;
    postToParent({{ type: 'iframe:height', height: h }});
  }}
  function schedule() {{
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(reportHeight);
  }}
  function sendPrompt(text) {{
    if (!text) return;
    postToParent({{ type: 'input:prompt:submit', text: String(text) }});
  }}
  function openLink(url) {{
    try {{
      var u = new URL(String(url || ''), window.location.href);
      if (!/^(https?|mailto|tel):$/.test(u.protocol)) return;
      var w = window.open(u.href, '_blank', 'noopener,noreferrer');
      if (w) w.opener = null;
    }} catch (e) {{}}
  }}
  function renderError(message) {{
    var el = document.getElementById('openui-root');
    el.textContent = '';
    var box = document.createElement('div');
    box.className = 'openui-error';
    box.textContent = 'Widget failed to render: ' + (message || 'unknown error');
    el.appendChild(box);
    reportHeight();
  }}
  function handleAction(event) {{
    event = event || {{}};
    if (event.type === 'open_url') {{
      openLink(event.params && event.params.url);
      return;
    }}
    var prompt = event.humanFriendlyMessage || (event.params && event.params.message) || '';
    if (event.formState && Object.keys(event.formState).length > 0) {{
      var rows = Object.keys(event.formState).map(function (k) {{
        return k + ': ' + JSON.stringify(event.formState[k]);
      }});
      prompt = (prompt ? prompt + '\\n\\n' : '') + 'Form data:\\n' + rows.join('\\n');
    }}
    if (prompt) sendPrompt(prompt);
  }}
  var script = document.createElement('script');
  script.src = bundle + '/dist/openui-bundle.min.js';
  script.onload = function () {{
    try {{
      var O = window.__OpenUI;
      if (!O || !O.Renderer || !O.openuiChatLibrary || !O.createRoot) {{
        throw new Error('bundle loaded but its exports are missing');
      }}
      var container = document.getElementById('openui-root');
      container.textContent = '';
      O.createRoot(container).render(
        O.React.createElement(O.Renderer, {{
          response: {payload_json},
          library: O.openuiChatLibrary,
          isStreaming: false,
          onAction: handleAction
        }})
      );
      setTimeout(reportHeight, 400);
      setTimeout(reportHeight, 1500);
    }} catch (err) {{
      renderError(err && err.message ? err.message : String(err));
    }}
  }};
  script.onerror = function () {{ renderError('could not load ' + script.src); }};
  document.body.appendChild(script);
  window.addEventListener('load', reportHeight);
  window.addEventListener('resize', schedule);
  new MutationObserver(schedule).observe(document.body, {{ childList: true, subtree: true }});
  reportHeight();
}})();
</script>
</body>
</html>"""


def data_url(html: str) -> str:
    """A `data:` URL for a widget document (embeds take a URL, not HTML)."""
    b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
    return "data:text/html;base64," + b64


def widget_embed_url(
    payload: str,
    *,
    bundle_base: str,
    title: str = "Visual",
    theme: str = "light",
) -> str:
    """Build a deliverable embed URL for a verified OpenUI payload."""
    return data_url(build_widget_document(payload, bundle_base=bundle_base, title=title, theme=theme))
