# KNOWLEDGE BASE

> Purpose: This is the persistent learning record. Zo reads it at the start of every session and updates it after each session.

## Metadata

- **Topic:** AI/ML & Data Science (general)
- **Learner:** Aheebwa Delight
- **Date Created:** 2026-04-13
- **Last Updated:** 2026-06-02 (Compiler/Interpreter review session)
- **System:** Zo + Obsidian Learning System v3
- **Mode:** Local-first live vault with archive/reference separation

🔴 FOCUS MODE: Compilers & Interpreters — all non-compiler/interpreter concepts are paused (next_review = paused).

---

## Live System Notes

- `Sessions/` is the session history for the active learning system
- `Reviews/` stores spaced-repetition review notes
- `Concept Notes/` stores reusable atomic concept pages
- `Archive/` is reference-only and does not count as active learning history
- The Knowledge Base is the source of truth for what is due, what is developing, what is pending mastery, and what remains open
- `pending_mastery` is the bridge status between first successful retrieval and durable mastery
- Legacy `mastered` entries are treated as provisional until they survive one more successful review under the stricter v3 rules
- No more than 5 review concepts should be actively handled in one session; overflow belongs in the review queue
- NLP concepts are excluded from due/review checks by user preference.
- Backlog amnesty declared 2026-05-19 — 18 concepts moved out of active rotation; see `Archive/Backlog Amnesty — 2026-05-19.md`. They retain their status and can be revived on request.

---

## Concepts

> Each concept you encounter goes here. Status values: `not_started` → `developing` → `pending_mastery` → `mastered` → `consolidated`

