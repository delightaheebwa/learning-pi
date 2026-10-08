// Seeded-error red-team harness for the learning-gate (P1.8).
//
//   deno run --allow-all test/redteam/redteam_test.mjs
//
// Injects known-wrong load-bearing content into sandboxed gate flows and asserts
// the gate catches it — via the deterministic hard-fact completeness check
// (CLAIMS_INCOMPLETE) or the fact-check ISSUES path (FACT_CHECK_ISSUES). Offline:
// no real models are called; the "verifier" is a synthetic receipt, which is
// exactly the gate's contract surface. Clean controls assert the gate does not
// false-block a correct, fully-listed draft.
//
// Reports caught/total. Wired into scripts/learn-check as a behavior suite.
process.env.LEARNING_GATE_LEDGER_DIR = '/tmp/learning-gate-redteam/';
const handlers = {};
const pi = { on: (ev, h) => { (handlers[ev] ||= []).push(h); } };
const mod = await import('../../.pi/extensions/learning-gate/index.ts');
mod.default(pi);
const fire = async (ev, e) => { let r; for (const h of handlers[ev] || []) r = await h(e, { ui: { notify() {} } }); return r; };
const setPrompt = (p) => fire('before_agent_start', { prompt: p });
const msg = (t) => fire('message_end', { message: { role: 'assistant', content: [{ type: 'text', text: t }], stopReason: 'stop' } });
const dispatch = (agent, task, id) => fire('tool_call', { toolName: 'subagent', toolCallId: id, input: { agent, task } });
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
const blocked = (r, code) => !!(r && r.message && outText(r).startsWith('⛔') && (!code || outText(r).includes(code)));
const allowed = (r) => r && r.message && !outText(r).startsWith('⛔');

const FC_PASS = JSON.stringify({ verdicts: [{ id: 1, verdict: 'PASS', explanation: 'ok' }], contradictions: [] });
const fcEnvelope = (draft, claims) =>
  JSON.stringify({ gate: 'fact_check', claims: claims.map((c, i) => ({ id: i + 1, claim: c })), rendered_content: draft, source_urls: ['https://e.com'] });

let idn = 0;
const nextId = () => `rt${++idn}`;

// Run a claims turn through a sandboxed flow: optional fact-check dispatch, then
// emit. Returns the gate's message result.
const claimsFlow = async (draft, claims, verifierOutput) => {
  await setPrompt('[[FLOW:resume]] continue the lesson');
  const env = fcEnvelope(draft, claims);
  const id = nextId();
  await dispatch('fact-check', env, id);
  await fg(id, 'fact-check', env, verifierOutput);
  return await msg(`[[TURN:claims]]\n${draft}`);
};

let caught = 0;
const total = 5;
const report = (name, ok) => {
  console.log((ok ? 'PASS ' : 'FAIL ') + name);
  return ok;
};
const reportError = (name, ok) => {
  if (report(name, ok)) caught++;
};

// ---------------------------------------------------------------------------
// Seeded errors — each must be caught.
// ---------------------------------------------------------------------------

// 1. Wrong numeric claim whose hard fact the generator never listed.
{
  const draft = 'The treatment effect is 2.7 points and the sample size is 480.';
  const r = await claimsFlow(draft, ['the treatment effect is 2.7 points'], FC_PASS);
  reportError('redteam: unlisted decimal caught as CLAIMS_INCOMPLETE', blocked(r, 'CLAIMS_INCOMPLETE'));
}

// 2. Wrong formula (LaTeX) the generator never placed before the verifier.
{
  const draft = 'By definition $E = mc^2$ and the entropy is $H = -\\sum p \\log p$.';
  const r = await claimsFlow(draft, ['the entropy is $H = -\\sum p \\log p$'], FC_PASS);
  reportError('redteam: unlisted LaTeX formula caught as CLAIMS_INCOMPLETE', blocked(r, 'CLAIMS_INCOMPLETE'));
}

// 3. Wrong attribution the verifier flags (the ISSUES path).
{
  const draft = 'The backpropagation algorithm was invented by Alan Turing in 1950.';
  const issues = JSON.stringify({ verdicts: [{ id: 1, verdict: 'ISSUES', explanation: 'misattribution', corrected_claim: 'popularised by Rumelhart, Hinton & Williams' }], contradictions: [] });
  const r = await claimsFlow(draft, ['the algorithm was invented by Alan Turing in 1950'], issues);
  reportError('redteam: verifier-flagged wrong attribution caught as FACT_CHECK_ISSUES', blocked(r, 'FACT_CHECK_ISSUES'));
}

// 4. Wrong percentage never listed.
{
  const draft = 'The false-positive rate is 12% under the default threshold.';
  const r = await claimsFlow(draft, ['the false-positive rate is high'], FC_PASS);
  reportError('redteam: unlisted percentage caught as CLAIMS_INCOMPLETE', blocked(r, 'CLAIMS_INCOMPLETE'));
}

// 5. Wrong scientific-notation constant never listed.
{
  const draft = 'The speed of light is 3.00e8 metres per second.';
  const r = await claimsFlow(draft, ['the speed of light is a large constant'], FC_PASS);
  reportError('redteam: unlisted scientific notation caught as CLAIMS_INCOMPLETE', blocked(r, 'CLAIMS_INCOMPLETE'));
}

// ---------------------------------------------------------------------------
// Clean controls — the gate must not false-block correct, fully-listed drafts.
// ---------------------------------------------------------------------------
const controls = [
  {
    name: 'redteam: clean draft with every hard fact listed renders',
    draft: 'The explained variance is 4.98 on both arms (n=200).',
    claims: ['the explained variance is 4.98', 'the sample size is n=200'],
  },
  {
    name: 'redteam: clean prose with no hard facts renders',
    draft: 'Entropy is the average surprise of a distribution.',
    claims: ['entropy is the average surprise of a distribution'],
  },
];
let controlsOk = 0;
for (const c of controls) {
  const r = await claimsFlow(c.draft, c.claims, FC_PASS);
  const ok = allowed(r);
  report(c.name, ok);
  if (ok) controlsOk++;
}

console.log(`REDTEAM: caught ${caught}/${total} seeded errors; clean controls ${controlsOk}/${controls.length}`);
