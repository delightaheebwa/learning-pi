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

DONE_DATE="2026-10-02"
MISS_DATE="2026-09-29"

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

assert_json() { # name json field expected
  local got
  got="$(json_field "$2" "$3")"
  if [[ "$got" == "$4" ]]; then
    pass "$1"
  else
    fail "$1: $3 expected '$4', got '$got' (json: $2)"
  fi
}

at() { # date hour:min -> json
  REVIEW_STATUS_DATE="$1" REVIEW_STATUS_NOW="$2" "$BIN"
}

# --- --check ----------------------------------------------------------------
check_status 1 "$DONE_DATE" "no note"
touch "$SESSIONS/Session — Review — $DONE_DATE.md"
check_status 0 "$DONE_DATE" "plain review note"
check_status 1 "$MISS_DATE" "no note on another date"

touch "$SESSIONS/Session — Review (5-concept) — $MISS_DATE.md"
check_status 0 "$MISS_DATE" "5-concept review note"

mkdir "$SESSIONS/Session — Review — 2026-09-30.md"
check_status 1 "2026-09-30" "directory does not count"

# --- JSON: date is the calendar date (never shifted) ------------------------
j="$(at "$DONE_DATE" 10:00)"
assert_json "day date is today" "$j" date "$DONE_DATE"
j="$(at "$DONE_DATE" 01:00)"
assert_json "1am date is still today" "$j" date "$DONE_DATE"

# --- JSON: done -------------------------------------------------------------
j="$(at "$DONE_DATE" 10:00)"
assert_json "done when note exists" "$j" done true
j="$(at "$MISS_DATE" 10:00)"
assert_json "done when 5-concept note exists" "$j" done true
j="$(at 2026-09-28 10:00)"
assert_json "not done without a note" "$j" done false

# --- JSON: visible (evening window 18:00-03:59) -----------------------------
assert_json "hidden at 17:59" "$(at "$DONE_DATE" 17:59)" visible false
assert_json "visible at 18:00" "$(at "$DONE_DATE" 18:00)" visible true
assert_json "visible at 22:59" "$(at "$DONE_DATE" 22:59)" visible true
assert_json "visible at 23:00" "$(at "$DONE_DATE" 23:00)" visible true
assert_json "visible at 01:00" "$(at "$DONE_DATE" 01:00)" visible true
assert_json "visible at 03:59" "$(at "$DONE_DATE" 03:59)" visible true
assert_json "hidden at 04:00" "$(at "$DONE_DATE" 04:00)" visible false

# --- JSON: missed (not done and hour >= 23) ---------------------------------
assert_json "not missed at 22:59" "$(at 2026-09-28 22:59)" missed false
assert_json "missed at 23:00" "$(at 2026-09-28 23:00)" missed true
assert_json "not missed at 01:00 (new day)" "$(at 2026-09-28 01:00)" missed false
assert_json "done is never missed" "$(at "$DONE_DATE" 23:00)" missed false

# --- invalid input ----------------------------------------------------------
"$BIN" --check "not-a-date" >/dev/null 2>&1
[[ $? == 2 ]] && pass "rejects bad date" || fail "should reject bad date"

echo
if [[ "$FAILED" == 0 ]]; then echo "pi-review-status: OK"; else echo "pi-review-status: FAILED"; fi
exit "$FAILED"
