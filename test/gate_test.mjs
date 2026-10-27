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
  JSON.stringify({ gate: 'fact_check', turn_kind: 'answer', claims: [{ id: 1, claim: 'x' }], rendered_content: draft, source_urls: ['https://e.com'] });
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
  gate: 'fact_check', turn_kind: 'answer',
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
const SCOUT_AUDIT_ENV = JSON.stringify({ gate: 'scout_audit', slug: 'x', digest: 'Learning System/.tmp/context-x.json', raw_files: [], failed_refs: [] });
const SCOUT_AUDIT_PASS = JSON.stringify({ verdict: 'PASS', evidence: ['read Learning System/.tmp/context-x.json + raw sources'], issues: [], context_notes: [] });
await setPrompt('[[FLOW:teach]] teach me X');
await dispatch('scout', 'topic X', 'sc1');
await notify('Background task completed: **scout**\n\nSCOUT DIGEST: no machine line here');
await dispatch('scout-audit', SCOUT_AUDIT_ENV, 'sa1');
await fg('sa1', 'scout-audit', SCOUT_AUDIT_ENV, SCOUT_AUDIT_PASS);
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc1');
await fg('fc1', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const scoutUnverified = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('scout-unverified banner surfaced', allowed(scoutUnverified) && outText(scoutUnverified).includes('SCOUT DIGEST UNVERIFIED'));

// --- A1: a Scout with failed_refs surfaces the incomplete-sources banner ---
await setPrompt('[[FLOW:teach]] teach me Y');
await dispatch('scout', 'topic Y', 'sc2');
await notify('Background task completed: **scout**\n\nSCOUT_DIGEST: {"slug":"y","digest":"Learning System/.tmp/context-x.json","raw_files":[],"failed_refs":[{"url":"u","reason":"404"}]}');
await dispatch('scout-audit', SCOUT_AUDIT_ENV, 'sa2');
await fg('sa2', 'scout-audit', SCOUT_AUDIT_ENV, SCOUT_AUDIT_PASS);
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc2');
await fg('fc2', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const scoutIncomplete = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('sources-incomplete banner surfaced', allowed(scoutIncomplete) && outText(scoutIncomplete).includes('SOURCES INCOMPLETE'));

// --- Lesson-start context audit (copies the ingest review-gate): completeness + fact-check ---
// Missing audit withholds the first teaching turn.
await setPrompt('[[FLOW:teach]] teach me Z');
await dispatch('scout', 'topic Z', 'sc3');
await notify('Background task completed: **scout**\n\nSCOUT_DIGEST: {"slug":"z","digest":"Learning System/.tmp/context-z.json","raw_files":["Knowledge Wiki/raw/sources/z.md"],"failed_refs":[]}');
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc3');
await fg('fc3', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const noScoutAudit = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('teaching without a scout-audit is withheld', blocked(noScoutAudit, 'NO_SCOUT_AUDIT_PASS'));

// A valid audit releases the first teaching turn.
await setPrompt('[[FLOW:teach]] teach me W');
await dispatch('scout', 'topic W', 'sc4');
await notify('Background task completed: **scout**\n\nSCOUT_DIGEST: {"slug":"w","digest":"Learning System/.tmp/context-w.json","raw_files":["Knowledge Wiki/raw/sources/w.md"],"failed_refs":[]}');
const SCOUT_AUDIT_ENV_W = JSON.stringify({ gate: 'scout_audit', slug: 'w', digest: 'Learning System/.tmp/context-w.json', raw_files: ['Knowledge Wiki/raw/sources/w.md'], failed_refs: [] });
await dispatch('scout-audit', SCOUT_AUDIT_ENV_W, 'sa4');
await fg('sa4', 'scout-audit', SCOUT_AUDIT_ENV_W, SCOUT_AUDIT_PASS);
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc4');
await fg('fc4', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const scoutAudited = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('scout-audit pass releases the first teaching turn', allowed(scoutAudited));

// An ISSUES audit surfaces flags but never withholds (mirrors ingest REVIEW FLAGS SURFACED).
await setPrompt('[[FLOW:teach]] teach me V');
await dispatch('scout', 'topic V', 'sc5');
await notify('Background task completed: **scout**\n\nSCOUT_DIGEST: {"slug":"v","digest":"Learning System/.tmp/context-v.json","raw_files":[],"failed_refs":[]}');
const SCOUT_AUDIT_ENV_V = JSON.stringify({ gate: 'scout_audit', slug: 'v', digest: 'Learning System/.tmp/context-v.json', raw_files: [], failed_refs: [] });
await dispatch('scout-audit', SCOUT_AUDIT_ENV_V, 'sa5');
await fg('sa5', 'scout-audit', SCOUT_AUDIT_ENV_V, JSON.stringify({ verdict: 'ISSUES', evidence: ['read digest'], issues: [{ severity: 'high', location: 'Learning System/.tmp/context-v.json:synthesis[0].theory', issue: 'missing theory line' }], context_notes: [] }));
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc5');
await fg('fc5', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const scoutAuditIssues = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('scout-audit ISSUES surfaces flags without withholding', allowed(scoutAuditIssues) && outText(scoutAuditIssues).includes('SCOUT AUDIT FLAGS'));

// A wrong-shape audit naming no digest releases nothing.
await setPrompt('[[FLOW:teach]] teach me U');
await dispatch('scout', 'topic U', 'sc6');
await notify('Background task completed: **scout**\n\nSCOUT_DIGEST: {"slug":"u","digest":"Learning System/.tmp/context-u.json","raw_files":[],"failed_refs":[]}');
const SCOUT_AUDIT_NODIGEST = JSON.stringify({ gate: 'scout_audit', slug: 'u' });
await dispatch('scout-audit', SCOUT_AUDIT_NODIGEST, 'sa6');
await fg('sa6', 'scout-audit', SCOUT_AUDIT_NODIGEST, SCOUT_AUDIT_PASS);
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc6');
await fg('fc6', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const noDigestAudit = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('scout-audit without digest does not release the teaching turn', blocked(noDigestAudit, 'NO_SCOUT_AUDIT_PASS'));

// `raw_files` alone, without the `digest` under audit, also releases nothing.
await setPrompt('[[FLOW:teach]] teach me U2');
await dispatch('scout', 'topic U2', 'sc6b');
await notify('Background task completed: **scout**\n\nSCOUT_DIGEST: {"slug":"u2","digest":"Learning System/.tmp/context-u2.json","raw_files":[],"failed_refs":[]}');
const SCOUT_AUDIT_RAWONLY = JSON.stringify({ gate: 'scout_audit', slug: 'u2', raw_files: ['Knowledge Wiki/raw/sources/u2.md'] });
await dispatch('scout-audit', SCOUT_AUDIT_RAWONLY, 'sa6b');
await fg('sa6b', 'scout-audit', SCOUT_AUDIT_RAWONLY, SCOUT_AUDIT_PASS);
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc6b');
await fg('fc6b', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const rawOnlyAudit = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('scout-audit raw_files without digest does not release the teaching turn', blocked(rawOnlyAudit, 'NO_SCOUT_AUDIT_PASS'));

// An audit PASS with no evidence list is unsubstantiated (flagged, not withheld).
await setPrompt('[[FLOW:teach]] teach me T');
await dispatch('scout', 'topic T', 'sc7');
await notify('Background task completed: **scout**\n\nSCOUT_DIGEST: {"slug":"t","digest":"Learning System/.tmp/context-t.json","raw_files":[],"failed_refs":[]}');
const SCOUT_AUDIT_ENV_T = JSON.stringify({ gate: 'scout_audit', slug: 't', digest: 'Learning System/.tmp/context-t.json', raw_files: [], failed_refs: [] });
await dispatch('scout-audit', SCOUT_AUDIT_ENV_T, 'sa7');
await fg('sa7', 'scout-audit', SCOUT_AUDIT_ENV_T, JSON.stringify({ verdict: 'PASS', issues: [], context_notes: [] }));
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc7');
await fg('fc7', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const scoutAuditNoEvidence = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('scout-audit missing-evidence banner surfaced', allowed(scoutAuditNoEvidence) && outText(scoutAuditNoEvidence).includes('SCOUT AUDIT'));

// A flagged (ISSUES) audit is flow-level and non-blocking: it must not pin the
// retry-cap escape for an unrelated later withhold.
await setPrompt('[[FLOW:teach]] teach me Q');
await dispatch('scout', 'topic Q', 'sc8');
await notify('Background task completed: **scout**\n\nSCOUT_DIGEST: {"slug":"q","digest":"Learning System/.tmp/context-q.json","raw_files":[],"failed_refs":[]}');
const SCOUT_AUDIT_ENV_Q = JSON.stringify({ gate: 'scout_audit', slug: 'q', digest: 'Learning System/.tmp/context-q.json', raw_files: [], failed_refs: [] });
await dispatch('scout-audit', SCOUT_AUDIT_ENV_Q, 'sa8');
await fg('sa8', 'scout-audit', SCOUT_AUDIT_ENV_Q, JSON.stringify({ verdict: 'ISSUES', evidence: ['read digest'], issues: [{ severity: 'low', location: 'Learning System/.tmp/context-q.json:prereqs', issue: 'thin keywords' }], context_notes: [] }));
await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
const flaggedCap = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('flagged scout-audit does not pin the retry cap', outText(flaggedCap).includes('⛔ UNVERIFIED'));

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

// --- graph targets on items are additive record-keeping, never binding text ---
// `targets[]` (knowledge-graph node/chain ids) travels with a quiz question and
// its grade item. It must not change what the receipt binds, and it must not be
// mistaken for learner-facing content.
const uuidTargets = '5f607182-9304-4125-de67-890123456f0b';
const targetedEnvelope = JSON.stringify({
  gate: 'grade_audit',
  items: [
    {
      id: 1,
      concept: 'Bayes theorem',
      question: 'Q1 update the posterior',
      learner_answer: 'multiply prior by likelihood',
      claimed_verdict: 'pass',
      targets: ['n_ab12cd34ef', 'arg_ab12cd34ef'],
    },
    {
      id: 2,
      concept: 'KL divergence',
      question: 'Q2 name the floor',
      learner_answer: 'zero when equal',
      claimed_verdict: 'pass',
      targets: ['n_0123456789'],
    },
  ],
});
const targetedText =
  '[[TURN:grade]]\nQ1 update the posterior — PASS; Q2 name the floor — PASS.';
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('a11', 'grade-audit', targetedEnvelope);
await asyncResult('a11', uuidTargets);
gradeNotify(
  uuidTargets,
  JSON.stringify({
    verdict: 'PASS',
    agrees: true,
    correct_verdict: 'pass',
    issues: [],
    items: [
      { id: 1, agrees: true, correct_verdict: 'pass', explanation: 'ok' },
      { id: 2, agrees: true, correct_verdict: 'pass', explanation: 'ok' },
    ],
  })
);
const targetedGrade = await msg(targetedText, 'stop');
assert('grade targets do not change batch binding', allowed(targetedGrade));

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

// Graph targets and per-question concepts are record-keeping: they must not
// break the full-batch binding (nor leak into the bound learner-facing text).
await setPrompt('[[FLOW:resume]] continue the lesson');
const targetedBatch = 'Review — 1 due item.\n1. Which update rule follows from the posterior? ';
const targetedQuizEnv = JSON.stringify({
  gate: 'quiz_audit',
  context: 'review',
  rendered_content: targetedBatch,
  questions_json: [
    {
      id: 'q1',
      type: 'qualitative',
      concept: 'Bayes theorem',
      question: 'Which update rule follows from the posterior?',
      targets: ['n_ab12cd34ef', 'arg_ab12cd34ef'],
    },
  ],
});
await dispatch('quiz-audit', targetedQuizEnv, 'sq6');
await fg('sq6', 'quiz-audit', targetedQuizEnv, JSON.stringify({ verdict: 'PASS', issues: [] }));
const targetedQuiz = await msg('[[TURN:quiz]]\n' + targetedBatch, 'stop');
assert('quiz targets do not break full-batch binding', allowed(targetedQuiz));

// Any severity blocks: a low-severity quiz issue is an ISSUES verdict, not an
// accepted caveat. (Lows used to pass as PASS_WITH_FLAGS, silently.)
await setPrompt('[[FLOW:resume]] continue the lesson');
const lowQuizEnv = JSON.stringify({ gate: 'quiz_audit', purpose: 'probe', questions_json: [{ id: 1, question: 'What is entropy?' }] });
await dispatch('quiz-audit', lowQuizEnv, 'sq4');
await fg('sq4', 'quiz-audit', lowQuizEnv, JSON.stringify({ verdict: 'ISSUES', issues: [{ id: 'q1', severity: 'low', problem: 'wording nit' }] }));
const lowQuizTurn = await msg('[[TURN:quiz]]\nWhat is entropy?', 'stop');
assert('low-severity issue blocks a quiz turn', blocked(lowQuizTurn, 'QUIZ_AUDIT_ISSUES'));

// A `PASS_WITH_FLAGS` that still lists residual low issues is NOT a pass: any
// non-empty `issues[]` is an ISSUES verdict regardless of the verdict word.
await setPrompt('[[FLOW:resume]] continue the lesson');
const flagQuizEnv = JSON.stringify({ gate: 'quiz_audit', purpose: 'probe', questions_json: [{ id: 1, question: 'What is KL divergence?' }] });
await dispatch('quiz-audit', flagQuizEnv, 'sq5');
await fg('sq5', 'quiz-audit', flagQuizEnv, JSON.stringify({ verdict: 'PASS_WITH_FLAGS', issues: [{ id: 'q1', severity: 'low', problem: 'wording nit' }] }));
const flagQuizTurn = await msg('[[TURN:quiz]]\nWhat is KL divergence?', 'stop');
assert('PASS_WITH_FLAGS residual low issue blocks a quiz turn', blocked(flagQuizTurn, 'QUIZ_AUDIT_ISSUES'));

// An envelope-less async notification still mints an unbound receipt that binds
// (its dispatch could not be correlated, so there is nothing to bind against).
await setPrompt('[[FLOW:resume]] continue the lesson');
await notify('Background task completed: **quiz-audit**\n\nquiz-audit:\n[[TURN:none]]\n{"verdict":"PASS","issues":[]}\n\nRetention-managed async directory: /tmp/x/legacy-notify');
const legacyQuiz = await msg('[[TURN:quiz]]\nWhat is the entropy of a fair coin?', 'stop');
assert('envelope-less async quiz receipt still binds its turn', allowed(legacyQuiz));

// --- 2026-10-12: the script-drift guard (legacy path) ---
// A model that drifts into another script (a fluent Chinese translation of an
// English quiz, later explained as a "rendering glitch") must be withheld, not
// shown. The guard is deterministic and runs before the binding check, so it
// fires even when a verified English receipt exists.
await setPrompt('[[FLOW:resume]] continue the lesson');
const driftEnv = JSON.stringify({
  gate: 'quiz_audit',
  rendered_content:
    'Pause exit ticket. Which kernel does t-SNE use on which side of the comparison, and why? A) Student-t data B) Gaussian data',
  questions_json: [
    {
      id: 'X1',
      type: 'mcq',
      question: 'Which kernel does t-SNE use on which side of the comparison, and why?',
      options: ['A) Student-t data', 'B) Gaussian data'],
    },
  ],
});
await dispatch('quiz-audit', driftEnv, 'ld1');
await fg('ld1', 'quiz-audit', driftEnv, JSON.stringify({ verdict: 'PASS', issues: [] }));
const driftedQuiz = await msg(
  '[[TURN:quiz]]\n暂停退出凭证 — 仅限今天的三个后续问题。请回答选项字母，并针对每个问题标注置信度。在对比中，t-SNE 在哪一侧使用哪种内核，为什么？',
  'stop'
);
assert('legacy path withholds a Chinese emission of an English quiz', blocked(driftedQuiz, 'LANGUAGE_MISMATCH'));
const cleanQuiz = await msg('[[TURN:quiz]]\nPause exit ticket. Which kernel does t-SNE use on which side of the comparison, and why?', 'stop');
assert('legacy path renders the English re-emit after drift', allowed(cleanQuiz));

// Primitive unit checks for the guard.
assert(
  'scriptDrift flags Chinese text with only English references',
  P.scriptDrift('暂停退出凭证 仅限今天的三个后续问题 请回答选项字母 并针对每个问题标注置信度', ['Which kernel does t-SNE use?'])
);
assert('scriptDrift allows a CJK learner writing CJK', !P.scriptDrift('暂停退出凭证 仅限今天的三个后续问题 请回答选项字母', ['请解释内核']));
assert('scriptDrift ignores ordinary English', !P.scriptDrift('Which kernel does t-SNE use on which side?', ['x']));
assert('scriptDrift ignores a few CJK chars in English prose', !P.scriptDrift('The 内 kernel is Gaussian.', ['English draft']));
assert('looksLikeGateEnvelope detects a GATE envelope', P.looksLikeGateEnvelope('GATE:fact_check\n{"gate":"fact_check"}'));
assert('looksLikeGateEnvelope ignores learner prose', !P.looksLikeGateEnvelope('please explain the t-SNE kernel'));

// A CJK learner keeps getting CJK: their own message exempts the guard.
await setPrompt('[[FLOW:resume]] continue the lesson');
await setPrompt('请用中文解释一下 t-SNE 的内核');
const cjkNone = await msg('[[TURN:none]]\n我们继续学习 t-SNE 的内核，请用中文回答这个问题。', 'stop');
assert('a CJK learner keeps getting CJK', allowed(cjkNone));

// A fresh English learner emitting the same CJK transition is withheld, and
// repeated drift never dumps foreign-script content at the retry cap.
await setPrompt('[[FLOW:resume]] continue the lesson');
for (let i = 0; i < 3; i++) {
  const driftNone = await msg('[[TURN:none]]\n我们继续学习 t-SNE 的内核，请用中文回答这个问题。', 'stop');
  assert(`drift never dumps at the retry cap (attempt ${i + 1})`, blocked(driftNone, 'LANGUAGE_MISMATCH'));
}

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

// review-session-audit ISSUES blocks the close summary until a fresh PASS.
await setPrompt('[[FLOW:review]] review my due concepts');
await bashCall("python3 scripts/ops.py apply <<'SPEC'\nLearning System/Sessions/Session — Review — 2026-09-27.md\nSPEC", 'rw2');
const rsEnv = JSON.stringify({ gate: 'review_session', concepts: ['X'], written_files: [{ path: 'Learning System/Sessions/Session — Review — 2026-09-27.md' }] });
await dispatch('review-session-audit', rsEnv, 'rsa2');
await fg('rsa2', 'review-session-audit', rsEnv, JSON.stringify({ verdict: 'ISSUES', evidence: ['read'], issues: [{ severity: 'low', issue: 'session note date wrong', location: 'Learning System/Sessions/Session — Review — 2026-09-27.md' }] }));
const rsIssues = await msg('Review — mastery 4/5, next review 2026-10-01. Recap below.', 'stop');
assert('review-session audit ISSUES blocks the close summary', blocked(rsIssues, 'REVIEW_SESSION_AUDIT_ISSUES'));
await dispatch('review-session-audit', rsEnv, 'rsa3');
await fg('rsa3', 'review-session-audit', rsEnv, JSON.stringify({ verdict: 'PASS', evidence: ['read'], issues: [] }));
const rsPass = await msg('Review — mastery 4/5, next review 2026-10-01. Recap below.', 'stop');
assert('review-session audit PASS releases the close summary after ISSUES', allowed(rsPass));

// review-clerk fix re-dispatch is exempt from its cap while a flagged
// review-session audit is pending (the close is not done).
await setPrompt('[[FLOW:review]] review my due concepts');
await bashCall("python3 scripts/ops.py apply <<'SPEC'\nLearning System/Sessions/Session — Review — 2026-09-28.md\nSPEC", 'rw3');
const rcEnv = JSON.stringify({ gate: 'review_session', concepts: ['X'], written_files: [{ path: 'Learning System/Sessions/Session — Review — 2026-09-28.md' }] });
await dispatch('review-session-audit', rcEnv, 'rsa4');
await fg('rsa4', 'review-session-audit', rcEnv, JSON.stringify({ verdict: 'ISSUES', evidence: ['read'], issues: [{ severity: 'low', issue: 'date wrong', location: 'Learning System/Sessions/Session — Review — 2026-09-28.md' }] }));
let rcBlocked = false;
for (let i = 1; i <= 4; i++) {
  const r = await fire('tool_call', { toolName: 'subagent', toolCallId: `rccap${i}`, input: { agent: 'review-clerk', task: JSON.stringify({ gate: 'review_clerk', concepts: ['X'] }) } });
  if (r && r.block) rcBlocked = true;
}
assert('review-clerk re-dispatch uncapped while a review-session audit is flagged', !rcBlocked);

// review-gate without `target_files` reviewed nothing.
await setPrompt('[[FLOW:ingest]] ingest this');
await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), 'ic1');
await notify('Background task completed: **clerk**\n\n[[TURN:none]]\nCLERK_WRITES: {"wiki":["Knowledge Wiki/wiki/X.md"],"state":[],"concepts":["X"],"commit":"abc"}');
await dispatch('review-gate', JSON.stringify({ gate: 'review', concepts: ['X'] }), 'irg1');
await fg('irg1', 'review-gate', JSON.stringify({ gate: 'review', concepts: ['X'] }), JSON.stringify({ verdict: 'PASS', evidence: ['x'], issues: [], context_notes: [] }));
const noTargetsRG = await msg('[[TURN:none]]\nIngest complete. STATE_AUDIT_VERDICT: {"errors":0,"warnings":0}', 'stop');
assert('review-gate without target_files does not release the ingest summary', blocked(noTargetsRG, 'NO_REVIEW_GATE_PASS'));

// --- Graph fact-check gate: a Clerk graph write owes an independent graph-audit ---
const GRAPH_WRITES = '[[TURN:none]]\nCLERK_WRITES: {"wiki":["Knowledge Wiki/wiki/X.md"],"state":[],"concepts":["X"],"graph":{"created_nodes":["n_aaaaaaaaaa"],"linked_nodes":["n_bbbbbbbbbb"],"created_chains":["arg_cccccccccc"],"linked_chains":[],"status":"ok"},"commit":"abc"}';
const GRAPH_IDS = ['n_aaaaaaaaaa', 'n_bbbbbbbbbb', 'arg_cccccccccc'];
const graphEnv = (ids) => JSON.stringify({
  gate: 'graph_audit',
  session: 's',
  written_nodes: ids.filter((i) => i.startsWith('n_')),
  written_chains: ids.filter((i) => i.startsWith('arg_')),
  material: [{ file: 'Learning System/Lessons/L.md', kind: 'lesson' }],
  lesson_ref: 'Learning System/Lessons/L.md',
});
const GRAPH_PASS = JSON.stringify({ verdict: 'PASS', evidence: ['read nodes.jsonl:12'], issues: [], context_notes: [] });
const INGEST_SUMMARY = '[[TURN:none]]\nIngest complete. STATE_AUDIT_VERDICT: {"errors":0,"warnings":0}';
const ingestWithGraph = async (id) => {
  await setPrompt('[[FLOW:ingest]] ingest this');
  await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), `g${id}c`);
  await notify(`Background task completed: **clerk**\n\n${GRAPH_WRITES}`);
  const rg = JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'Knowledge Wiki/wiki/X.md' }] });
  await dispatch('review-gate', rg, `g${id}rg`);
  await fg(`g${id}rg`, 'review-gate', rg, REVIEW_PASS);
};

