// Regression tests for the learning-gate extension.
//
//   deno run --allow-all test/gate_test.mjs
//
// Covers the partial-generation dead-end: an assistant message whose
// generation did not finish (`stopReason` error/aborted/length) must pass
// through ungated without consuming a verifier receipt, so the retried or
// continued message can still bind to it.
// Keep the always-on receipt ledger out of the real pi agent dir during tests.
process.env.LEARNING_GATE_LEDGER_DIR = '/tmp/learning-gate-test/';
const handlers = {};
const tools = {};
const listeners = {};
const eventBus = {
  on: (ev, h) => {
    (listeners[ev] ||= []).push(h);
    return () => {
      const a = listeners[ev] || [];
      const i = a.indexOf(h);
      if (i >= 0) a.splice(i, 1);
    };
  },
  emit: (ev, payload) => {
    for (const h of [...(listeners[ev] || [])]) h(payload);
  },
};
const pi = {
  on: (ev, h) => {
    (handlers[ev] ||= []).push(h);
  },
  registerTool: (t) => {
    tools[t.name] = t;
  },
  events: eventBus,
};
const mod = await import('../.pi/extensions/learning-gate/index.ts');
mod.default(pi);
const P = await import('../.pi/extensions/learning-gate/gate-core/primitives.ts');
const fire = async (ev, e) => { let r; for (const h of handlers[ev] || []) r = await h(e, { ui: { notify() {} } }); return r; };
const setPrompt = (p) => fire('before_agent_start', { prompt: p });
const msg = (t, stopReason) => fire('message_end', { message: { role: 'assistant', content: [{ type: 'text', text: t }], stopReason } });
const notify = (t) => fire('message_end', { message: { role: 'custom', customType: 'subagent-notify', content: [{ type: 'text', text: t }] } });
const dispatch = async (agent, task, id) => { await fire('tool_call', { toolName: 'subagent', toolCallId: id, input: { agent, task } }); };
const writeCall = (path, id) => fire('tool_call', { toolName: 'write', toolCallId: id, input: { filePath: path, content: 'x' } });
const bashCall = (command, id) => fire('tool_call', { toolName: 'bash', toolCallId: id, input: { command } });
const outText = (r) => {
  if (!r || !r.message) return '';
  const c = r.message.content;
  if (typeof c === 'string') return c;
  if (Array.isArray(c)) return c.map((p) => (p && p.type === 'text' ? p.text : '')).join('');
  return '';
};
const allowed = (r) => r && r.message && !outText(r).startsWith('⛔');
const blocked = (r, code) => !!(r && r.message && outText(r).startsWith('⛔') && (!code || outText(r).includes(code)));
const stripped = (r) => allowed(r) && !outText(r).includes('[[TURN');
const assert = (n, c) => console.log((c ? 'PASS ' : 'FAIL ') + n);

const GATE = JSON.stringify({ verdict: 'PASS', agrees: true, correct_verdict: 'pass', issues: [] });
const NOTIFY = `Background task completed: **grade-audit**\n\ngrade-audit:\n[[TURN:none]]\n${GATE}\n\nRetention-managed async directory: /tmp/x`;
const PARTIAL = '[[TURN:grade]]\nGraded (verifier-agreed):\n\n| Item | Verdict |\n|---|---|\n| W1 | PASS |';
const FULL = '[[TURN:grade]]\nGraded (verifier-agreed): W1 PASS, W2 PASS, W3 FAIL. Use the verifier verdicts.';
const ENVELOPE = JSON.stringify({ gate: 'grade_audit', question: 'W1', learner_answer: 'C', claimed_verdict: 'pass' });

// --- bug: errored partial grade turn must not consume the receipt ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('grade-audit', ENVELOPE, 'c1');
await notify(NOTIFY);
const partial = await msg(PARTIAL, 'error');
assert('errored partial is not withheld', allowed(partial));
assert('errored partial has tag stripped', stripped(partial));
const full = await msg(FULL, 'stop');
assert('re-emitted grade turn allowed after errored partial', allowed(full));
assert('re-emitted grade turn tag stripped', stripped(full));

// --- regression: a normal (completed) grade turn still consumes the receipt ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('grade-audit', ENVELOPE, 'c2');
await notify(NOTIFY);
const first = await msg(FULL, 'stop');
assert('normal grade turn allowed', allowed(first));
const second = await msg(FULL, 'stop');
assert('second grade turn blocked once receipt consumed', blocked(second, 'NO_GRADE_AUDIT_PASS'));

// --- regression: block still fires when there is no receipt at all ---
await setPrompt('[[FLOW:resume]] continue the lesson');
const none = await msg(FULL, 'stop');
assert('grade turn with no receipt withheld', blocked(none, 'NO_GRADE_AUDIT_PASS'));

// ============================================================================
// New hardening tests (scout receipt, ingest scoping, evidence, fallback).
// ============================================================================
const fg = (id, agent, task, output) =>
  fire('tool_result', {
    toolName: 'subagent',
    toolCallId: id,
    isError: false,
    content: [{ type: 'text', text: '' }],
    details: { results: [{ agent, task, finalOutput: output, runId: `r-${id}` }] },
  });
// Real pi-subagents compaction: a completed foreground result reaches extensions
// with `task` redacted and `messages` dropped. The gate must recover the dispatch
// envelope from `tool_call`, not from the (now unusable) result task.
const fgRedacted = (id, agent, output) =>
  fire('tool_result', {
    toolName: 'subagent',
    toolCallId: id,
    isError: false,
    content: [{ type: 'text', text: output }],
    details: { mode: 'single', runId: `r-${id}`, results: [{ index: 0, agent, task: '[prompt redacted]', finalOutput: output }] },
  });
