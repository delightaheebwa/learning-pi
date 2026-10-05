/**
 * pi-adapter — the ONLY version-aware file of the learning gate.
 *
 * It translates pi and pi-subagents wire shapes into the normalized inputs the
 * pure engine (../gate-core/engine.ts) consumes, and it builds the model judge
 * and the on-disk ledger from the live pi context. When no judge model is
 * configured (or authentication is missing) the engine runs its legacy
 * deterministic path unchanged.
 *
 * Sources of coupled knowledge:
 *   - the pi ExtensionAPI and its event names
 *   - the pi message content shape passed through to gate-core
 *   - pi-subagents' `subagent` tool input shapes (single / chain / workflow)
 *   - pi-subagents' `tool_result.details.results` shape (agent/finalOutput/task)
 *   - pi-subagents' async completion notification text and run-id URLs
 *   - ctx.modelRegistry (the judge model) and the agent dir (the ledger)
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { appendFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { createGate, type BlockResult, type GateEngine, type MessageEndResult } from "../gate-core/engine.ts";
import { parseTask, type CallRef } from "../gate-core/primitives.ts";
import {
  createModelJudge,
  createRouterJudge,
  type CompleteFn,
  type Judge,
} from "../gate-core/judge/index.ts";
import { createLedger, type AppendFn } from "../gate-core/ledger.ts";
import type { Ledger } from "../gate-core/judge/types.ts";

/**
 * pi-subagents' structured delegation events. Another extension asks
 * pi-subagents to run one configured foreground leaf agent by emitting the
 * request event and awaiting the response event (docs/extension-api.md
 * "Structured delegation API" in pi-subagents 0.74). The names are stable
 * public API but are pinned here, in the adapter, so a package rename is a
 * one-file fix. The `subagent` tool is `exposure: "model-only"`, so this event
 * bridge is the only way another extension may launch a child.
 */
const DELEGATION_REQUEST_EVENT = "prompt-template:subagent:request";
const DELEGATION_STARTED_EVENT = "prompt-template:subagent:started";
const DELEGATION_RESPONSE_EVENT = "prompt-template:subagent:response";
const DELEGATION_CANCEL_EVENT = "prompt-template:subagent:cancel";
const THINKING_LEVELS = new Set(["off", "minimal", "low", "medium", "high", "xhigh", "max"]);

/**
 * JSON-Schema params for the `dispatch` tool. Kept as a plain schema (not a
 * `typebox` `Type.Object`) so the extension module graph loads under the
 * offline `deno` gate tests, which cannot resolve pi's bundled `typebox`.
 * pi validates plain JSON schemas through its ajv path.
 */
const DISPATCH_PARAMS = {
  type: "object",
  properties: {
    agent: {
      type: "string",
      description:
        "verifier/worker agent name: fact-check, quiz-audit, grade-audit, tutor-audit, viz, viz-audit, scout, clerk, review-scout, review-clerk, review-gate, review-session-audit",
    },
    task: {
      description: "the JSON envelope object (or a plain string task). NOT a JSON-encoded string.",
    },
    model: { type: "string", description: "override the child model (provider/id)" },
    thinking: { type: "string", description: "override the child thinking level" },
  },
  required: ["agent", "task"],
  additionalProperties: false,
};

/** Source inside the balanced `(`…`)` pair whose opening paren sits at `openIdx`. */
function sliceBalanced(text: string, openIdx: number): string | undefined {
  const open = text[openIdx];
  const close = open === "(" ? ")" : open === "[" ? "]" : open === "{" ? "}" : "";
  if (!close) return undefined;
  let depth = 0;
  let quote = "";
  let esc = false;
  for (let i = openIdx; i < text.length; i++) {
    const ch = text[i];
    if (quote) {
      if (esc) esc = false;
      else if (ch === "\\") esc = true;
      else if (ch === quote) quote = "";
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") {
      quote = ch;
      continue;
    }
    if (ch === open) depth++;
    else if (ch === close) {
      depth--;
      if (depth === 0) return text.slice(openIdx + 1, i);
    }
  }
  return undefined;
}