await ingestWithGraph('1');
const noGraphAudit = await msg(INGEST_SUMMARY, 'stop');
assert('graph write without graph-audit withholds the ingest summary', blocked(noGraphAudit, 'NO_GRAPH_AUDIT_PASS'));

// The fix exemption must not disable the normal cap: with no flagged audit, the
// third Clerk dispatch is still blocked.
let clerkCapBlocked = false;
for (let i = 1; i <= 3; i++) {
  const r = await fire('tool_call', {
    toolName: 'subagent',
    toolCallId: `cap${i}`,
    input: { agent: 'clerk', task: JSON.stringify({ gate: 'clerk' }) },
  });
  if (r && r.block) clerkCapBlocked = true;
}
assert('clerk ingest cap still blocks without a flagged graph audit', clerkCapBlocked);

await ingestWithGraph('2');
const gEnv = graphEnv(GRAPH_IDS);
await dispatch('graph-audit', gEnv, 'g2ga');
await fg('g2ga', 'graph-audit', gEnv, GRAPH_PASS);
const graphAudited = await msg(INGEST_SUMMARY, 'stop');
assert('graph-audit PASS over the written ids releases the ingest summary', allowed(graphAudited));

await ingestWithGraph('3');
const gEnv3 = graphEnv(GRAPH_IDS);
await dispatch('graph-audit', gEnv3, 'g3ga');
await fg('g3ga', 'graph-audit', gEnv3, JSON.stringify({
  verdict: 'ISSUES',
  evidence: ['read chains.jsonl:4'],
  issues: [{ severity: 'high', code: 'NO_ENTAILMENT', location: 'arg_cccccccccc', issue: 'premises do not entail the conclusion' }],
  context_notes: [],
}));
const graphIssues = await msg(INGEST_SUMMARY, 'stop');
assert('graph-audit ISSUES withholds the ingest summary until fixed', blocked(graphIssues, 'GRAPH_AUDIT_ISSUES'));

