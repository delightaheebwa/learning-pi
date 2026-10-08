// Golden scenario tests for the learning-gate, in domain terms.
//
//   deno run --allow-all test/golden/golden_test.mjs
//
// These cover the invariants that gate_test.mjs does not: non-learning sessions,
// the tutor-audit and review-session write gates, scout-required, the retry cap,
// out-of-scope review demotion, and the verified-draft `none` evasion guard.
// Assertions are named to match the `tests` entries in contracts/learning-core.json.
// Keep the always-on receipt ledger out of the real pi agent dir during tests.
process.env.LEARNING_GATE_LEDGER_DIR = '/tmp/learning-gate-test/';
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
const REVIEW_SCOUT_OK =
  'REVIEW_SCOUT_DIGEST: {"track":"aiefs","digest":"Learning System/.tmp/review-x.json","queue":[],"failed_refs":[]}';

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

// P1.6: at the cap, a claims turn stating hard facts is withheld outright —
// only the banner renders, no content — while non-hard-fact prose still degrades.
await setPrompt('[[FLOW:resume]] continue the lesson');
const hfDraft = 'The mean is 12.5 and the variance is 3.2.';
const hf1 = await msg(`[[TURN:claims]]\n${hfDraft}`, 'stop');
const hf2 = await msg(`[[TURN:claims]]\n${hfDraft}`, 'stop');
const hf3 = await msg(`[[TURN:claims]]\n${hfDraft}`, 'stop');
assert('retry cap withholds a hard-fact claims turn', blocked(hf3, 'WITHHELD') && !outText(hf3).includes('12.5'));
assert('repeated hard-fact claims turns are blocked before the cap', blocked(hf1, 'NO_FACT_CHECK_MATCH') && blocked(hf2, 'NO_FACT_CHECK_MATCH'));

// ============================================================================
// none-evasion: a verified fact-check draft tagged [[TURN:none]] is withheld.
// ============================================================================
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('fact-check', fcEnvelope(DRAFT), 'fc3');
await fg('fc3', 'fact-check', fcEnvelope(DRAFT), FC_PASS);
const noneVerified = await msg(`[[TURN:none]]\n${DRAFT}`, 'stop');
assert('none tag over a verified draft is withheld', blocked(noneVerified, 'TURN_TAG_MISMATCH'));

// ============================================================================
// review-flow carve-out: closing review feedback legitimately reuses verified
// prose under a [[TURN:none]] tag, so a content-matching PASS renders there.
// ============================================================================
const REVIEW_DRAFT = 'Review closed: direction right, instantiation skipped; given food spoilt, time tells nothing about smell.';
await setPrompt('[[FLOW:review]] review my due concepts');
await dispatch('fact-check', fcEnvelope(REVIEW_DRAFT), 'fc4');
await fg('fc4', 'fact-check', fcEnvelope(REVIEW_DRAFT), FC_PASS);
const reviewNone = await msg(`[[TURN:none]]\n${REVIEW_DRAFT}`, 'stop');
assert('review-flow none summary over a verified draft renders', allowed(reviewNone));

