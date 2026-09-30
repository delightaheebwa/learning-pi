/**
 * spec — the declarative visualization spec: schema, validator, canonical form,
 * fence extraction, and parameter/formula sampling.
 *
 * PURE: no pi imports, no I/O. Everything here is unit-testable under deno and
 * is shared by the renderer, the interactive explorer, and the gate's
 * deterministic pre-checks (the gate keeps its own copy of the tiny helpers so
 * it stays self-contained; keep the canonical-JSON rule in sync).
 */
import { compileExpr, validateExpr } from "./expr.ts";

export type VizKind = "line" | "scatter" | "bar" | "table" | "diagram";

export interface VizPoint {
  x: number;
  y: number;
}

export interface VizSeries {
  name?: string;
  points: VizPoint[];
}

export interface VizBar {
  label: string;
  value: number;
}

export interface VizNode {
  id: string;
  label?: string;
}

export interface VizEdge {
  from: string;
  to: string;
  label?: string;
}

export interface VizAnnotation {
  text: string;
  x?: number;
  y?: number;
}

export interface VizParam {
  name: string;
  min: number;
  max: number;
  step: number;
  value: number;
}

export interface VizFormula {
  expr: string;
  xMin: number;
  xMax: number;
  samples?: number;
}

export interface VizFrame {
  caption?: string;
  spec: VizSpec;
}

export interface VizSpec {
  viz: "1";
  kind: VizKind;
  title?: string;
  xLabel?: string;
  yLabel?: string;
  series?: VizSeries[];
  bars?: VizBar[];
  columns?: string[];
  rows?: (string | number)[][];
  nodes?: VizNode[];
  edges?: VizEdge[];
  annotations?: VizAnnotation[];
  params?: VizParam[];
  formula?: VizFormula;
  frames?: VizFrame[];
  caption?: string;
  /** Optional hand-tuned Unicode fallback; used verbatim when render fails. */
  ascii?: string;
}

export const VIZ_KINDS: readonly VizKind[] = ["line", "scatter", "bar", "table", "diagram"];

// Hard caps so a malformed/huge spec cannot hang a render or blow up context.
export const LIMITS = {
  series: 12,
  pointsPerSeries: 500,
  bars: 40,
  columns: 12,
  rows: 60,
  nodes: 40,
  edges: 80,
  annotations: 20,
  params: 8,
  frames: 64,
  samples: 400,
};

export interface ValidateOk {
  ok: true;
  spec: VizSpec;
}
export interface ValidateErr {
  ok: false;
  errors: string[];
}
export type ValidateResult = ValidateOk | ValidateErr;

const isObj = (v: unknown): v is Record<string, unknown> =>
  typeof v === "object" && v !== null && !Array.isArray(v);
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const str = (v: unknown): v is string => typeof v === "string";

function validateSeries(s: unknown, errors: string[], path: string): s is VizSeries {
  if (!isObj(s)) {
    errors.push(`${path}: series entry must be an object`);
    return false;
  }
  if (!Array.isArray(s.points) || s.points.length === 0) {
    errors.push(`${path}: series needs a non-empty points[]`);
    return false;
  }
  if (s.points.length > LIMITS.pointsPerSeries) {
    errors.push(`${path}: too many points (${s.points.length} > ${LIMITS.pointsPerSeries})`);
    return false;
  }
  for (let i = 0; i < s.points.length; i++) {
    const p: any = s.points[i];
    const pair = Array.isArray(p) && p.length >= 2 && finite(p[0]) && finite(p[1]);
    const obj = isObj(p) && finite(p.x) && finite(p.y);
    if (!pair && !obj) {
      errors.push(`${path}: point ${i} must be [x,y] or {x,y} with finite values`);
      return false;
    }
    // Normalize to {x,y} in place so the renderer has one shape.
    s.points[i] = pair ? { x: p[0], y: p[1] } : { x: p.x, y: p.y };
  }
  if (s.name !== undefined && !str(s.name)) {
    errors.push(`${path}: series name must be a string`);
    return false;
  }
  return true;
}

/**
 * Validate a viz spec. Returns the normalized spec (typed) or a list of
 * human-readable errors. Length caps are enforced so the renderer and the
 * agent stay bounded.
 */
