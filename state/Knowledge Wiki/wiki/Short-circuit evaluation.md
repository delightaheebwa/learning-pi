<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Short-Circuit Evaluation

Logical operators (`and`, `or`) in languages like Python and JavaScript are not just boolean operators — they act as **implicit control flow structures** because they conditionally evaluate their second operand.

## How It Works

Short-circuiting means the second operand is only evaluated if the first operand doesn't already determine the result.

**`A and B`** — returns A if A is falsy, otherwise evaluates and returns B. Equivalent to: `if A then B else A`.

**`A or B`** — returns A if A is truthy, otherwise evaluates and returns B. Equivalent to: `if A then A else B`.

Crucially, these operators return the **actual operand value**, not just `True`/`False`:

```python
# and: returns the first falsy value, or the last value
None and "Hello"       # → None
"Apple" and "Banana"   # → "Banana"

# or: returns the first truthy value, or the last value
"Apple" or "Banana"    # → "Apple"
None or "Banana"       # → "Banana"
```

## Common Use Cases

### Guard Clauses

Prevent errors by ensuring prerequisites are met before accessing properties:

```javascript
if (object != null && object.hasProperty())
```

If `object` is `null`, the second check is skipped entirely — no null pointer error.

### Default Values

Provide fallback values when input may be empty or missing:

```python
name = user_input or "Guest"
```

If `user_input` is falsy (empty string, `None`, etc.), `"Guest"` is used instead.

## Pitfalls

### Side Effects Can Be Silently Skipped

If the right operand mutates state, short-circuiting may skip it:

```python
if condition or perform_action()
```

If `condition` is truthy, `perform_action()` is never called — potentially causing elusive bugs.

### Readability Degrades Quickly

Chaining too many short-circuit operators makes code unreadable. When logic is complex, prefer explicit `if-else` blocks.

## Related

- [[Compiler]] — short-circuit evaluation is a language-level optimization that compilers must handle
- [[Python performance tradeoffs]] — Python's dynamic dispatch model

---

*Source: `raw/sources/2026-06-04 - short-circuit-evaluation-memory-management.md`*

## Sources

- Short-circuit evaluation (Wikipedia): https://en.wikipedia.org/wiki/Short-circuit_evaluation
- Python boolean operations: https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not
