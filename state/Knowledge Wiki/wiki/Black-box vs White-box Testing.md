<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Black-box vs White-box Testing

## Overview

**Black-box vs white-box** and **unit vs integration vs E2E** are two different axes — don't conflate them. Black-box/white-box describe *how* you test (visibility). Unit/integration/E2E describe *what* you test (scope). Black-box is a technique; integration/E2E are testing levels.

## The Two Axes

| Axes | Question | Options |
|---|---|---|
| Visibility (technique) | Can the test see inside the implementation? | Black-box (no), White-box (direct internal access), Gray-box (partial) |
| Scope (level) | How much of the system is exercised? | Unit (one function/class), Integration (2+ modules), E2E (full user flow) |

The axes intersect: a black-box integration test (spawn the binary, check stdout) vs a white-box integration test (call `prepare_statement()` then `execute_statement()` directly in C).

## The Process-I/O Pattern (cstack Part 4)

The SQLite-clone test suite is **black-box integration testing**:

```ruby
IO.popen("./db", "r+") do |pipe|
  pipe.puts "insert 1 user1 person1@example.com"
  pipe.puts "select"
  pipe.puts ".exit"
  raw_output = pipe.gets(nil)   # read full stdout stream
end
```

- **Input-driven:** commands piped to the binary's stdin, mimicking a user typing.
- **Output-driven:** assertions check exact printed lines (`db > Executed.`, `db > (1, user1, person1@example.com)`).
- **Decoupled from internals:** tests don't care whether rows live in an array, B-tree, or linked list — refactor C internals freely as long as the CLI contract holds.
- It's a *lightweight E2E* too: it validates the real compiled binary's prompt strings, error messages, and exit behavior.

## The Testing Pyramid

Keep many fast, isolated **unit tests** (pinpoint errors instantly) plus a small set of **integration tests** (verify modules talk to each other in a real environment). An integration-only suite is slow, runs less often, and its failures are ambiguous — the break could be a live OS format change, a permission issue, a missing dependency, *or* a parser bug.

## One Line Summary

Black-box/white-box = visibility; unit/integration/E2E = scope; the CLI tests are black-box integration tests, and you need the whole pyramid, not just the top.

## Sources

- cstack — Let's Build a Simple Database, Part 4: https://cstack.github.io/db_tutorial/parts/part4.html
- Gemini tutoring on testing categories (notebook: https://gemini.google.com/app/f3ceade4034d6bf0)
- Software testing (black-box/white-box): https://en.wikipedia.org/wiki/Software_testing
