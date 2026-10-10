// Test for the opt-in judge raw-exchange dump (pi-adapter makeJudgeDump).
//
//   deno run --allow-all test/judge_dump_test.mjs
//
// When a gate block is not obvious from the decisions ledger, setting
// LEARNING_GATE_JUDGE_DUMP captures the exact package the engine sent the judge
// and the model's raw response, so the binding/substantiveness that produced the
// block can be replayed. It is off by default and must never change behavior.
const pass = (n, c) => console.log((c ? 'PASS ' : 'FAIL ') + n);
const includes = (hay, needle) => typeof hay === 'string' && hay.includes(needle);

const tmp = '/tmp/learning-gate-judge-dump-test';
try { Deno.removeSync(tmp, { recursive: true }); } catch { /* fresh */ }
Deno.mkdirSync(tmp, { recursive: true, mode: 0o700 });
process.env.LEARNING_GATE_LEDGER_DIR = tmp;
process.env.LEARNING_GATE_JUDGE_DUMP = '1';

const handlers = {};
const pi = { on: (ev, h) => { (handlers[ev] ||= []).push(h); }, events: { on: () => () => {} } };

const JUDGE_JSON = JSON.stringify({
  turnType: 'none',
  summaryKind: 'transition',
  bindings: [],
  substantiveness: [],
  bestReceipt: -1,
  remedy: '',
  reason: 'dump test',
});
// A fake registry that resolves the configured judge model and answers with a
// well-formed assessment, so the adapter's judge path runs end-to-end.
const registry = {
  find: (provider, id) => ({ provider, id }),
  hasConfiguredAuth: () => true,
  complete: async () => ({ content: [{ type: 'text', text: JUDGE_JSON }] }),
};

const mod = await import('../.pi/extensions/learning-gate/index.ts');
mod.default(pi);
const fire = async (ev, e) => {
  let r;
  for (const h of handlers[ev] || []) r = await h(e, { ui: { notify() {} }, modelRegistry: registry });
  return r;
};

await fire('before_agent_start', { prompt: '[[FLOW:resume]] continue the lesson' });
await fire('message_end', { message: { role: 'assistant', content: [{ type: 'text', text: 'A transition turn.' }], stopReason: 'stop' } });

const dumpPath = `${tmp}/judge-raw.ndjson`;
const lines = Deno.readTextFileSync(dumpPath).trim().split('\n').filter(Boolean);
pass('one judge call is dumped', lines.length === 1);
const entry = JSON.parse(lines[0]);
pass('dump entry names the judge model', entry.model === 'primary');
pass('dump entry carries the serialized package', includes(entry.user, 'JUDGE PACKAGE:'));
pass('dump entry carries the raw response', includes(entry.response, '"turnType"'));
pass('dump entry carries a timestamp', !!entry.at);
