# Review — API Key Security

**Date:** 2026-06-28
**Track:** AI Engineering (aie)
**Status:** developing — kept interval (3d reset)

## Result

Solid on SDK vs raw HTTP distinction — SDKs abstract boilerplate (headers, retries, rate limiting). Correct on storing keys in env variables via .env files, and the never-commit-to-git rule. Understood `os.getenv()` vs `os.environ[]`. Slightly vague on the full endpoint→key→request→response pattern but acceptable.

## Action

Keep interval. Retest in 3 days.
