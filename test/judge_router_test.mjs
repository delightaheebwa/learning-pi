// Tests for the judge router: cache, budget, and Flash-Lite -> Flash escalation.
//
//   deno run --allow-all test/judge_router_test.mjs
import { createRouterJudge, isHardCase } from '../.pi/extensions/learning-gate/gate-core/judge/router.ts';

const assert = (n, c) => console.log((c ? 'PASS ' : 'FAIL ') + n);

const pkg = (over = {}) => ({
  flow: 'teach',
  explicitTag: 'claims',
  text: 'A is B. C is D.',
  hasVizFence: false,
  receipts: [{ index: 0, gate: 'fact_check', verdict: 'PASS', boundText: 'A is B.', issues: [], raw: '' }],
  pendingDrafts: [],
  hasIngestSummaryHint: false,
  hasReviewSummaryHint: false,
  tutorWrote: false,
  reviewSessionWrote: false,
  scoutCalled: true,
  reviewScoutCalled: false,
  writtenPaths: [],
  ...over,
});

const assessment = (over = {}) => ({
  turnType: 'claims',
  summaryKind: 'content',
  bindings: [{ index: 0, covers: true, uncovered: [] }],
  substantiveness: ['strong'],
  bestReceipt: 0,
  remedy: '',
  reason: '',
  source: 'model',
  ...over,
});

const judge = (kind, fn) => ({ kind, assessTurn: async (p) => fn(p), assessDispute: async () => ({ applies: true, reason: '', source: kind }) });

// --- a hard case (valid receipt that does not cover) escalates ---
{
  const primary = judge('model', () => assessment({ bindings: [{ index: 0, covers: false, uncovered: ['C is D.'] }] }));
  const esc = judge('model', () => assessment({ bindings: [{ index: 0, covers: true, uncovered: [] }] }));
  const router = createRouterJudge(primary, { escalate: esc, maxEscalationsPerDay: 10 });
  const r = await router.assessTurn(pkg());
  assert('hard case escalates to the secondary judge', r.escalated === true && r.bindings[0].covers === true);
}

// --- a clean case does NOT escalate ---
{
  let escCalls = 0;
  const primary = judge('model', () => assessment());
  const esc = judge('model', () => { escCalls++; return assessment(); });
  const router = createRouterJudge(primary, { escalate: esc, maxEscalationsPerDay: 10 });
  const r = await router.assessTurn(pkg());
  assert('clean case does not escalate', escCalls === 0 && r.escalated !== true);
}

// --- escalation is capped per day ---
{
  let escCalls = 0;
  const primary = judge('model', () => assessment({ bestReceipt: -1 }));
  const esc = judge('model', () => { escCalls++; return assessment(); });
  const router = createRouterJudge(primary, { escalate: esc, maxEscalationsPerDay: 1 });
  await router.assessTurn(pkg({ text: 'one' }));
  await router.assessTurn(pkg({ text: 'two' }));
  await router.assessTurn(pkg({ text: 'three' }));
  assert('escalation is capped per day', escCalls === 1);
}

// --- a primary outage escalates instead of failing ---
{
  const primary = judge('model', () => { throw new Error('503'); });
  const esc = judge('model', () => assessment());
  const router = createRouterJudge(primary, { escalate: esc, maxEscalationsPerDay: 10 });
  const r = await router.assessTurn(pkg());
  assert('primary outage falls through to the escalation judge', r.escalated === true);
}

// --- a primary outage with no escalation still throws (engine falls back) ---
{
  const primary = judge('model', () => { throw new Error('503'); });
  const router = createRouterJudge(primary, { maxEscalationsPerDay: 0 });
  let threw = false;
  try { await router.assessTurn(pkg()); } catch { threw = true; }
  assert('primary outage with no escalation throws for the legacy fallback', threw);
}

// --- isHardCase definition ---
{
  assert('isHardCase: no best receipt with receipts present', isHardCase(assessment({ bestReceipt: -1 }), pkg()));
  assert('isHardCase: thin substantiveness', isHardCase(assessment({ substantiveness: ['thin'] }), pkg()));
  assert('isHardCase: valid receipt uncovered', isHardCase(assessment({ bindings: [{ index: 0, covers: false, uncovered: [] }] }), pkg()));
  assert('isHardCase: clean case is not hard', !isHardCase(assessment(), pkg()));
}