const subFail = (id, text) =>
  fire('tool_result', { toolName: 'subagent', toolCallId: id, isError: true, content: [{ type: 'text', text }] });
const fcEnvelope = (draft) =>
  JSON.stringify({ gate: 'fact_check', claims: [{ id: 1, claim: 'x' }], rendered_content: draft, source_urls: ['https://e.com'] });
const FC_PASS = JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }], contradictions: [] });
const REVIEW_PASS = JSON.stringify({ verdict: 'PASS', evidence: ['read X.md'], issues: [], context_notes: [] });
const CLERK_WRITES = '[[TURN:none]]\nCLERK_WRITES: {"wiki":["Knowledge Wiki/wiki/X.md"],"state":[],"concepts":["X"],"commit":"abc"}';

// --- 2026-10-05: a grade turn that also teaches/repairs ---
// The grade-audit binds only the graded question/answer/verdict, so a repair
// tail is not covered by it. When the repair prose is separately fact-checked
// (rendered_content = the full turn), the two receipts together cover the turn
// and it must render (the 2026-10-05 session looped as GRADE_AUDIT_STALE).
const repairDraft =
  'Close — your dot products are right, but you divided by 3. The recipe divides by n−1, and with 3 points that is 2, so C = [[4,2],[2,4]]. Name the slip: biased 1/n instead of unbiased 1/(n−1). Detector: with n points the denominator is n−1. Micro-check: recompute with 3 points and divide by 2.';
const repairGradeEnv = JSON.stringify({
  gate: 'grade_audit',
  concept: 'PCA',
  question:
    'Compute entry (1,2) of the covariance matrix C as the dot product of the centered columns divided by (n−1), then the diagonal entries the same way — what is C?',
  learner_answer: 'I believe the answer is the identity matrix because the two columns look independent to me',
  claimed_verdict: 'fail',
});
const repairGradeResult = JSON.stringify({
  verdict: 'PASS',
  agrees: true,
  correct_verdict: 'fail',
  issues: [],
  items: [{ id: 1, agrees: true, correct_verdict: 'fail', explanation: 'divisor slip' }],
});
const repairFcEnv = JSON.stringify({
  gate: 'fact_check',
  claims: [{ id: 1, claim: 'the recipe divides by n-1' }],
  rendered_content: repairDraft,
  source_urls: ['https://e.com'],
});
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('grade-audit', repairGradeEnv, 'gr1');
await fg('gr1', 'grade-audit', repairGradeEnv, repairGradeResult);
await dispatch('fact-check', repairFcEnv, 'fc1');
await fg('fc1', 'fact-check', repairFcEnv, JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok', corrected_claim: null }] }));
const combined = await msg('[[TURN:grade]]\n' + repairDraft, 'stop');
assert('grade+repair turn allowed when grade-audit and fact-check both cover it', allowed(combined));

await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('grade-audit', repairGradeEnv, 'gr2');
await fg('gr2', 'grade-audit', repairGradeEnv, repairGradeResult);
const staleRepair = await msg('[[TURN:grade]]\n' + repairDraft, 'stop');
assert('grade+repair without a fact-check is GRADE_AUDIT_STALE', blocked(staleRepair, 'GRADE_AUDIT_STALE'));

// --- 2026-10-06: a verdict-only grade turn ---
// The grade-audit binds only the graded question/answer/verdict, so a terse
// verdict presentation ("Correct on all three: W1 B, W2 C, W3 A") is not
// literally covered by the full question text. A grade turn that only presents
// the graded answers must still bind the receipt (the 2026-10-06 resume session
// looped as GRADE_AUDIT_STALE on exactly this).
const verdictOnlyEnv = JSON.stringify({
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
      question:
        'A 2-feature blob has eigenvalues λ1 = 6 and λ2 = 2. You keep only the first principal axis. What fraction of the total variance did you keep?',
      learner_answer: 'C',
      claimed_verdict: 'pass',
    },
    {
      id: 3,
      question:
        'X is n×d and you keep k principal components, so V (the directions matrix) is d×k. What is the shape of the projected data Xp = Xc @ V — and what does its shape tell you?',
      learner_answer: 'A',
      claimed_verdict: 'pass',
    },
  ],
});
const verdictOnlyResult = JSON.stringify({
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
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('grade-audit', verdictOnlyEnv, 'gr3');
await fg('gr3', 'grade-audit', verdictOnlyEnv, verdictOnlyResult);
const verdictOnly = await msg('[[TURN:grade]]\nCorrect on all three: **W1 B, W2 C, W3 A** ✓.', 'stop');
assert('verdict-only grade turn binds a full-sentence grade envelope', allowed(verdictOnly));

// A teaching/repair tail behind the same full-sentence envelope is still stale
// without its own fact-check (the dual-verify invariant is preserved).
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('grade-audit', verdictOnlyEnv, 'gr4');
await fg('gr4', 'grade-audit', verdictOnlyEnv, verdictOnlyResult);
const verdictOnlyRepair = await msg('[[TURN:grade]]\nCorrect on all three. ' + repairDraft, 'stop');
assert('verdict-only envelope does not cover a repair tail', blocked(verdictOnlyRepair, 'GRADE_AUDIT_STALE'));

// --- P1.2: a tagged follow-up after an ingest summary must not be held hostage ---
await setPrompt('[[FLOW:ingest]] ingest this');
await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), 'ing1');
await notify(`Background task completed: **clerk**\n\n${CLERK_WRITES}`);
await dispatch('review-gate', JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'Knowledge Wiki/wiki/X.md' }] }), 'rg1');
await notify(`Background task completed: **review-gate**\n\n[[TURN:none]]\n${REVIEW_PASS}`);
const ingestSummary = await msg(
  '[[TURN:none]]\nIngest complete. REVIEW_GATE_VERDICT: {"verdict":"PASS"} STATE_AUDIT_VERDICT: {"errors":0,"warnings":0}',
  'stop'
);
assert('ingest summary renders', allowed(ingestSummary));
const ingestFollowup = await msg('[[TURN:none]]\nThe Clerk was reviewed by an independent review-gate run.', 'stop');
assert('tagged ingest follow-up not held hostage', allowed(ingestFollowup));

