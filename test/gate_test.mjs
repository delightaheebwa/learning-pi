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
