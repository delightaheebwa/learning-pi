# Review — Python Logging for Training — 2026-07-08

**Date:** 2026-07-08
**Track:** aie
**Interval status:** Kept

## Question
Give me the one-liner to set up basic logging with timestamp, INFO level, and a file output.

## Response
logger.time(), logger.info(), logger.file() — invented method names, not actual API.

## Evaluation
Wrong/incomplete. Diagnostic confirmed it was syntax (function names), not conceptual. Correct answer:
```python
import logging
logging.basicConfig(filename='training.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

## Next Review: 2026-07-11
