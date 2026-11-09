<!-- provenance: status=verified | source=https://github.com/mity/acutest/blob/master/README.md | verified-by=fact-check-agent | date=2026-10-26 -->

# Acutest Unit Testing

## Overview

**Acutest** is a single-header C/C++ unit-testing facility. You vendor `acutest.h` into the project (e.g. `third_party/acutest.h` via `curl`) — no library installation or linker flag required, so the test command stays reproducible on any machine with just a C compiler. Acutest generates `main()` itself; your test file only defines test functions and a registry. (The course project is C-only, but the framework also supports C++ — see "Beyond the C lesson" below.)

## Registering Tests: TEST_LIST

Test functions are plain C functions with the prototype `void test_name(void)`. They're mapped to readable names in the `TEST_LIST` array, which **must end with the sentinel `{ NULL, NULL }`** so the runner knows where the list stops:

```c
TEST_LIST = {
    { "parses memory totals", test_parses_memory_totals },
    { NULL, NULL }
};
```

## The Assertion Macros

| Macro | Behavior | Use when |
| --- | --- | --- |
| `TEST_CHECK(cond)` | Logs the failure (with file:line) but **continues** the test | Default choice — value comparisons, you want every assertion checked |
| `TEST_ASSERT(cond)` | Logs and **immediately aborts** the current test | A failure makes the next lines unsafe (e.g. dereferencing a NULL pointer) |
| `TEST_MSG(...)` | printf-style diagnostic message printed when a check fails | Explaining expected vs actual (requires variadic macro support, C99+) |
| `TEST_DUMP(...)` | Hex-dumps a memory buffer when a check fails | Binary / raw byte-array comparisons |
| `TEST_CASE("name")` | Labels the current test vector in a data-driven loop | With `--verbose`, the vector name is logged even when the check passes |
| `TEST_EXCEPTION(code)` | C++ only: verifies `code` throws the expected exception type | C++ exception tests (not used in the C course) |

**Why TEST_ASSERT's "dire" consequences are acceptable:** aborting skips object destructors and can leave file descriptors unflushed or memory unfreed — which is why the README explicitly says to prefer `TEST_CHECK` "unless you know exactly what you do and why you chose TEST_ASSERT". The abort is performed by calling `abort()` when the test runs as a child process, or via `longjmp()` when it doesn't (e.g. under a debugger). What makes the abort tolerable in practice: by default Acutest runs each test in its **own isolated child process**, so when the child aborts the OS reclaims all memory and file descriptors — nothing leaks into other tests, and short-lived fixtures make the skipped cleanup irrelevant to results.

**Rule of thumb:** default to `TEST_CHECK`; use `TEST_ASSERT` as a shield before crash-prone operations (NULL-pointer guard, array bounds, file-handle checks).

## Running Tests (auto-generated CLI)

- `./tests/test_meminfo` — run all tests; **exit 0** when all pass, **1** when any test fails, any other number if an internal error occurs.
- `./tests/test_meminfo "parses memory totals"` — run only matching tests (exact, word, or substring match).
- `./tests/test_meminfo --list` (or `-l`) — list all registered tests without running them.
- `./tests/test_meminfo --verbose` — show diagnostics for passing checks too (custom messages, test-vector names), not just failures.
- `./tests/test_meminfo --exclude <name>` — skip specific tests.

**Naming tests for the CLI:** avoid spaces and shell-special characters in test names, and never start a name with `-` — it would be parsed as a command-line option instead of a test name (use `--` or rename).

## The Seam Connection

Acutest fits the [[Testable Seam]] pattern: compile the test file linked against the module under test, feed it fixture text, assert on parsed fields:

```bash
cc -Wall -Wextra -std=c17 -g -Ithird_party -Isrc \
    tests/test_meminfo.c src/meminfo.c -o tests/test_meminfo
```

`-Ithird_party -Isrc` are the include search paths that let `#include "acutest.h"` and `#include "meminfo.h"` resolve. Start with a failing test (the function doesn't exist yet) — the missing symbol is a useful Red, and the test states the interface before implementation details distract.

## Key Insight

TEST_CHECK vs TEST_ASSERT is a judgment call: CHECK gathers all failures and lets the test finish; ASSERT stops immediately when continuing would crash. Prefer CHECK by default; reserve ASSERT for guard conditions.

## Beyond the C Lesson (Optional Reading)

The README covers more than the C course uses:

- **Custom message variants:** underscore-suffix macros (`TEST_CHECK_`, `TEST_ASSERT_`, `TEST_CASE_`, `TEST_EXCEPTION_`) take printf-style format arguments for richer failure output — and with `--verbose` their messages are logged even when the check passes.
- **C++ exceptions:** any exception thrown from a test is caught and treated as a failure; for `std::exception`-derived types, `what()` is printed.
- **TAP & XML:** `--tap` emits Test Anything Protocol output; `--xml-output=FILE` writes xUnit-compatible XML.
- **Debuggers:** when a debugger is detected, the per-test child-process isolation is suppressed to make debugging easier.

## Sources

- Acutest README and examples: https://github.com/mity/acutest (checked 2026-10-26: `TEST_CHECK`/`TEST_ASSERT`/`TEST_MSG`/`TEST_DUMP`/`TEST_CASE`/`TEST_EXCEPTION`, `TEST_LIST` zeroed sentinel, exit codes 0/1/other, `--list`/`-l`, `--exclude`, `--verbose`, `--tap`, `--xml-output=FILE`, child-process isolation, abort()/longjmp(), debugger suppression)
- Teach C Course — Lesson 3: Acutest and the Parser Seam
- Gemini Socratic tutoring on Acutest macros (notebook: https://gemini.google.com/app/8870dcd71e2919f5)

Related: [[Testable Seam]], [[Static Fixtures & Boundary Cases]], [[Red-Green-Refactor]]