// --- P2.1: a Clerk-relayed verdict surfaces the INGEST GATE provenance banner ---
await setPrompt('[[FLOW:ingest]] ingest this');
await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), 'ing2');
await notify('Background task completed: **clerk**\n\n[[TURN:none]]\nREVIEW_GATE_VERDICT: {"verdict":"PASS","issues":[]}');
const relayed = await msg('[[TURN:none]]\nIngest complete. STATE_AUDIT_VERDICT: {"errors":0,"warnings":0}', 'stop');
assert('clerk-relayed verdict triggers INGEST GATE banner', allowed(relayed) && outText(relayed).includes('INGEST GATE'));

// --- P2.2: a review verdict with no evidence list surfaces the unsubstantiated banner ---
await setPrompt('[[FLOW:ingest]] ingest this');
await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), 'ing3');
await notify(`Background task completed: **clerk**\n\n${CLERK_WRITES}`);
await dispatch('review-gate', JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'p.md' }] }), 'rg3');
await notify('Background task completed: **review-gate**\n\n[[TURN:none]]\n{"verdict":"PASS","issues":[],"context_notes":[]}');
const noEvidence = await msg('[[TURN:none]]\nIngest complete. STATE_AUDIT_VERDICT: {"errors":0,"warnings":0}', 'stop');
assert('missing-evidence banner surfaced', allowed(noEvidence) && outText(noEvidence).includes('no `evidence`'));

