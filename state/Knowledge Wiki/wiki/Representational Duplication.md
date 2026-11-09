<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Representational Duplication

A form of DRY violation that occurs when your code connects to external systems — APIs, databases, third-party services — and you manually recreate the external system's data model in your code.

## The problem

When your program talks to something outside itself (another app, a database, a service like Stripe), both sides must agree on how data looks. If you manually type out matching structures in your code and the external system changes, your code silently breaks.

## Solutions

### Option 1: Schema-driven code generation
Use tools that read the external schema and **auto-generate** the matching code structures. Examples:
- ORMs with introspection: Prisma (`prisma db pull`), Entity Framework, SQLAlchemy
- OpenAPI/Swagger code generators for REST APIs
- Protocol Buffer compilers for gRPC

If the schema changes, rerun the tool — your code updates automatically.

### Option 2: Flexible data structures + validation
Instead of rigid typed structures, store data in generic containers (dicts, maps, JSON objects) and validate them against a lightweight rules table. Examples:
- **Pydantic** (Python): Define a schema model, dump raw data into it, get validation
- **Zod** (JavaScript/TypeScript): Schema declaration and validation
- **JSON Schema**: Language-agnostic validation rules

If the schema changes, update only the validation rule — not dozens of code structures.

## The key insight

Both approaches eliminate the need for **manual** synchronization between external schemas and internal code. The duplication is handled automatically.

## Related

- [[DRY Principle]] — representational duplication is a DRY violation
- [[Uniform Access Principle]] — accessor functions help abstract data access

## Source

The Pragmatic Programmer (Hunt & Thomas)

## Sources (verified)

- https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/