// A flagged graph audit keeps the ingest open: a Clerk fix re-dispatch beyond
// the normal per-flow cap must be allowed (no cycle cap).
let graphFixBlocked = false;
for (let i = 1; i <= 3; i++) {
  const r = await fire('tool_call', {
    toolName: 'subagent',
    toolCallId: `gfix${i}`,
    input: { agent: 'clerk', task: JSON.stringify({ gate: 'clerk' }) },
  });
  if (r && r.block) graphFixBlocked = true;
}
assert('clerk fix re-dispatch is uncapped while a graph audit is flagged', !graphFixBlocked);

await ingestWithGraph('4');
const gEnv4 = graphEnv(['n_aaaaaaaaaa']);
await dispatch('graph-audit', gEnv4, 'g4ga');
await fg('g4ga', 'graph-audit', gEnv4, GRAPH_PASS);
const partialGraphAudit = await msg(INGEST_SUMMARY, 'stop');
assert('graph-audit covering only some written ids does not release the summary', blocked(partialGraphAudit, 'NO_GRAPH_AUDIT_PASS'));

// Partial-coverage ISSUES must surface as ISSUES, not as a missing audit.
await ingestWithGraph('6');
const gEnv6 = graphEnv(['n_aaaaaaaaaa']);
await dispatch('graph-audit', gEnv6, 'g6ga');
await fg('g6ga', 'graph-audit', gEnv6, JSON.stringify({
  verdict: 'ISSUES',
  evidence: ['read nodes.jsonl:12'],
  issues: [{ severity: 'high', code: 'UNGROUNDED', location: 'n_aaaaaaaaaa', issue: 'not in the source' }],
  context_notes: [],
}));
const partialIssues = await msg(INGEST_SUMMARY, 'stop');
assert('partial graph-audit ISSUES reports the audit issue, not a missing audit', blocked(partialIssues, 'GRAPH_AUDIT_ISSUES'));