// --- A1: a Scout with no parseable receipt surfaces the unverified banner ---
const DRAFT = 'The definition of X is the thing.';
await setPrompt('[[FLOW:teach]] teach me X');
await dispatch('scout', 'topic X', 'sc1');
await notify('Background task completed: **scout**\n\nSCOUT DIGEST: no machine line here');
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc1');
await fg('fc1', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const scoutUnverified = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('scout-unverified banner surfaced', allowed(scoutUnverified) && outText(scoutUnverified).includes('SCOUT DIGEST UNVERIFIED'));

// --- A1: a Scout with failed_refs surfaces the incomplete-sources banner ---
await setPrompt('[[FLOW:teach]] teach me Y');
await dispatch('scout', 'topic Y', 'sc2');
await notify('Background task completed: **scout**\n\nSCOUT_DIGEST: {"slug":"y","digest":"Learning System/.tmp/context-x.json","raw_files":[],"failed_refs":[{"url":"u","reason":"404"}]}');
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc2');
await fg('fc2', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const scoutIncomplete = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('sources-incomplete banner surfaced', allowed(scoutIncomplete) && outText(scoutIncomplete).includes('SOURCES INCOMPLETE'));

// --- B: two provider failures surface the fallback-model directive ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('fact-check', fcEnvelope(DRAFT), 'ff1');
await subFail('ff1', 'OpenAI API error (503): service_overloaded');
await dispatch('fact-check', fcEnvelope(DRAFT), 'ff2');
await subFail('ff2', 'OpenAI API error (503): service_overloaded');
const fallbackMsg = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('fallback directive after two provider failures', outText(fallbackMsg).includes('failed 2') && outText(fallbackMsg).includes('deepseek-v4.1-flash'));

// ============================================================================
// 2026-09-21 resume hardening: async fact-check binding, duplicate-dispatch
// guard, claims-tag inference, grade `items[]` tolerance, corrected re-dispatch.
// ============================================================================
const uuid1 = 'ab12cd34-ef56-4a78-9b90-1234567890ab';
const uuid2 = 'bc23de45-fa67-4b89-8c01-2345678901bc';
const uuid3 = 'cd34ef56-ab78-4c90-8d12-3456789012cd';
const uuid4 = 'de45fa67-bc89-4d01-8e23-4567890123de';
const vDraft = 'The variation of information is V(X,Y) = H(X,Y) minus I(X,Y), equal to H(X|Y) plus H(Y|X).';

const asyncDispatch = (id, agent, task) =>
  fire('tool_call', { toolName: 'subagent', toolCallId: id, input: { agent, task } });
const asyncResult = (id, runId) =>
  fire('tool_result', {
    toolName: 'subagent',
    toolCallId: id,
    isError: false,
    content: [{ type: 'text', text: `Async: ${runId}` }],
    details: { asyncId: runId },
  });
const fcNotify = (runId, body) =>
  notify(`Background task completed: **fact-check**\n\nfact-check:\n[[TURN:none]]\n${body}\n\nRetention-managed async directory: /tmp/x/async-subagent-runs/${runId}`);
const gradeNotify = (runId, body) =>
  notify(`Background task completed: **grade-audit**\n\ngrade-audit:\n[[TURN:none]]\n${body}\n\nRetention-managed async directory: /tmp/x/async-subagent-runs/${runId}`);

// --- async fact-check mints a *bound* receipt; a duplicate re-dispatch is blocked ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('a1', 'fact-check', fcEnvelope(vDraft));
await asyncResult('a1', uuid1);
fcNotify(uuid1, FC_PASS);
const dup = await asyncDispatch('a2', 'fact-check', fcEnvelope(vDraft));
assert('duplicate fact-check of a verified draft is blocked', !!(dup && dup.block));
const asyncClaims = await msg(`[[TURN:claims]]\n${vDraft}`, 'stop');
assert('async fact-check binds its tagged claims turn', allowed(asyncClaims));

// --- a dropped claims tag is recovered from the bound receipt ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('a3', 'fact-check', fcEnvelope(vDraft));
await asyncResult('a3', uuid2);
fcNotify(uuid2, FC_PASS);
const untaggedClaims = await msg(vDraft, 'stop');
assert('dropped claims tag recovered from bound fact-check', allowed(untaggedClaims));

// --- malformed grade `items[]` envelope still binds a dropped-tag grade turn ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch(
  'a4',
  'grade-audit',
  JSON.stringify({ gate: 'grade_audit', items: [{ question: 'Compute I(X;Y).', learner_answer: '-0.119', claimed_verdict: 'fail' }] })
);
await asyncResult('a4', uuid3);
gradeNotify(uuid3, JSON.stringify({ verdict: 'PASS', agrees: true, correct_verdict: 'fail', issues: [] }));
const itemsGrade = await msg('Compute I(X;Y) for the fresh joint: FAIL — -0.119, the sign is impossible.', 'stop');
assert('items[] grade envelope binds a dropped-tag grade turn', allowed(itemsGrade));

// --- batched `items[]` grade envelope: several answers, ONE dispatch ---
const uuid7 = '1b2c3d4e-5f60-4789-9a01-2345678901cd';
const uuid8 = '2c3d4e5f-6071-4890-ab12-3456789012de';
const batchEnvelope = JSON.stringify({
  gate: 'grade_audit',
  items: [
    { id: 1, concept: 'A', question: 'Q1 compute the number', learner_answer: 'B', claimed_verdict: 'pass' },
    { id: 2, concept: 'B', question: 'Q2 compute the number', learner_answer: 'A', claimed_verdict: 'fail' },
  ],
});
const batchText = '[[TURN:grade]]\nQ1 compute the number — PASS (answer B); Q2 compute the number — FAIL (answer A).';
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('a7', 'grade-audit', batchEnvelope);
await asyncResult('a7', uuid7);
gradeNotify(
  uuid7,
  JSON.stringify({
    verdict: 'PASS',
    agrees: true,
    correct_verdict: 'pass',
    issues: [],
    items: [
      { id: 1, agrees: true, correct_verdict: 'pass', explanation: 'ok' },
      { id: 2, agrees: true, correct_verdict: 'fail', explanation: 'as claimed' },
    ],
  })
);
const batchGrade = await msg(batchText, 'stop');
assert('batched items[] grade envelope binds a multi-answer grade turn', allowed(batchGrade));

// --- a batched mismatch surfaces which answers the verifier corrected ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('a8', 'grade-audit', batchEnvelope);
await asyncResult('a8', uuid8);
gradeNotify(
  uuid8,
  JSON.stringify({
    verdict: 'ISSUES',
    agrees: false,
    correct_verdict: 'pass',
    issues: ['#2 wrong'],
    items: [
      { id: 1, agrees: true, correct_verdict: 'pass', explanation: 'ok' },
      { id: 2, agrees: false, correct_verdict: 'pass', explanation: 'the dot product is shown' },
    ],
  })
);
const batchMismatch = await msg(batchText, 'stop');
assert(
  'batched grade mismatch surfaces per-item corrections',
  blocked(batchMismatch, 'GRADE_MISMATCH') && outText(batchMismatch).includes('#2 → pass')
);

// --- a materially corrected batch clears the mismatch and renders ---
const uuid9 = '3d4e5f60-7182-4903-bc34-567890123def';
const uuid10 = '4e5f6071-8293-4014-cd56-789012345efa';
const correctedEnvelope = JSON.stringify({
  gate: 'grade_audit',
  items: [
    { id: 1, concept: 'A', question: 'Q1 compute the number', learner_answer: 'B', claimed_verdict: 'pass' },
    { id: 2, concept: 'B', question: 'Q2 compute the number', learner_answer: 'A', claimed_verdict: 'pass' },
  ],
});
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('a9', 'grade-audit', batchEnvelope);
await asyncResult('a9', uuid9);
gradeNotify(
  uuid9,
  JSON.stringify({
    verdict: 'ISSUES',
    agrees: false,
    correct_verdict: 'pass',
    issues: ['#2 wrong'],
    items: [
      { id: 1, agrees: true, correct_verdict: 'pass', explanation: 'ok' },
      { id: 2, agrees: false, correct_verdict: 'pass', explanation: 'the dot product is shown' },
    ],
  })
);
await asyncDispatch('a10', 'grade-audit', correctedEnvelope);
await asyncResult('a10', uuid10);
gradeNotify(
  uuid10,
  JSON.stringify({
    verdict: 'PASS',
    agrees: true,
    correct_verdict: 'pass',
    issues: [],
    items: [
      { id: 1, agrees: true, correct_verdict: 'pass', explanation: 'ok' },
      { id: 2, agrees: true, correct_verdict: 'pass', explanation: 'confirmed' },
    ],
  })
);
const corrected = await msg('[[TURN:grade]]\nQ1 compute the number — PASS (answer B); Q2 compute the number — PASS (answer A).', 'stop');
assert('corrected batched re-dispatch clears the mismatch', allowed(corrected));

// --- an ISSUES verdict does not block a materially corrected re-dispatch ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('a5', 'fact-check', fcEnvelope(vDraft));
await asyncResult('a5', uuid4);
fcNotify(uuid4, JSON.stringify({ verdicts: [{ id: 1, verdict: 'ISSUES', explanation: 'sign inverted', corrected_claim: 'ratio > 1 is a positive term' }], contradictions: [] }));
const redispatch = await asyncDispatch('a6', 'fact-check', fcEnvelope(`${vDraft} Costs dominate the rebates.`));
assert('corrected re-dispatch after ISSUES is allowed', !(redispatch && redispatch.block));

// --- a genuinely unverified untagged message is still withheld ---
await setPrompt('[[FLOW:resume]] continue the lesson');
const bare = await msg('Nice work — shall we continue?', 'stop');
assert('unverified untagged message still withheld', blocked(bare, 'NO_TURN_TAG'));

// --- 2026-09-21 evasion: `[[TURN:none]]` must not slip a pending fact-check draft ---
const uuid5 = 'ef56ab78-cd90-4e12-9f34-5678901234ef';
const uuid6 = 'fa67bc89-de01-4f23-8a45-6789012345fa';
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('n1', 'fact-check', fcEnvelope(vDraft));
await asyncResult('n1', uuid5);
const noneBypass = await msg(`[[TURN:none]]\n${vDraft}`, 'stop');
assert('none-tagged teaching draft withheld while fact-check in flight', blocked(noneBypass, 'FACT_CHECK_PENDING'));
const early = await msg(`[[TURN:claims]]\n${vDraft}`, 'stop');
assert('claims emit before notification is withheld with a wait hint', blocked(early, 'NO_FACT_CHECK_MATCH') && outText(early).includes('still in flight'));
fcNotify(uuid5, FC_PASS);
const afterNotify = await msg(`[[TURN:claims]]\n${vDraft}`, 'stop');
assert('claims emit after the completion notification renders', allowed(afterNotify));

// --- 2026-09-22: a compacted foreground task must still bind its receipt ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('fact-check', fcEnvelope(vDraft), 'rfc1');
await fgRedacted('rfc1', 'fact-check', FC_PASS);
const redactedTagged = await msg(`[[TURN:claims]]\n${vDraft}`, 'stop');
assert('redacted foreground task binds a tagged claims turn', allowed(redactedTagged));
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('fact-check', fcEnvelope(vDraft), 'rfc2');
await fgRedacted('rfc2', 'fact-check', FC_PASS);
const redactedUntagged = await msg(vDraft, 'stop');
assert('redacted foreground task binds a dropped-tag claims turn', allowed(redactedUntagged));

// --- 2026-10-03: a double-encoded `task` must still bind its receipt ---
// Some models pass the envelope as a JSON string literal (the task value
// literally begins with a quote and carries escaped inner quotes), sometimes
// leaving the object's final `}` outside the quotes. The gate must unwrap it so
// the passing fact-check binds instead of dead-ending with
// FACT_CHECK_MISSING_DRAFT.
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('fact-check', JSON.stringify(fcEnvelope(vDraft)), 'rfc3');
await fgRedacted('rfc3', 'fact-check', FC_PASS);
const quotedTask = await msg(`[[TURN:claims]]\n${vDraft}`, 'stop');
assert('double-encoded (quoted) task binds a tagged claims turn', allowed(quotedTask));
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('fact-check', JSON.stringify(fcEnvelope(vDraft)) + '}', 'rfc4');
await fgRedacted('rfc4', 'fact-check', FC_PASS);
const quotedTrailingBrace = await msg(`[[TURN:claims]]\n${vDraft}`, 'stop');
assert('double-encoded task with a stray trailing brace binds', allowed(quotedTrailingBrace));

// --- 2026-09-26: a receipt from a wrong-shape envelope must not bind ---
// A quiz-audit sent with `items[]` (no `questions_json`) mints a valid receipt
// with no bound text. It must NOT authorize an unrelated quiz turn (the empty
// bound used to fall through the back-compat path and bind anything).
await setPrompt('[[FLOW:resume]] continue the lesson');
const itemsQuiz = JSON.stringify({ gate: 'quiz_audit', purpose: 'probe', items: [{ id: 1, question: 'What is the entropy of a fair coin?' }] });
await dispatch('quiz-audit', itemsQuiz, 'sq1');
await fg('sq1', 'quiz-audit', itemsQuiz, JSON.stringify({ verdict: 'PASS', issues: [] }));
const wrongShapeQuiz = await msg('[[TURN:quiz]]\nState the KL divergence identity and compute it for Q=(0.5,0.5), P=(0.8,0.2).', 'stop');
assert('wrong-shape quiz receipt does not bind an unrelated quiz turn', blocked(wrongShapeQuiz, 'QUIZ_AUDIT_STALE'));

// A correctly shaped `questions_json` receipt binds only its own batch.
await setPrompt('[[FLOW:resume]] continue the lesson');
const qEnv = JSON.stringify({ gate: 'quiz_audit', purpose: 'probe', questions_json: [{ id: 1, question: 'State the KL divergence identity.' }] });
await dispatch('quiz-audit', qEnv, 'sq2');
await fg('sq2', 'quiz-audit', qEnv, JSON.stringify({ verdict: 'PASS', issues: [] }));
const boundQuiz = await msg('[[TURN:quiz]]\nState the KL divergence identity.', 'stop');
assert('questions_json quiz receipt binds its own batch', allowed(boundQuiz));

// A quiz envelope with the full batch as `rendered_content` binds the whole
// emitted turn (intro + options), not just the question stems.
await setPrompt('[[FLOW:resume]] continue the lesson');
const fullBatch = 'Review — 1 due item. Reply with the letter.\n1. What is entropy? A) surprise B) certainty';
const fullEnv = JSON.stringify({
  gate: 'quiz_audit',
  rendered_content: fullBatch,
  questions_json: [{ id: 1, type: 'mcq', question: 'What is entropy?', options: ['A) surprise', 'B) certainty'] }],
});
await dispatch('quiz-audit', fullEnv, 'sq3');
await fg('sq3', 'quiz-audit', fullEnv, JSON.stringify({ verdict: 'PASS', issues: [] }));
const fullQuiz = await msg('[[TURN:quiz]]\n' + fullBatch, 'stop');
assert('rendered_content quiz receipt binds the full batch', allowed(fullQuiz));

// An envelope-less async notification still mints an unbound receipt that binds
// (its dispatch could not be correlated, so there is nothing to bind against).
await setPrompt('[[FLOW:resume]] continue the lesson');
await notify('Background task completed: **quiz-audit**\n\nquiz-audit:\n[[TURN:none]]\n{"verdict":"PASS","issues":[]}\n\nRetention-managed async directory: /tmp/x/legacy-notify');
const legacyQuiz = await msg('[[TURN:quiz]]\nWhat is the entropy of a fair coin?', 'stop');
assert('envelope-less async quiz receipt still binds its turn', allowed(legacyQuiz));

// --- 2026-09-26: write-gate receipts that name no artifacts must not bind ---
// tutor-audit without `files` audited nothing identifiable.
await setPrompt('[[FLOW:teach]] teach me X');
await writeCall('Learning System/Lessons/Lesson — X.md', 'tw1');
await dispatch('tutor-audit', JSON.stringify({ gate: 'tutor_audit', flow: 'pause' }), 'twa1');
await fg('twa1', 'tutor-audit', JSON.stringify({ gate: 'tutor_audit', flow: 'pause' }), JSON.stringify({ verdict: 'PASS', issues: [] }));
const noFilesTutor = await msg('[[TURN:none]]\nLesson handoff complete.', 'stop');
assert('tutor-audit without files does not release the handoff summary', blocked(noFilesTutor, 'NO_TUTOR_AUDIT'));

// review-session-audit without `written_files` cannot have audited the writes.
await setPrompt('[[FLOW:review]] review my due concepts');
await bashCall("python3 scripts/ops.py apply <<'SPEC'\nLearning System/Sessions/Session — Review — 2026-09-26.md\nSPEC", 'rw1');
await dispatch('review-session-audit', JSON.stringify({ gate: 'review_session', concepts: ['X'] }), 'rsa1');
await fg('rsa1', 'review-session-audit', JSON.stringify({ gate: 'review_session', concepts: ['X'] }), JSON.stringify({ verdict: 'PASS', evidence: ['read'], issues: [] }));
const noWritesRS = await msg('Review — mastery 4/5, next review 2026-10-01. Recap below.', 'stop');
assert('review-session audit without written_files does not release the close summary', blocked(noWritesRS, 'NO_REVIEW_SESSION_AUDIT'));

// review-gate without `target_files` reviewed nothing.
await setPrompt('[[FLOW:ingest]] ingest this');
await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), 'ic1');
await notify('Background task completed: **clerk**\n\n[[TURN:none]]\nCLERK_WRITES: {"wiki":["Knowledge Wiki/wiki/X.md"],"state":[],"concepts":["X"],"commit":"abc"}');
await dispatch('review-gate', JSON.stringify({ gate: 'review', concepts: ['X'] }), 'irg1');
await fg('irg1', 'review-gate', JSON.stringify({ gate: 'review', concepts: ['X'] }), JSON.stringify({ verdict: 'PASS', evidence: ['x'], issues: [], context_notes: [] }));
const noTargetsRG = await msg('[[TURN:none]]\nIngest complete. STATE_AUDIT_VERDICT: {"errors":0,"warnings":0}', 'stop');
assert('review-gate without target_files does not release the ingest summary', blocked(noTargetsRG, 'NO_REVIEW_GATE_PASS'));

