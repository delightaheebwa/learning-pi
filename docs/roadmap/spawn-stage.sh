#!/usr/bin/env bash
# Spawn the next stage of the roadmap cascade in a new Herdr tab.
#
#   spawn-stage.sh <P1|P2|P3|REVIEW|E2E> [model]
#
# Creates a new tab in the current Herdr workspace, starts a fresh `opencode`
# agent (auto-approving, so the cascade runs unattended), and sends it that
# stage's brief. Optional 2nd arg sets the model id (e.g.
# opencode-go/muse-spark-1.3-contributor); default is the agent default.
# The caller should finish its own turn immediately after.
set -euo pipefail

STAGE="${1:?usage: spawn-stage.sh <P1|P2|P3|REVIEW|E2E> [model]}"
MODEL="${2:-}"
ROOT="/home/delightaheebwa/learning-pi"
BRIEF="$ROOT/docs/roadmap/${STAGE}.md"
NAME="roadmap-$(printf '%s' "$STAGE" | tr '[:upper:]' '[:lower:]')"

if [ "${HERDR_ENV:-}" != "1" ]; then
  echo "ERROR: not running inside a Herdr-managed pane (HERDR_ENV != 1)" >&2
  exit 1
fi
if [ ! -f "$BRIEF" ]; then
  echo "ERROR: missing brief: $BRIEF" >&2
  exit 1
fi

TAB_JSON="$(herdr tab create --cwd "$ROOT" --label "roadmap $STAGE" --no-focus)"
PANE="$(printf '%s' "$TAB_JSON" | jq -r '.result.root_pane.pane_id // .result.pane.pane_id // .result.root_pane // empty')"
if [ -z "$PANE" ] || [ "$PANE" = "null" ]; then
  echo "ERROR: could not parse pane id from: $TAB_JSON" >&2
  exit 1
fi

if [ -n "$MODEL" ]; then
  herdr agent start "$NAME" --kind opencode --pane "$PANE" -- --auto --model "$MODEL" >/dev/null
else
  herdr agent start "$NAME" --kind opencode --pane "$PANE" -- --auto >/dev/null
fi
herdr agent prompt "$NAME" "$(cat "$BRIEF")"

echo "spawned $NAME in pane $PANE (tab 'roadmap $STAGE')${MODEL:+ model=$MODEL}"