| Concept | Status | Prerequisites | Last Reviewed | Next Review | Notes |
|---------|--------|---------------|---------------|-------------|-------|
| Difference quotient | mastered | Basic function notation; input/output change; interval interpretation | 2026-05-19 | paused | Average rate of change over an interval; secant slope. Passed mixed practice May 19 — advanced to 30-day interval. |
| Derivative | mastered | Difference quotient; limit intuition | 2026-05-19 | paused | Instantaneous rate of change at a point; limit of the difference quotient. Passed mixed practice May 19 — advanced to 30-day interval. |
| Taylor series | mastered | Derivative; higher-order derivatives; limit intuition | 2026-05-19 | paused | Infinite polynomial centered at any point a; coefficients come from derivatives at a. Passed mixed practice May 19 — correctly applied quadratic approximation at minimum. Advanced to 30-day interval. |
| Maclaurin series | mastered | Taylor series; center at 0 | 2026-05-19 | paused | Taylor series centered at 0. Passed mixed practice May 19 — correctly identified eˣ from series. Advanced to 30-day interval. |
| Partial differentiation | pending_mastery | Derivative; multivariable functions; holding other variables constant | 2026-05-16 | paused | Differentiate with respect to one variable while treating the others as constants; recalled correctly in review. |
| Gradient | pending_mastery | Partial differentiation; vector notation | 2026-05-16 | paused | Vector of partial derivatives; points in the direction of steepest increase; corrected during review. |
| Jacobian | developing | Partial differentiation; Gradient; vector-valued functions | 2026-04-20 | paused | Matrix of all first partial derivatives of a vector-valued function; shape m×n; J(i,j)=∂fi/∂xj; outputs are rows and inputs are columns |
| Jacobian determinant | developing | Jacobian; square transformation f: R^n → R^n | 2026-04-20 | paused | Absolute value gives local scaling of area/volume; sign preserves orientation |
| Chain rule (matrix form) | developing | Jacobian; matrix multiplication | 2026-04-20 | paused | ∂(g∘f)/∂x = (∂g/∂f)(∂f/∂x); order matters because matrix multiplication is not commutative |
| Backpropagation | developing | Partial differentiation; Gradient; Jacobian; Chain rule (matrix form) | 2026-05-19 | paused | Forward pass stores activations/intermediates; backward pass reuses them and applies the chain rule from the loss backward to compute parameter gradients and earlier-layer gradients |
| Automatic differentiation | mastered | Derivative; Chain rule (matrix form); Jacobian; Backpropagation | 2026-05-19 | paused | Chain rule applied to basic ops; forward mode collects tangents left-to-right; reverse mode runs a forward pass for intermediates then a backward pass to accumulate gradients. Passed mixed practice May 19 — correctly selected reverse mode for GAN generator update. Advanced to 30-day interval. |
| Directional derivative | developing | Partial differentiation; Jacobian matrix | 2026-05-19 | paused | Change in output along an arbitrary direction in input space; formula is gradient dot unit direction vector; a partial derivative is the axis-aligned special case |
| Jacobian-vector product | developing | Jacobian matrix; Directional derivative | 2026-05-19 | paused | Product J_f(x)r; same quantity as a directional derivative in matrix form when the direction vector is unit length; computed directly by forward mode |
| Hessian matrix | developing | Partial differentiation; Gradient; Jacobian matrix; Directional derivative | 2026-05-19 | paused | Matrix of second-order partial derivatives; symmetric when mixed partials are continuous; curvature information around a point; off-diagonal entries are mixed partial derivatives, and the full 2×2 form was recalled correctly. |
| Natural language processing | mastered (excluded) | AI / machine learning basics; text vs speech understanding | 2026-04-18 | 2026-04-21 | [excluded per user preference — NLP concepts not surfaced in reviews] |
| Segmentation | mastered (excluded) | Natural language processing | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Tokenizing | mastered (excluded) | Segmentation | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Stop words | mastered (excluded) | Tokenizing | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Stemming | mastered (excluded) | Tokenizing | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Lemmatization | mastered (excluded) | Stemming | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Part of speech tagging | mastered (excluded) | Tokenizing | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Named entity tagging | mastered (excluded) | Tokenizing | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Lexical analysis | mastered (excluded) | Natural language processing; tokenizing | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Syntactic analysis | mastered (excluded) | Lexical analysis | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Semantic analysis | mastered (excluded) | Syntactic analysis | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Discourse integration | mastered (excluded) | Semantic analysis | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Pragmatic analysis | mastered (excluded) | Discourse integration | 2026-04-18 | 2026-04-21 | [excluded per user preference] |
| Robotics | developing | None yet | 2026-04-19 | paused | Field that designs, builds, programs, and uses robots |
| Robot definitions | developing | Robotics | 2026-04-19 | paused | Reprogrammable, multifunctional, sensing, acting, autonomous, computer-controlled machine |
| Degrees of freedom | developing | Robot definitions | 2026-04-19 | paused | Number of independent ways a robot can move and act |
| Control theory | developing | Robotics; basic systems thinking | 2026-04-19 | paused | Math/logic for stable, precise, and reliable robot behavior |
| Cybernetics | developing | Control theory; Robotics | 2026-04-19 | paused | Feedback loop of sensing, acting, and adjusting to the environment |
| History of robotics | developing | Control theory; Cybernetics; Artificial intelligence | 2026-04-19 | paused | Robotics emerged from control theory, cybernetics, and AI |
| Need for robotics | developing | Robotics basics | 2026-04-19 | paused | Robots help with repetitive work, harsh conditions, and fatigue-free performance |
| Optimization | developing | Need for robotics | 2026-04-19 | paused | Adjusting a process to improve efficiency, safety, comfort, or reliability |
| Robotics myths and facts | developing | Need for robotics | 2026-04-19 | paused | Common misconceptions versus chapter-backed facts about robots |
| Laws of robotics | developing | Robotics basics | 2026-04-19 | paused | Asimov’s hierarchy: humanity, humans, obedience, self-protection |
| Multivariate Taylor series | developing | Derivative; Partial differentiation; Gradient; Hessian matrix | 2026-05-07 | paused | Scalar-function expansion around a point using value, gradient, Hessian, and higher-order derivative tensors; \(\delta^k\) is the k-fold outer product and the Taylor terms are contractions |
| Cox-Jaynes view | developing | Probability foundations | 2026-05-21 | paused | User described basic probability axioms (sum to 1, mapping to real world) but did not retrieve the three Cox desiderata (real-valued monotonic plausibility, logical consistency → product rule, use all available information). Reset to 3-day interval. |
| Random variable | developing | Probability foundations | 2026-05-21 | paused | Correctly identified mapping from sample space to target space and practical motivation (numbers are easier to work with), but missed the pushforward measure mechanism (P_X(B) = P(X⁻¹(B))) and the measurable function formality. Reset to 3-day interval. |
| Pre-image of a random variable | developing | Random variable | — | paused | X^{-1}(S) = {ω ∈ Ω : X(ω) ∈ S}; the set of all outcomes whose X-value falls in S; lives in Ω, not T |
| Cumulative distribution function | developing | Probability mass and density functions; Random variable | 2026-05-21 | paused | $F_X(x) = P(X \leq x)$; accumulates probability from the left; derivative of the CDF is the PDF for continuous variables; works for both discrete and continuous cases |
| Distribution of a random variable (P_X) | developing | Random variable; Pre-image of a random variable | — | paused | P_X(S) = P(X^{-1}(S)); the function S ↦ P_X(S) giving probability that X lands in S; original measure "pushed through" X |
| Independence of random variables | developing | Joint, marginal, and conditional probabilities; Random variable | 2026-05-21 | paused | $P(X, Y) = P(X)P(Y)$; equivalently $P(X \mid Y) = P(X)$; not the same as mutual exclusivity — coin flip and die roll can happen together and are independent |
| Joint, marginal, and conditional probabilities | developing | Probability mass and density functions; Random variable | 2026-05-21 | paused | Joint $P(X=x_i, Y=y_j)$ is the table entry; marginal $P(X=x_i)$ sums a row; conditional $P(X=x_i \mid Y=y_j) = P(X=x_i, Y=y_j) / P(Y=y_j)$ restricts the sample space |
| Probability mass and density functions | developing | Random variable; Probability foundations | 2026-05-21 | paused | PMF assigns probability directly to discrete states (sums to 1); PDF is a density curve where probability comes from area under the curve; PDF values can exceed 1 — only the integral must be 1 |
| Interpreter internals | developing | Basic programming knowledge | 2026-05-30 | 2026-06-05 | EVAL loop reads code as text, parses symbols, and calls internal pre-compiled functions; the interpreter binary is the only executable — it never creates new machine code; code is treated as data, not converted to CPU instructions |
| Interpreter overhead | developing | Interpreter internals | 2026-05-30 | 2026-06-09 | Translator metaphor: the computer simultaneously figures out what code means AND executes it; line-by-line execution prevents look-ahead optimization; sacrifices deep optimization for instant REPL feedback |
| Compiler optimizations | developing | Compiler (general knowledge) | 2026-05-30 | 2026-06-05 | Compilers see the entire program at once and can apply: math simplification (slow formula → faster equivalent), dead code elimination (remove unreachable lines), register allocation (data → CPU's fastest memory); these are impossible for line-by-line interpreters |
| JIT compilation tradeoffs | developing | JIT Compilation; Interpreter; Compiler | 2026-05-30 | 2026-06-09 | Five real downsides: startup latency (warm-up period), memory footprint (bytecode + compiler + machine code in RAM), CPU overhead (compiler thread steals cycles), implementation complexity (specialized engineering), platform constraints (iOS forbids dynamic code generation) |
| Dev vs Production workflow | developing | Interpreter; Compiler | 2026-05-30 | 2026-06-09 | During development: interpreter runs code instantly for fast iteration (slow execution, fast human feedback); For production: compiler builds an optimized binary (slow build, fast execution); the two approaches complement each other |
| Compiler | developing | None | 2026-05-30 | 2026-06-03 | Pipeline that translates source code (C, Rust, Go) into machine code for direct CPU execution; sees the entire program at once enabling optimization; stages: frontend (lexing/parsing), backend (code generation), and optimization passes; outputs native binaries, assembly, or bytecode |
| Interpreter | developing | None | 2026-05-30 | 2026-06-03 | Executes code line-by-line; reads source as text; uses internal pre-compiled functions; no new machine code generated |
| Virtual Machine | developing | None | 2026-05-30 | 2026-06-03 | Abstract machine that executes bytecode; provides a consistent execution environment; decouples source from hardware |
| Bytecode | developing | None | 2026-05-30 | 2026-06-04 | Intermediate representation of source code; platform-independent; executed by a virtual machine |
| JIT Compilation | developing | None | 2026-05-30 | 2026-06-04 | Just-in-time compilation; compiles code at runtime; balances startup speed with execution performance |
| Compiled vs Interpreted | developing | None | 2026-05-30 | 2026-06-05 | Comparison of execution models: compiled (pre-processed to machine code) vs interpreted (executed line-by-line) |
| Transpiler | developing | None | 2026-05-30 | 2026-06-05 | Translates code from one language to another; often used for polyglot support or language migration |
| Runtime | developing | None | 2026-05-30 | 2026-06-06 | Environment where code executes; includes interpreter, virtual machine, or JIT compiler; manages memory and execution flow |
| Python dynamic execution model | developing | Interpreter internals; Interpreter overhead | 2026-05-30 | 2026-06-02 | Variables are labels (references to PyObjects), not fixed memory boxes; code can modify itself at runtime; every operator dispatches as a method call (a+b → a.__add__(b)); runtime type lookup on every operation makes machine-code translation inherently bloated |
| Python distribution model | developing | Interpreter; Compiler | 2026-05-30 | 2026-06-02 | Standalone executables (PyInstaller) bundle the entire CPython interpreter; interpreter unpacks and runs code at runtime; results in much larger executables vs compiled binaries from Go/Rust/C |
| Dynamic language optimization limits | developing | JIT compilation tradeoffs; Interpreter overhead | 2026-05-30 | 2026-06-02 | PyPy's tracing JIT excels at stable-type loops but real-world code unpredictability forces frequent fallbacks to slower interpretation; Cython requires manual static type annotations (cdef int, cdef double) that sacrifice Python's simplicity — at that point you're writing C with Python syntax |
| Memory management models | developing | Interpreter internals; Compiler | 2026-05-30 | 2026-06-02 | Three strategies: GC (Python — reference counting + cyclic GC pauses, high runtime overhead), manual (C — developer-managed malloc/free, zero overhead but error-prone), compile-time ownership (Rust — compiler hardcodes allocation/deallocation at build time, zero runtime cost) |

---

## Open Questions

> Questions that emerged during sessions but haven't been fully resolved yet. Zo surfaces these at the start of every session.

- Revisit Taylor series with the exact derivative-based coefficient formula.
- Continue the robotics chapter with robot components and any remaining pages beyond the current section.
- Practice tracing backpropagation gradient chains through a concrete two-layer network.
- Connect Hessian to Newton's method quadratic approximation and direct-solve update.

---

## Scripture Memory

> Bible verses for memorization using spaced repetition. Triggered by the "meditate" keyword.
> Intervals: 3d → 7d → 14d → 30d → 90d → consolidated

| Reference | Verse Text | Translation | Status | Last Reviewed | Next Review | Interval |
|-----------|------------|-------------|--------|---------------|-------------|----------|
| Psalm 31:3 | Since you are my rock and my fortress, for the sake of your name lead and guide me. | NIV | developing | 2026-05-31 | 2026-06-03 | 3d |
| Psalm 31:15 | My times are in your hands; deliver me from the hands of my enemies, from those who pursue me. | NIV | developing | 2026-05-31 | 2026-06-03 | 3d |
| Psalm 31:16 | Let your face shine on your servant; save me in your unfailing love. | NIV | developing | 2026-05-31 | 2026-06-03 | 3d |
| Psalm 31:19 | How abundant are the good things that you have stored up for those who fear you, that you bestow in the sight of all, on those who take refuge in you. | NIV | developing | 2026-05-31 | 2026-06-03 | 3d |
| Psalm 31:24 | Be strong and take heart, all you who hope in the LORD. | NIV | developing | 2026-05-31 | 2026-06-03 | 3d |
| Psalm 32:1 | Blessed is the one whose transgressions are forgiven, whose sins are covered. | NIV | developing | 2026-05-31 | 2026-06-03 | 3d |
| Psalm 32:2 | Blessed is the one whose sin the LORD does not count against them and in whose spirit is no deceit. | NIV | developing | 2026-05-31 | 2026-06-03 | 3d |
| Psalm 32:5 | Then I acknowledged my sin to you and did not cover up my iniquity. I said, "I will confess my transgressions to the LORD." And you forgave the guilt of my sin. | NIV | developing | 2026-05-31 | 2026-06-03 | 3d |

---

## Session Log

> Brief record of each session. Zo updates this automatically.

| Date | Session | Concepts Covered | Key Outcomes |
|------|---------|-----------------|--------------|
| 2026-04-15 | Difference Quotient vs Derivative | Difference quotient, derivative, limit | User correctly distinguished average rate of change from instantaneous rate of change and understood why the limit is needed |
| 2026-04-16 | Taylor Series and Maclaurin Series | Taylor series, Maclaurin series, coefficients, local approximation, e^x Maclaurin series | User correctly distinguished Taylor vs Maclaurin, understood that higher derivatives add local shape information at the center point, and computed e^{0.1} ≈ 1.105 using the series |
| 2026-04-18 | Partial Differentiation and Gradients | Difference quotient, derivative, partial differentiation, gradient | User reviewed the finite-interval vs limit distinction, learned partial derivatives by holding other variables constant, and connected gradients to steepest ascent and optimization |
| 2026-04-18 | Natural Language Processing | NLP, segmentation, tokenizing, stop words, stemming, lemmatization, POS tagging, named entity tagging, lexical analysis, syntactic analysis, semantic analysis, discourse integration, pragmatic analysis | User defined NLP as the branch of AI for human language, distinguished the field from applications, explained the preprocessing pipeline, and correctly worked through the analysis phases from lexical to pragmatic analysis; one named-entity example missed the money entity, but understanding was otherwise solid |
| 2026-04-19 | Robotics Chapter 1 | Robotics, robot definitions, degrees of freedom, control theory, cybernetics, history of robotics, need for robotics, optimization, robotics myths and facts, laws of robotics | User started the robotics chapter and accurately explained the core foundations, the historical roots, the motivation for robotics, the 3D's, the myths vs facts section, and Asimov's laws |
| 2026-04-20 | MML 5.3 — Jacobians and Chain Rule | Jacobian, Jacobian determinant, matrix chain rule, vector-valued functions | User correctly identified the Jacobian as the matrix of first partial derivatives, matched shapes in the chain rule, interpreted J(i,j) as ∂fi/∂xj, and understood the Jacobian determinant as local scaling |
| 2026-05-02 | Backpropagation Review Schedule Setup | Backpropagation | Initial review schedule set for 2026-05-05, then 2026-05-09, 2026-05-16, 2026-06-01, and 2026-07-31 |
| 2026-05-04 | Automatic Differentiation Review Schedule Setup | Automatic differentiation | Initial review schedule set for 2026-05-07, then 2026-05-11, 2026-05-18, 2026-06-03, and 2026-08-02 |
| 2026-05-05 | Backpropagation Review | Backpropagation | User explained that the forward pass stores intermediates, the backward pass reuses them, and gradients flow backward from the loss through earlier layers; concept moved to pending_mastery |
| 2026-05-05 | Automatic Differentiation Ingest | Automatic differentiation, Directional derivative, Jacobian-vector product | User synthesized symbolic vs numerical vs automatic differentiation, explained forward mode as tangent propagation, and connected JVPs to directional derivatives and Jacobian columns |
| 2026-05-06 | Hessian Matrix Retrieval Schedule | Hessian matrix | Added Hessian matrix to the knowledge base and set the spaced-repetition schedule for 2026-05-09, 2026-05-16, 2026-05-30, 2026-06-29, and 2026-09-27 |
| 2026-05-07 | Automatic Differentiation Review | Automatic differentiation | User explained automatic differentiation as breaking expressions into primitive operations and differentiating them, distinguished forward mode as left-to-right tangent propagation and reverse mode as a forward pass for intermediates followed by backward accumulation, and correctly connected reverse mode to neural-network training; one nuance about reverse-mode efficiency was corrected and the concept moved to pending_mastery |
| 2026-05-08 | Directional Derivative and Jacobian-Vector Product Review | Directional derivative, Jacobian-vector product | User recovered the directional derivative intuition but needed a formula correction, then correctly explained Jacobian-vector product as the Jacobian applied to a vector and connected it to directional derivatives |
| 2026-05-16 | Partial Differentiation and Gradient Review | Partial differentiation, gradient | User correctly defined partial differentiation and identified gradient as the vector of partial derivatives; one expression was corrected during the review |
| 2026-05-18 | Cox-Jaynes and Random Variable Retrieval Schedule | Cox-Jaynes view, Random variable | Added both probability concepts to the knowledge base and set spaced-repetition schedules starting 2026-05-21 |
| 2026-05-19 | Spaced Repetition Review | Automatic differentiation, directional derivative, backpropagation, Jacobian-vector product, Hessian matrix | Automatic differentiation promoted to mastered; backpropagation, JVP, and Hessian demoted to developing due to incomplete retrieval; directional derivative stays developing with formula corrected. Post-session audit conducted; backlog amnesty declared; naming inconsistencies fixed; mixed practice scheduled. |
| 2026-05-19 | Random Variable Pre-image and Distribution Ingest | Random variable (enriched), Pre-image of a random variable, Distribution of a random variable (P_X) | Added pre-image and distribution as new concepts; enriched existing random variable page with pre-image definition, target space types, and ML motivation; retrieval schedules set for 2026-05-22 |
| 2026-05-19 | Mixed Practice | Derivative, Difference quotient, Taylor series, Maclaurin series, Automatic differentiation | Mixed practice interleaved session. User correctly retrieved and applied all 5 concepts in transfer-style scenarios including GAN training (AD mode choice), loss function approximation (Taylor at minimum), and series identification (eˣ from Maclaurin coefficients). All 5 moved to 30-day interval. |
| 2026-05-21 | Probability Distribution Retrieval Schedule Setup | Cumulative distribution function, Joint marginal and conditional probabilities, Independence of random variables, Probability mass and density functions | Added 4 probability concepts to the knowledge base; retrieval schedules set starting 2026-05-24 |
| 2026-05-21 | Cox-Jaynes and Random Variable Review | Cox-Jaynes view, Random variable | Cox-Jaynes: user did not retrieve the three desiderata; re-explained and reset. Random variable: user correctly identified the function mapping but missed the pushforward measure; corrected and reset. Both remain developing with 3-day interval. |
| 2026-05-30 | Interpreter Mechanics and JIT Tradeoffs Ingest | Interpreter internals, Interpreter overhead, Compiler optimizations, JIT compilation tradeoffs, Dev vs Production workflow | Ingested Perplexity conversation about interpreter EVAL loop, code-as-data execution, translator overhead, compiler optimizations, JIT downsides, and dev vs production workflow. 5 new concepts added to KB with 3-day retrieval schedules. |
| 2026-05-30 | Focus Mode: Compilers & Interpreters Setup | all 13 compiler/interpreter concepts | Added 8 foundational compiler/interpreter concepts (Compiler, Interpreter, VM, Bytecode, JIT Compilation, Compiled vs Interpreted, Transpiler, Runtime) with staggered retrieval schedules. Paused all non-compiler concepts. Focus mode active. 13 total compiler/interpreter concepts in rotation. |
| 2026-05-30 | Python Performance Tradeoffs Ingest | Python dynamic execution model, Python distribution model, Dynamic language optimization limits, Memory management models | Ingested Perplexity conversation about Python's architectural slowness (variables-as-labels, runtime mutability, operator dispatch, interpreter bundling) and why optimization strategies (PyPy, Cython, GC) have inherent tradeoffs. 4 new concepts added to KB with 3-day retrieval schedules. |
| 2026-06-02 | Interpreter Internals, Overhead, Compiler Optimizations, JIT Tradeoffs, Dev vs Production Workflow Review | Interpreter internals, Interpreter overhead, Compiler optimizations, JIT compilation tradeoffs, Dev vs Production workflow | Reviewed 5 concepts; updated review dates based on session performance. |
| 2026-06-02 | Compilers & Interpreters — Review Session | Interpreter internals, Interpreter overhead, Compiler optimizations, JIT compilation tradeoffs, Dev vs Production workflow | Interpreter internals reset (conflated with optimization); Interpreter overhead advanced to 7d (correct line-by-line EVAL loop overhead); Compiler optimizations reset (missed register allocation + the "why"); JIT compilation tradeoffs advanced to 7d (named 3 of 5 downsides); Dev vs Production workflow advanced to 7d (correct feedback-vs-speed tradeoff) |

---

## Review Queue

> 🔴 Focus Mode active — only compiler/interpreter concepts in rotation.

### Due 2026-06-02 (9 concepts)

- Interpreter internals (developing)
- Interpreter overhead (developing)
- Compiler optimizations (developing)
- JIT compilation tradeoffs (developing)
- Dev vs Production workflow (developing)
- Python dynamic execution model (developing)
- Python distribution model (developing)
- Dynamic language optimization limits (developing)
- Memory management models (developing)

### Due 2026-06-03

- Compiler (developing)
- Interpreter (developing)
- Virtual Machine (developing)

### Due 2026-06-04

- Bytecode (developing)
- JIT Compilation (developing)

### Due 2026-06-05

- Compiled vs Interpreted (developing)
- Transpiler (developing)

### Due 2026-06-06

- Runtime (developing)

---

## Mastery Summary

- **Not Started:** 0
- **Developing:** 17 (active — compiler/interpreter/PL-implementation focus)
- **Paused:** 39 (non-compiler concepts suspended during focus mode)
- **Mastered:** 0 active + 12 (excluded NLP) = 12 total
- **Consolidated:** 0
- **Backlog Amnesty:** 18 (retain status, not in active rotation)
- **Total concepts tracked:** 52

---

## Session Counter & Interleaving

- **Total sessions:** 21
- **Last mixed practice:** 2026-05-19
- **Next session type:** compiler/interpreter retrieval
- **Mixed practice target concepts next time:** Partial differentiation, Gradient, Backpropagation, Jacobian-vector product, Hessian matrix