// --- a failed async verifier clears the in-flight state (no stale hint) ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('n2', 'fact-check', fcEnvelope(vDraft));
await asyncResult('n2', uuid6);
await notify(`Background task failed: **fact-check**\n\nfact-check:\nOpenAI API error (429): rate_limit_exceeded\n\nRetention-managed async directory: /tmp/x/async-subagent-runs/${uuid6}`);
const afterFail = await msg(`[[TURN:claims]]\n${vDraft}`, 'stop');
assert('failed verifier is not reported as in-flight', blocked(afterFail, 'NO_FACT_CHECK_MATCH') && !outText(afterFail).includes('still in flight'));

// --- 2026-10-05: the `dispatch` helper accepts the envelope as an OBJECT ---
// The `subagent` tool requires `task` to be a JSON string; a flash model emits
// it as an object and dead-ends (`task: must be string`, 2026-10-05 resume).
// `dispatch` takes the envelope object, runs the child through pi-subagents'
// structured delegation bridge, and mints the gate receipt itself.
await setPrompt('[[FLOW:resume]] continue the lesson');
assert('dispatch helper is registered', !!tools.dispatch && typeof tools.dispatch.execute === 'function');

// Simulate the pi-subagents structured delegation bridge.
const bridgeOutput = '[[TURN:none]]\n{"verdict":"PASS","issues":[]}';
const reqListeners = (listeners['prompt-template:subagent:request'] ||= []);
reqListeners.push((payload) => {
  eventBus.emit('prompt-template:subagent:started', {
    requestId: payload.requestId,
    ownerRunId: payload.ownerRunId,
    nodeId: payload.nodeId,
  });
  eventBus.emit('prompt-template:subagent:response', {
    requestId: payload.requestId,
    ownerRunId: payload.ownerRunId,
    nodeId: payload.nodeId,
    status: 'completed',
    agent: payload.agent,
    result: { kind: 'text', text: bridgeOutput },
  });
});

