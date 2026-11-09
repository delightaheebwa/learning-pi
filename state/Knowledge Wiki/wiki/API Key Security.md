<!-- provenance: status=verified | source=https://docs.anthropic.com/en/api/getting-started (and provider API docs) | verified-by=fact-check-agent | date=2026-10-26 -->

# API Key Security

> Every AI API works the same way: send a request, get a response. The pattern never changes.

## The Universal Pattern

```
Your Code → HTTP Request (with API key) → API Server → HTTP Response (JSON)
```

Every API call has:
1. An endpoint (URL)
2. An API key (authentication)
3. A request body (what you want)
4. A response body (what you get back)

## Security Rules

- **Never** put API keys in code. Use environment variables.
- Store them as `export ANTHROPIC_API_KEY="sk-ant-..."` or in a `.env` file (always gitignored).
- Tools like Zo's Settings > Advanced let you store secrets as environment variables for skills and zo.space routes.

## SDK vs Raw HTTP

SDKs are convenient wrappers. Raw HTTP is what they do under the hood:

```python
# SDK
client = anthropic.Anthropic()
response = client.messages.create(model="...", messages=[...])

# Raw HTTP (what the SDK does internally)
urllib.request.Request(url, data=body, headers=headers)
```

Understanding raw HTTP calls helps when debugging.

## Common Errors

- **Authentication** — wrong or missing API key → 401
- **Rate limit** — too many requests per minute → 429
- **Token limit** — request exceeds model's context window → 400

## Key Terms

| Term | Meaning |
|------|---------|
| API key | Unique string identifying your account for authorization |
| Rate limit | Max requests per minute/hour to ensure fair usage |
| Token | Billing unit; input and output tokens counted and charged separately |
| Streaming | Getting the response word-by-word instead of waiting for the full response |

## Related
- [[AI Engineering - Dev Environment Stack]]

## Sources
- Anthropic API getting started: https://docs.anthropic.com/en/api/getting-started
- General API key hygiene (OWASP): https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
