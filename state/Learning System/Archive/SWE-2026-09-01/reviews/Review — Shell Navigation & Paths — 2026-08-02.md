# Review: Shell Navigation & Paths
**Date:** 2026-08-02
**Type:** discriminative
**Source:** MIT Missing Semester — Shell

## Question
When you cd into a directory and open a new terminal, where does it open? What's the difference between cd and pushd/popd in a scripting context?

## Answer
New terminal opens in home directory (correct). Pushd pushes a file in a certain directory (partially wrong).

## Verdict: ⚠️ Partial
Got the new-terminal-open-home part right. Pushd misunderstanding — it pushes the **current working directory** onto a directory stack, not a file. popd pops the stack and cd's back.

## Key Correction
pushd/popd = breadcrumb trail for directories. Push current location, move somewhere, popd to return without manually remembering.
