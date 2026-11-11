#!/usr/bin/env python3
"""_root.py — the one place that decides which learning-state tree to read.

Resolution priority, highest first:

  1. an explicit argument (`--root`, `STATE_ROOT`, ...)
  2. the `LEARNING_SYSTEM_ROOT` environment variable
  3. `<layer>/state` — the in-repo state tree next to this layer

There is no further fallback: if the resolved directory lacks
`Learning System/Core`, resolution fails closed with `StateRootError` instead of
silently reading an unrelated or stale path.

`state/scripts/ops.py` is intentionally NOT a consumer: it runs inside the Open
WebUI container, where the state tree is mounted elsewhere, so it resolves its
own root from that mount.
"""

from __future__ import annotations

import os
from pathlib import Path

LAYER_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_ROOT = LAYER_ROOT / "state"

ENV_VAR = "LEARNING_SYSTEM_ROOT"
REQUIRED_DIR = Path("Learning System") / "Core"


class StateRootError(ValueError):
    """No usable learning-state tree at the resolved path."""


def resolve_state_root(explicit: str | None = None) -> Path:
    """Return the learning-state root: explicit > env > `<layer>/state`."""
    candidate = explicit or os.environ.get(ENV_VAR) or str(DEFAULT_STATE_ROOT)
    root = Path(candidate).expanduser()
    if (root / REQUIRED_DIR).is_dir():
        return root
    raise StateRootError(
        f"not a learning-state root: {root} (need '{REQUIRED_DIR}'); "
        f"pass --root or set {ENV_VAR}"
    )
