// LIVE smoke test for the judge against the real Gemini endpoint.
//
//   GEMINI_API_KEY=... deno run --allow-net --allow-env test/live_judge_test.mjs
//
// Opt-in: skipped when GEMINI_API_KEY is unset. It is NOT part of learn-check.
// It validates the endpoint, the model id, and that the model honors the 100%
// coverage rule.
import { createModelJudge } from '../.pi/extensions/learning-gate/gate-core/judge/model.ts';

if (!globalThis.Deno?.env?.get('GEMINI_API_KEY')) {
  console.log('SKIP live judge (GEMINI_API_KEY not set)');
} else {
  const model = (globalThis.Deno.env.get('LEARNING_GATE_JUDGE_MODEL') || 'gemini/gemini-3.5-flash-lite').split('/').pop();
  const assert = (n, c) => console.log((c ? 'PASS ' : 'FAIL ') + n);

  const complete = async ({ system, user, maxTokens }) => {
    const res = await fetch('https://generativelanguage.googleapis.com/v1beta/openai/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${globalThis.Deno.env.get('GEMINI_API_KEY')}`,
      },
      body: JSON.stringify({
        model,
        messages: [{ role: 'user', content: `${system}\n\n${user}` }],
        max_tokens: maxTokens || 2000,
      }),
    });
    if (!res.ok) throw new Error(`gemini ${res.status}: ${(await res.text()).slice(0, 300)}`);
    const j = await res.json();
    return j.choices?.[0]?.message?.content ?? '';
  };

  const judge = createModelJudge(complete);
  const pkg = {
    flow: 'teach',
    explicitTag: undefined,
    text: 'A is B. C is D.',
    hasVizFence: false,
    receipts: [
      { index: 0, gate: 'fact_check', verdict: 'PASS', boundText: 'A is B.', issues: [], raw: '' },
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
  const a = await judge.assessTurn(pkg);
  console.log('live assessment:', JSON.stringify(a));
  assert('live: classifies the turn as claims', a.turnType === 'claims');
  assert('live: partial coverage is NOT covered (100% rule)', a.bindings[0] && a.bindings[0].covers === false);
  assert('live: names the uncovered span', (a.bindings[0]?.uncovered || []).length > 0);
}
