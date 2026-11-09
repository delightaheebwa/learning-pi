<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Software Engineering Philosophy

> A personal synthesis of professionalism, engineering mindset, and software design principles — drawn from *The Pragmatic Programmer*, *Clean Architecture*, and applied lessons in code craftsmanship.

## Mental Model: Four Layers

These notes organize into a coherent four-layer philosophy:

| Layer | Focus | Key Ideas |
| --- | --- | --- |
| **Character** | Responsibility, ownership, honesty | Own mistakes; provide options, not excuses; respond immediately |
| **Thinking** | Learning, curiosity, communication | Read broadly; diversify; learn deliberately; verify understanding |
| **Engineering** | Design principles | DRY, information hiding, ETC, maintainability, abstraction |
| **Execution** | Delivering value | Under-promise & over-deliver; define "good enough"; fix problems early; involve users |

---

## 1. Professionalism & Responsibility

Core principles about how to behave as an engineer:

**Think while you build** — Don't blindly code. Constantly question assumptions. Design evolves during implementation.

**Own your mistakes** — Admit them quickly. Never hide problems.

**No excuses — provide options.** Instead of "I couldn't finish because...", say: "I ran into X. Here are three possible ways forward."

**If you don't know...** Never stop at "I don't know." Say: "I don't know, but I'll find out."

**Respond immediately to problems** — Fix issues while they're small. If you can't solve them immediately: acknowledge, communicate, show progress. People tolerate delays much better than silence.

→ Related: [[Professional Responsibility]]

---

## 2. Engineering Mindset

**Avoid collateral damage** (Broken Windows Theory) — Broken things encourage more broken things. If you inherit messy code: improve it slightly, leave it cleaner than you found it.

→ Related: [[Broken Window Theory]]

**Know when to stop** — Perfect software doesn't exist. Eventually, diminishing returns appear and maintenance becomes more important than perfection.

→ Related: [[Good Enough Software]]

**We are always in maintenance mode** — Requirements change. Knowledge changes. Understanding changes. Design should assume change is inevitable.

→ Related: [[Maintenance Mindset]]

**Build for change** — Whenever adding code, ask: "Will this be easy to modify six months from now?" Good code is adaptable.

→ Related: [[ETC (Easier To Change)]]

---

## 3. Delivering Value

**Under-promise and over-deliver** — Figure out what's realistic. Deliver it exceptionally well. *Then* add: "It would also be nice if..."

**Success attracts people** — People prefer joining something already working. Show them progress, momentum, vision. A prototype is often more persuasive than a specification.

→ Related: [[Tracer Bullets]]

**Define "good enough"** — Whenever possible, include users in deciding what quality means. Some systems (like medical devices) don't allow compromise. Most products do.

→ Related: [[Good Enough Software]]

---

## 4. Continuous Learning

**Your knowledge expires** — Technology ages rapidly. Treat expertise like food: it has an expiration date.

**Diversify** — Don't become "the Java person." Become an engineer who knows many ways to solve problems.

**Learn emerging technologies early** — Before they're popular. Advantages: less competition, deeper understanding, better intuition.

**Learn one programming language every year** — Not because you'll use them. Every language teaches different ways of thinking:

- Haskell → functional thinking
- Rust → ownership
- Lisp → metaprogramming
- Prolog → logic programming

**Read constantly** — Technical: architecture, networking, distributed systems. Nontechnical: psychology, communication, design, history. Software is built for people.

**Experiment** — Use Windows, Linux, macOS. Try different IDEs, editors, workflows. Every environment teaches something.

**Once comfortable, move on** — Learning itself expands your thinking. Cross-pollination is often more valuable than mastery of one tool.

**Read outside your bubble** — Don't only follow your own ecosystem. A Java developer should occasionally read about Rust. A Python developer should read about Go.

→ Related: [[Knowledge Portfolio]]

---

## 5. Problem Solving

**Dig deeper** — When unsure, research. Even if you don't find the exact answer, you often discover better questions.

**Balance implementation and architecture** — If coding all day, read architecture. If designing all day, build software. Theory without practice is weak. Practice without theory stagnates.

---

## 6. Communication

**Learn communication deliberately** — Communication is an engineering skill. Study great speakers. Observe their clarity, pacing, explanations.

**Ask: "Does this communicate what I intend?"** — Communication isn't what you say. It's what the audience understands.

**Verify understanding** — Ask someone to summarize your explanation. If they misunderstand, improve the explanation — not the listener.

**Make meetings dialogues** — Less presenting, more questioning. People support ideas they helped create.

→ Related: [[Communication for Developers]]

---

## 7. Design Philosophy

### ETC — Easier To Change

This is one of the core ideas from *The Pragmatic Programmer*. Good design is about adaptability, not beauty. Every design decision should make future changes cheaper. Ask before every change: "Is this the easiest thing to change later?"

→ Related: [[ETC (Easier To Change)]]

### Good design is easy to change

