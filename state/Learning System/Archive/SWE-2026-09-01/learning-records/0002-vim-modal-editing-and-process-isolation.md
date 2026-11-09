# Vim modal editing + the built-in/function/script taxonomy

The learner demonstrated understanding of Vim's modal-editing philosophy and
composable command model (verb + noun + count + modifier), and corrected a
load-bearing misconception about process isolation: that a shell *script* (a
child process) can change the parent shell's working directory. This sets the
floor for the rest of Stage 0's tooling lessons (debugging, git, data wrangling
all lean on the "child copies, never writes back" principle).

**Evidence:** Feynman explain-back passed (Bloom: Evaluate) — articulated the
function-in-current-shell vs script-in-own-process split in own words, and
closed the disk-vs-memory distinction (mkdir persists; cd in a script
evaporates) after a `sure`-confident miss on the both-effects-present quiz item
was re-probed to correct. Vim inversion of `i` (inside) vs `t` (until) was fixed
to `sure` confidence after a 2×2 grid + soccer mnemonic.

**Implications:** Process isolation is now a *reliable* building block — the
misconception is recorded in the Mistakes ledger (retry 2026-08-31) because it
recurred once under the both-effects frame. Vim's three new concepts (Modal
Editing, Composable Commands, Buffers & Windows) enter Active Concepts as
`developing` with first review +3d.
