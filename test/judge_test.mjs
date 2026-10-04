// Tests for the judge-driven gate path (gate-core/engine.ts with a judge).
//
//   deno run --allow-all test/judge_test.mjs
//
// The judge here is a stub: it returns scripted assessments so the engine's
// policy (tags-as-hints, 100% coverage, PASS-real, no-cap, dispute) is tested
// deterministically and offline. The model judge's prompt/parse is covered by
// test/judge_model_test.mjs.
import { createGate } from '../.pi/extensions/learning-gate/gate-core/engine.ts';

const assert = (n, c) => console.log((c ? 'PASS ' : 'FAIL ') + n);

const outText = (r) => {
  if (!r || !r.message) return '';
  const c = r.message.content;
  if (typeof c === 'string') return c;
  if (Array.isArray(c)) return c.map((p) => (p && p.type === 'text' ? p.text : '')).join('');
  return '';
};
const allowed = (r) => r && r.message && !outText(r).startsWith('⛔');
const blocked = (r, code) => !!(r && r.message && outText(r).startsWith('⛔') && (!code || outText(r).includes(code)));

const FC_ENV = JSON.stringify({ gate: 'fact_check', rendered_content: 'The definition of X is the thing.', claims: [] });
const FC_PASS = JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }], contradictions: [] });
const FC_ISSUES_HIGH = JSON.stringify({
  verdict: 'ISSUES',
  issues: [{ severity: 'high', location: 'X', issue: 'the definition of X is wrong' }],
});

/**
 * A scriptable judge. `script` maps a predicate over the package to an
 * assessment partial; `dispute` answers the dispute call.
 */
function stubJudge({ evaluate, dispute = { applies: true, reason: 'still applies', source: 'replay' } }) {
  let lastPkg = null;
  const judge = {
    kind: 'replay',
    async assessTurn(pkg) {
      lastPkg = pkg;
      const base = {
        turnType: pkg.explicitTag || 'none',
        summaryKind: 'content',
        bindings: pkg.receipts.map((r) => ({ index: r.index, covers: false, uncovered: [] })),
        substantiveness: pkg.receipts.map(() => 'strong'),
        bestReceipt: -1,
        remedy: '',
        reason: 'stub',
        source: 'replay',
      };
      const over = evaluate ? evaluate(pkg) : {};
      return { ...base, ...over, bindings: over.bindings || base.bindings, substantiveness: over.substantiveness || base.substantiveness };
    },
    async assessDispute() {
      return typeof dispute === 'function' ? dispute() : dispute;
    },
  };
  return { judge, getPkg: () => lastPkg };
}

const msg = (t, stop = 'stop') => ({ role: 'assistant', content: [{ type: 'text', text: t }], stopReason: stop });

function drive(engine, { scout = true } = {}) {
  engine.onBeforeAgentStart('[[FLOW:teach]] teach X');
  if (scout) engine.onToolCall({ tool: 'subagent', input: {}, calls: [{ agent: 'scout' }], agentless: false });
}

const mintFC = (engine, output = FC_PASS) =>
  engine.onToolResult({
    tool: 'subagent',
    isError: false,
    text: output,
    dispatchCalls: [],
    mintCalls: [{ agent: 'fact-check', envelope: JSON.parse(FC_ENV), output }],
  });

// --- S1: tags become hints — an untagged claims turn is classified by the judge ---
{
  const j = stubJudge({ evaluate: (pkg) => ({ turnType: 'claims', bindings: pkg.receipts.map((r) => ({ index: r.index, covers: true, uncovered: [] })), bestReceipt: 0 }) });
  const engine = createGate({ judge: j.judge });
  drive(engine);
  mintFC(engine);
  const res = await engine.onMessageEnd({ message: msg('The definition of X is the thing.') });
  assert('untagged claims turn allowed via judge classification', allowed(res));
  assert('untagged turn tag stripped / not present', !outText(res).includes('[[TURN'));
}

// --- S2: 100% coverage — an uncovered span blocks and the remedy names it ---
{
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'claims',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: false, uncovered: ['X is also Y'] })),
      bestReceipt: -1,
    }),
  });
  const engine = createGate({ judge: j.judge });
  drive(engine);
  mintFC(engine);
  const res = await engine.onMessageEnd({ message: msg('The definition of X is the thing. X is also Y.') });
  assert('uncovered span blocks', blocked(res, 'FACT_CHECK_MISMATCH'));
  assert('remedy names the uncovered span', outText(res).includes('X is also Y'));
}

// --- S3: PASS-real — a hollow PASS does not verify ---
{
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'claims',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: true, uncovered: [] })),
      substantiveness: pkg.receipts.map(() => 'none'),
      bestReceipt: 0,
    }),
  });
  const engine = createGate({ judge: j.judge });
  drive(engine);
  mintFC(engine);
  const res = await engine.onMessageEnd({ message: msg('The definition of X is the thing.') });
  assert('hollow PASS blocked as unsubstantiated', blocked(res, 'FACT_CHECK_UNSUBSTANTIATED'));
}

// --- S4: no-cap — a persistent high issue never becomes UNVERIFIED ---
{
  const j = stubJudge({ evaluate: () => ({ turnType: 'claims' }), dispute: { applies: true, reason: 'still wrong', source: 'replay' } });
  const engine = createGate({ judge: j.judge });
  drive(engine);
  mintFC(engine, FC_ISSUES_HIGH);
  let sawUnverified = false;
  for (let i = 0; i < 6; i++) {
    const res = await engine.onMessageEnd({ message: msg('The definition of X is the thing.') });
    if (outText(res).includes('UNVERIFIED')) sawUnverified = true;
  }
  assert('high/medium issue never dumps as UNVERIFIED', !sawUnverified);
}

