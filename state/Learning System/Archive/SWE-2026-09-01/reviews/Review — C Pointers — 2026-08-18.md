# Review — C Pointers (&, *, ->) — 2026-08-18

**Track:** SWE (C / Pointers)
**Question Type:** discriminative
**Interval:** 3d → 7d (advanced)

**Question:** `int x = 10; int *p = &x; *p = 20;` — what prints, and what do `&`, `*` (declaration vs dereference), and `->` each mean?

**Answer:** 20 prints — the pointer p points at where x lives, so `*p = 20` writes 20 into x's location. `&` = address-of, `*` (in `int *p`) = holds an address, `*p = 20` = dereference/write through the pointer.

**Assessment:** ⚠️ Mostly correct. Got `&` (address-of), `*` declaration (holds address), dereference, and that `*p = 20` changes x to 20. But mis-described `->`: it is NOT "assigning a value/address to a pointer" — it is shorthand for `(*ptr).field` (dereference, then access a struct member). E.g. `p->name` == `(*p).name`.

**Next Review:** 2026-08-25 (7d)
