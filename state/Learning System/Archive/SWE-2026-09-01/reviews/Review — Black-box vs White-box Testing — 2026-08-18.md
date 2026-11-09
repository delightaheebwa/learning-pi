# Review — Black-box vs White-box Testing — 2026-08-18

**Date:** 2026-08-18
**Next Review:** 2026-09-01 (14d)
**Q Type asked:** definitional

## Result: Clean pass

- Two independent axes:
  - **Black-box / white-box = the HOW (visibility):** black-box tests through the public interface (no internal access); white-box calls internals directly.
  - **Unit / integration = the WHAT (scope):** unit tests one small unit in isolation; integration tests multiple units working together.
- Black-box can be unit OR integration — the axes are independent.
- cstack `db`: black-box integration via **process I/O** (spawn `./db`, pipe `insert`/`select`/`.exit` to stdin, assert exact stdout) — decoupled from memory layout → refactor internals freely while the observable CLI contract holds.
- Tradeoff (noted): black-box integration failures are harder to localize → testing pyramid favors many unit tests + few integration tests.

## Interval
7d → 14d (advanced).