export function validateSpec(input: unknown): ValidateResult {
  const errors: string[] = [];
  if (!isObj(input)) return { ok: false, errors: ["spec must be a JSON object"] };
  if (input.viz !== "1") errors.push("spec.viz must be the string \"1\"");
  const kind = input.kind;
  if (!str(kind) || !VIZ_KINDS.includes(kind as VizKind)) {
    errors.push(`spec.kind must be one of: ${VIZ_KINDS.join(", ")}`);
    return { ok: false, errors };
  }
  const k = kind as VizKind;
  // A frames/steps spec carries its data inside each frame's `spec`; the
  // top-level kind is just a container, so its data fields are not required.
  const hasFrames = Array.isArray(input.frames) && input.frames.length > 0;

  if (input.title !== undefined && !str(input.title)) errors.push("spec.title must be a string");
  if (input.caption !== undefined && !str(input.caption)) errors.push("spec.caption must be a string");

  const params: VizParam[] = [];
  if (input.params !== undefined) {
    if (!Array.isArray(input.params)) errors.push("spec.params must be an array");
    else if (input.params.length > LIMITS.params) errors.push(`spec.params too long (>${LIMITS.params})`);
    else
      for (let i = 0; i < input.params.length; i++) {
        const p = input.params[i] as any;
        const path = `spec.params[${i}]`;
        if (!isObj(p) || !str(p.name) || !finite(p.min) || !finite(p.max) || !finite(p.step) || !finite(p.value)) {
          errors.push(`${path} must be {name:string,min,max,step,value:number}`);
          continue;
        }
        if (!(p.min < p.max)) errors.push(`${path}: min must be < max`);
        if (!(p.step > 0)) errors.push(`${path}: step must be > 0`);
        if (p.value < p.min || p.value > p.max) errors.push(`${path}: value must be within [min,max]`);
        params.push({ name: p.name, min: p.min, max: p.max, step: p.step, value: p.value });
      }
  }

  let formula: VizFormula | undefined;
  if (input.formula !== undefined) {
    const f = input.formula as any;
    if (!isObj(f) || !str(f.expr) || !finite(f.xMin) || !finite(f.xMax)) {
      errors.push("spec.formula must be {expr:string,xMin,xMax:number,samples?:number}");
    } else if (!(f.xMin < f.xMax)) {
      errors.push("spec.formula: xMin must be < xMax");
    } else {
      // `x` is the independent variable; parameters are the declared sliders.
      const exprErr = validateExpr(f.expr, ["x", ...params.map((p) => p.name)]);
      if (exprErr) errors.push(`spec.formula.expr: ${exprErr}`);
      const samples = f.samples === undefined ? 200 : f.samples;
      if (!finite(samples) || samples < 2 || samples > LIMITS.samples) {
        errors.push(`spec.formula.samples must be a number in [2,${LIMITS.samples}]`);
      }
      formula = { expr: f.expr, xMin: f.xMin, xMax: f.xMax, samples: Math.round(samples) };
    }
  }

  let series: VizSeries[] | undefined;
  if ((k === "line" || k === "scatter") && !hasFrames) {
    if (!formula) {
      if (!Array.isArray(input.series) || input.series.length === 0) {
        errors.push(`${k} needs a non-empty series[] or a formula`);
      } else if (input.series.length > LIMITS.series) {
        errors.push(`spec.series too long (>${LIMITS.series})`);
      } else {
        const out: VizSeries[] = [];
        for (let i = 0; i < input.series.length; i++) {
          if (validateSeries(input.series[i], errors, `spec.series[${i}]`)) out.push(input.series[i] as VizSeries);
        }
        if (out.length === input.series.length) series = out;
      }
    }
  }

  let bars: VizBar[] | undefined;
  if (k === "bar" && !hasFrames) {
    if (!Array.isArray(input.bars) || input.bars.length === 0) errors.push("bar needs a non-empty bars[]");
    else if (input.bars.length > LIMITS.bars) errors.push(`spec.bars too long (>${LIMITS.bars})`);
    else {
      const out: VizBar[] = [];
      for (let i = 0; i < input.bars.length; i++) {
        const b = input.bars[i] as any;
        if (!isObj(b) || !str(b.label) || !finite(b.value)) {
          errors.push(`spec.bars[${i}] must be {label:string,value:number}`);
          continue;
        }
        out.push({ label: b.label, value: b.value });
      }
      if (out.length === input.bars.length) bars = out;
    }
  }

  let columns: string[] | undefined;
  let rows: (string | number)[][] | undefined;
  if (k === "table" && !hasFrames) {
    if (!Array.isArray(input.columns) || input.columns.length === 0 || !input.columns.every(str)) {
      errors.push("table needs a non-empty columns[] of strings");
    } else if (input.columns.length > LIMITS.columns) {
      errors.push(`spec.columns too long (>${LIMITS.columns})`);
    } else {
      columns = input.columns as string[];
    }
    if (!Array.isArray(input.rows)) errors.push("table needs a rows[] array");
    else if (input.rows.length > LIMITS.rows) errors.push(`spec.rows too long (>${LIMITS.rows})`);
    else {
      const out: (string | number)[][] = [];
      let bad = false;
      for (let i = 0; i < input.rows.length; i++) {
        const r = input.rows[i];
        if (!Array.isArray(r) || !r.every((c) => str(c) || finite(c))) {
          errors.push(`spec.rows[${i}] must be an array of strings/numbers`);
          bad = true;
          continue;
        }
        out.push(r as (string | number)[]);
      }
      if (!bad) rows = out;
    }
  }

  let nodes: VizNode[] | undefined;
  let edges: VizEdge[] | undefined;
  if (k === "diagram" && !hasFrames) {
    if (!Array.isArray(input.nodes) || input.nodes.length === 0) errors.push("diagram needs a non-empty nodes[]");
    else if (input.nodes.length > LIMITS.nodes) errors.push(`spec.nodes too long (>${LIMITS.nodes})`);
    else {
      const out: VizNode[] = [];
      const ids = new Set<string>();
      let bad = false;
      for (let i = 0; i < input.nodes.length; i++) {
        const n = input.nodes[i] as any;
        if (!isObj(n) || !str(n.id)) {
          errors.push(`spec.nodes[${i}] must be {id:string,label?:string}`);
          bad = true;
          continue;
        }
        if (ids.has(n.id)) {
          errors.push(`spec.nodes[${i}]: duplicate id '${n.id}'`);
          bad = true;
          continue;
        }
        ids.add(n.id);
        out.push({ id: n.id, label: str(n.label) ? n.label : undefined });
      }
      if (!bad) nodes = out;
      if (Array.isArray(input.edges)) {
        if (input.edges.length > LIMITS.edges) errors.push(`spec.edges too long (>${LIMITS.edges})`);
        else {
          const eout: VizEdge[] = [];
          for (let i = 0; i < input.edges.length; i++) {
            const e = input.edges[i] as any;
            if (!isObj(e) || !str(e.from) || !str(e.to)) {
              errors.push(`spec.edges[${i}] must be {from:string,to:string,label?:string}`);
              continue;
            }
            if (!ids.has(e.from) || !ids.has(e.to)) {
              errors.push(`spec.edges[${i}] references an unknown node`);
              continue;
            }
            eout.push({ from: e.from, to: e.to, label: str(e.label) ? e.label : undefined });
          }
          edges = eout;
        }
      }
    }
  }

  const annotations: VizAnnotation[] = [];
  if (Array.isArray(input.annotations)) {
    if (input.annotations.length > LIMITS.annotations) errors.push(`spec.annotations too long (>${LIMITS.annotations})`);
    else
      for (let i = 0; i < input.annotations.length; i++) {
        const a = input.annotations[i] as any;
        if (!isObj(a) || !str(a.text)) {
          errors.push(`spec.annotations[${i}] must be {text:string,x?:number,y?:number}`);
          continue;
        }
        if (a.x !== undefined && !finite(a.x)) errors.push(`spec.annotations[${i}].x must be a number`);
        if (a.y !== undefined && !finite(a.y)) errors.push(`spec.annotations[${i}].y must be a number`);
        annotations.push({ text: a.text, x: finite(a.x) ? a.x : undefined, y: finite(a.y) ? a.y : undefined });
      }
  }

  let frames: VizFrame[] | undefined;
  if (input.frames !== undefined) {
    if (!Array.isArray(input.frames) || input.frames.length === 0) errors.push("spec.frames must be a non-empty array");
    else if (input.frames.length > LIMITS.frames) errors.push(`spec.frames too long (>${LIMITS.frames})`);
    else {
      const out: VizFrame[] = [];
      for (let i = 0; i < input.frames.length; i++) {
        const fr = input.frames[i] as any;
        if (!isObj(fr) || !isObj(fr.spec)) {
          errors.push(`spec.frames[${i}] must be {caption?:string,spec:{...}}`);
          continue;
        }
        const sub = validateSpec(fr.spec);
        if (!sub.ok) {
          errors.push(`spec.frames[${i}].spec: ${sub.errors.join("; ")}`);
          continue;
        }
        out.push({ caption: str(fr.caption) ? fr.caption : undefined, spec: sub.spec });
      }
      frames = out;
    }
  }

  if (input.ascii !== undefined && !str(input.ascii)) errors.push("spec.ascii must be a string");
  if (input.xLabel !== undefined && !str(input.xLabel)) errors.push("spec.xLabel must be a string");
  if (input.yLabel !== undefined && !str(input.yLabel)) errors.push("spec.yLabel must be a string");

  if (errors.length > 0) return { ok: false, errors };
  const spec: VizSpec = {
    viz: "1",
    kind: k,
    title: str(input.title) ? input.title : undefined,
    xLabel: str(input.xLabel) ? input.xLabel : undefined,
    yLabel: str(input.yLabel) ? input.yLabel : undefined,
    series,
    bars,
    columns,
    rows,
    nodes,
    edges,
    annotations,
    params,
    formula,
    frames,
    caption: str(input.caption) ? input.caption : undefined,
    ascii: str(input.ascii) ? input.ascii : undefined,
  };
  return { ok: true, spec };
}