// Coverage may be split across passing audits (the re-audit fix cycle).
await ingestWithGraph('7');
const gEnv7a = graphEnv(['n_aaaaaaaaaa', 'n_bbbbbbbbbb']);
await dispatch('graph-audit', gEnv7a, 'g7ga');
await fg('g7ga', 'graph-audit', gEnv7a, GRAPH_PASS);
const gEnv7b = graphEnv(['arg_cccccccccc']);
await dispatch('graph-audit', gEnv7b, 'g7gb');
await fg('g7gb', 'graph-audit', gEnv7b, GRAPH_PASS);
const splitCoverage = await msg(INGEST_SUMMARY, 'stop');
assert('split passing audits covering every id release the summary', allowed(splitCoverage));

// A Clerk that copies the merge's record objects (not plain id strings) must
// still arm the gate.
await setPrompt('[[FLOW:ingest]] ingest this');
await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), 'g8c');
await notify('Background task completed: **clerk**\n\n[[TURN:none]]\nCLERK_WRITES: {"wiki":["Knowledge Wiki/wiki/X.md"],"state":[],"concepts":["X"],"graph":{"created_nodes":[{"id":"n_aaaaaaaaaa","name":"A"}],"linked_nodes":[],"created_chains":[],"linked_chains":[]},"commit":"abc"}');
const rg8 = JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'Knowledge Wiki/wiki/X.md' }] });
await dispatch('review-gate', rg8, 'g8rg');
await fg('g8rg', 'review-gate', rg8, REVIEW_PASS);
const objectGraphWrites = await msg(INGEST_SUMMARY, 'stop');
assert('graph record objects in CLERK_WRITES still arm the audit gate', blocked(objectGraphWrites, 'NO_GRAPH_AUDIT_PASS'));

// An intermediate released message must not disarm the armed id set.
await ingestWithGraph('9');
const intermediate = await msg('[[TURN:none]]\nThe Clerk returned; preparing the close summary.', 'stop');
assert('intermediate ingest status message renders', allowed(intermediate));
const stillGated = await msg(INGEST_SUMMARY, 'stop');
assert('intermediate message does not disarm the graph audit gate', blocked(stillGated, 'NO_GRAPH_AUDIT_PASS'));

const parsedObjectIds = P.graphIdsOf({ written_nodes: [{ id: 'n_aaaaaaaaaa' }], written_chains: ['arg_cccccccccc'] });
assert('graph envelope ids accept record objects', !!parsedObjectIds && parsedObjectIds.length === 2);
const parsedClerkObjectIds = P.parseClerkGraph('CLERK_WRITES: {"graph":{"created_nodes":[{"id":"n_aaaaaaaaaa"}],"linked_nodes":[],"created_chains":[],"linked_chains":[]}}');
assert('clerk graph parser accepts record objects', !!parsedClerkObjectIds && parsedClerkObjectIds.includes('n_aaaaaaaaaa'));

await ingestWithGraph('5');
const gEnv5 = graphEnv(GRAPH_IDS);
await dispatch('graph-audit', gEnv5, 'g5ga');
await fg('g5ga', 'graph-audit', gEnv5, JSON.stringify({ verdict: 'PASS', issues: [], context_notes: [] }));
const graphNoEvidence = await msg(INGEST_SUMMARY, 'stop');
assert('graph-audit without evidence surfaces the unsubstantiated banner', allowed(graphNoEvidence) && outText(graphNoEvidence).includes('GRAPH AUDIT'));

// --- uncapped verifier re-check: review-gate / review-session-audit are not dispatch-capped ---
// The Tutor/Reviewer may keep fixing and re-checking a verifier until it returns
// zero issues (any severity). A 3rd/4th dispatch must not be blocked by an old
// per-flow cap of 2.
await setPrompt('[[FLOW:ingest]] ingest this');
let rgCapped = false;
for (let i = 1; i <= 4; i++) {
  const r = await fire('tool_call', {
    toolName: 'subagent',
    toolCallId: `rgcap${i}`,
    input: { agent: 'review-gate', task: JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: `p${i}.md` }] }) },
  });
  if (r && r.block) rgCapped = true;
}
assert('review-gate re-check is uncapped', !rgCapped);

await setPrompt('[[FLOW:review]] review my due concepts');
let rsaCapped = false;
for (let i = 1; i <= 4; i++) {
  const r = await fire('tool_call', {
    toolName: 'subagent',
    toolCallId: `rsacap${i}`,
    input: { agent: 'review-session-audit', task: JSON.stringify({ gate: 'review_session', concepts: ['X'], written_files: [{ path: 'Learning System/Sessions/s.md' }] }) },
  });
  if (r && r.block) rsaCapped = true;
}
assert('review-session-audit re-check is uncapped', !rsaCapped);

await setPrompt('[[FLOW:teach]] teach me X');
let saCapped = false;
for (let i = 1; i <= 4; i++) {
  const r = await fire('tool_call', {
    toolName: 'subagent',
    toolCallId: `sacap${i}`,
    input: { agent: 'scout-audit', task: JSON.stringify({ gate: 'scout_audit', slug: 'x', digest: `Learning System/.tmp/context-x${i}.json`, raw_files: [], failed_refs: [] }) },
  });
  if (r && r.block) saCapped = true;
}
assert('scout-audit re-check is uncapped', !saCapped);

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
  gate: 'fact_check', turn_kind: 'answer',
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
  gate: 'fact_check', turn_kind: 'answer',
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
  gate: 'fact_check', turn_kind: 'answer',
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

// A widget turn in solo is withheld (no interactive aids in a closed-book check).
await setPrompt('[[FLOW:solo]] solo check');
const soloUi = await msg('[[TURN:ui]]\nA widget.\n```openui\nroot = Card([])\n```', 'stop');
assert('solo flow withholds a ui widget', blocked(soloUi, 'SOLO_NO_AIDS'));

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



// ============================================================================
// 2026-10-08 REVIEW fixes: solo enforcement, hard-fact correctness, context
// degrade, and demotion path-anchoring.
// ============================================================================

