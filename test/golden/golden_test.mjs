// Golden scenario tests for the learning-gate, in domain terms.
//
//   deno run --allow-all test/golden/golden_test.mjs
//
// These cover the invariants that gate_test.mjs does not: non-learning sessions,
// the tutor-audit and review-session write gates, scout-required, the retry cap,
// out-of-scope review demotion, and the verified-draft `none` evasion guard.
// Assertions are named to match the `tests` entries in contracts/learning-core.json.
const handlers = {};
const pi = { on: (ev, h) => { (handlers[ev] ||= []).push(h); } };
const mod = await import('../../.pi/extensions/learning-gate/index.ts');
mod.default(pi);
const fire = async (ev, e) => { let r; for (const h of handlers[ev] || []) r = await h(e, { ui: { notify() {} } }); return r; };
const setPrompt = (p) => fire('before_agent_start', { prompt: p });
const msg = (t, stopReason) => fire('message_end', { message: { role: 'assistant', content: [{ type: 'text', text: t }], stopReason } });
const notify = (t) => fire('message_end', { message: { role: 'custom', customType: 'subagent-notify', content: [{ type: 'text', text: t }] } });
const dispatch = (agent, task, id) => fire('tool_call', { toolName: 'subagent', toolCallId: id, input: { agent, task } });
const bashCall = (command, id) => fire('tool_call', { toolName: 'bash', toolCallId: id, input: { command } });
const writeCall = (filePath, id) => fire('tool_call', { toolName: 'write', toolCallId: id, input: { filePath } });
const fg = (id, agent, task, output) =>
  fire('tool_result', {
    toolName: 'subagent',
    toolCallId: id,
    isError: false,
    content: [{ type: 'text', text: '' }],
    details: { results: [{ agent, task, finalOutput: output, runId: `r-${id}` }] },
  });
const outText = (r) => {
  if (!r || !r.message) return '';
  const c = r.message.content;
  if (typeof c === 'string') return c;
  if (Array.isArray(c)) return c.map((p) => (p && p.type === 'text' ? p.text : '')).join('');
  return '';
};
const allowed = (r) => r && r.message && !outText(r).startsWith('⛔');
const notBlocked = (r) => !(r && r.message && outText(r).startsWith('⛔'));
const blocked = (r, code) => !!(r && r.message && outText(r).startsWith('⛔') && (!code || outText(r).includes(code)));
const stripped = (r) => allowed(r) && !outText(r).includes('[[TURN');
const assert = (n, c) => console.log((c ? 'PASS ' : 'FAIL ') + n);

const DRAFT = 'The variation of information is V(X,Y) = H(X,Y) minus I(X,Y).';
const FC_PASS = JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }], contradictions: [] });
const fcEnvelope = (draft) =>
  JSON.stringify({ gate: 'fact_check', claims: [{ id: 1, claim: 'x' }], rendered_content: draft, source_urls: ['https://e.com'] });
const SCOUT_OK = 'SCOUT_DIGEST: {"slug":"x","digest":"d","raw_files":[],"failed_refs":[]}';
const CLERK_WRITES = '[[TURN:none]]\nCLERK_WRITES: {"wiki":["Knowledge Wiki/wiki/X.md"],"state":[],"concepts":["X"],"commit":"abc"}';

// ============================================================================
// First: a session with no [[FLOW:...]] marker is never gated. (Must run before
// any learning flow starts, since a flow persists for the rest of the session.)
// ============================================================================
const chat = await msg('It is four.', 'stop');
assert('non-learning session is never gated', chat === undefined);