const dispatchBatch = 'Recall — reply with the letter.\n1. What is entropy? A) surprise B) certainty';
const dispatchRes = await tools.dispatch.execute(
  'd1',
  {
    agent: 'quiz-audit',
    task: {
      gate: 'quiz_audit',
      rendered_content: dispatchBatch,
      questions_json: [{ id: 1, type: 'mcq', question: 'What is entropy?', options: ['A) surprise', 'B) certainty'] }],
      purpose: 'probe',
    },
  },
  undefined,
  undefined,
  { cwd: '/tmp', ui: { notify() {} } }
);
assert('dispatch accepts an object task and returns the child output', !!dispatchRes?.content?.[0]?.text?.includes('PASS'));
const dispatchQuiz = await msg('[[TURN:quiz]]\n' + dispatchBatch, 'stop');
assert('dispatch-minted quiz receipt binds the emitted batch', allowed(dispatchQuiz));

// The legacy `subagent` workflow/args forms are blocked toward `dispatch`.
const malformedSubagent = await fire('tool_call', {
  toolName: 'subagent',
  toolCallId: 'mw1',
  input: { workflow: 'true' },
});
assert('malformed subagent workflow is blocked toward dispatch', !!(malformedSubagent?.block && /dispatch/.test(malformedSubagent.reason || '')));