/**
 * Agent names launched by a pi-subagents workflow script (`runs.run(key, …)` /
 * `runs.all([…])`). Only these names are needed at dispatch time — the caps and
 * the scout/clerk flags — because the tool result carries each child's envelope
 * and output structurally in `details.results`. The scan is fenced to the
 * `runs.run`/`runs.all` argument lists so an `agent:` word inside a task string
 * cannot inject a phantom child.
 */
export function workflowScriptAgents(script: string): string[] {
  const agents: string[] = [];
  const callRe = /\bruns\s*\.\s*(?:run|all)\s*\(/g;
  let call: RegExpExecArray | null;
  while ((call = callRe.exec(script))) {
    const paren = script.indexOf("(", call.index);
    const body = paren >= 0 ? sliceBalanced(script, paren) : undefined;
    if (!body) continue;
    const agentRe = /\bagent\s*:\s*(["'`])([\w.-]+)\1/g;
    let m: RegExpExecArray | null;
    while ((m = agentRe.exec(body))) agents.push(m[2]);
  }
  return agents;
}

/**
 * Child calls behind a `subagent` tool_call input. Handles the legacy
 * single/chain/tasks shapes and pi-subagents >= 0.68 workflow scripts.
 * Management actions (validate/status/list/…) launch nothing and are ignored.
 */
export function subagentCalls(input: any): CallRef[] {
  const out: CallRef[] = [];
  const push = (agent: any, task: any) => {
    if (typeof agent !== "string") return;
    const env = parseTask(task);
    out.push({ agent, envelope: env, gate: env && typeof env.gate === "string" ? env.gate : undefined });
  };
  if (!input || typeof input !== "object") return out;
  if (typeof input.agent === "string") push(input.agent, input.task);
  for (const key of ["tasks", "chain", "calls", "subagents"]) {
    const arr = (input as any)[key];
    if (Array.isArray(arr)) for (const t of arr) push(t?.agent, t?.task);
  }
  if (input.action === undefined && typeof input.workflowScript === "string") {
    for (const agent of workflowScriptAgents(input.workflowScript)) out.push({ agent });
  }
  return out;
}

/**
 * Resolve the child calls behind a `subagent` tool result.
 *
 * pi-subagents >= 0.68 reports workflow children structurally in
 * `details.results` (`agent`, `finalOutput`), but it **compacts completed
 * foreground results before the extension sees them**: `task` is rewritten to
 * `[prompt redacted]` and `messages` are dropped. The dispatch envelope
 * (which carries `rendered_content` / `questions_json` / grade text) therefore
 * cannot be parsed back out of `r.task`, and a receipt minted without it can
 * never bind. Recover the envelope from the calls captured at `tool_call` time,
 * matched per agent in dispatch order so a parallel same-agent fan-out stays
 * aligned. Fall back to the calls captured from the request input for legacy
 * single/chain shapes and async fan-out notices.
 */
export function resultCalls(event: any, text: string, pending: CallRef[]): CallRef[] {
  const results = event?.details?.results;
  if (Array.isArray(results) && results.length > 0) {
    const out: CallRef[] = [];
    const pendingByAgent = new Map<string, CallRef[]>();
    for (const c of pending) {
      const q = pendingByAgent.get(c.agent) || [];
      q.push(c);
      pendingByAgent.set(c.agent, q);
    }
    for (const r of results) {
      if (!r || typeof r.agent !== "string") continue;
      const finalOutput = typeof r.finalOutput === "string" ? r.finalOutput : undefined;
      if (!finalOutput) continue; // async/pending child — the notify fallback mints it
      const queued = pendingByAgent.get(r.agent)?.shift();
      const env = parseTask(r.task) ?? queued?.envelope;
      out.push({
        agent: r.agent,
        envelope: env,
        gate: env && typeof env.gate === "string" ? env.gate : undefined,
        output: finalOutput,
      });
    }
    if (out.length > 0) return out;
  }
  return pending.map((c) => ({ ...c, output: text }));
}

/** Text of a pi message/event, tolerating string content, parts, or details. */
export function resultText(ev: any): string {
  const c = ev?.content;
  if (typeof c === "string") return c;
  if (Array.isArray(c)) {
    return c
      .map((p: any) => (typeof p === "string" ? p : p && typeof p.text === "string" ? p.text : ""))
      .join("\n");
  }
  if (ev?.details) {
    try {
      return JSON.stringify(ev.details);
    } catch {
      return "";
    }
  }
  return "";
}

/** Async run id from a pi-subagents completion notification URL. */
export function extractAsyncRunId(text: string): string | undefined {
  const m = text.match(/async-subagent-(?:runs|results)(?:\/output-archives)?\/([0-9a-fA-F-]{36})/);
  return m ? m[1] : undefined;
}

const NOTIFY_HEADER_RE = /(?:Background task|Detached foreground task) completed:\s*\*\*([\w-]+)\*\*/i;
const NOTIFY_FAIL_RE = /(?:Background task|Detached foreground task) failed:\s*\*\*([\w-]+)\*\*/i;

const DEFAULT_JUDGE_MODEL = "gemini/gemini-3.5-flash-lite";
const DEFAULT_JUDGE_ESCALATION_MODEL = "gemini/gemini-3.5-flash";

/** Text parts of a modelRegistry.complete response, tolerating shape drift. */
function responseText(response: any): string {
  if (typeof response === "string") return response;
  const content = response?.content;
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    const parts = content
      .map((c: any) => (c && typeof c.text === "string" ? c.text : typeof c === "string" ? c : ""))
      .filter((s: string) => s.length > 0);
    if (parts.length > 0) return parts.join("\n");
  }
  if (typeof response?.text === "string") return response.text;
  return "";
}

/** Best-effort on-disk ledger under the pi agent dir. Returns NOOP on failure. */
function makeFileLedger(): Ledger {
  try {
    const dir = process.env.LEARNING_GATE_LEDGER_DIR || join(homedir(), ".pi", "agent", "learning-gate");
    mkdirSync(dir, { recursive: true });
    const append: AppendFn = (stream, line) => {
      try {
        appendFileSync(join(dir, `${stream}.ndjson`), line);
      } catch {
        /* best effort */
      }
    };
    return createLedger(append);
  } catch {
    return createLedger(() => {});
  }
}

/** Split a "provider/model" id and resolve it against the live model registry. */
function resolveModel(registry: any, configured: string): any | undefined {
  if (!registry?.find) return undefined;
  const slash = configured.indexOf("/");
  const provider = slash > 0 ? configured.slice(0, slash) : "google";
  const modelId = slash > 0 ? configured.slice(slash + 1) : configured;
  const model = registry.find(provider, modelId);
  if (!model) return undefined;
  if (typeof registry.hasConfiguredAuth === "function" && !registry.hasConfiguredAuth(model)) return undefined;
  return model;
}

/** A `complete` function that calls one resolved model through pi. */
function makeComplete(registry: any, model: any): CompleteFn {
  return async ({ system, user, maxTokens }) => {
    const sessionId =
      (globalThis as any).crypto?.randomUUID?.() ?? `gate-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const response = await registry.complete(
      model,
      {
        messages: [
          {
            role: "user",
            content: [{ type: "text", text: `${system}\n\n${user}` }],
            timestamp: Date.now(),
          },
        ],
      },
      { maxTokens: maxTokens ?? 4096, cacheRetention: "none", sessionId }
    );
    const text = responseText(response);
    if (!text.trim()) {
      throw new Error(`judge returned no text (raw=${JSON.stringify(response).slice(0, 900)})`);
    }
    return text;
  };
}

export default function learningGate(pi: ExtensionAPI): void {
  let engine: GateEngine | undefined;
  let judgeUnavailableNotified = false;
  // toolCallId -> child calls captured at dispatch. Needed to recover the
  // dispatch envelope when pi-subagents redacts `task` on the result.
  const pendingCalls = new Map<string, CallRef[]>();

  const buildJudge = (ctx: any): Judge | undefined => {
    try {
      const registry = ctx?.modelRegistry;
      const primaryModel = resolveModel(registry, process.env.LEARNING_GATE_JUDGE_MODEL || DEFAULT_JUDGE_MODEL);
      if (!primaryModel) return undefined;
      const primary = createModelJudge(makeComplete(registry, primaryModel));

      // Escalation model (hard cases + primary outage). Optional: if it is not
      // configured, the router runs primary-only.
      let escalate: Judge | undefined;
      try {
        const escModel = resolveModel(
          registry,
          process.env.LEARNING_GATE_JUDGE_ESCALATION_MODEL || DEFAULT_JUDGE_ESCALATION_MODEL
        );
        if (escModel) escalate = createModelJudge(makeComplete(registry, escModel));
      } catch {
        escalate = undefined;
      }

      const maxPerDay = Number(process.env.LEARNING_GATE_JUDGE_MAX_PER_DAY || 450);
      const maxEscalations = Number(process.env.LEARNING_GATE_JUDGE_ESCALATION_MAX_PER_DAY || 20);
      return createRouterJudge(primary, { maxCallsPerDay: maxPerDay, escalate, maxEscalationsPerDay: maxEscalations });
    } catch {
      return undefined;
    }
  };

  const ensureEngine = (ctx: any): GateEngine => {
    if (engine) return engine;
    const judge = buildJudge(ctx);
    engine = createGate({ judge, ledger: judge ? makeFileLedger() : undefined });
    if (!judge && ctx?.hasUI && !judgeUnavailableNotified) {
      judgeUnavailableNotified = true;
      try {
        ctx.ui?.notify?.(
          "learning-gate: no judge model configured; running legacy deterministic checks.",
          "info"
        );
      } catch {
        /* ignore */
      }
    }
    return engine;
  };

  // --- dispatch helper ------------------------------------------------------
  // pi-subagents declares `subagent` as `exposure: "model-only"` (no
  // `ctx.executeTool`), so the structured delegation event bridge is the only
  // way another extension may launch a child. The `subagent` tool also requires
  // `task` to be a JSON *string*; flash models emit it as an object and then
  // dead-end retrying (2026-10-05 resume session). `dispatch` takes the envelope
  // as an object, stringifies it once here (no escaping by the model), and
  // mints the gate receipt itself.
  const ownerRunId =
    (globalThis as any).crypto?.randomUUID?.() ?? `dispatch-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const delegationWaiters = new Map<string, { resolve: (payload: any) => void; onStarted: () => void }>();
  try {
    pi.events?.on?.(DELEGATION_STARTED_EVENT, (payload: any) => {
      delegationWaiters.get(payload?.requestId)?.onStarted();
    });
    pi.events?.on?.(DELEGATION_RESPONSE_EVENT, (payload: any) => {
      delegationWaiters.get(payload?.requestId)?.resolve(payload);
    });
  } catch {
    /* events unavailable — dispatch will time out with a clear message */
  }

  const runDelegation = (request: any, signal: any): Promise<any> =>
    new Promise((resolve, reject) => {
      let settled = false;
      let startTimer: any;
      let overallTimer: any;
      const cleanup = () => {
        clearTimeout(startTimer);
        clearTimeout(overallTimer);
        delegationWaiters.delete(request.requestId);
        try {
          signal?.removeEventListener?.("abort", onAbort);
        } catch {
          /* ignore */
        }
      };
      const finish = (fn: (v: any) => void, value: any) => {
        if (settled) return;
        settled = true;
        cleanup();
        fn(value);
      };
      const cancel = () => {
        try {
          pi.events?.emit?.(DELEGATION_CANCEL_EVENT, {
            requestId: request.requestId,
            ownerRunId: request.ownerRunId,
            nodeId: request.nodeId,
          });
        } catch {
          /* ignore */
        }
      };
      const onAbort = () => {
        cancel();
        finish(reject, new Error(`dispatch of ${request.agent} was cancelled`));
      };
      delegationWaiters.set(request.requestId, {
        resolve: (payload) => finish(resolve, payload),
        onStarted: () => clearTimeout(startTimer),
      });
      if (signal?.aborted) {
        onAbort();
        return;
      }
      try {
        signal?.addEventListener?.("abort", onAbort, { once: true });
      } catch {
        /* ignore */
      }
      // pi-subagents emits `started` synchronously once the bridge owns the
      // request; no start means the package is not loaded or not active.
      startTimer = setTimeout(() => {
        finish(
          reject,
          new Error("dispatch: pi-subagents structured delegation did not start — is pi-subagents loaded?")
        );
      }, 20_000);
      overallTimer = setTimeout(() => {
        cancel();
        finish(reject, new Error(`dispatch of ${request.agent} timed out after 30 minutes`));
      }, 30 * 60 * 1000);
      try {
        pi.events?.emit?.(DELEGATION_REQUEST_EVENT, request);
      } catch (err) {
        finish(reject, err instanceof Error ? err : new Error(String(err)));
      }
    });

  const dispatchResult = (text: string, isError = false) => ({
    content: [{ type: "text" as const, text }],
    details: {},
    isError,
  });

  try {
    pi.registerTool({
      name: "dispatch",
      label: "Dispatch",
      description:
        "Run ONE learning-system subagent (verifier or worker) on a JSON envelope, foreground, and return its output. Use this instead of `subagent`: pass `task` as the envelope OBJECT, never a JSON-encoded string.",
      promptSnippet:
        "dispatch({ agent, task }) — run a learning-system verifier/worker with its JSON envelope object.",
      promptGuidelines: [
        "Use dispatch (not subagent) for every learning-system verifier or worker; `task` is the envelope object, not a stringified JSON.",
      ],
      parameters: DISPATCH_PARAMS,
      async execute(toolCallId: string, params: any, signal: any, _onUpdate: any, ctx: any) {
        const agent = typeof params?.agent === "string" ? params.agent.trim() : "";
        if (!agent) return dispatchResult("dispatch requires a non-empty `agent`.", true);
        const raw = params?.task;
        let taskString: string;
        if (typeof raw === "string") taskString = raw;
        else if (raw === undefined || raw === null) taskString = "";
        else {
          try {
            taskString = JSON.stringify(raw);
          } catch {
            return dispatchResult("dispatch `task` is not JSON-serializable.", true);
          }
        }
        if (!taskString.trim()) return dispatchResult("dispatch requires a non-empty `task` (the JSON envelope).", true);

        const calls = subagentCalls({ agent, task: taskString });
        const g = ensureEngine(ctx);
        // Run the engine's subagent bookkeeping (dispatch caps, the duplicate
        // fact-check guard) before launching the child.
        const guard = g.onToolCall({
          tool: "subagent",
          input: { agent, task: taskString },
          calls,
          agentless: false,
          toolCallId,
        });
        if (guard?.block) return dispatchResult(guard.reason, true);

        const uuid = () =>
          (globalThis as any).crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`;
        const request: any = {
          requestId: uuid(),
          ownerRunId,
          nodeId: uuid(),
          agent,
          task: taskString,
          context: "fresh",
          cwd: typeof ctx?.cwd === "string" && ctx.cwd ? ctx.cwd : process.cwd(),
          result: { kind: "text" },
        };
        if (typeof params?.model === "string" && params.model.trim()) request.model = params.model.trim();
        if (typeof params?.thinking === "string" && THINKING_LEVELS.has(params.thinking)) request.thinking = params.thinking;

        let output = "";
        let isError = false;
        let status = "failed";
        let runId: string | undefined;
        let exitCode: number | undefined;
        try {
          const resp = await runDelegation(request, signal);
          runId = typeof resp?.runId === "string" ? resp.runId : undefined;
          status = typeof resp?.status === "string" ? resp.status : "failed";
          if (typeof resp?.exitCode === "number") exitCode = resp.exitCode;
          if (status === "completed" && resp?.result?.kind === "text") {
            output = resp.result.text;
          } else {
            isError = true;
            output = resp?.error || `dispatch ${agent}: ${status}`;
          }
        } catch (err) {
          isError = true;
          output = err instanceof Error ? err.message : String(err);
        }
        // The child ran through the delegation bridge (no model-issued
        // `subagent` call), so mint the gate receipt here.
        g.onToolResult({
          tool: "subagent",
          toolCallId,
          isError,
          text: output,
          dispatchCalls: calls,
          mintCalls: calls.map((c) => ({ ...c, output })),
        });
        return {
          content: [{ type: "text" as const, text: output }],
          details: { agent, mode: "single", runId, status, ...(exitCode !== undefined ? { exitCode } : {}) },
          isError,
        };
      },
    });
  } catch {
    /* tool registration failure must not take down the gate */
  }

  pi.on("before_agent_start", async (event: any, ctx: any) => {
    ensureEngine(ctx).onBeforeAgentStart(event?.prompt);
  });

  pi.on("tool_call", async (event: any, ctx: any): Promise<BlockResult | undefined> => {
    const g = ensureEngine(ctx);
    const tool = typeof event?.toolName === "string" ? event.toolName : "";
    if (tool.toLowerCase() === "subagent") {
      const input = event?.input;
      const calls = subagentCalls(input);
      // A verifier/worker dispatch belongs on `dispatch`, which takes the
      // envelope as an object. The legacy workflow/args forms launch no child
      // and the 2026-10-05 resume session dead-ended flailing through them.
      if (
        calls.length === 0 &&
        input &&
        typeof input === "object" &&
        (input.workflow !== undefined || input.args !== undefined)
      ) {
        return {
          block: true,
          reason:
            'To dispatch a learning-system verifier/worker, use `dispatch({ agent: "quiz-audit", task: { "gate": "quiz_audit", ... } })` with the envelope as an OBJECT. Do not use `subagent`, `workflow`, or `args`.',
        };
      }
      const agentless = !!(input && typeof input === "object" && ("task" in input || "prompt" in input));
      const res = g.onToolCall({ tool, input, calls, agentless, toolCallId: event?.toolCallId });
      if (!res?.block && event?.toolCallId) pendingCalls.set(event.toolCallId, calls);
      return res;
    }
    return g.onToolCall({ tool, input: event?.input, calls: [], agentless: false, toolCallId: event?.toolCallId });
  });

  pi.on("tool_result", async (event: any, ctx: any) => {
    const g = ensureEngine(ctx);
    const tool = typeof event?.toolName === "string" ? event.toolName : "";
    const text = resultText(event);
    let dispatchCalls: CallRef[] = [];
    let mintCalls: CallRef[] = [];
    let asyncId: string | undefined;
    if (tool.toLowerCase() === "subagent") {
      dispatchCalls = (event?.toolCallId && pendingCalls.get(event.toolCallId)) || [];
      if (event?.toolCallId) pendingCalls.delete(event.toolCallId);
      asyncId = typeof event?.details?.asyncId === "string" ? event.details.asyncId : undefined;
      mintCalls = resultCalls(event, text, dispatchCalls);
    }
    g.onToolResult({ tool, toolCallId: event?.toolCallId, isError: event?.isError === true, text, asyncId, dispatchCalls, mintCalls });
  });

  pi.on("message_end", async (event: any, ctx: any): Promise<MessageEndResult | undefined> => {
    const g = ensureEngine(ctx);
    const message = event?.message;
    if (message?.role === "custom") {
      try {
        const text = resultText(message);
        g.onCustomMessage({
          text,
          agent: text.match(NOTIFY_HEADER_RE)?.[1]?.toLowerCase(),
          failedAgent: text.match(NOTIFY_FAIL_RE)?.[1]?.toLowerCase(),
          runId: extractAsyncRunId(text),
        });
      } catch {
        /* fail open */
      }
      return;
    }
    const res = await g.onMessageEnd({ message });
    if (res?.notify) {
      try {
        ctx?.ui?.notify?.(res.notify, "warning");
      } catch {
        /* ignore */
      }
    }
    if (res && res.message !== undefined) return { message: res.message };
    return;
  });
}
