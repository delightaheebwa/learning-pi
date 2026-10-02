#!/usr/bin/env bash
# pi_review_status_test.sh — boundary tests for bin/pi-review-status.
#
# Run directly:  bash test/pi_review_status_test.sh
# Exit 0 on success. Uses a throwaway LEARNING_SYSTEM_ROOT and the
# REVIEW_STATUS_DATE / REVIEW_STATUS_NOW hooks, so it never touches real state.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$HERE/../bin/pi-review-status"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/pi-review-status.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

SESSIONS="$TMP/Learning System/Sessions"
mkdir -p "$SESSIONS"
export LEARNING_SYSTEM_ROOT="$TMP"

TODAY="2026-10-02"
YESTERDAY="2026-10-01"

FAILED=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; FAILED=1; }

check_status() { # expected_exit date name
  "$BIN" --check "$2" >/dev/null 2>&1
  local got=$?
  if [[ "$got" == "$1" ]]; then
    pass "check $3 ($2)"
  else
    fail "check $3 ($2): expected exit $1, got $got"
  fi
}

json_field() { # json key -> value
  printf '%s' "$1" | sed -E 's/.*"'"$2"'":"?([^",}]+)"?.*/\1/'
}

json_done() { # json -> true/false
  printf '%s' "$1" | grep -q '"done":true' && echo true || echo false
}

assert_json() { # name json field expected
  local got
  got="$(json_field "$2" "$3")"
  if [[ "$got" == "$4" ]]; then
    pass "$1"
  else
    fail "$1: $3 expected '$4', got '$got' (json: $2)"
  fi
}

assert_done() { # name json expected
  local got
  got="$(json_done "$2")"
  if [[ "$got" == "$3" ]]; then
    pass "$1"
  else
    fail "$1: done expected '$3', got '$got' (json: $2)"
  fi
}

# --- --check ----------------------------------------------------------------
check_status 1 "$TODAY" "no note"
touch "$SESSIONS/Session — Review — $TODAY.md"
check_status 0 "$TODAY" "plain review note"
check_status 1 "$YESTERDAY" "unrelated date"

touch "$SESSIONS/Session — Review (5-concept) — $YESTERDAY.md"
check_status 0 "$YESTERDAY" "5-concept review note"

mkdir "$SESSIONS/Session — Review — 2026-09-30.md"
check_status 1 "2026-09-30" "directory does not count"

# --- JSON phases ------------------------------------------------------------
j="$(REVIEW_STATUS_DATE="$TODAY" REVIEW_STATUS_NOW=10:00 "$BIN")"
assert_json "day phase" "$j" phase day
assert_json "day target" "$j" date "$TODAY"
assert_done "day done" "$j" true

j="$(REVIEW_STATUS_DATE="$TODAY" REVIEW_STATUS_NOW=18:30 "$BIN")"
assert_json "evening phase" "$j" phase evening
assert_json "evening target" "$j" date "$TODAY"

j="$(REVIEW_STATUS_DATE="$TODAY" REVIEW_STATUS_NOW=22:59 "$BIN")"
assert_json "late evening phase" "$j" phase evening

j="$(REVIEW_STATUS_DATE="$TODAY" REVIEW_STATUS_NOW=23:00 "$BIN")"
assert_json "23:00 catchup" "$j" phase catchup
assert_json "23:00 target today" "$j" date "$TODAY"

j="$(REVIEW_STATUS_DATE="$TODAY" REVIEW_STATUS_NOW=01:00 "$BIN")"
assert_json "01:00 catchup" "$j" phase catchup
assert_json "01:00 target yesterday" "$j" date "$YESTERDAY"
assert_done "01:00 yesterday done" "$j" true

j="$(REVIEW_STATUS_DATE="$TODAY" REVIEW_STATUS_NOW=03:59 "$BIN")"
assert_json "03:59 catchup" "$j" phase catchup
assert_json "03:59 target yesterday" "$j" date "$YESTERDAY"

j="$(REVIEW_STATUS_DATE="$TODAY" REVIEW_STATUS_NOW=04:00 "$BIN")"
assert_json "04:00 day" "$j" phase day
assert_json "04:00 target today" "$j" date "$TODAY"

# --- invalid input ----------------------------------------------------------
"$BIN" --check "not-a-date" >/dev/null 2>&1
[[ $? == 2 ]] && pass "rejects bad date" || fail "should reject bad date"

echo
if [[ "$FAILED" == 0 ]]; then echo "pi-review-status: OK"; else echo "pi-review-status: FAILED"; fi
exit "$FAILED"
