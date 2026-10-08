#!/usr/bin/env bash
# Reliably deliver a brief to a just-started Herdr agent.
#
#   prompt-agent.sh <agent-name> <brief-path>
#
# `herdr agent start` can return before the agent's TUI input is ready, so a
# prompt sent immediately is sometimes dropped (the agent stays on its welcome
# screen). This waits for idle, sends the brief, and retries until the agent
# actually starts working.
set -uo pipefail

NAME="${1:?usage: prompt-agent.sh <agent-name> <brief-path>}"
BRIEF="${2:?usage: prompt-agent.sh <agent-name> <brief-path>}"
[ -f "$BRIEF" ] || { echo "ERROR: missing brief: $BRIEF" >&2; exit 1; }

status() { herdr agent get "$NAME" 2>/dev/null | jq -r '.result.agent.agent_status // empty' 2>/dev/null; }

for attempt in 1 2 3 4 5; do
  # Wait for a settled idle state before sending.
  for _ in $(seq 1 20); do
    st="$(status)"
    [ "$st" = "idle" ] && break
    [ "$st" = "working" ] && { echo "prompt accepted (already working)"; exit 0; }
    [ "$st" = "blocked" ] && break
    sleep 1
  done
  herdr agent send-keys "$NAME" ctrl+u >/dev/null 2>&1 || true
  sleep 1
  herdr agent prompt "$NAME" "$(cat "$BRIEF")" >/dev/null 2>&1 || true
  for _ in $(seq 1 15); do
    st="$(status)"
    if [ "$st" = "working" ] || [ "$st" = "blocked" ]; then
      echo "prompt accepted ($st)"
      exit 0
    fi
    sleep 1
  done
  echo "attempt $attempt: agent still '${st:-unknown}'; retrying" >&2
done

echo "ERROR: could not deliver brief to $NAME after 5 attempts" >&2
exit 1