// ============================================================================
// tutor-audit: a handoff write in teach/resume requires a passing tutor-audit
// over the files written before the summary renders.
// ============================================================================
await setPrompt('[[FLOW:teach]] teach me eigenvalue decomposition');
await dispatch('scout', 'topic eigenvalues', 'sc1');
await fg('sc1', 'scout', 'topic eigenvalues', SCOUT_OK);
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc1');
await fg('fc1', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
await writeCall('Learning System/Lessons/Lesson — eigenvalues.md', 'w1');
const noTutorAudit = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('tutor-audit required after a learning-system write', blocked(noTutorAudit, 'NO_TUTOR_AUDIT'));
await dispatch('tutor-audit', JSON.stringify({ gate: 'tutor_audit', files: ['Learning System/Lessons/Lesson — eigenvalues.md'] }), 't1');
await fg('t1', 'tutor-audit', JSON.stringify({ gate: 'tutor_audit', files: ['Learning System/Lessons/Lesson — eigenvalues.md'] }), '{"verdict":"PASS","issues":[]}');
const tutorReleased = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('tutor-audit pass releases the handoff summary', allowed(tutorReleased) && stripped(tutorReleased));

// ============================================================================
// new lesson: teaching claims without a scout run is withheld NO_SCOUT_CONTEXT.
// ============================================================================
await setPrompt('[[FLOW:teach]] teach me a brand new topic');
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc2');
await fg('fc2', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const noScout = await msg(`[[TURN:claims]]\n${DRAFT}`, 'stop');
assert('new lesson without a scout run is withheld', blocked(noScout, 'NO_SCOUT_CONTEXT'));

// ============================================================================
// review close: after the session note is written, a summary-like turn needs a
// review-session audit.
// ============================================================================
await setPrompt('[[FLOW:review]] review my due concepts');
await bashCall("python3 scripts/ops.py apply <<'SPEC'\nLearning System/Sessions/Session — Review — 2026-09-23.md\nSPEC", 'b1');
const noRS = await msg('Review — mastery 4/5, next review 2026-10-01. Recap below.', 'stop');
assert('review-session audit required after session-note write', blocked(noRS, 'NO_REVIEW_SESSION_AUDIT'));
await dispatch('review-session-audit', JSON.stringify({ gate: 'review_session', files: ['Learning System/Sessions/Session — Review — 2026-09-23.md'] }), 'rs1');
await fg(
  'rs1',
  'review-session-audit',
  JSON.stringify({ gate: 'review_session', files: ['Learning System/Sessions/Session — Review — 2026-09-23.md'] }),
  JSON.stringify({ verdict: 'PASS', evidence: ['read the session note'], issues: [] })
);
const rsReleased = await msg('Review — mastery 4/5, next review 2026-10-01. Recap below.', 'stop');
assert('review-session pass releases the close summary', allowed(rsReleased));

// ============================================================================
// retry cap: repeated withheld turns surface ⛔ UNVERIFIED rather than looping.
// ============================================================================
await setPrompt('[[FLOW:resume]] continue the lesson');
const r1 = await msg('[[TURN:grade]]\nGraded (verifier-agreed): W1 PASS.', 'stop');
const r2 = await msg('[[TURN:grade]]\nGraded (verifier-agreed): W1 PASS.', 'stop');
const r3 = await msg('[[TURN:grade]]\nGraded (verifier-agreed): W1 PASS.', 'stop');
assert('repeated withheld turns are blocked before the cap', blocked(r1, 'NO_GRADE_AUDIT_PASS') && blocked(r2, 'NO_GRADE_AUDIT_PASS'));
assert('retry cap surfaces unverified after 2 withholdings', outText(r3).includes('⛔ UNVERIFIED'));

// ============================================================================
// none-evasion: a verified fact-check draft tagged [[TURN:none]] is withheld.
// ============================================================================
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc3');
await fg('fc3', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const noneVerified = await msg(`[[TURN:none]]\n${DRAFT}`, 'stop');
assert('none tag over a verified draft is withheld', blocked(noneVerified, 'TURN_TAG_MISMATCH'));

// ============================================================================
// out-of-scope review findings on an ingest render as flags, never a withhold.
// ============================================================================
await setPrompt('[[FLOW:ingest]] ingest this');
await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), 'c1');
await notify(`Background task completed: **clerk**\n\n${CLERK_WRITES}`);
await dispatch('review-gate', JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'p.md' }] }), 'rg1');
await fg(
  'rg1',
  'review-gate',
  JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'p.md' }] }),
  JSON.stringify({ verdict: 'ISSUES', issues: [{ severity: 'high', location: 'ATTEMPTS.json', issue: 'stale schedule' }], evidence: ['x'] })
);
const demoted = await msg('[[TURN:none]]\nIngest complete. STATE_AUDIT_VERDICT: {"errors":0,"warnings":0}', 'stop');
assert('out-of-scope review issues render as flags, not withheld', allowed(demoted) && outText(demoted).includes('REVIEW FLAGS SURFACED'));