// Exact containment: a longer number no longer subsumes a shorter hard fact.
assert(
  'hard fact is not subsumed by a longer number',
  P.missingHardFacts('The sample size is n=200.', 'the sample was n=2000 here').length === 1
);
assert(
  'comma-grouped thousands are not treated as a hard fact',
  !P.extractHardFacts('The corpus has 3,000 sentences.').includes('000')
);
assert(
  'four-digit years are not hard facts',
  !P.extractHardFacts('This was known in 1800 already.').includes('1800')
);

// Allow side of the tail bound: a reordered/punctuated re-emission renders.
await setPrompt('[[FLOW:resume]] continue the lesson');
const tailDraft2 = 'Entropy is the average surprise of a distribution.';
const envTail2 = JSON.stringify({
  gate: 'fact_check', turn_kind: 'answer',
  claims: [{ id: 1, claim: 'entropy is the average surprise of a distribution' }],
  rendered_content: tailDraft2,
  source_urls: ['https://e.com'],
});
await dispatch('fact-check', envTail2, 'tb2');
await fg('tb2', 'fact-check', envTail2, FC_PASS);
const reordered = await msg(`[[TURN:claims]]\nIn short, the average surprise of a distribution is entropy.`, 'stop');
assert('reordered verified draft still renders', allowed(reordered));

// Solo retry cap: teaching is withheld outright, never UNVERIFIED-with-content.
await setPrompt('[[FLOW:solo]] solo check');
const soloProse = 'Entropy is the average surprise of a distribution.';
await msg(`[[TURN:claims]]\n${soloProse}`, 'stop');
await msg(`[[TURN:claims]]\n${soloProse}`, 'stop');
const soloCap = await msg(`[[TURN:claims]]\n${soloProse}`, 'stop');
assert(
  'solo retry cap withholds teaching outright',
  blocked(soloCap, 'WITHHELD') && !outText(soloCap).includes('average surprise')
);

// A solo `none` transition carrying hard facts is teaching.
await setPrompt('[[FLOW:solo]] solo check');
const soloNoneTeach = await msg(`[[TURN:none]]\nThe explained variance is 4.98 (n=200).`, 'stop');
assert('solo none turn with hard facts is withheld', blocked(soloNoneTeach, 'SOLO_NO_TEACHING'));

// A solo `grade` turn carrying a fact-checked repair tail is teaching.
const soloRepairProse =
  'Close — a point value has probability zero, so that reading is wrong. Detector: a point has zero probability.';
const soloGradeEnv = JSON.stringify({
  gate: 'grade_audit',
  concept: 'X',
  question: 'What is P(X=1.7)?',
  learner_answer: '1.7',
  claimed_verdict: 'fail',
});
await setPrompt('[[FLOW:solo]] solo check');
await dispatch('grade-audit', soloGradeEnv, 'sg0');
await fg('sg0', 'grade-audit', soloGradeEnv, GATE);
const fcRepair = fcEnvelope(soloRepairProse);
await dispatch('fact-check', fcRepair, 'sgf');
await fg('sgf', 'fact-check', fcRepair, FC_PASS);
const soloRepair = await msg(`[[TURN:grade]]\n${soloRepairProse}`, 'stop');
assert('solo grade repair tail is withheld', blocked(soloRepair, 'SOLO_NO_TEACHING'));

// M11: a verified hard-fact claims turn blocked only on review context degrades
// to UNVERIFIED (not withheld) — no verification receipt is missing.
const ctxDraft = 'The explained variance is 4.98 on both arms (n=200).';
const ctxEnv = JSON.stringify({
  gate: 'fact_check', turn_kind: 'answer',
  claims: [
    { id: 1, claim: 'the explained variance is 4.98' },
    { id: 2, claim: 'the sample size is n=200' },
  ],
  rendered_content: ctxDraft,
  source_urls: ['https://e.com'],
});
await setPrompt('[[FLOW:review]] review the due items');
await dispatch('fact-check', ctxEnv, 'cx1');
await fg('cx1', 'fact-check', ctxEnv, FC_PASS);
await msg(`[[TURN:claims]]\n${ctxDraft}`, 'stop');
await msg(`[[TURN:claims]]\n${ctxDraft}`, 'stop');
const ctxCap = await msg(`[[TURN:claims]]\n${ctxDraft}`, 'stop');
assert(
  'retry cap delivers verified hard-fact prose blocked only on context',
  outText(ctxCap).includes('⛔ UNVERIFIED') && outText(ctxCap).includes('4.98')
);

// Demotion is path-anchored: a content path embedding a bookkeeping keyword is
// NOT demoted, while a real bookkeeping path still is.
assert(
  'content path embedding a bookkeeping word is not demoted',
  !P.reviewIssuesAllOutOfScope(
    JSON.stringify({
      verdict: 'ISSUES',
      issues: [{ severity: 'high', location: 'Knowledge Wiki/wiki/Backprop.md provenance marker missing', issue: 'missing provenance' }],
    })
  )
);
assert(
  'a real bookkeeping path still demotes',
  P.reviewIssuesAllOutOfScope(
    JSON.stringify({
      verdict: 'ISSUES',
      issues: [{ severity: 'low', location: 'Learning System/Reviews/Quality Gates/x.md', issue: 'bookkeeping' }],
    })
  )
);

// ============================================================================
// 2026-10-09: the CLAIMS_INCOMPLETE dead-end. (a) Hard-fact matching is
// notation-insensitive: a LaTeX formula/parameter listed in the claims as plain
// prose is NOT a missing fact. (b) The remedy CLAIMS_INCOMPLETE mandates — a
// re-dispatch of the SAME draft with the missing claim added — must be allowed,
// and its corrected receipt must supersede the incomplete one.
// ============================================================================
const latexDraft =
  'Perplexity is $\\mathrm{Per}(P_i) = 2^{H(P_i)}$ and each point spreads by $\\sigma_i$; it can be 23.7.';
const latexClaimsProse = 'perplexity is Per(P_i) = 2^(H(P_i))\neach point spreads by sigma_i';
assert(
  'prose-notation claims cover LaTeX hard facts (only the unlisted number is missing)',
  JSON.stringify(P.missingHardFacts(latexDraft, latexClaimsProse)) === JSON.stringify(['23.7'])
);

// 2026-10-12: the t-SNE kernel loop. The draft rendered `$q_{ij} \propto
// 1/(1+d_{ij}^2)$` while the claims listed the same fact in prose
// ("q_ij proportional to 1/(1 + d_ij^2)"): a symbol macro (`\propto`) and
// operator spacing both differed, so an already-verified formula was withheld
// as CLAIMS_INCOMPLETE on every re-dispatch. Symbol macros must translate to
// their prose spelling and whitespace around operators is insignificant.
const proptoDraft = 'The map-side curve is $q_{ij} \\propto 1/(1+d_{ij}^2)$ (normalized over all pairs).';
const proptoClaims =
  'In the map, Q is defined from distances by q_ij proportional to 1/(1 + d_ij^2), normalized over all pairs.';
assert(
  'prose-notation claims cover a LaTeX symbol macro and operator spacing',
  P.missingHardFacts(proptoDraft, proptoClaims).length === 0
);
assert(
  'a mutated formula is still reported as a missing hard fact',
  P.missingHardFacts(proptoDraft, 'q_ij proportional to 1/(1 + d_ij^3), normalized over all pairs.')
    .length === 1
);
// A math span that normalises to the empty string (`\cdot`, `\ast`) carries no
// content and must not be reported — and must not wedge `factPresent`.
assert(
  'a content-free math span normalises to nothing and is not a missing fact',
  P.missingHardFacts('a $\\cdot$ b', 'claims here').length === 0
);

await setPrompt('[[FLOW:resume]] continue the lesson');
const envLatex1 = JSON.stringify({
  gate: 'fact_check', turn_kind: 'answer',
  claims: [
    { id: 1, claim: 'perplexity is Per(P_i) = 2^(H(P_i))' },
    { id: 2, claim: 'each point spreads by sigma_i' },
  ],
  rendered_content: latexDraft,
  source_urls: ['https://e.com'],
});
await dispatch('fact-check', envLatex1, 'lx1');
await fg('lx1', 'fact-check', envLatex1, FC_PASS);
const lateIncomplete = await msg(`[[TURN:claims]]\n${latexDraft}`, 'stop');
assert(
  'claims turn with an unlisted hard fact is withheld (CLOSURE)',
  blocked(lateIncomplete, 'CLAIMS_INCOMPLETE') && outText(lateIncomplete).includes('23.7')
);

