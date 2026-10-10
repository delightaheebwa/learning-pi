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

// --- S10b: a red (ISSUES) quiz receipt the judge marks covers:true must not
// shadow the valid PASS for the same gate (the 2026-10-10 warm-up loop). After a
// fix cycle the run holds two quiz receipts — the old ISSUES and the corrected
// PASS. When the judge marks the ISSUES receipt `covers:true` (alone, or
// alongside the PASS), `bindingFor` returned the invalid receipt first and
// stranded the fully-verified quiz as QUIZ_AUDIT_STALE.
{
  const batch = 'Warm-up — 3 quick MCQs.\n**W1.** What is entropy? A) surprise B) certainty C) zero D) negative';
  const oldDraft = 'Warm-up — 3 quick MCQs.\n**W1.** What is entropy? A) surprise B) certainty';
  const mintQuiz = (engine, draft, output) =>
    engine.onToolResult({
      tool: 'subagent',
      isError: false,
      text: output,
      dispatchCalls: [],
      mintCalls: [{ agent: 'quiz-audit', envelope: { gate: 'quiz_audit', rendered_content: draft }, output }],
    });
  const ISSUES = JSON.stringify({ verdict: 'ISSUES', issues: [{ severity: 'medium', location: 'W1', issue: 'length parity' }] });
  const PASS = JSON.stringify({ verdict: 'PASS', evidence: ['W1 checked'], issues: [] });
  const driveTwo = (coversFor, engine) => {
    engine.onBeforeAgentStart('[[FLOW:resume]] continue');
    mintQuiz(engine, oldDraft, ISSUES);
    mintQuiz(engine, batch, PASS);
  };

  // Judge marks BOTH receipts as covering — the invalid one would shadow the PASS.
  {
    const j = stubJudge({
      evaluate: (pkg) => ({
        turnType: 'quiz',
        bindings: pkg.receipts.map((r) => ({ index: r.index, covers: true, uncovered: [] })),
        bestReceipt: 1,
        reason: 'Receipt 1 is a strong PASS from quiz_audit and covers 100% of the emitted text.',
      }),
    });
    const engine = createGate({ judge: j.judge });
    driveTwo(() => true, engine);
    const res = await engine.onMessageEnd({ message: msg('[[TURN:quiz]]\n' + batch) });
    assert('red receipt marked covers does not shadow a valid PASS quiz', allowed(res));
  }

  // Judge binds only the invalid ISSUES receipt, but the PASS binds the text.
  {
    const j = stubJudge({
      evaluate: (pkg) => ({
        turnType: 'quiz',
        bindings: pkg.receipts.map((r) => ({ index: r.index, covers: r.index === 0, uncovered: [] })),
        bestReceipt: 0,
      }),
    });
    const engine = createGate({ judge: j.judge });
    driveTwo((i) => i === 0, engine);
    const res = await engine.onMessageEnd({ message: msg('[[TURN:quiz]]\n' + batch) });
    assert('binding that points at the red receipt falls back to the binding PASS', allowed(res));
  }

  // Guard: the fallback still blocks a genuinely stale quiz and a hollow PASS.
  {
    const j = stubJudge({
      evaluate: (pkg) => ({
        turnType: 'quiz',
        bindings: pkg.receipts.map((r) => ({ index: r.index, covers: false, uncovered: [] })),
        substantiveness: pkg.receipts.map(() => 'strong'),
        bestReceipt: -1,
      }),
    });
    const engine = createGate({ judge: j.judge });
    engine.onBeforeAgentStart('[[FLOW:resume]] continue');
    mintQuiz(engine, oldDraft, ISSUES);
    mintQuiz(engine, batch, PASS);
    const res = await engine.onMessageEnd({ message: msg('[[TURN:quiz]]\nEntirely different questions nobody audited. A) x B) y') });
    assert('a genuinely stale quiz is still withheld', blocked(res, 'QUIZ_AUDIT_STALE'));
  }
  {
    const j = stubJudge({
      evaluate: (pkg) => ({
        turnType: 'quiz',
        bindings: pkg.receipts.map((r) => ({ index: r.index, covers: true, uncovered: [] })),
        substantiveness: pkg.receipts.map(() => 'none'),
        bestReceipt: 1,
      }),
    });
    const engine = createGate({ judge: j.judge });
    engine.onBeforeAgentStart('[[FLOW:resume]] continue');
    mintQuiz(engine, oldDraft, ISSUES);
    mintQuiz(engine, batch, PASS);
    const res = await engine.onMessageEnd({ message: msg('[[TURN:quiz]]\n' + batch) });
    assert('a hollow PASS is still withheld (G-pass-substantive holds)', blocked(res, 'QUIZ_AUDIT_STALE'));
  }
}

