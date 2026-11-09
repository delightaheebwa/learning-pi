#!/usr/bin/env python3
"""Tests for the OpenUI widget static assets and the gate's visual-fence carve-out.

Run: python3 -m unittest scripts.openui_test -v

`gate_pipe` imports `pydantic`; install it (`pip install pydantic`) before running.
"""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Skills" / "learning-review" / "openwebui"))

from scripts import setup_openwebui as s  # noqa: E402

try:
    import gate_pipe  # noqa: E402
except ImportError as exc:  # pragma: no cover - depends on the environment
    gate_pipe = None
    _GATE_IMPORT_ERROR = exc
else:
    _GATE_IMPORT_ERROR = None


class TestGateVisualFenceCarveOut(unittest.TestCase):
    def setUp(self):
        if gate_pipe is None:
            self.skipTest(f"gate_pipe unavailable: {_GATE_IMPORT_ERROR}")

    def test_visual_fences_are_excluded_from_binding(self):
        text = (
            "Before the figure.\n"
            "```openui\nroot = Card([])\n```\n"
            "Between.\n"
            "```mermaid\ngraph TD\n```\n"
            "```html\n<p>free form</p>\n```\n"
            "After the figure."
        )
        norm = gate_pipe._normalize_for_binding(text)
        self.assertIn("before the figure.", norm)
        self.assertIn("between.", norm)
        self.assertIn("after the figure.", norm)
        self.assertNotIn("root = card", norm)
        self.assertNotIn("graph td", norm)
        self.assertNotIn("free form", norm)

    def test_fence_language_with_info_string_is_carved(self):
        text = 'A\n```openui title="x"\nroot = Card([])\n```\nB'
        self.assertEqual(gate_pipe._normalize_for_binding(text), "a b")

    def test_plain_text_and_katex_still_normalize(self):
        self.assertEqual(gate_pipe._normalize_for_binding("  A  \\(x\\)  B  "), "a x b")

    def test_non_visual_fences_are_kept(self):
        text = "A\n```python\nprint(1)\n```\nB"
        norm = gate_pipe._normalize_for_binding(text)
        self.assertIn("print(1)", norm)


class TestOpenUiStaticAssets(unittest.TestCase):
    def test_origins_include_both_loopback_spellings(self):
        self.assertEqual(
            s.openui_script_origins("http://localhost:3000"),
            ["http://127.0.0.1:3000", "http://localhost:3000"],
        )

    def test_shell_csp_locks_network_and_names_origins(self):
        html = s.build_widget_html(s.openui_script_origins("http://localhost:3000"))
        self.assertIn("default-src 'none'", html)
        self.assertIn("connect-src 'none'", html)
        self.assertIn("script-src http://127.0.0.1:3000 http://localhost:3000", html)
        self.assertIn('src="widget.js"', html)
        self.assertIn("dist/openui-styles.css", html)

    def test_shell_follows_os_theme(self):
        # No hardcoded light theme: the bundle's own prefers-color-scheme media
        # query applies until widget.js pins data-openui-theme to the OS value.
        html = s.build_widget_html(s.openui_script_origins("http://localhost:3000"))
        self.assertIn("color-scheme: light dark", html)
        self.assertNotIn('data-openui-theme="light"', html)
        self.assertIn("prefers-color-scheme", s.OPENUI_WIDGET_JS)
        self.assertIn("applyTheme", s.OPENUI_WIDGET_JS)

    def test_shell_has_accessible_focus_and_invalid_state(self):
        html = s.build_widget_html(s.openui_script_origins("http://localhost:3000"))
        self.assertIn(":focus-visible", html)
        self.assertIn(":user-invalid", html)
        self.assertIn('aria-invalid="true"', html)

    def test_shell_copy_falls_back_when_clipboard_is_denied(self):
        js = s.OPENUI_WIDGET_JS
        self.assertIn("legacyCopy", js)
        self.assertIn("execCommand", js)
        self.assertIn("Copy details", js)
        self.assertIn("openui-toast", s.OPENUI_WIDGET_HTML)

    def test_height_tracks_resize_fonts_and_disclosure(self):
        js = s.OPENUI_WIDGET_JS
        self.assertIn("ResizeObserver", js)
        self.assertIn('"toggle"', js)
        self.assertIn("document.fonts.ready", js)

    def test_install_writes_shell_and_verifies_pinned_hashes(self):
        blobs = {"dist/openui-bundle.min.js": b"JS", "dist/openui-styles.css": b"CSS"}
        with tempfile.TemporaryDirectory() as tmp:
            ver = os.path.join(tmp, s.OPENUI_BUNDLE_VERSION)
            for rel, body in blobs.items():
                dest = os.path.join(ver, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as fh:
                    fh.write(body)
            pinned = {rel: hashlib.sha256(body).hexdigest() for rel, body in blobs.items()}
            with mock.patch.object(s, "OPENUI_BUNDLE_SHA256", pinned):
                ok = s.install_openui_static(tmp, "http://127.0.0.1:3000")
            self.assertTrue(ok)
            shell = Path(ver, "widget.html").read_text(encoding="utf-8")
            self.assertIn("http://127.0.0.1:3000", shell)
            self.assertEqual(Path(ver, "widget.js").read_text(encoding="utf-8"), s.OPENUI_WIDGET_JS)

    def test_install_reports_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                s, "OPENUI_BUNDLE_SHA256", {"dist/openui-bundle.min.js": "deadbeef"}
            ), mock.patch.object(s, "_download_openui_bundle", side_effect=OSError("offline")):
                ok = s.install_openui_static(tmp, "http://127.0.0.1:3000")
            self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
