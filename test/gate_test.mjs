// Regression tests for the learning-gate extension.
//
//   deno run --allow-all test/gate_test.mjs
//
// Covers the partial-generation dead-end: an assistant message whose
// generation did not finish (`stopReason` error/aborted/length) must pass
// through ungated without consuming a verifier receipt, so the retried or
// continued message can still bind to it.
const handlers = {};
const pi = { on: (ev, h) => { (handlers[ev] ||= []).push(h); } };
const mod = await import('../.pi/extensions/learning-gate/index.ts');
mod.default(pi);
const fire = async (ev, e) => { let r; for (const h of handlers[ev] || []) r = await h(e, { ui: { notify() {} } }); return r; };
const setPrompt = (p) => fire('before_agent_start', { prompt: p });
const msg = (t, stopReason) => fire('message_end', { message: { role: 'assistant', content: [{ type: 'text', text: t }], stopReason } });
const notify = (t) => fire('message_end', { message: { role: 'custom', customType: 'subagent-notify', content: [{ type: 'text', text: t }] } });
const dispatch = async (agent, task, id) => { await fire('tool_call', { toolName: 'subagent', toolCallId: id, input: { agent, task } }); };
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

// --- a failed async verifier clears the in-flight state (no stale hint) ---
await setPrompt('[[FLOW:resume]] continue the lesson');
await asyncDispatch('n2', 'fact-check', fcEnvelope(vDraft));
await asyncResult('n2', uuid6);
await notify(`Background task failed: **fact-check**\n\nfact-check:\nOpenAI API error (429): rate_limit_exceeded\n\nRetention-managed async directory: /tmp/x/async-subagent-runs/${uuid6}`);
const afterFail = await msg(`[[TURN:claims]]\n${vDraft}`, 'stop');
assert('failed verifier is not reported as in-flight', blocked(afterFail, 'NO_FACT_CHECK_MATCH') && !outText(afterFail).includes('still in flight'));


