# Review — C Memory Regions — 2026-08-23

**Track:** SWE (monitor project)
**Question Type:** discriminative (alternated from definitional)
**Interval:** held 3d

**Question:** Both `char buf[4096]` and `char *buf = malloc(4096)` give you 4096 bytes — but one can leak and the other can't, and one dangles if you `return` its address. Which is which, and why?

**Answer:** "the first can't leak or dangle while the second can. This is because the first uses the stack which is cleared by the CPU automatically unlike the second which uses heap memory hence has to be manually and cleared."

**Assessment:** ⚠️ Hold. Leak half right: heap leaks without free(); a stack array cannot leak (its frame vanishes on return). Dangling INVERTED: returning the STACK array's address is exactly what dangles — the frame it points into is destroyed on return (UB). The heap block SURVIVES return; its failure mode is the leak, not dangling. Also minor: the OS/runtime reclaims the stack (not "the CPU"), and heap memory isn't "cleared" — you release it with free(). Held 3d.

**Next Review:** 2026-08-26 (held 3d)
