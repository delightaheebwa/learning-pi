# Review — Clean Targets & .PHONY — 2026-08-04

**Q Type:** discriminative
**Concept:** Clean Targets & .PHONY
**Source:** MIT Missing Semester — Shell

**Question:** A coworker's Makefile has a `clean` target but no `.PHONY: clean` declaration. They run `make clean` and nothing happens. Why?

**Answer:** User said: "because clean has no prerequisites and hence the 'clean' file is considered by make to be up to date and hence it doesn't do anything."

**Assessment:** ❌ Partially correct but missed the key trigger. The problem only happens when **a file named `clean` actually exists** in the directory. Without that file, `make clean` runs fine even without `.PHONY`. The `.PHONY` declaration tells Make "never treat this as a file target — always run the recipe." User got the "no prerequisites → up to date" reasoning right, but the missing piece is: there's an actual file called `clean` that Make sees as already up to date.

**Score:** Incorrect — reset interval