/**
 * Canonical JSON: recursively sort object keys and drop insignificant
 * whitespace so the gate can compare a dispatch envelope's `spec` with the
 * emitted fenced block regardless of formatting. Numbers use JSON's default
 * serialization; `undefined` values are dropped as in `JSON.stringify`.
 */
export function canonicalJson(value: unknown): string {
  const norm = (v: unknown): unknown => {
    if (Array.isArray(v)) return v.map(norm);
    if (isObj(v)) {
      const out: Record<string, unknown> = {};
      for (const key of Object.keys(v).sort()) {
        if (v[key] === undefined) continue;
        out[key] = norm(v[key]);
      }
      return out;
    }
    return v;
  };
  return JSON.stringify(norm(value));
}

/** Fenced ```viz blocks in a message; returns the raw inner JSON strings. */
export function extractVizFences(text: string): string[] {
  const out: string[] = [];
  if (typeof text !== "string") return out;
  const re = /```viz[^\n]*\n([\s\S]*?)```/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    const body = m[1].trim();
    if (body.length > 0) out.push(body);
  }
  return out;
}

/** Parse and validate every viz fence in a message. */
export function parseVizFences(text: string): { raw: string; result: ValidateResult }[] {
  return extractVizFences(text).map((raw) => {
    let parsed: unknown;
    try {
      parsed = JSON.parse(raw);
    } catch (e) {
      return { raw, result: { ok: false, errors: [`invalid JSON: ${e instanceof Error ? e.message : String(e)}`] } };
    }
    return { raw, result: validateSpec(parsed) };
  });
}

