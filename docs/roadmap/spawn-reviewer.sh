#!/usr/bin/env bash
# Spawn a per-checkpoint reviewer in a new Herdr tab, on the Muse Spark model.
#
#   spawn-reviewer.sh <P0|P1|P2|P3>
#
# Reviewers are review-only: they inspect the changes for their checkpoint and
# write findings to docs/roadmap/reviews/<CP>.md. They must not edit code or
# spawn further agents.
set -euo pipefail

CP="${1:?usage: spawn-reviewer.sh <P0|P1|P2|P3>}"
ROOT="/home/delightaheebwa/learning-pi"
BRIEF="$ROOT/docs/roadmap/reviews/R-${CP}.md"
NAME="roadmap-r-$(printf '%s' "$CP" | tr '[:upper:]' '[:lower:]')"
MODEL="opencode-go/muse-spark-1.3-contributor"

if [ "${HERDR_ENV:-}" != "1" ]; then
  echo "ERROR: not running inside a Herdr-managed pane (HERDR_ENV != 1)" >&2
  exit 1
fi
if [ ! -f "$BRIEF" ]; then
  echo "ERROR: missing reviewer brief: $BRIEF" >&2
  exit 1
fi

TAB_JSON="$(herdr tab create --cwd "$ROOT" --label "review $CP" --no-focus)"
PANE="$(printf '%s' "$TAB_JSON" | jq -r '.result.root_pane.pane_id // .result.pane.pane_id // .result.root_pane // empty')"
if [ -z "$PANE" ] || [ "$PANE" = "null" ]; then
  echo "ERROR: could not parse pane id from: $TAB_JSON" >&2
  exit 1
fi

herdr agent start "$NAME" --kind opencode --pane "$PANE" -- --auto --model "$MODEL" >/dev/null
bash "$ROOT/docs/roadmap/prompt-agent.sh" "$NAME" "$BRIEF"

echo "spawned reviewer $NAME in pane $PANE (tab 'review $CP', model $MODEL)"