// ============================================================================
// 2026-10-08 P0.2: deterministic hard-fact completeness + tight tail binding.
// The generator must not pick its own exam; and a passed receipt may not carry
// an appended, never-verified tail.
// ============================================================================
const hardDraft = 'The explained variance is 4.98 on both arms (n=200).';

// A hard fact in the draft that no claim covers is withheld before emission.
await setPrompt('[[FLOW:resume]] continue the lesson');
const envMissingFact = JSON.stringify({
  gate: 'fact_check',
  claims: [{ id: 1, claim: 'both arms agree' }],
  rendered_content: hardDraft,
  source_urls: ['https://e.com'],
});
await dispatch('fact-check', envMissingFact, 'hf1');
await fg('hf1', 'fact-check', envMissingFact, FC_PASS);
const unlistedFact = await msg(`[[TURN:claims]]\n${hardDraft}`, 'stop');
assert('draft with an unlisted hard fact is withheld', blocked(unlistedFact, 'CLAIMS_INCOMPLETE'));

// The same draft renders once every hard fact is placed before the verifier.
await setPrompt('[[FLOW:resume]] continue the lesson');
const envListedFact = JSON.stringify({
  gate: 'fact_check',
  claims: [
    { id: 1, claim: 'the explained variance is 4.98' },
    { id: 2, claim: 'the sample size is n=200' },
  ],
  rendered_content: hardDraft,
  source_urls: ['https://e.com'],
});
await dispatch('fact-check', envListedFact, 'hf2');
await fg('hf2', 'fact-check', envListedFact, FC_PASS);
const listedFact = await msg(`[[TURN:claims]]\n${hardDraft}`, 'stop');
assert('hard fact listed in claims is allowed', allowed(listedFact));

// An unverified tail appended to a verified draft is withheld (no 1.4x slack).
await setPrompt('[[FLOW:resume]] continue the lesson');
const tailDraft = 'Entropy is the average surprise of a distribution.';
const envTail = JSON.stringify({
  gate: 'fact_check',
  claims: [{ id: 1, claim: 'entropy is the average surprise of a distribution' }],
  rendered_content: tailDraft,
  source_urls: ['https://e.com'],
});
await dispatch('fact-check', envTail, 'tb1');
await fg('tb1', 'fact-check', envTail, FC_PASS);
const tailEmit =
  tailDraft +
  ' An extra conclusion appended after the fact-check receipt was minted and never verified by any verifier at all.';
const tailed = await msg(`[[TURN:claims]]\n${tailEmit}`, 'stop');
assert('unverified tail beyond the draft is withheld', blocked(tailed, 'FACT_CHECK_MISMATCH'));

// ============================================================================
// 2026-10-08 P0.3: the always-on receipt ledger records claim-level verdicts
// (and a draft fingerprint), so a recorded PASS is auditable, not a tally.
// ============================================================================
try {
  const ledgerText = await Deno.readTextFile('/tmp/learning-gate-test/receipts.ndjson');
  const entries = ledgerText.trim().split('\n').map((l) => JSON.parse(l));
  const auditable = entries.find(
    (e) => e.gate === 'fact_check' && Array.isArray(e.claims) && e.claims.length > 0 && typeof e.envelopeHash === 'string'
  );
  assert('ledger records claim-level verdicts with a draft hash', !!auditable);
} catch {
  assert('ledger records claim-level verdicts with a draft hash', false);
}