// --- S11: a verdict-only grade turn binds even when the judge marks it uncovered ---
// The grade-audit binds the graded question/answer/verdict; a terse verdict
// presentation is not literally covered by the full question text. The engine
// must not let the judge's 100% span coverage dead-end that turn (the
// 2026-10-06 resume session looped as GRADE_AUDIT_STALE on exactly this).
{
  const gradeEnv = {
    gate: 'grade_audit',
    items: [
      {
        id: 1,
        question:
          'You centered a cloud of 3 points and summed the squared (co)deviations for every covariance entry — the sums came out as plain numbers. What do you divide those sums by to get the covariance matrix?',
        learner_answer: 'B',
        claimed_verdict: 'pass',
      },
      {
        id: 2,
        question: 'A 2-feature blob has eigenvalues λ1 = 6 and λ2 = 2. You keep only the first principal axis. What fraction of the total variance did you keep?',
        learner_answer: 'C',
        claimed_verdict: 'pass',
      },
      {
        id: 3,
        question:
          'X is n×d and you keep k principal components, so V is d×k. What is the shape of the projected data Xp = Xc @ V?',
        learner_answer: 'A',
        claimed_verdict: 'pass',
      },
    ],
  };
  const gradeOut = JSON.stringify({
    verdict: 'PASS',
    agrees: true,
    correct_verdict: 'pass',
    issues: [],
    items: [
      { id: 1, agrees: true, correct_verdict: 'pass', explanation: 'divisor n-1' },
      { id: 2, agrees: true, correct_verdict: 'pass', explanation: 'kept fraction 3/4' },
      { id: 3, agrees: true, correct_verdict: 'pass', explanation: 'n×k shape' },
    ],
  });
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'grade',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: false, uncovered: ['the confirmation framing'] })),
      bestReceipt: -1,
    }),
  });
  const engine = createGate({ judge: j.judge });
  drive(engine, { scout: false });
  engine.onToolResult({
    tool: 'subagent',
    isError: false,
    text: gradeOut,
    dispatchCalls: [],
    mintCalls: [{ agent: 'grade-audit', envelope: gradeEnv, output: gradeOut }],
  });
  const res = await engine.onMessageEnd({ message: msg('[[TURN:grade]]\nCorrect on all three: **W1 B, W2 C, W3 A** ✓.') });
  assert('verdict-only grade turn binds despite uncovered judge verdict', allowed(res));
}

// --- S12: a grade+repair turn renders when the grade-audit and a fact-check cover it ---
{
  const prose = 'Name the slip: biased 1/n instead of unbiased 1/(n−1). Detector: with n points the denominator is n−1.';
  const gradeEnv = JSON.stringify({
    gate: 'grade_audit',
    question: 'What do you divide the centered sums by?',
    learner_answer: '3',
    claimed_verdict: 'fail',
  });
  const gradeOut = JSON.stringify({ verdict: 'PASS', agrees: true, correct_verdict: 'fail', issues: [], items: [{ id: 1, agrees: true, correct_verdict: 'fail' }] });
  const fcEnv = JSON.stringify({ gate: 'fact_check', rendered_content: prose, claims: [{ id: 1, claim: 'the denominator is n-1' }] });
  const fcOut = JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }], contradictions: [] });
  const j = stubJudge({
    evaluate: (pkg) => {
      const bindings = pkg.receipts.map((r) =>
        r.gate === 'fact_check'
          ? { index: r.index, covers: true, uncovered: [] }
          : { index: r.index, covers: false, uncovered: [prose] }
      );
      return { turnType: 'grade', bindings, bestReceipt: -1 };
    },
  });
  const engine = createGate({ judge: j.judge });
  drive(engine, { scout: false });
  const mint = (agent, envelope, output) =>
    engine.onToolResult({ tool: 'subagent', isError: false, text: output, dispatchCalls: [], mintCalls: [{ agent, envelope, output }] });
  mint('grade-audit', JSON.parse(gradeEnv), gradeOut);
  mint('fact-check', JSON.parse(fcEnv), fcOut);
  const res = await engine.onMessageEnd({ message: msg('[[TURN:grade]]\nThat is wrong by a divisor slip. ' + prose) });
  assert('grade+repair turn renders when grade-audit and fact-check both cover it (judge path)', allowed(res));
}

