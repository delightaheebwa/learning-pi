"""pi-bridge — expose the pinned pi runtime as an OpenAI-compatible endpoint.

Open WebUI is the face; pi (with the learning-gate, subagents, and skills) is
the brain. This package is the only new moving part: it runs `pi --mode rpc`,
translates one Open WebUI chat turn into one pi prompt, and streams the
post-gate assistant turn back.

Design constraints proven by the Phase 0 spike (see `README.md`):
  * assistant text comes ONLY from `message_end` (the gate's withheld banner or
    the verified turn); `message_update` deltas are never forwarded because they
    carry the raw, pre-verification draft;
  * a single pi session per chat, only the newest user message is forwarded;
  * `--bash-guard-disabled` keeps routine work flowing while the catastrophic
    command floor stays up.
"""

__all__ = ["__version__"]
__version__ = "0.1.0"