// --- S5: dispute — the judge can clear a stale issue after three blocks ---
{
  let calls = 0;
  const j = stubJudge({
    evaluate: () => ({ turnType: 'claims' }),
    dispute: () => {
      calls++;
      return { applies: false, reason: 'the current draft no longer contains this error', source: 'replay' };
    },
  });
  const engine = createGate({ judge: j.judge });
  drive(engine);
  mintFC(engine, FC_ISSUES_HIGH);
  let released = null;
  for (let i = 0; i < 3; i++) released = await engine.onMessageEnd({ message: msg('The definition of X is the thing.') });
  assert('dispute was asked on the third block', calls === 1);
  assert('dispute releases the turn with VERIFIER DISPUTED', allowed(released) && outText(released).includes('VERIFIER DISPUTED'));
}

// --- S6: the judge receives full receipts with their bound text ---
{
  const j = stubJudge({ evaluate: () => ({ turnType: 'claims' }) });
  const engine = createGate({ judge: j.judge });
  drive(engine);
  mintFC(engine);
  await engine.onMessageEnd({ message: msg('The definition of X is the thing.') });
  const pkg = j.getPkg();
  assert('judge package carries the receipt', pkg && pkg.receipts.length === 1 && pkg.receipts[0].gate === 'fact_check');
  assert('judge package carries the verified draft', pkg && pkg.receipts[0].boundText === JSON.parse(FC_ENV).rendered_content);
}

// --- S7: a judge failure falls back to the legacy deterministic path ---
{
  const bad = {
    kind: 'replay',
    async assessTurn() {
      throw new Error('judge down');
    },
    async assessDispute() {
      throw new Error('judge down');
    },
  };
  const engine = createGate({ judge: bad });
  drive(engine);
  mintFC(engine);
  const res = await engine.onMessageEnd({ message: msg('[[TURN:claims]]\nThe definition of X is the thing.') });
  assert('judge failure falls back to legacy checks', allowed(res));
}

// --- S8: a bare ISSUES verdict with no concrete issue text never disputes ---
{
  let disputeCalls = 0;
  const j = stubJudge({
    evaluate: () => ({ turnType: 'claims' }),
    dispute: () => {
      disputeCalls++;
      return { applies: false, reason: 'no details', source: 'replay' };
    },
  });
  const engine = createGate({ judge: j.judge });
  drive(engine);
  mintFC(engine, JSON.stringify({ verdict: 'ISSUES', issues: [] }));
  for (let i = 0; i < 4; i++) await engine.onMessageEnd({ message: msg('The definition of X is the thing.') });
  assert('issue with no concrete text never triggers a dispute', disputeCalls === 0);
}

// --- S9: a quiz receipt binds on the full batch `rendered_content` ---
// The judge enforces 100% coverage of the emitted turn; a questions-only
// envelope strands every quiz as QUIZ_AUDIT_STALE. The full batch must reach
// the judge as boundText.
{
  const batch = 'Review — 1 due item. Reply with the letter.\n1. What is entropy? A) surprise B) certainty';
  const env = {
    gate: 'quiz_audit',
    rendered_content: batch,
    questions_json: [{ id: 1, type: 'mcq', question: 'What is entropy?', options: ['A) surprise', 'B) certainty'] }],
  };
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'quiz',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: true, uncovered: [] })),
      bestReceipt: 0,
    }),
  });
  const engine = createGate({ judge: j.judge });
  drive(engine);
  engine.onToolResult({
    tool: 'subagent',
    isError: false,
    text: JSON.stringify({ verdict: 'PASS', issues: [] }),
    dispatchCalls: [],
    mintCalls: [{ agent: 'quiz-audit', envelope: env, output: JSON.stringify({ verdict: 'PASS', issues: [] }) }],
  });
  const res = await engine.onMessageEnd({ message: msg('[[TURN:quiz]]\n' + batch) });
  assert('quiz turn with full rendered_content binds', allowed(res));
  assert('judge package carries the full quiz batch as boundText', j.getPkg().receipts[0].boundText === batch);
}

// --- S10: without rendered_content the derived bound text still includes options ---
{
  const env = {
    gate: 'quiz_audit',
    questions_json: [{ id: 1, type: 'mcq', question: 'What is entropy?', options: ['A) surprise', 'B) certainty'] }],
  };
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'quiz',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: true, uncovered: [] })),
      bestReceipt: 0,
    }),
  });
  const engine = createGate({ judge: j.judge });
  drive(engine);
  engine.onToolResult({
    tool: 'subagent',
    isError: false,
    text: JSON.stringify({ verdict: 'PASS', issues: [] }),
    dispatchCalls: [],
    mintCalls: [{ agent: 'quiz-audit', envelope: env, output: JSON.stringify({ verdict: 'PASS', issues: [] }) }],
  });
  await engine.onMessageEnd({ message: msg('[[TURN:quiz]]\nWhat is entropy? A) surprise B) certainty') });
  const pkg = j.getPkg();
  assert('derived quiz boundText includes the options', pkg.receipts[0].boundText.includes('A) surprise'));
}
