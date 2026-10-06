// Tests for the model judge adapter (gate-core/judge/model.ts).
//
//   deno run --allow-all test/judge_model_test.mjs
import { createModelJudge, JudgeModelError } from '../.pi/extensions/learning-gate/gate-core/judge/model.ts';

const assert = (n, c) => console.log((c ? 'PASS ' : 'FAIL ') + n);

const pkg = {
  flow: 'teach',
  explicitTag: undefined,
  text: 'A is B. C is D.',
  hasVizFence: false,
  receipts: [
    { index: 0, gate: 'fact_check', verdict: 'PASS', boundText: 'A is B.', issues: [], raw: '' },
    { index: 1, gate: 'fact_check', verdict: 'ISSUES', boundText: 'A is B. C is D.', issues: [{ severity: 'high' }], raw: '' },
  ],
  pendingDrafts: [],
  hasIngestSummaryHint: false,
  hasReviewSummaryHint: false,
  tutorWrote: false,
  reviewSessionWrote: false,
  scoutCalled: true,
  reviewScoutCalled: false,
  writtenPaths: [],
};

// --- valid JSON is coerced and aligned to receipts ---
{
  let sawSystem = '';
  const judge = createModelJudge(async ({ system, user }) => {
    sawSystem = system;
    return JSON.stringify({
      turnType: 'claims',
      summaryKind: 'content',
      bindings: [
        { index: 0, covers: false, uncovered: ['C is D.'] },
        { index: 1, covers: true, uncovered: [] },
      ],
      substantiveness: ['thin', 'strong'],
      bestReceipt: 1,
      remedy: 'verify C is D',
      reason: 'partial coverage',
    });
  });
  const a = await judge.assessTurn(pkg);
  assert('turnType parsed', a.turnType === 'claims');
  assert('bindings aligned to receipts', a.bindings.length === 2 && a.bindings[0].uncovered[0] === 'C is D.' && a.bindings[1].covers === true);
  assert('substantiveness parsed', a.substantiveness[0] === 'thin' && a.substantiveness[1] === 'strong');
  assert('remedy parsed', a.remedy === 'verify C is D');
  assert('source is model', a.source === 'model');
  assert('system prompt states the 100 percent rule', /100 percent|100%/.test(sawSystem));
  assert('system prompt carves out verdict-only grade turns', /GRADE TURNS/.test(sawSystem) && /verdict/i.test(sawSystem));
}

// --- index-keyed substantiveness survives out-of-order judge output ---
// A weak judge can emit the scores in a different order than the receipts; the
// index key keeps them aligned (the 2026-10-05 session scored a strong
// fact-check as "none" and blocked a valid claims turn).
{
  const judge = createModelJudge(async () =>
    JSON.stringify({
      turnType: 'claims',
      bindings: [
        { index: 0, covers: true, uncovered: [] },
        { index: 1, covers: true, uncovered: [] },
      ],
      substantiveness: [
        { index: 1, score: 'none' },
        { index: 0, score: 'strong' },
      ],
      bestReceipt: 0,
      reason: 'out of order',
    })
  );
  const a = await judge.assessTurn(pkg);
  assert('index-keyed substantiveness aligns by receipt index', a.substantiveness[0] === 'strong' && a.substantiveness[1] === 'none');
}

// --- an explicit tag wins over the model's classification ---
{
  const judge = createModelJudge(async () => JSON.stringify({ turnType: 'claims', bindings: [], substantiveness: [], bestReceipt: -1, reason: '' }));
  const a = await judge.assessTurn({ ...pkg, explicitTag: 'quiz' });
  assert('explicit tag overrides model classification', a.turnType === 'quiz');
}

// --- invalid JSON throws so the engine can fall back ---
{
  const judge = createModelJudge(async () => 'I could not decide.');
  let threw = false;
  try {
    await judge.assessTurn(pkg);
  } catch (e) {
    threw = e instanceof JudgeModelError;
  }
  assert('invalid JSON throws JudgeModelError', threw);
}

// --- dispute parses a boolean answer ---
{
  const judge = createModelJudge(async () => '```json\n{"applies": false, "reason": "stale"}\n```');
  const d = await judge.assessDispute({ text: 'x', issue: { issue: 'y' }, changes: ['(unchanged)'] });
  assert('dispute applies=false parsed', d.applies === false && d.reason === 'stale');
}