// ============================================================================
// 2026-10-08 P0.5: the AI-free solo flow. Teaching and aids are withheld; the
// closed-book quiz batch is allowed; the first content turn needs review-scout.
// ============================================================================
const SOLO_QUIZ_PASS = JSON.stringify({ verdict: 'PASS', issues: [] });
const SOLO_SCOUT_OK =
  'REVIEW_SCOUT_DIGEST: {"track":"aiefs","digest":"Learning System/.tmp/review-x.json","queue":[],"failed_refs":[]}';

// A teaching claims turn in solo is withheld.
await setPrompt('[[FLOW:solo]] solo check');
await dispatch('fact-check', fcEnvelope(DRAFT), 'so1');
await fg('so1', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const soloTeach = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('solo flow withholds a teaching claims turn', blocked(soloTeach, 'SOLO_NO_TEACHING'));

// A visualization in solo is withheld.
await setPrompt('[[FLOW:solo]] solo check');
const soloFence = '```viz\n{"viz":"1","kind":"bar","bars":[]}\n```';
const soloViz = await msg(`[[TURN:viz]]\nA figure.\n${soloFence}`, 'stop');
assert('solo flow withholds a visualization', blocked(soloViz, 'SOLO_NO_AIDS'));

// The first solo quiz turn requires a review-scout run (deterministic queue).
const soloQEnv = JSON.stringify({
  gate: 'quiz_audit',
  purpose: 'probe',
  questions_json: [{ id: 1, question: 'Define entropy.' }],
});
await setPrompt('[[FLOW:solo]] solo check');
await dispatch('quiz-audit', soloQEnv, 'soq0');
await fg('soq0', 'quiz-audit', soloQEnv, SOLO_QUIZ_PASS);
const soloNoScout = await msg('[[TURN:quiz]]\nDefine entropy.', 'stop');
assert('solo first quiz requires a review-scout run', blocked(soloNoScout, 'NO_REVIEW_CONTEXT'));

// With a review-scout run, the closed-book quiz batch renders.
await setPrompt('[[FLOW:solo]] solo check');
await dispatch('review-scout', 'build the solo queue', 'sosc1');
await fg('sosc1', 'review-scout', 'build the solo queue', SOLO_SCOUT_OK);
await dispatch('quiz-audit', soloQEnv, 'soq1');
await fg('soq1', 'quiz-audit', soloQEnv, SOLO_QUIZ_PASS);
const soloQuiz = await msg('[[TURN:quiz]]\nDefine entropy.', 'stop');
assert('solo flow allows the closed-book quiz batch', allowed(soloQuiz));

// ============================================================================
// 2026-10-08 P1.6: at the retry cap, a claims turn stating hard facts is
// withheld outright (banner only, no content) rather than shown as UNVERIFIED.
// Non-hard-fact prose still degrades gracefully. G-retry-cap is unchanged.
// ============================================================================
const hardCapDraft = 'The explained variance is 4.98 on both arms (n=200).';
await setPrompt('[[FLOW:resume]] continue the lesson');
const hc1 = await msg(`[[TURN:claims]]\n${hardCapDraft}`, 'stop');
const hc2 = await msg(`[[TURN:claims]]\n${hardCapDraft}`, 'stop');
const hc3 = await msg(`[[TURN:claims]]\n${hardCapDraft}`, 'stop');
assert('repeated withheld turns are blocked before the cap', blocked(hc1, 'NO_FACT_CHECK_MATCH') && blocked(hc2, 'NO_FACT_CHECK_MATCH'));
assert(
  'retry cap withholds a hard-fact claims turn',
  blocked(hc3, 'WITHHELD') && !outText(hc3).includes('4.98') && !outText(hc3).includes('explained variance')
);

const proseCapDraft = 'The idea is that variation is the gap between joint and shared information.';
await setPrompt('[[FLOW:resume]] continue the lesson');
const pc1 = await msg(`[[TURN:claims]]\n${proseCapDraft}`, 'stop');
const pc2 = await msg(`[[TURN:claims]]\n${proseCapDraft}`, 'stop');
const pc3 = await msg(`[[TURN:claims]]\n${proseCapDraft}`, 'stop');
assert(
  'retry cap still delivers non-hard-fact prose',
  outText(pc3).includes('⛔ UNVERIFIED') && outText(pc3).includes('variation is the gap')
);

// ============================================================================
// 2026-10-08 P2.2: the out-of-scope demotion is restricted to findings that
// CITE a bookkeeping path. A content finding that merely mentions a bookkeeping
// word in its issue text must NOT be demoted (the old issue-text fallback and
// the blanket low-severity bypass are removed).
// ============================================================================
assert(
  'out-of-scope review issues with a bookkeeping location render as flags',
  P.reviewIssuesAllOutOfScope(
    JSON.stringify({
      verdict: 'ISSUES',
      issues: [{ severity: 'high', location: 'Learning System/Core/Attempts.json', issue: 'stale schedule' }],
    })
  )
);
assert(
  'content review findings are not demoted by a bookkeeping word',
  !P.reviewIssuesAllOutOfScope(
    JSON.stringify({
      verdict: 'ISSUES',
      issues: [{ severity: 'high', location: 'Knowledge Wiki/wiki/X.md', issue: 'the schedule in attempts.json is stale' }],
    })
  ) && !P.reviewIssuesAllOutOfScope(JSON.stringify({ verdict: 'ISSUES', issues: [{ severity: 'medium', issue: 'index.md is wrong' }] }))
);


