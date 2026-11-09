<!-- provenance: status=verified | source=https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html ; https://gcc.gnu.org/onlinedocs/cpp/ | verified-by=fact-check-agent | date=2026-10-26 -->

# GCC Compilation Stages

## Overview

GCC compiles C programs through up to four distinct stages. Only the stages specified are carried out on the input.

## The Four Stages

### 1. Preprocessing
- Expands `#include` directives, `#define` macros, and other preprocessor directives
- Command: `gcc -E file.c` (stops after preprocessing)
- Output: Preprocessed C file (typically `.i` extension)

### 2. Compilation Proper
- Translates preprocessed C code into assembly language
- Command: `gcc -S file.c` (stops after compilation)
- Output: Assembly file (typically `.s` extension)

### 3. Assembly
- The assembler converts assembly language into machine code object files
- Command: `gcc -c file.c` (stops after assembly)
- Output: Object file (`.o` extension)

### 4. Linking
- The linker combines all object files and libraries into an executable
- Command: `gcc file1.o file2.o -o program`
- Output: Executable binary

## Key Points

- GCC is capable of processing several input files through these stages
- The assembler inputs an assembly file and produces an object file
- The linker combines all the object files into an executable file
- Only those stages specified are carried out on the input
- By default, GCC runs all four stages when given a `.c` file

## Related Concepts

- [[Intermediate Object Files (.o)]]
- [[Make: Timestamp Evaluation]]
- [[Makefile: Targets, Prerequisites & Recipes]]

## Sources

- https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html
- https://gcc.gnu.org/onlinedocs/cpp/
