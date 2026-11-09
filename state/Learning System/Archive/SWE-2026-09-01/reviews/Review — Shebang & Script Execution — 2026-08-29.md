# Review — Shebang & Script Execution — 2026-08-29

- Track: SWE (Shell & Terminal)
- Type: procedure
- Last Q Type: discriminative → asked definitional
- Grade: FAIL

## Question
In one line, what job does the `#!` (shebang) line do — and why does `./script.sh` require `chmod +x` but `bash script.sh` does not?

## Expected
`#!` is read by the KERNEL (not the shell) when `./script.sh` is executed directly — it names the absolute interpreter path to spawn. `./script.sh` needs x bit (kernel executes file); `bash script.sh` only needs r (bash reads file; shebang is a comment).

## Learner answer
Improved: correctly explained chmod +x (kernel executes) vs bash reads. But still said shebang "tells the shell" and framed it as "interpreter for bash" (inverted — it IS the interpreter path).

## Error analysis
- error_type: structural
- self_attribution: did not separate the kernel-executes-file route from the bash-reads-file route; shebang still attributed to the shell.
- Root: same execution-model misconception as Process Substitution / Built-ins.

## Action
Mistake row stays `active` (retries 0). Next retry 2026-09-01. Advanced concept; Feynman explain-back due (advisory).