const envLatex2 = JSON.stringify({
  gate: 'fact_check', turn_kind: 'answer',
  claims: [
    { id: 1, claim: 'perplexity is Per(P_i) = 2^(H(P_i))' },
    { id: 2, claim: 'each point spreads by sigma_i' },
    { id: 3, claim: 'a distribution perplexity can be 23.7' },
  ],
  rendered_content: latexDraft,
  source_urls: ['https://e.com'],
});
const lateRedispatch = await fire('tool_call', { toolName: 'subagent', toolCallId: 'lx2', input: { agent: 'fact-check', task: envLatex2 } });
assert('corrected fact-check re-dispatch for missing claims is allowed', !(lateRedispatch && lateRedispatch.block));
await fg('lx2', 'fact-check', envLatex2, FC_PASS);
const lateDup = await fire('tool_call', { toolName: 'subagent', toolCallId: 'lx3', input: { agent: 'fact-check', task: envLatex2 } });
assert('complete fact-check re-dispatch is still blocked', !!(lateDup && lateDup.block));
const lateCorrected = await msg(`[[TURN:claims]]\n${latexDraft}`, 'stop');
assert('corrected claims turn renders after the mandated re-dispatch', allowed(lateCorrected));

// ============================================================================
// Foundation beats (G-foundation-beats). The failure mode is *omission*: a
// fluent "what"-only summary is factually true and fully covered, so every
// existing gate passes it. These tests make the missing "why"/theoretical
// foundation deterministically visible: a teach/resume claims turn must declare
// a turn_kind, and an `idea` turn must ship all four beats bound into the draft.
// ============================================================================
const FOUND_DRAFT =
  'Entropy counts the average number of yes/no questions needed to identify a draw. ' +
  'It is the expected surprise, and it comes from the logarithm of the number of typical sequences nH. ' +
  'It assumes the distribution is fixed and the draws are independent. ' +
  'Unlike variance, which measures spread in the values, entropy measures spread in the probabilities.';
const FOUNDATION = {
  problem: 'Entropy counts the average number of yes/no questions needed to identify a draw.',
  where_from: 'It comes from the logarithm of the number of typical sequences nH.',
  conditions: 'It assumes the distribution is fixed and the draws are independent.',
  contrast: 'Unlike variance, which measures spread in the values, entropy measures spread in the probabilities.',
};
const ideaEnv = (draft, foundation, kind = 'idea') =>
  JSON.stringify({
    gate: 'fact_check',
    turn_kind: kind,
    foundation,
    claims: [{ id: 1, claim: 'entropy is the expected surprise of a distribution' }],
    rendered_content: draft,
    source_urls: ['https://e.com'],
  });
const runFoundationClaims = async (id, draft, envelope, verifierOutput = FC_PASS) => {
  await setPrompt('[[FLOW:resume]] continue the lesson');
  await dispatch('fact-check', envelope, id);
  await fg(id, 'fact-check', envelope, verifierOutput);
  return msg(`[[TURN:claims]]\n${draft}`, 'stop');
};

{
  const r = await runFoundationClaims('fb1', FOUND_DRAFT, ideaEnv(FOUND_DRAFT, FOUNDATION));
  assert('idea turn with a complete bound foundation renders', allowed(r));
}
{
  const noKind = JSON.stringify({ ...JSON.parse(ideaEnv(FOUND_DRAFT, FOUNDATION)), turn_kind: undefined });
  const r = await runFoundationClaims('fb2', FOUND_DRAFT, noKind);
  assert('teach/resume claims turn without turn_kind is withheld', blocked(r, 'FOUNDATION_INCOMPLETE'));
}
{
  const partial = { ...FOUNDATION };
  delete partial.conditions;
  const r = await runFoundationClaims('fb3', FOUND_DRAFT, ideaEnv(FOUND_DRAFT, partial));
  assert(
    'idea turn missing a foundation beat is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('conditions')
  );
}
{
  const unbound = { ...FOUNDATION, contrast: 'Entropy is the same thing as enthalpy.' };
  const r = await runFoundationClaims('fb4', FOUND_DRAFT, ideaEnv(FOUND_DRAFT, unbound));
  assert(
    'idea turn whose foundation beat is not in the draft is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('contrast')
  );
}
{
  const r = await runFoundationClaims('fb5', 'It is 2^H(P).', ideaEnv('It is 2^H(P).', undefined, 'answer'));
  assert('answer turn needs no foundation beat', allowed(r));
}
{
  await setPrompt('[[FLOW:resume]] continue the lesson');
  await dispatch('fact-check', ideaEnv(FOUND_DRAFT, undefined), 'fb6');
  await fg('fb6', 'fact-check', ideaEnv(FOUND_DRAFT, undefined), FC_PASS);
  const incomplete = await msg(`[[TURN:claims]]\n${FOUND_DRAFT}`, 'stop');
  assert('idea turn without a foundation block is withheld', blocked(incomplete, 'FOUNDATION_INCOMPLETE'));
  const fixed = await fire('tool_call', {
    toolName: 'subagent',
    toolCallId: 'fb7',
    input: { agent: 'fact-check', task: ideaEnv(FOUND_DRAFT, FOUNDATION) },
  });
  assert('corrected fact-check re-dispatch for a missing foundation is allowed', !(fixed && fixed.block));
  await fg('fb7', 'fact-check', ideaEnv(FOUND_DRAFT, FOUNDATION), FC_PASS);
  const reemit = await msg(`[[TURN:claims]]\n${FOUND_DRAFT}`, 'stop');
  assert('corrected foundation re-emit renders', allowed(reemit));
}
{
  const omitted = JSON.stringify({
    verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }],
    omitted_foundations: [{ theory: 'the derivation from typical sequences', source: 'rohit' }],
    contradictions: [],
  });
  const r = await runFoundationClaims('fb8', FOUND_DRAFT, ideaEnv(FOUND_DRAFT, FOUNDATION), omitted);
  assert('fact-check that names omitted foundations blocks the turn', blocked(r, 'FACT_CHECK_ISSUES'));
}

// --- at the retry cap a foundation-incomplete idea turn is withheld, not shown ---
{
  await setPrompt('[[FLOW:resume]] continue the lesson');
  const env = ideaEnv(FOUND_DRAFT, undefined);
  await dispatch('fact-check', env, 'fb9');
  await fg('fb9', 'fact-check', env, FC_PASS);
  let last;
  for (let i = 0; i < 3; i++) last = await msg(`[[TURN:claims]]\n${FOUND_DRAFT}`, 'stop');
  assert(
    'retry cap withholds a foundation-incomplete idea turn',
    outText(last).startsWith('⛔ WITHHELD') && outText(last).includes('FOUNDATION_INCOMPLETE')
  );
}

// ============================================================================
// Interrogation turn kinds (G-triage-shape / G-attack-shape /
// G-interrogation-turn-kinds). The Tutor now interrogates rather than lectures:
// triage and attack turns must carry their shape fields, while plan/autopsy/
// answer/repair/hint/grade_feedback need no foundation beat.
// ============================================================================
const TRIAGE_DRAFT =
  '| Claim | Bucket | Reason |\n|---|---|---|\n| "entropy captures the information" | suspect | no mechanism: which knob moves, which way? |\n| the log of typical sequences | missing | source paragraph 3 states it |';
const triageEnv = (triage) =>
  JSON.stringify({
    gate: 'fact_check',
    turn_kind: 'triage',
    triage,
    visual_plan: { kind: 'prose', why: 'a Markdown table carries the comparison' },
    claims: [{ id: 1, claim: 'the table buckets the learner claims' }],
    rendered_content: TRIAGE_DRAFT,
    source_urls: ['https://e.com'],
  });
{
  const r = await runFoundationClaims(
    'it1',
    TRIAGE_DRAFT,
    triageEnv([
      { item: 'entropy captures the information', bucket: 'suspect', evidence: 'learner: "entropy captures the information"' },
      { item: 'log of typical sequences', bucket: 'missing', evidence: 'source p.3: nH typical sequences' },
      { item: 'independent draws', bucket: 'solid' },
    ])
  );
  assert('triage turn with a grounded triage table renders', allowed(r));
}
{
  const r = await runFoundationClaims(
    'it2',
    TRIAGE_DRAFT,
    triageEnv([{ item: 'entropy captures the information', bucket: 'suspect', evidence: '' }])
  );
  assert(
    'triage turn with an ungrounded suspect row is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('triage')
  );
}
{
  const r = await runFoundationClaims(
    'it3',
    TRIAGE_DRAFT,
    JSON.stringify({ ...JSON.parse(triageEnv([])), triage: undefined })
  );
  assert(
    'triage turn with no triage table is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('triage')
  );
}
const ATTACK_DRAFT =
  'You said entropy "captures the information". Take a fair coin and a biased coin with the same two outcomes — which one carries more information per draw, and which way does your rule move?';
