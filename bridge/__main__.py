"""CLI entrypoint: `python -m bridge [options]`."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .server import BridgeConfig, serve

DEFAULT_PI = str(Path.home() / "learning-pi" / "bin" / "pi")
DEFAULT_STATE = str(Path.home() / "learning-system")
DEFAULT_MODELS = "learning,learning-tutor,learning-review,learning-teach,learning-ingest"


def _api_key(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = os.environ.get("PI_BRIDGE_API_KEY")
    if env:
        return env
    keyfile = Path(os.environ.get("PI_BRIDGE_KEY_FILE", str(Path.home() / ".pi-bridge-key")))
    if keyfile.is_file():
        return keyfile.read_text(encoding="utf-8").strip()
    return ""


def build_config(argv=None) -> BridgeConfig:
    ap = argparse.ArgumentParser(prog="pi-bridge", description="OpenAI-compatible bridge to pi")
    ap.add_argument("--pi-bin", default=os.environ.get("PI_BRIDGE_PI_BIN", DEFAULT_PI))
    ap.add_argument("--state-repo", default=os.environ.get("PI_BRIDGE_STATE_REPO", DEFAULT_STATE))
    ap.add_argument("--host", default=os.environ.get("PI_BRIDGE_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("PI_BRIDGE_PORT", "8790")))
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--models", default=os.environ.get("PI_BRIDGE_MODELS", DEFAULT_MODELS))
    ap.add_argument("--timeout", type=float, default=float(os.environ.get("PI_BRIDGE_TIMEOUT", "900")))
    ap.add_argument("--max-sessions", type=int, default=int(os.environ.get("PI_BRIDGE_MAX_SESSIONS", "8")))
    ap.add_argument("--agent-dir", default=os.environ.get("PI_BRIDGE_AGENT_DIR"))
    ap.add_argument("--session-dir", default=os.environ.get("PI_BRIDGE_SESSION_DIR"))
    ap.add_argument("--ledger-dir", default=os.environ.get("PI_BRIDGE_LEDGER_DIR"))
    ap.add_argument(
        "--allow-bash-guard",
        action="store_true",
        help="do NOT pass --bash-guard-disabled (default keeps the catastrophic floor only)",
    )
    args = ap.parse_args(argv)

    key = _api_key(args.api_key)
    if not key:
        ap.error(
            "no API key: set --api-key, PI_BRIDGE_API_KEY, or write ~/.pi-bridge-key "
            "(the bridge drives a real shell; it will not run unauthenticated)"
        )
    return BridgeConfig(
        pi_bin=args.pi_bin,
        state_repo=args.state_repo,
        api_key=key,
        host=args.host,
        port=args.port,
        timeout=args.timeout,
        models=[m.strip() for m in args.models.split(",") if m.strip()],
        agent_dir=args.agent_dir,
        session_dir=args.session_dir,
        ledger_dir=args.ledger_dir,
        disable_bash_guard=not args.allow_bash_guard,
        max_sessions=args.max_sessions,
    )


def main(argv=None) -> int:
    config = build_config(argv)
    print(
        f"pi-bridge listening on http://{config.host}:{config.port} "
        f"(models: {', '.join(config.models)}; state: {config.state_repo})",
        file=sys.stderr,
    )
    serve(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
