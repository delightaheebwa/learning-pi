# AI Engineering from Scratch — Glossary

> Canonical language for the workspace (AIEFS). One glossary for the workspace, per-track subheadings.
> Add a term only when the user understands it (compressed knowledge, not a dictionary). Be opinionated; keep definitions tight.
> As understanding deepens, revise in place. **Active track: AIEFS (Rohit)** — SWE terms below are archived reference.

## AIEFS (Active — Phase 0 + Phase 1 catch-up)

- **4-layer env stack**: System → Packages → Runtimes → AI libs (Rohit P0 L01) — install bottom-up; `uv`/`pnpm`/`cargo`/`juliaup` sit on System; rig survives via `verify.py --route`.
- **PMF vs PDF**: PMF = discrete outcome → exact probability, sums to 1 (classifier outputs). PDF = continuous density — probability = area under curve (density can exceed 1); integrate to get `P`.
- **Softmax + cross-entropy**: `softmax(z_i)=exp(z_i−max)/∑exp(z_j−max)` (subtract-max trick) → PMF; `cross-entropy = −log P(correct)` = NLL; `log-sum-exp` stabilizes.
- **Central Limit Theorem**: mean of many i.i.d. samples → Normal regardless of source — why gradients/initializations/errors look Gaussian; max-entropy for given μ,σ.
- **Expected value / variance**: `E[X]=∑ x·P(x)`, `Var=E[(X−μ)²]=E[X²]−μ²` — loss is an expected value; gradient variance → training noise.
- **Dot product / projection**: `a·b` = similarity; `proj_b(a)` residual ⟂ basis — attention, regression, PCA primitive.
- **Eigendecomposition**: `Av=λv` — eigenvectors = directions the matrix only scales; eigenvalues = scale factors.

## SWE (Archived 2026-09-01 — reference only)

- **Testable seam**: The boundary where a controlled input replaces the real environment (e.g. `parse_meminfo(text, out)` instead of `read_meminfo(path, out)`); the second is where most bugs live, so most unit tests belong there.
- **Fixture**: Controlled sample data that makes a moving target predictable (stable text with exact asserts).
- **Smoke test**: A live read with range/sanity bounds, not exact values (e.g. `total > 0`, `available <= total`).
- **Arrange–Act–Assert (AAA)**: Three recognizable test phases — arrange inputs, act on the behavior under test, assert the observable result. If you can't point to the Act, the test checks too much.
- **Red–green–refactor**: The TDD loop — fail for a meaningful reason, make it pass, improve design without changing protected behavior.
- **Make**: A build tool, not a compiler — checks prerequisites and runs a recipe when a target is out of date (timestamp comparison).
- **Signal**: An asynchronous message the kernel delivers to a process (a "software interrupt") that it may catch, ignore, or default-handle — the mechanism behind Ctrl-C (SIGINT), Ctrl-Z (SIGTSTP), and `kill` (SIGTERM/SIGKILL).
- **Job control**: The shell's toolkit for pausing and resuming processes — `Ctrl-Z` suspends, `fg`/`bg` resume, `jobs` lists; background jobs die with the terminal (SIGHUP) unless `nohup`/`disown` protect them.
- **`is_pid_name`**: A predicate that accepts names made entirely of digits, rejecting `self`, `thread-self`, and other kernel entries; validate the string, don't use `atoi==0` to mean "not a PID".

## Color taxonomy (Primary Colors — archived, reference) — see `Knowledge Wiki/wiki/SWE Primary Colors & Roadmap.md`

- **Process**: How humans build reliably — testing, debugging, git, reading code.
- **Systems**: What the machine actually does — OS, processes, memory layout.
- **Interaction**: How things talk — I/O, protocols, network, UIs.
- **Computation**: How we transform data — algorithms, logic, complexity.
- **State**: How we remember things — memory, files, databases.
- **Abstraction**: How we tame complexity — functions, modules, interfaces.