const attackEnv = (attack) =>
  JSON.stringify({
    gate: 'fact_check',
    turn_kind: 'attack',
    attack,
    learner_model: 'entropy captures the information',
    visual_plan: { kind: 'none', why: 'a one-line mechanism press is carried by its sentence' },
    claims: [{ id: 1, claim: 'the attack asks for the causal chain' }],
    rendered_content: ATTACK_DRAFT,
    source_urls: ['https://e.com'],
  });
{
  const r = await runFoundationClaims('it4', ATTACK_DRAFT, attackEnv('mechanism'));
  assert('attack turn with one valid subtype renders', allowed(r));
}
{
  const r = await runFoundationClaims('it5', ATTACK_DRAFT, attackEnv(''));
  assert(
    'attack turn with no subtype is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('attack')
  );
}
{
  const r = await runFoundationClaims('it6', ATTACK_DRAFT, attackEnv('lecture'));
  assert(
    'attack turn with an unknown subtype is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('attack')
  );
}
const AUTOPSY_DRAFT =
  'Here is the patch, not your understanding: entropy is the expected surprise of a draw. ' +
  'Check: with a fair coin, is the surprise per draw high or low?';
const AUTOPSY_STEP = {
  index: 1,
  total: 1,
  fact: 'entropy is the expected surprise of a draw',
  rests_on: 'you already accepted that a rare outcome carries more surprise',
  check: 'with a fair coin, is the surprise per draw high or low?',
};
{
  const autopsy = JSON.stringify({
    gate: 'fact_check',
    turn_kind: 'autopsy',
    step: AUTOPSY_STEP,
    visual_plan: { kind: 'prose', why: 'the patch and the check are carried by prose' },
    claims: [{ id: 1, claim: 'entropy is the expected surprise of a distribution' }],
    rendered_content: AUTOPSY_DRAFT,
    source_urls: ['https://e.com'],
  });
  const r = await runFoundationClaims('it7', AUTOPSY_DRAFT, autopsy);
  assert('autopsy patch turn needs no foundation beat', allowed(r));
}
{
  const noStep = JSON.stringify({
    gate: 'fact_check',
    turn_kind: 'autopsy',
    visual_plan: { kind: 'prose', why: 'the patch and the check are carried by prose' },
    claims: [{ id: 1, claim: 'entropy is the expected surprise of a distribution' }],
    rendered_content: AUTOPSY_DRAFT,
    source_urls: ['https://e.com'],
  });
  const r = await runFoundationClaims('it11', AUTOPSY_DRAFT, noStep);
  assert(
    'autopsy without one bound reasoning step is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('step')
  );
}
{
  const noCheck = { ...AUTOPSY_STEP };
  delete noCheck.check;
  const r = await runFoundationClaims(
    'it12',
    AUTOPSY_DRAFT,
    JSON.stringify({
      gate: 'fact_check',
      turn_kind: 'autopsy',
      step: noCheck,
      visual_plan: { kind: 'prose', why: 'the patch and the check are carried by prose' },
      claims: [{ id: 1, claim: 'entropy is the expected surprise of a distribution' }],
      rendered_content: AUTOPSY_DRAFT,
      source_urls: ['https://e.com'],
    })
  );
  assert(
    'autopsy step missing its check is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('step')
  );
}
{
  const unbound = { ...AUTOPSY_STEP, fact: 'variance measures the spread of a Gaussian' };
  const r = await runFoundationClaims(
    'it13',
    AUTOPSY_DRAFT,
    JSON.stringify({
      gate: 'fact_check',
      turn_kind: 'autopsy',
      step: unbound,
      visual_plan: { kind: 'prose', why: 'the patch and the check are carried by prose' },
      claims: [{ id: 1, claim: 'entropy is the expected surprise of a distribution' }],
      rendered_content: AUTOPSY_DRAFT,
      source_urls: ['https://e.com'],
    })
  );
  assert(
    'autopsy step whose fact is not in the draft is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('step')
  );
}
{
  const r = await runFoundationClaims(
    'it14',
    TRIAGE_DRAFT,
    triageEnv([
      { item: 'entropy captures the information', bucket: 'suspect', evidence: 'learner: "entropy captures the information"', on_path: true },
      { item: 'log of typical sequences', bucket: 'missing', evidence: 'source p.3: nH typical sequences', requires: ['entropy captures the information'] },
      { item: 'independent draws', bucket: 'solid' },
    ])
  );
  assert('triage turn with dependency ordering renders', allowed(r));
}
{
  const r = await runFoundationClaims(
    'it15',
    TRIAGE_DRAFT,
    triageEnv([
      { item: 'entropy captures the information', bucket: 'suspect', evidence: 'learner: "entropy captures the information"', requires: ['not a row'] },
    ])
  );
  assert(
    'triage turn with unmet dependency is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('requires')
  );
}
{
  const r = await runFoundationClaims(
    'it16',
    TRIAGE_DRAFT,
    triageEnv([
      { item: 'entropy captures the information', bucket: 'suspect', evidence: 'learner: "entropy captures the information"', requires: ['log of typical sequences'] },
      { item: 'log of typical sequences', bucket: 'missing', evidence: 'source p.3: nH typical sequences', requires: ['entropy captures the information'] },
    ])
  );
  assert(
    'triage turn with a cyclic requires edge is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('cycle')
  );
}
{
  const r = await runFoundationClaims(
    'it17',
    TRIAGE_DRAFT,
    triageEnv([
      { item: 'entropy captures the information', bucket: 'suspect', evidence: 'learner: "entropy captures the information"' },
      { item: 'entropy captures the information', bucket: 'missing', evidence: 'source p.3: nH typical sequences' },
    ])
  );
  assert(
    'triage turn with duplicate item names is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('duplicate')
  );
}
{
  const plan = JSON.stringify({
    gate: 'fact_check',
    turn_kind: 'plan',
    visual_plan: { kind: 'none', why: 'a reading brief is scope, not mechanism' },
    claims: [{ id: 1, claim: 'read the chapter and its Further Reading' }],
    rendered_content: 'Read section 3 and its Further Reading, then bring your notes and a closed-book model.',
    source_urls: ['https://e.com'],
  });
  const r = await runFoundationClaims(
    'it8',
    'Read section 3 and its Further Reading, then bring your notes and a closed-book model.',
    plan
  );
  assert('reading-brief plan turn needs no foundation beat', allowed(r));
}
{
  const feedback = JSON.stringify({
    gate: 'fact_check',
    turn_kind: 'grade_feedback',
    grade_verdicts: [{ id: 1, concept: 'entropy', verdict: 'fail', trace_step: 'direction' }],
    visual_plan: { kind: 'prose', why: 'the failed step is one sentence' },
    claims: [{ id: 1, claim: 'the trace missed the direction check' }],
    rendered_content: 'Your trace named the right knob but not which way it moves.',
    source_urls: ['https://e.com'],
  });
  const r = await runFoundationClaims(
    'it9',
    'Your trace named the right knob but not which way it moves.',
    feedback
  );
  assert('review grade-feedback turn needs no foundation beat', allowed(r));
}
{
  const r = await runFoundationClaims('it10', FOUND_DRAFT, ideaEnv(FOUND_DRAFT, FOUNDATION, 'lecture'));
  assert(
    'claims turn with an unknown turn_kind is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('turn_kind')
  );
}