// ============================================================================
// grade verdict supersession: an older disagreeing receipt must not block a
// later grade+repair turn when a corrected (agreeing) receipt and a covering
// fact-check exist (the 2026-10-06 review close looped as GRADE_MISMATCH).
// ============================================================================
const staleProse = 'Name the slip: the direction is inverted. Detector: once Z is known, X tells you nothing about Y.';
const staleBadEnv = JSON.stringify({
  gate: 'grade_audit',
  items: [{ id: 2, concept: 'CI', question: 'Q2 restate screening-off', learner_answer: 'abstract', claimed_verdict: 'fail' }],
});
const staleBadOut = JSON.stringify({
  verdict: 'ISSUES',
  agrees: false,
  correct_verdict: 'fail',
  issues: [{ id: 2, correction: 'no concrete instantiation' }],
  items: [{ id: 2, agrees: false, correct_verdict: 'fail' }],
});
const staleGoodEnv = JSON.stringify({
  gate: 'grade_audit',
  items: [{ id: 3, concept: 'CI', question: 'Q3 fill the blanks', learner_answer: 'spoilt', claimed_verdict: 'pass' }],
});
const staleGoodOut = JSON.stringify({
  verdict: 'PASS',
  agrees: true,
  correct_verdict: 'pass',
  issues: [],
  items: [{ id: 3, agrees: true, correct_verdict: 'pass' }],
});
await setPrompt('[[FLOW:review]] review my due concepts');
await dispatch('grade-audit', staleBadEnv, 'gb1');
await fg('gb1', 'grade-audit', staleBadEnv, staleBadOut);
await dispatch('grade-audit', staleGoodEnv, 'gg1');
await fg('gg1', 'grade-audit', staleGoodEnv, staleGoodOut);
await dispatch('fact-check', fcEnvelope(staleProse), 'gfc1');
await fg('gfc1', 'fact-check', fcEnvelope(staleProse), FC_PASS);
const superseded = await msg(`[[TURN:grade]]\n${staleProse}`, 'stop');
assert('newest grade verdict supersedes an older disagreement', allowed(superseded));

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
assert('out-of-scope review issues with a bookkeeping location render as flags', allowed(demoted) && outText(demoted).includes('REVIEW FLAGS SURFACED'));

// ============================================================================
// P2.1 state gate: at the ingest close, a state-audit ERROR withholds the
// summary (state drift must be fixed first); a WARNING only banners.
// ============================================================================
await setPrompt('[[FLOW:ingest]] ingest this');
await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), 'sg-c1');
await notify(`Background task completed: **clerk**\n\n${CLERK_WRITES}\nSTATE_AUDIT_VERDICT: {"errors":1,"warnings":0}`);
await dispatch('review-gate', JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'p.md' }] }), 'sg-rg1');
await fg(
  'sg-rg1',
  'review-gate',
  JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'p.md' }] }),
  JSON.stringify({ verdict: 'PASS', evidence: ['x'], issues: [] })
);
const stateAuditBlocked = await msg('[[TURN:none]]\nIngest complete. STATE_AUDIT_VERDICT: {"errors":1,"warnings":0}', 'stop');
assert('state-audit error withholds the close summary', blocked(stateAuditBlocked, 'STATE_AUDIT_ERRORS'));

await setPrompt('[[FLOW:ingest]] ingest this');
await dispatch('clerk', JSON.stringify({ gate: 'clerk' }), 'sg-c2');
await notify(`Background task completed: **clerk**\n\n${CLERK_WRITES}\nSTATE_AUDIT_VERDICT: {"errors":0,"warnings":2}`);
await dispatch('review-gate', JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'p.md' }] }), 'sg-rg2');
await fg(
  'sg-rg2',
  'review-gate',
  JSON.stringify({ gate: 'review', concepts: ['X'], target_files: [{ path: 'p.md' }] }),
  JSON.stringify({ verdict: 'PASS', evidence: ['x'], issues: [] })
);
const stateAuditWarned = await msg('[[TURN:none]]\nIngest complete. STATE_AUDIT_VERDICT: {"errors":0,"warnings":2}', 'stop');
assert('state-audit warnings render a non-blocking banner', allowed(stateAuditWarned) && outText(stateAuditWarned).includes('STATE AUDIT'));

// ============================================================================
// review context: the review flow's first claims/quiz turn needs a review-scout
// run; a partial digest banners but never withholds.
// ============================================================================
const qEnv = JSON.stringify({ gate: 'quiz_audit', purpose: 'probe', questions_json: [{ id: 1, question: 'State the Bayes rule.' }] });
const QUIZ_PASS = JSON.stringify({ verdict: 'PASS', issues: [] });
await setPrompt('[[FLOW:review]] review my due concepts');
await dispatch('quiz-audit', qEnv, 'rq1');
await fg('rq1', 'quiz-audit', qEnv, QUIZ_PASS);
const noReviewScout = await msg('[[TURN:quiz]]\nState the Bayes rule.', 'stop');
assert('review without a context scout run is withheld', blocked(noReviewScout, 'NO_REVIEW_CONTEXT'));

