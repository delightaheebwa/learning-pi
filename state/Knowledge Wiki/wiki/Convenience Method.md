<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Convenience Method

A method that exists strictly for the convenience of the programmer using the class. It reduces boilerplate by filling in sensible defaults and delegating to a more complete version.

## Core idea

Without a convenience method, every call site must supply all arguments, even when most are the same default:

```java
// Without convenience method — repetitive boilerplate
addToken(TokenType.COMMA, null);
addToken(TokenType.SEMICOLON, null);
addToken(TokenType.LPAREN, null);

// With convenience method — clean and readable
addToken(COMMA);
addToken(SEMICOLON);
addToken(LPAREN);
```

The convenience method fills in `null` (or another default) and calls the full version internally.

## Telescoping methods

When you have a chain of convenience methods at different levels of default-filling, they stack like a collapsible telescope:

```java
addToken()                          // chains to →
addToken(TokenType.UNKNOWN)         // chains to →
addToken(TokenType.UNKNOWN, null)   // the "master" method that does the work
```

Each shorter version fills one more default and delegates down. All paths lead to the one master method at the bottom.

## Where the term comes from

Used in formal API design documentation — Apple's developer docs, Java's internal libraries. The short overloads are called "convenience methods" because they exist for programmer convenience, not because the class needs them to function.

## Related

- [[Delegation Pattern]] — convenience methods delegate to the full implementation
- [[Single Responsibility Principle (SRP)]] — splitting into convenience + full version keeps each method's job singular
- [[DRY Principle]] — convenience methods eliminate repetitive default-argument boilerplate

## Sources

- https://martinfowler.com/bliki/HumaneInterface.html
- https://martinfowler.com/bliki/MinimalInterface.html