// ============================================================================
// Auto-ingest at lesson end (G-interrogation-stance / writes & session end):
// after the Tutor's handoff passes tutor-audit, the Tutor dispatches clerk and
// review-gate inline and then presents the completion summary. The summary must
// render with those receipts present.
// ============================================================================
{
  await setPrompt('[[FLOW:teach]] teach me fixture linear algebra');
  const lessonPath = 'Learning System/Lessons/Lesson — Fixture — 2026-10-25.md';
  await writeCall(lessonPath, 'ai1');
  const tutorEnv = JSON.stringify({ gate: 'tutor_audit', flow: 'lesson-end', files: [lessonPath] });
  await dispatch('tutor-audit', tutorEnv, 'ai2');
  await fg('ai2', 'tutor-audit', tutorEnv, JSON.stringify({ verdict: 'PASS', evidence: ['read lesson file'], issues: [], context_notes: [] }));
  const clerkEnv = JSON.stringify({ mode: 'ingest', source: 'Learning System/Core/Pending Ingest.json' });
  await dispatch('clerk', clerkEnv, 'ai3');
  await fg('ai3', 'clerk', clerkEnv, CLERK_WRITES);
  const rgEnv = JSON.stringify({ gate: 'review', concepts: ['Fixture'], target_files: [{ path: 'Knowledge Wiki/wiki/Fixture.md' }] });
  await dispatch('review-gate', rgEnv, 'ai4');
  await fg('ai4', 'review-gate', rgEnv, REVIEW_PASS);
  const summary = await msg(
    '[[TURN:none]]\nLesson complete: the v1 model missed the mechanism, the attack exposed it, and v2 now carries the condition. Ingested one wiki page; next review in 3 days. STATE_AUDIT_VERDICT: {"errors":0,"warnings":0}',
    'stop'
  );
  assert('lesson-end auto-ingest summary renders after tutor-audit + clerk + review-gate', allowed(summary));
}

// ============================================================================
// Repair mode (G-repair-trigger / G-repair-method / G-repair-scope /
// G-repair-complete). After a graded miss survives the hint ladder the Tutor
// teaches the diagnosed gap one checked step at a time; the battery may not
// resume (NO_REPAIR_RECEIPT) until a `done` repair names the fresh-surface
// check the learner already passed plus their own-words restatement.
// ============================================================================
const REPAIR_DRAFT =
  'Build it from what you already hold: a rare outcome carries more surprise than a common one, so ' +
  'entropy is the expected surprise of a draw. Check: with a fair coin, is the surprise per draw high or low?';
const REPAIR_STEP = {
  index: 1,
  total: 1,
  fact: 'entropy is the expected surprise of a draw',
  rests_on: 'you already hold that a rare outcome carries more surprise',
  check: 'with a fair coin, is the surprise per draw high or low?',
};
const repairEnv = (repair, draft = REPAIR_DRAFT) =>
  JSON.stringify({
    gate: 'fact_check',
    turn_kind: 'repair',
    repair,
    visual_plan: { kind: 'prose', why: 'a one-step repair and its check are carried by prose' },
    claims: [{ id: 1, claim: 'the repair installs one motivated step and checks it' }],
    rendered_content: draft,
    source_urls: ['https://e.com'],
  });
const TEACH_REPAIR = {
  gap: 'entropy captures the information',
  miss_class: 'structural',
  tactic: 'push_down',
  status: 'teaching',
  step: REPAIR_STEP,
};
{
  const r = await runFoundationClaims('rp1', REPAIR_DRAFT, repairEnv(TEACH_REPAIR));
  assert('repair turn with one bound step renders', allowed(r));
}
{
  const noBlock = JSON.stringify({ ...JSON.parse(repairEnv(TEACH_REPAIR)), repair: undefined });
  const r = await runFoundationClaims('rp2', REPAIR_DRAFT, noBlock);
  assert(
    'repair turn without one bound step is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('repair')
  );
}
{
  const badClass = { ...TEACH_REPAIR, miss_class: 'vibes' };
  const r = await runFoundationClaims('rp3', REPAIR_DRAFT, repairEnv(badClass));
  assert(
    'repair turn with an invalid miss class is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('miss_class')
  );
}
{
  const noStep = { ...TEACH_REPAIR };
  delete noStep.step;
  const r = await runFoundationClaims('rp4', REPAIR_DRAFT, repairEnv(noStep));
  assert(
    'repair turn without a bound step is withheld',
    blocked(r, 'FOUNDATION_INCOMPLETE') && outText(r).includes('step')
  );
}
{
  // Open a repair, then try to resume the attack battery before closing it.
  await setPrompt('[[FLOW:resume]] continue the lesson');
  const teachEnv = repairEnv(TEACH_REPAIR);
  await dispatch('fact-check', teachEnv, 'rp5');
  await fg('rp5', 'fact-check', teachEnv, FC_PASS);
  const opened = await msg(`[[TURN:claims]]\n${REPAIR_DRAFT}`, 'stop');
  const attack = attackEnv('mechanism');
  await dispatch('fact-check', attack, 'rp6');
  await fg('rp6', 'fact-check', attack, FC_PASS);
  const r = await msg(`[[TURN:claims]]\n${ATTACK_DRAFT}`, 'stop');
  assert(
    'attack turn withheld while a repair is open',
    allowed(opened) && blocked(r, 'NO_REPAIR_RECEIPT')
  );
}
{
  // A `done` repair without a graded fresh-surface pass is not a receipt.
  await setPrompt('[[FLOW:resume]] continue the lesson');
  const teachEnv = repairEnv(TEACH_REPAIR);
  await dispatch('fact-check', teachEnv, 'rp7');
  await fg('rp7', 'fact-check', teachEnv, FC_PASS);
  await msg(`[[TURN:claims]]\n${REPAIR_DRAFT}`, 'stop');
  const doneEnv = repairEnv(
    {
      gap: 'entropy captures the information',
      miss_class: 'structural',
      tactic: 'push_down',
      status: 'done',
      fresh_surface_check: 'with a fair coin, is the surprise per draw high or low?',
      learner_restate: 'entropy is what a draw surprises you by on average',
    },
    'Closed: you now hold that entropy is the expected surprise. Next we re-test it.'
  );
  await dispatch('fact-check', doneEnv, 'rp8');
  await fg('rp8', 'fact-check', doneEnv, FC_PASS);
  const r = await msg('[[TURN:claims]]\nClosed: you now hold that entropy is the expected surprise. Next we re-test it.', 'stop');
  assert('repair done without a passing fresh-surface check is withheld', blocked(r, 'REPAIR_INCOMPLETE'));
}
{
  // The full loop: teach one step → grade the fresh-surface check pass → close
  // the repair → the battery resumes.
  await setPrompt('[[FLOW:resume]] continue the lesson');
  const teachEnv = repairEnv(TEACH_REPAIR);
  await dispatch('fact-check', teachEnv, 'rp9');
  await fg('rp9', 'fact-check', teachEnv, FC_PASS);
  await msg(`[[TURN:claims]]\n${REPAIR_DRAFT}`, 'stop');
  const gradeEnv = JSON.stringify({
    gate: 'grade_audit',
    items: [
      {
        id: 1,
        concept: 'entropy',
        qtype: 'micro-check',
        question: 'with a fair coin, is the surprise per draw high or low?',
        learner_answer: 'High — a fair coin is maximally uncertain.',
        claimed_verdict: 'pass',
      },
    ],
  });
  await dispatch('grade-audit', gradeEnv, 'rp10');
  await fg('rp10', 'grade-audit', gradeEnv, GATE);
  const gradeTurn = await msg(
    '[[TURN:grade]]\nwith a fair coin, is the surprise per draw high or low? PASS — you said "High — a fair coin is maximally uncertain."',
    'stop'
  );
  const doneDraft = 'Closed: you now hold that entropy is the expected surprise, and a fair coin is maximally uncertain. Next we re-test it.';
  const doneEnv = repairEnv(
    {
      gap: 'entropy captures the information',
      miss_class: 'structural',
      tactic: 'push_down',
      status: 'done',
      fresh_surface_check: 'with a fair coin, is the surprise per draw high or low?',
      learner_restate: 'entropy is what a draw surprises you by on average',
    },
    doneDraft
  );
  await dispatch('fact-check', doneEnv, 'rp11');
  await fg('rp11', 'fact-check', doneEnv, FC_PASS);
  const closed = await msg(`[[TURN:claims]]\n${doneDraft}`, 'stop');
  const attack = attackEnv('mechanism');
  await dispatch('fact-check', attack, 'rp12');
  await fg('rp12', 'fact-check', attack, FC_PASS);
  const resumed = await msg(`[[TURN:claims]]\n${ATTACK_DRAFT}`, 'stop');
  assert(
    'repair done with a passing fresh-surface check renders',
    allowed(gradeTurn) && allowed(closed)
  );
  assert('attack turn resumes after a repair receipt', allowed(resumed));
}

