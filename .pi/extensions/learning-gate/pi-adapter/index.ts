/**
 * pi-adapter — the ONLY version-aware file of the learning gate.
 *
 * It translates pi and pi-subagents wire shapes into the normalized inputs the
 * pure engine (../gate-core/engine.ts) consumes. When pi renames an event, a
 * field, or changes how a subagent result is reported, this file is the only
 * one that should need to change. Everything else is version-agnostic.
 *
 * Sources of coupled knowledge:
 *   - the pi ExtensionAPI and its event names
 *   - the pi message content shape passed through to gate-core
 *   - pi-subagents' `subagent` tool input shapes (single / chain / workflow)
 *   - pi-subagents' `tool_result.details.results` shape (agent/finalOutput/task)
 *   - pi-subagents' async completion notification text and run-id URLs
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { createGate, type BlockResult, type MessageEndResult } from "../gate-core/engine.ts";
import { parseTask, type CallRef } from "../gate-core/primitives.ts";

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
      // Consume the queued call for this agent even when `r.task` parsed, so the
      // per-agent queues stay aligned across a multi-result fan-out.
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

export default function learningGate(pi: ExtensionAPI): void {
  const engine = createGate();
  // toolCallId -> child calls captured at dispatch. Needed to recover the
  // dispatch envelope when pi-subagents redacts `task` on the result.
  const pendingCalls = new Map<string, CallRef[]>();

  pi.on("before_agent_start", async (event: any) => {
    engine.onBeforeAgentStart(event?.prompt);
  });

  pi.on("tool_call", async (event: any): Promise<BlockResult | undefined> => {
    const tool = typeof event?.toolName === "string" ? event.toolName : "";
    if (tool.toLowerCase() === "subagent") {
      const input = event?.input;
      const calls = subagentCalls(input);
      const agentless = !!(input && typeof input === "object" && ("task" in input || "prompt" in input));
      const res = engine.onToolCall({ tool, input, calls, agentless, toolCallId: event?.toolCallId });
      if (!res?.block && event?.toolCallId) pendingCalls.set(event.toolCallId, calls);
      return res;
    }
    return engine.onToolCall({ tool, input: event?.input, calls: [], agentless: false, toolCallId: event?.toolCallId });
  });

  pi.on("tool_result", async (event: any) => {
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
    engine.onToolResult({ tool, toolCallId: event?.toolCallId, isError: event?.isError === true, text, asyncId, dispatchCalls, mintCalls });
  });

  pi.on("message_end", async (event: any, ctx: any): Promise<MessageEndResult | undefined> => {
    const message = event?.message;
    if (message?.role === "custom") {
      try {
        const text = resultText(message);
        engine.onCustomMessage({
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
    const res = engine.onMessageEnd({ message });
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