/** Default parameter values as a plain map. */
export function paramValues(spec: VizSpec | undefined): Record<string, number> {
  const vars: Record<string, number> = {};
  for (const p of spec?.params || []) vars[p.name] = p.value;
  return vars;
}

/**
 * Materialize the plot data for a spec: either the explicit series, or the
 * formula sampled across [xMin,xMax] using the given parameter values. The
 * formula's dependent variable is `y` by convention (`expr` is f(x)).
 */
export function sampleSpec(spec: VizSpec | undefined, overrides?: Record<string, number>): VizSeries[] {
  if (!spec) return [];
  const vars = { ...paramValues(spec), ...(overrides || {}) };
  if (spec.formula) {
    const { expr, xMin, xMax, samples = 200 } = spec.formula;
    const fn = compileExpr(expr);
    const pts: VizPoint[] = [];
    const n = Math.max(2, Math.min(LIMITS.samples, Math.round(samples)));
    for (let i = 0; i < n; i++) {
      const x = xMin + ((xMax - xMin) * i) / (n - 1);
      let y: number;
      try {
        y = fn({ ...vars, x });
      } catch {
        continue;
      }
      pts.push({ x, y });
    }
    const name = Object.entries(vars)
      .filter(([k]) => (spec.params || []).some((p) => p.name === k))
      .map(([k, v]) => `${k}=${round3(v)}`)
      .join(", ");
    return [{ name: name || undefined, points: pts }];
  }
  return spec.series || [];
}

function round3(v: number): string {
  return String(Math.round(v * 1000) / 1000);
}