// --- S13: a stale disagreeing grade receipt must not block a later grade+repair turn ---
// The 2026-10-06 review close looped as GRADE_MISMATCH: an old `agrees:false`
// receipt persisted after a corrected agreeing re-dispatch, so every later grade
// turn blocked even though the newest verdict agreed and a fact-check covered
// the prose. Only the newest grade verdict may block.
{
  const prose =
    'Direction right, but the concrete X, Y, Z instantiation was skipped. Name the slip and give a detector for next time.';
  const badEnv = JSON.stringify({
    gate: 'grade_audit',
    items: [{ id: 2, question: 'Q2 restate screening-off', learner_answer: 'abstract', claimed_verdict: 'fail' }],
  });
  const badOut = JSON.stringify({
    verdict: 'ISSUES',
    agrees: false,
    correct_verdict: 'fail',
    issues: [{ id: 2, correction: 'no instantiation' }],
    items: [{ id: 2, agrees: false, correct_verdict: 'fail' }],
  });
  const goodEnv = JSON.stringify({
    gate: 'grade_audit',
    items: [{ id: 3, question: 'Q3 fill the blanks', learner_answer: 'spoilt', claimed_verdict: 'pass' }],
  });
  const goodOut = JSON.stringify({
    verdict: 'PASS',
    agrees: true,
    correct_verdict: 'pass',
    issues: [],
    items: [{ id: 3, agrees: true, correct_verdict: 'pass' }],
  });
  const fcEnv = JSON.stringify({ gate: 'fact_check', rendered_content: prose, claims: [{ id: 1, claim: 'x' }] });
  const fcOut = JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }], contradictions: [] });
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'grade',
      bindings: pkg.receipts.map((r) =>
        r.gate === 'fact_check'
          ? { index: r.index, covers: true, uncovered: [] }
          : { index: r.index, covers: false, uncovered: [prose] }
      ),
      bestReceipt: -1,
    }),
  });
  const engine = createGate({ judge: j.judge });
  drive(engine, { scout: false });
  const mint = (agent, envelope, output) =>
    engine.onToolResult({ tool: 'subagent', isError: false, text: output, dispatchCalls: [], mintCalls: [{ agent, envelope, output }] });
  mint('grade-audit', JSON.parse(badEnv), badOut);
  mint('grade-audit', JSON.parse(goodEnv), goodOut);
  mint('fact-check', JSON.parse(fcEnv), fcOut);
  const res = await engine.onMessageEnd({ message: msg('[[TURN:grade]]\n' + prose) });
  assert('newest grade verdict supersedes an older disagreement (judge path)', allowed(res));
}

// --- S14: a review-flow none summary over verified prose renders ---
{
  const closing = 'Review closed. Direction right; the spoilt-food fill-in passed. Any deeper dig before I close?';
  const fcEnv = JSON.stringify({ gate: 'fact_check', rendered_content: closing, claims: [{ id: 1, claim: 'x' }] });
  const fcOut = JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }], contradictions: [] });
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'none',
      summaryKind: 'review',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: r.gate === 'fact_check', uncovered: [] })),
      bestReceipt: -1,
    }),
  });
  const engine = createGate({ judge: j.judge });
  engine.onBeforeAgentStart('[[FLOW:review]] review my due concepts');
  engine.onToolResult({ tool: 'subagent', isError: false, text: fcOut, dispatchCalls: [], mintCalls: [{ agent: 'fact-check', envelope: JSON.parse(fcEnv), output: fcOut }] });
  const res = await engine.onMessageEnd({ message: msg('[[TURN:none]]\n' + closing) });
  assert('review-flow none summary over a verified draft renders (judge path)', allowed(res));
}