Design isn't about aesthetics. It's about adaptability.

---

## 8. DRY (Don't Repeat Yourself)

**Key insight:** DRY is about duplication of *knowledge*, not duplication of code.

**Knowledge duplication** (bad): A business rule (e.g. minimum age = 18) repeated in frontend, backend, and database. Change one, forget another → bug.

**Code duplication** (sometimes acceptable): Two pieces of similar code can represent completely different knowledge that evolves independently.

**Breaking DRY intentionally:** Sometimes duplicate data for performance (e.g., caching expensive computations). The catch: **localize the violation** — hide the duplicated data inside one class that manages consistency.

→ Related: [[DRY Principle]], [[Representational Duplication]], [[Interdeveloper Duplication]]

---

## 9. Information Hiding

Don't expose implementation details. Expose behavior.

**Accessor functions** — Instead of exposing fields directly, use methods or properties. Benefits: validation, caching, logging, future flexibility — all without changing callers.

**Uniform Access Principle** — Users of a module shouldn't know whether data comes from memory, computation, cache, or database. The interface stays the same. Implementation stays flexible.

→ Related: [[Uniform Access Principle]]

---

## 10. Managing External Representations

Whenever software communicates with APIs, databases, or file formats: avoid manually duplicating schemas. Generate code from schemas or validate flexible structures. This reduces representational duplication.

→ Related: [[Representational Duplication]]

---

## 11. Team Knowledge

Duplication also happens between people. Prevent it with: code reviews, shared libraries, communication, documentation, ownership. Knowledge should spread intentionally.

→ Related: [[Interdeveloper Duplication]]

---

## Core Ideas (Compressed)

| Principle | Central Question |
| --- | --- |
| Professionalism | Am I taking ownership? |
| Continuous Learning | Am I becoming obsolete? |
| Design for Change | Will this be easy to modify? |
| Communication | Does my audience understand? |
| Deliver Value | Am I solving the right problem? |
| DRY | Am I duplicating knowledge? |
| Information Hiding | Can I change internals safely? |
| Maintainability | Am I leaving the code cleaner? |
| Curiosity | Have I investigated enough? |
| Adaptability | Am I preparing for future change? |

---

## Appendix: Code Review — Applying Information Hiding & Accessor Principles

> The following documents a code review session applying the core design principles above.

### 1. Information Hiding — 9.5/10

```python
class ShoppingCart:
    def __init__(self):
        self._items = []

    def add_item(self, item):
        if item not in self._items:
            self._items.append(item)

    def remove_item(self, item):
        if item in self._items:
            self._items.remove(item)

    def view_items(self):
        return self._items.copy()  # Safer: return tuple(self._items)
```

**Good:** Made list "private", exposed behavior, added duplicate checking.

**One subtle improvement:** `view_items()` returning `self._items.copy()` prevents callers from bypassing duplicate checks via `cart.view_items().append("Phone")`. A tuple is even safer — it communicates "look but don't modify."

### 2. Accessor Functions — 10/10

```python
class Employee:
    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, amount):
        self._salary = amount
        # validation, logging
```

**Correct:** Hid the field, used a property, validated, logged, kept the interface. Users still write `employee.salary = 7000` without knowing a setter is running.

### 3. Uniform Access Principle — 8.5/10

```python
class Weather:
    @property
    def temperature(self):
        return read_sensor()  # caller never knows it's computed
```

The caller writes `weather.temperature` without knowing whether it comes from memory, a sensor, a cache, a database, or an API. That's the Uniform Access Principle.

### How the Three Principles Build on Each Other

```markdown
Information Hiding
    └── Accessor Functions
            └── Uniform Access Principle
```

1. **Information Hiding** — the broad design philosophy: expose behavior, hide implementation.
2. **Accessor Functions** — a practical technique for exposing data safely when you must.
3. **Uniform Access Principle** — a guideline for designing accessors so callers never need to care where the data comes from.

They aren't competing principles — they're complementary, each operating at a different level of abstraction.

### Trade-off: Returning Internal State

The key question: *"If someone modifies the object I return, can they break my class's assumptions?"*

- **If yes** → don't expose it directly (use `.copy()`, `tuple()`, or a read-only view)
- **If no** → exposing may be acceptable (small scripts, performance-critical code, trusted callers)

Experienced engineers prefer the safer default (`return self._items.copy()` or `return tuple(self._items)`) because even your own code becomes "someone else's code" six months from now.

---

## Sources

- *The Pragmatic Programmer* (Hunt & Thomas): https://en.wikipedia.org/wiki/The_Pragmatic_Programmer
- *Clean Architecture* (Robert C. Martin): https://en.wikipedia.org/wiki/Clean_architecture
- *Object-Oriented Software Construction* (Bertrand Meyer) — Uniform Access Principle: https://en.wikipedia.org/wiki/Uniform_access_principle
- Broken windows theory: https://en.wikipedia.org/wiki/Broken_windows_theory
- Personal notes and code reviews