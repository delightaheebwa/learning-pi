# Review — Python Logging for Training

**Date:** 2026-07-02
**Track:** AI Engineering (aie)
**Concept:** Python Logging for Training
**Source:** ai-engineering-from-scratch Phase 0, Lesson 12

## Performance

**Retrieval attempt:** Understood logging provides more detail than print, but couldn't articulate specific advantages (levels, dual handlers, structured output) or show basic config.

### Key advantages over print:
1. Severity levels — `debug/info/warning/error`, filter at runtime
2. Automatic timestamps and metadata (module, line number)
3. Dual output — file for persistence, stdout for live monitoring
4. Structured logging (JSON) for production monitoring

### Basic setup:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
```

**Verdict:** ⚠️ Kept current interval
**Next review:** 2026-07-05