// --- S15: the same none tag outside review is still withheld as evasion ---
{
  const prose = 'Verified teaching prose that was then mis-tagged none, outside any review flow.';
  const fcEnv = JSON.stringify({ gate: 'fact_check', rendered_content: prose, claims: [{ id: 1, claim: 'x' }] });
  const fcOut = JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }], contradictions: [] });
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'none',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: r.gate === 'fact_check', uncovered: [] })),
      bestReceipt: -1,
    }),
  });
  const engine = createGate({ judge: j.judge });
  drive(engine, { scout: false });
  engine.onToolResult({ tool: 'subagent', isError: false, text: fcOut, dispatchCalls: [], mintCalls: [{ agent: 'fact-check', envelope: JSON.parse(fcEnv), output: fcOut }] });
  const res = await engine.onMessageEnd({ message: msg('[[TURN:none]]\n' + prose) });
  assert('none over a verified draft still withholds outside review (judge path)', blocked(res, 'TURN_TAG_MISMATCH'));
}

// --- S16: a DROPPED tag read as `none` is recovered from the bound fact-check ---
// The 2026-10-07 resume loop: the tutor emitted an untagged, 100%-fact-checked
// pause, the judge read it as `none`, and the non-review evasion guard withheld
// TURN_TAG_MISMATCH forever (retagging `none` could not fix it). A dropped tag
// is recovered from the bound receipt (G-infer-claims-from-bound).
{
  const pause = 'Mini 4 sealed. Coming next: the round-cloud degenerate case, then the practice. Any questions before we move on?';
  const fcEnv = JSON.stringify({ gate: 'fact_check', rendered_content: pause, claims: [{ id: 1, claim: 'x' }] });
  const fcOut = JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }], contradictions: [] });
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'none',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: r.gate === 'fact_check', uncovered: [] })),
      bestReceipt: -1,
    }),
  });
  const engine = createGate({ judge: j.judge });
  engine.onBeforeAgentStart('[[FLOW:resume]] continue the lesson');
  engine.onToolResult({ tool: 'subagent', isError: false, text: fcOut, dispatchCalls: [], mintCalls: [{ agent: 'fact-check', envelope: JSON.parse(fcEnv), output: fcOut }] });
  const res = await engine.onMessageEnd({ message: msg(pause) });
  assert('dropped tag recovered from bound fact-check when the judge reads it as none', allowed(res));
}

// --- S17: the judge path cannot soften the deterministic solo guard (P0 H2) ---
{
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'claims',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: true, uncovered: [] })),
      bestReceipt: 0,
    }),
  });
  const engine = createGate({ judge: j.judge });
  engine.onBeforeAgentStart('[[FLOW:solo]] solo check');
  const env = JSON.stringify({ gate: 'fact_check', rendered_content: 'The definition of X is the thing.', claims: [{ id: 1, claim: 'x' }] });
  engine.onToolResult({ tool: 'subagent', isError: false, text: FC_PASS, dispatchCalls: [], mintCalls: [{ agent: 'fact-check', envelope: JSON.parse(env), output: FC_PASS }] });
  const res = await engine.onMessageEnd({ message: msg('[[TURN:claims]]\nThe definition of X is the thing.') });
  assert('judge path withholds a solo teaching claims turn', blocked(res, 'SOLO_NO_TEACHING'));
}

// --- S18: the judge path still enforces hard-fact completeness (P0 H2) ---
{
  const hard = 'The sample size is n=200.';
  const j = stubJudge({
    evaluate: (pkg) => ({
      turnType: 'claims',
      bindings: pkg.receipts.map((r) => ({ index: r.index, covers: true, uncovered: [] })),
      bestReceipt: 0,
    }),
  });
  const engine = createGate({ judge: j.judge });
  engine.onBeforeAgentStart('[[FLOW:resume]] continue the lesson');
  const env = JSON.stringify({ gate: 'fact_check', rendered_content: hard, claims: [{ id: 1, claim: 'small sample' }] });
  engine.onToolResult({ tool: 'subagent', isError: false, text: FC_PASS, dispatchCalls: [], mintCalls: [{ agent: 'fact-check', envelope: JSON.parse(env), output: FC_PASS }] });
  const res = await engine.onMessageEnd({ message: msg(`[[TURN:claims]]\n${hard}`) });
  assert('judge path withholds claims with an unlisted hard fact', blocked(res, 'CLAIMS_INCOMPLETE'));
}
