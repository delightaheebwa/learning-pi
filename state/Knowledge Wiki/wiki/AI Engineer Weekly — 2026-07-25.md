<!-- provenance: status=verified | source=https://www.youtube.com/@aiDotEngineer (AI Engineer Conf talks) | verified-by=fact-check-agent | date=2026-10-26 -->

# AI Engineer Weekly — July 25, 2026

**10 talks from AI Engineer Conf — selected for someone tinkering with agents**

---

## The Big Picture

Three themes ran through this week's talks:

**1. Agents break in production, and the fix isn't in the prompt.**
Dex Horthy's lights-off factory failure story says it all: no amount of prompt engineering fixes a model that can't maintain codebase quality. Elizabeth Fuentes showed 5 code-level fixes for hallucinations — tool filtering, graph RAG, multi-agent validation, code-enforced rules, and runtime steering. Every single one is a code change, not a prompt change.

**2. The trend is toward simpler agent architectures.**
ZS Associates killed their multi-agent pipeline and replaced it with one agent + a knowledge graph. Lance Martin decouples brain from hands. Sam Bhagwat shows harnesses evolving toward claws: single agents that gradually gain autonomy. The message is consistent — distributed reasoning between agents creates coherence problems.

**3. Measure or regret it.**
Alex Shaw's claim: "agent development is ML, not software engineering — treat performance as a blackbox artifact you eval." Google DeepMind won't ship a skill without an eval suite. DSPy's entire thesis is that you need specs + code + evals to make agent programs reliable.

---

## Must Watch

🔴 **Harness Engineering is not Enough** — Dex Horthy, HumanLayer
The highest-signal talk this week. Dex ran a lights-off software factory where nobody read the code. It fell apart. He explains why current eval benchmarks can't measure codebase maintainability, and why reading code still matters. If you use agents to write production code, this is required viewing.

🔴 **Stop AI Agent Hallucinations: 5 Techniques** — Elizabeth Fuentes, AWS
Live-coded walkthrough of 5 techniques (semantic tool selection, graph RAG, multi-agent validation, neuro-symbolic guardians, runtime steering). Each one demonstrated with and without the fix. Practical enough to steal the code.

---

## By the Numbers

- **29 tools** in the demo travel agent → **3 tools** after semantic filtering. Token cost dropped from thousands to <300 per call.
- **15%** average improvement when skills are used (Skills Bench 1.1, across 100+ tasks).
- **17K views** on Dex Horthy's talk in 1 day. The industry is feeling this pain.
- **50%** of skill failures caused by bad descriptions, not bad logic (Google DeepMind).
- **117 test cases** used to tune one Gemini Interactions API skill from ~50% to ~90% accuracy.

---

## What to Actually Do

### On agent reliability
- Semantic tool selection is the easiest win. Build a vector index of tool schemas, filter to top-K before each call. Code change only, no prompt work.
- Graph RAG beats text RAG for any question involving counts, aggregations, or multi-hop relationships. If your agent answers "how many" questions, switch.
- Multi-agent validation catches failures the primary agent hides. A second agent with a rubric in a separate call is cheap insurance.

### On architecture
- Start with one agent. Add sub-agents only for parallel investigation tasks, not for distributed reasoning. The ZS team learned this the hard way.
- Use a knowledge graph as a control plane, not just a lookup. The agent navigates the graph; the graph bounds the agent's decision space.

### On evals for your own skills
- Start with 10-20 test prompts. 5 for "should trigger this skill," 5 for "should NOT trigger." Regex-based asserts are faster and cheaper than LLM judges.
- Run evals with and without the skill. Retire skills the model doesn't need anymore.

### On memory and context
- Give the model general memory tools (filesystem or database) but don't prescribe the schema. Let the model structure its own memory. Lance Martin's key finding from the Pokemon experiments.
- Use an offline "dreaming" pass to correct incorrect memories. The model writes bad context in-band; an out-of-band consolidation pass fixes it.

---

## Talk Index

| Talk | Speaker | Focus | Link |
|------|---------|-------|------|
| 🔴 Harness Engineering is not Enough | Dex Horthy, HumanLayer | Why code review still matters | [Watch](https://youtube.com/watch?v=Ib5GBkD555M) |
| 🔴 Stop AI Agent Hallucinations: 5 Techniques | Elizabeth Fuentes, AWS | Code-level fixes for hallucinations | [Watch](https://youtube.com/watch?v=vJukHCIv7Ck) |
| Why We Killed Our Multi-Agent Pipeline | Subbiah Sethuraman, ZS | Why one agent + graph beats many agents | [Watch](https://youtube.com/watch?v=u6jJcIFDLE4) |
| Don't Ship Skills Without Evals | Philipp Schmid, Google DeepMind | Practical eval workflow for agent skills | [Watch](https://youtube.com/watch?v=0vphxNt4wyk) |
| Claude for Long-Horizon Tasks | Lance Martin, Anthropic | Brain/hand decoupling, verifier loops, dreaming | [Watch](https://youtube.com/watch?v=9QebvrrY3KY) |
| Everything Is a Rollout | Alex Shaw, Harbor | Agent evals as rollouts, treat agents like ML models | [Watch](https://youtube.com/watch?v=jRCpXUjz4CI) |
| Every Harness Will Become A Claw | Sam Bhagwat, Mastra | Harness evolution toward autonomous agents | [Watch](https://youtube.com/watch?v=8qWIPUia2O8) |
| Separating Task from Model | Maxime Rivest & Isaac Miller, DSPy | Specs + code + evals as agent programming | [Watch](https://youtube.com/watch?v=GgLQ02aO-hs) |
| HTML Is All Agents Need | James Russo, HeyGen | Agents creating content in their native format | [Watch](https://youtube.com/watch?v=Cz4v1WHVyZc) |
| Why Agentic Systems Need Ontologies | Frank Coyle, UC Berkeley | Structured context to keep agents on rails | [Watch](https://youtube.com/watch?v=Sir59K8ZDPU) |

---

## How to Apply Right Now

1. **Filter your tools.** If your agent has more than 5-10 tools, build a semantic selector. Largest token savings, no model retraining.
2. **Eval one skill this week.** Pick your most-used skill, write 5 positive and 5 negative test prompts. You'll find at least one failure mode.
3. **Delete one agent from your pipeline.** If you have >1 agent doing reasoning, try consolidating to one. The ZS team's biggest improvement came from this.
4. **Add a second-agent verifier.** One generates output, one checks it with a rubric. Two separate calls, dramatically fewer hallucinations.
5. **Stop asking agents "how many" questions against text.** Use a graph database or structured query instead. The agent will invent numbers.
6. **Don't prescribe memory schemas.** Give the model a filesystem or database and let it learn to structure its own memory.
7. **Run an ablation on your skills.** Test performance with and without each skill. Retire anything below the threshold.

## Sources
- AI Engineer YouTube channel: https://www.youtube.com/@aiDotEngineer