await setPrompt('[[FLOW:review]] review my due concepts');
await dispatch('review-scout', 'build the review queue', 'rsc1');
await fg(
  'rsc1',
  'review-scout',
  'build the review queue',
  'REVIEW_SCOUT_DIGEST: {"track":"aiefs","digest":"Learning System/.tmp/review-x.json","queue":[],"failed_refs":[{"what":"Attempts.json","reason":"unreadable"}]}'
);
await dispatch('quiz-audit', qEnv, 'rq2');
await fg('rq2', 'quiz-audit', qEnv, QUIZ_PASS);
const partialCtx = await msg('[[TURN:quiz]]\nState the Bayes rule.', 'stop');
assert('review context incomplete banner surfaced', allowed(partialCtx) && outText(partialCtx).includes('REVIEW CONTEXT INCOMPLETE'));

await setPrompt('[[FLOW:review]] review my due concepts');
await dispatch('review-scout', 'build the review queue', 'rsc2');
await fg('rsc2', 'review-scout', 'build the review queue', REVIEW_SCOUT_OK);
await dispatch('quiz-audit', qEnv, 'rq3');
await fg('rq3', 'quiz-audit', qEnv, QUIZ_PASS);
const okCtx = await msg('[[TURN:quiz]]\nState the Bayes rule.', 'stop');
assert('review context scout releases the first review turn', allowed(okCtx) && !outText(okCtx).includes('REVIEW CONTEXT'));

// ============================================================================
// review close: a completed review-clerk (the delegated writer) arms the
// review-session audit gate; the summary needs a passing audit.
// ============================================================================
const RC_ENV = JSON.stringify({ gate: 'review_writes', track: 'aiefs', concepts: ['X'], grade_verdicts: [{ concept: 'X', correct_verdict: 'pass' }] });
const SESSION_PATH = 'Learning System/Sessions/Session — Review — 2026-09-28.md';
await setPrompt('[[FLOW:review]] review my due concepts');
await dispatch('review-clerk', RC_ENV, 'rc1');
await fg('rc1', 'review-clerk', RC_ENV, 'REVIEW_CLERK_WRITES: {"reviews":[],"session":"' + SESSION_PATH + '","state":[],"concepts":["X"],"commit":"abc","state_audit":{"errors":0,"warnings":0}}');
const noRsaAfterClerk = await msg('[[TURN:none]]\nReview — mastery 4/5, next review 2026-10-01. Recap below.', 'stop');
assert('review-clerk writes require a review-session audit', blocked(noRsaAfterClerk, 'NO_REVIEW_SESSION_AUDIT'));
const rsaEnv = JSON.stringify({ gate: 'review_session', written_files: [{ path: SESSION_PATH }] });
await dispatch('review-session-audit', rsaEnv, 'rsa2');
await fg('rsa2', 'review-session-audit', rsaEnv, JSON.stringify({ verdict: 'PASS', evidence: ['read the session note'], issues: [] }));
const rsaReleased = await msg('[[TURN:none]]\nReview — mastery 4/5, next review 2026-10-01. Recap below.', 'stop');
assert('review-clerk close released by review-session pass', allowed(rsaReleased));

// ============================================================================
// viz turns: a [[TURN:viz]] message carries a ```viz spec and requires a
// passing viz-audit bound to that exact spec plus the supporting prose.
// ============================================================================
const VSPEC = { viz: '1', kind: 'bar', title: 'Counts', bars: [{ label: 'a', value: 1 }, { label: 'b', value: 4 }] };
const VSPEC_OTHER = { viz: '1', kind: 'bar', title: 'Counts', bars: [{ label: 'a', value: 4 }, { label: 'b', value: 1 }] };
const fence = (s) => '```viz\n' + JSON.stringify(s) + '\n```';
const VDRAFT = `Here is the distribution.\n${fence(VSPEC)}\nNotice b dominates.`;
const VENV = JSON.stringify({ gate: 'viz_audit', concept: 'counts', spec: VSPEC, rendered_content: VDRAFT });
const VIZ_PASS = JSON.stringify({ verdict: 'PASS', issues: [] });

