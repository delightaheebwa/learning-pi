# ADR-0003: Adopt a solo-first operating mode with the contract as the verification layer

- Status: Accepted
- Date: 2026-11-19
- Deciders: repo owner (learning-pi)

## Context

A 2026-11-19 methodology review compared a distillation of Justin Sung's coaching videos
(Nov 2023 to Nov 2026, 127 captioned uploads) element by element with this repo's teaching
contract and flows. Sung's claims are coaching experience, not independently verified research.
The source document is outside the repo. This ADR records what matters from it.

The comparison found overlap, not conflict. Sung's current positions are already contract
invariants here, and `docs/teaching-methodology.md` anchors them: free recall over recognition,
fluency treated as suspect, prediction before feedback, interleaving, retrieval at real
difficulty, AI never authoring the learner's structure. His superseded positions are what this
system was built to avoid: flashcard-centric study, coverage speed as the metric, AI summaries
replacing learning. A wholesale rewrite would discard verified behavior to import what is already
present.

The owner then set the direction that survived review. The pre-contact phase of Sung's system is
learner-owned solo work: metacognitive radar, gist priming, prediction from headings, multi-pass
reading, iterative messy mind-mapping, the confusion compass. The system's role narrows to three
jobs: gist and keyword priming support before reading, ingest of the learner's finished products
(notes and photographed mind-maps), and scheduled free recall afterwards.

Two research passes tested that direction.

Evidence on the learning design:

- Solo generative encoding is the best-supported part. Self-explanation shows g = 0.55 across 64
  studies (Bisra et al., 2018). Attempting an explanation punctures the illusion of explanatory
  depth (Rozenblit & Keil, 2002). Struggling before instruction beats instruction-first (Sinha &
  Kapur, 2021, meta-analysis).
- Ungraded repeated retrieval is the specific hazard. The testing effect reversed in a no-feedback
  design: learners consolidated their own erroneous pairings (Tse, Balota & Roediger, 2010).
  Self-scored free recall gives partial or full credit to completely wrong answers (Grimaldi &
  Karpicke, 2014). Retrieval's advantage over elaborative encoding is conditional on feedback
  (Gonçalves et al., 2025, meta-analysis). Hypercorrection, the finding most often cited for
  "errors now, feedback later", is mechanistically a feedback effect (Butterfield & Metcalfe,
  2006). Uncorrected high-confidence errors return at retest (Butler, Fazio & Marsh, 2011).
- New reading does not reliably correct an old wrong model. Revision requires co-activation and
  refutation of the existing conception (Kendeou's KReC framework; Posner et al., 1982). A
  coherent wrong model absorbs plain expository text without triggering revision.
- Expertise reversal (Kalyuga et al., 2003; 2025 meta-analysis of 60 experiments) argues for
  assistance on first exposure to a new domain and against it for review in known domains.

The review also checked the Excalidraw ingest. There, the owner photographs a paper mind-map,
and the agent transcribes the photo into an `.excalidraw` file that ingest then parses:

- `.excalidraw` is plain JSON with an element array. Labeled boxes plus bound arrows reduce
  offline and dependency-free to nodes and edges. Excalidraw core and CLI are MIT.
- The format has no machine-readable schema. The file version stays 2 while the element schema
  drifts, and bindings migrated from v1 to v2 upstream with no version bump. The parser must read
  only `elementId` and treat other binding fields as optional.
- The main failure mode of hand-drawn files is unbound arrows. Agent-generated files avoid it:
  every arrow the agent writes is fully bound by construction. Any geometrically inferred edge
  must be marked `inferred` and never mixed with binding-derived edges.
- Rendering for confirmation is offline. The official `@excalidraw/cli render` uses a local
  browser, and jsdom plus resvg is the deterministic alternative. No Excalidraw MCP server is
  warranted. Parsing is about a hundred lines, and the servers add a runtime and a supply-chain
  risk for no benefit. Two licensing cautions: the official `excalidraw-mcp` repo ships no
  LICENSE, and the Obsidian plugin is AGPL. Neither is needed.
- Mermaid `mindmap` is a rejected fallback for snapshots. It is a strict tree, indentation only,
  with no edge labels and no cross-links, and it discards the spatial semantics the mind-maps
  exist to record. Mermaid stays the rendering choice inside sessions.

## Decision

Adopt the solo-first operating mode as a usage pattern. The contract, its tests, and the `.pi/`
teaching behavior are unchanged. No invariant is edited, and the revise door stays closed.

Division of labor:

- The learner owns all pre-contact encoding: radar, priming self-checks, prediction from
  headings, multi-pass reading, messy paper mind-maps, the confusion compass. No AI dialogue
  during refinement.
- The agent's three jobs: gist and keyword lists for priming (low-level delegation that Sung's
  own AI rules permit); faithful transcription of a photographed mind-map into `.excalidraw`, as
  transcription and never as improvement, since reorganizing or completing the model would be
  model ghostwriting; ingest of the transcription into the graph and wiki as a dated, verbatim
  mental-model snapshot.
- Transcription discipline. The photograph is archived in `Knowledge Wiki/raw/assets/` as the
  immutable source. The learner confirms the rendered transcription before ingest.
- `/teach` and `/lesson` remain the entry point for first exposure to a new domain, on the
  expertise-reversal evidence. Solo-first mode applies to expansion and review.
- The review flow is the mandatory guardrail and is kept unchanged. Every recall item ends in a
  ground-truth comparison against the source, with confidence rated before checking. Ungraded
  recall is the known failure mode this decision rules out.
- A learning log (tried, prediction, result, next experiment) records the pilot, with one or two
  changes at a time.
- The memorization filter (why is this important, how does it relate to what is already known,
  is high-level mastery needed) is applied before anything reaches rote scheduling. It is piloted
  manually against repeatedly failing facts before any code is proposed.

## Consequences

- This ADR and the later pilot artifacts are ordinary commits. Nothing here needs the revise
  door.
- The system's value concentrates at the recall checkpoints. The review flow's diff against
  sources is what converts a wrong candidate model into a corrected one. The evidence predicts
  that solo study without that loop produces confident, rehearsed errors.
- The wiki and graph gain dated verbatim mental-model snapshots, which also enrich cross-session
  attack material.
- Transcription errors can corrupt the verbatim record. The photograph is the source of truth,
  and the confirm step stays in the flow.
- Sung's unverified claims are adopted only as learner-side protocol. Nothing unverified becomes
  an invariant.

## Revisit when

- The pilot log shows the entry gate or the graduation gates conflicting with solo-first usage.
  Then a small revise-door change is justified, for example a formally recognized "closed with
  open questions" session outcome. Land one invariant cluster per commit.
- The manual memorization-filter pilot succeeds and needs to become part of the review flow.
  Wiring it in is an ordinary commit if the ingest envelope absorbs it. It needs the revise door
  if contracted clerk behavior must change.
- An Excalidraw schema drift breaks the parser. Tolerant parsing, pinned versions, and a single
  render adapter are the containment.
- The pilot is abandoned or revised. Supersede this ADR rather than editing it.