// A bound, passing viz-audit releases the viz turn.
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('viz-audit', VENV, 'v1');
await fg('v1', 'viz-audit', VENV, VIZ_PASS);
const okViz = await msg(`[[TURN:viz]]\n${VDRAFT}`, 'stop');
assert('viz turn renders with a bound viz-audit', allowed(okViz) && stripped(okViz));

// No receipt at all -> withheld.
await setPrompt('[[FLOW:resume]] continue the lesson');
const noViz = await msg(`[[TURN:viz]]\n${VDRAFT}`, 'stop');
assert('viz turn without a viz-audit is withheld', blocked(noViz, 'NO_VIZ_AUDIT'));

// The audited spec must match the emitted spec.
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('viz-audit', VENV, 'v2');
await fg('v2', 'viz-audit', VENV, VIZ_PASS);
const otherSpec = await msg(`[[TURN:viz]]\nHere is the distribution.\n${fence(VSPEC_OTHER)}\nNotice a dominates.`, 'stop');
assert('viz-audit with a different spec does not bind', blocked(otherSpec, 'VIZ_AUDIT_STALE'));

// A wrong-shape receipt (no spec / no rendered_content) binds nothing.
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('viz-audit', JSON.stringify({ gate: 'viz_audit', concept: 'counts' }), 'v3');
await fg('v3', 'viz-audit', JSON.stringify({ gate: 'viz_audit', concept: 'counts' }), VIZ_PASS);
const wrongShapeViz = await msg(`[[TURN:viz]]\n${VDRAFT}`, 'stop');
assert('wrong-shape viz receipt does not bind a viz turn', blocked(wrongShapeViz, 'VIZ_AUDIT_STALE'));

// ISSUES withholds the viz turn.
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('viz-audit', VENV, 'v4');
await fg('v4', 'viz-audit', VENV, JSON.stringify({ verdict: 'ISSUES', issues: [{ severity: 'high', problem: 'axes inverted' }] }));
const issuesViz = await msg(`[[TURN:viz]]\n${VDRAFT}`, 'stop');
assert('viz-audit ISSUES withholds the viz turn', blocked(issuesViz, 'VIZ_AUDIT_ISSUES'));

// A viz spec must be present and parseable.
await setPrompt('[[FLOW:resume]] continue the lesson');
const noSpecViz = await msg('[[TURN:viz]]\nHere is a picture — trust me.', 'stop');
assert('unparseable viz spec is withheld', blocked(noSpecViz, 'VIZ_SPEC_INVALID'));

// A dropped viz tag is recovered from a bound viz-audit.
await setPrompt('[[FLOW:resume]] continue the lesson');
await dispatch('viz-audit', VENV, 'v5');
await fg('v5', 'viz-audit', VENV, VIZ_PASS);
const droppedViz = await msg(VDRAFT, 'stop');
assert('dropped viz tag recovered from a bound viz-audit', allowed(droppedViz));

// A viz fence inside a claims turn is withheld (it must be its own turn).
await setPrompt('[[FLOW:resume]] continue the lesson');
const claimsViz = await msg(`[[TURN:claims]]\n${VDRAFT}`, 'stop');
assert('viz block in a claims turn is withheld', blocked(claimsViz, 'VIZ_REQUIRES_OWN_TURN'));

// A viz fence inside a transition turn is withheld too.
await setPrompt('[[FLOW:resume]] continue the lesson');
const noneViz = await msg(`[[TURN:none]]\n${VDRAFT}`, 'stop');
assert('viz block in a none turn is withheld', blocked(noneViz, 'VIZ_REQUIRES_OWN_TURN'));
