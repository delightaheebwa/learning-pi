/**
 * expr — a tiny, safe arithmetic-expression evaluator for interactive viz.
 *
 * A viz spec may carry a `formula` (`{expr, xMin, xMax}`) whose `expr` is
 * sampled live while the learner moves a parameter slider. Model-authored
 * expressions must never be `eval`'d, so this is a self-contained recursive
 * descent parser over a deliberately small grammar:
 *
 *   expr    := term (('+' | '-') term)*
 *   term    := factor (('*' | '/') factor)*
 *   factor  := unary ('^' factor)?          // right associative
 *   unary   := ('-' | '+')? primary
 *   primary := number | const | call | ident | '(' expr ')'
 *   call    := name '(' [expr (',' expr)*] ')'
 *
 * Constants: pi, e, tau. Functions: sin, cos, tan, asin, acos, atan, atan2,
 * sinh, cosh, tanh, exp, ln, log (base e), log2, log10, sqrt, cbrt, abs, sign,
 * floor, ceil, round, min, max, pow, hypot. Unknown names are an error, never
 * undefined.
 */

type Node =
  | { t: "num"; v: number }
  | { t: "var"; name: string }
  | { t: "un"; op: "-" | "+"; a: Node }
  | { t: "bin"; op: "+" | "-" | "*" | "/" | "^"; a: Node; b: Node }
  | { t: "call"; name: string; args: Node[] };

export const CONSTS: Record<string, number> = {
  pi: Math.PI,
  e: Math.E,
  tau: Math.PI * 2,
};

export const FUNCS: Record<string, (...args: number[]) => number> = {
  sin: Math.sin,
  cos: Math.cos,
  tan: Math.tan,
  asin: Math.asin,
  acos: Math.acos,
  atan: Math.atan,
  atan2: Math.atan2,
  sinh: Math.sinh,
  cosh: Math.cosh,
  tanh: Math.tanh,
  exp: Math.exp,
  ln: Math.log,
  log: Math.log,
  log2: Math.log2,
  log10: Math.log10,
  sqrt: Math.sqrt,
  cbrt: Math.cbrt,
  abs: Math.abs,
  sign: Math.sign,
  floor: Math.floor,
  ceil: Math.ceil,
  round: Math.round,
  min: Math.min,
  max: Math.max,
  pow: Math.pow,
  hypot: Math.hypot,
};

interface Token {
  kind: "num" | "ident" | "op" | "lparen" | "rparen" | "comma";
  value: string;
  pos: number;
}

function tokenize(input: string): Token[] {
  const out: Token[] = [];
  let i = 0;
  while (i < input.length) {
    const ch = input[i];
    if (ch === " " || ch === "\t" || ch === "\n" || ch === "\r") {
      i++;
      continue;
    }
    if (/[0-9.]/.test(ch)) {
      let j = i;
      while (j < input.length && /[0-9.]/.test(input[j])) j++;
      if (input[j] === "e" || input[j] === "E") {
        j++;
        if (input[j] === "+" || input[j] === "-") j++;
        while (j < input.length && /[0-9]/.test(input[j])) j++;
      }
      const raw = input.slice(i, j);
      if (!/^\d*\.?\d+(?:[eE][+-]?\d+)?$/.test(raw)) throw new Error(`invalid number '${raw}'`);
      out.push({ kind: "num", value: raw, pos: i });
      i = j;
      continue;
    }
    if (/[A-Za-z_]/.test(ch)) {
      let j = i;
      while (j < input.length && /[A-Za-z0-9_]/.test(input[j])) j++;
      out.push({ kind: "ident", value: input.slice(i, j), pos: i });
      i = j;
      continue;
    }
    if (ch === "(") {
      out.push({ kind: "lparen", value: ch, pos: i });
      i++;
      continue;
    }
    if (ch === ")") {
      out.push({ kind: "rparen", value: ch, pos: i });
      i++;
      continue;
    }
    if (ch === ",") {
      out.push({ kind: "comma", value: ch, pos: i });
      i++;
      continue;
    }
    if ("+-*/^".includes(ch)) {
      out.push({ kind: "op", value: ch, pos: i });
      i++;
      continue;
    }
    throw new Error(`unexpected character '${ch}' at ${i}`);
  }
  return out;
}

class Parser {
  private toks: Token[];
  private pos = 0;
  constructor(toks: Token[]) {
    this.toks = toks;
  }
  private peek(): Token | undefined {
    return this.toks[this.pos];
  }
  private next(): Token | undefined {
    return this.toks[this.pos++];
  }
  private expect(kind: Token["kind"], value?: string): Token {
    const t = this.next();
    if (!t || t.kind !== kind || (value !== undefined && t.value !== value)) {
      throw new Error(`expected ${value ?? kind}${t ? ` but found '${t.value}'` : ""}`);
    }
    return t;
  }
  parse(): Node {
    const n = this.expr();
    if (this.pos !== this.toks.length) throw new Error(`unexpected '${this.peek()?.value}'`);
    return n;
  }
  private expr(): Node {
    let a = this.term();
    for (;;) {
      const t = this.peek();
      if (t && t.kind === "op" && (t.value === "+" || t.value === "-")) {
        this.next();
        a = { t: "bin", op: t.value as "+" | "-", a, b: this.term() };
      } else break;
    }
    return a;
  }
  private term(): Node {
    let a = this.factor();
    for (;;) {
      const t = this.peek();
      if (t && t.kind === "op" && (t.value === "*" || t.value === "/")) {
        this.next();
        a = { t: "bin", op: t.value as "*" | "/", a, b: this.factor() };
      } else break;
    }
    return a;
  }
  private factor(): Node {
    const a = this.unary();
    const t = this.peek();
    if (t && t.kind === "op" && t.value === "^") {
      this.next();
      return { t: "bin", op: "^", a, b: this.factor() };
    }
    return a;
  }
  private unary(): Node {
    const t = this.peek();
    if (t && t.kind === "op" && (t.value === "-" || t.value === "+")) {
      this.next();
      return { t: "un", op: t.value as "-" | "+", a: this.unary() };
    }
    return this.primary();
  }
  private primary(): Node {
    const t = this.next();
    if (!t) throw new Error("unexpected end of expression");
    if (t.kind === "num") return { t: "num", v: Number(t.value) };
    if (t.kind === "lparen") {
      const n = this.expr();
      this.expect("rparen");
      return n;
    }
    if (t.kind === "ident") {
      const nt = this.peek();
      if (nt && nt.kind === "lparen") {
        this.next();
        const args: Node[] = [];
        if (this.peek()?.kind !== "rparen") {
          args.push(this.expr());
          while (this.peek()?.kind === "comma") {
            this.next();
            args.push(this.expr());
          }
        }
        this.expect("rparen");
        return { t: "call", name: t.value, args };
      }
      return { t: "var", name: t.value };
    }
    throw new Error(`unexpected '${t.value}'`);
  }
}

function walk(n: Node, visit: (n: Node) => void): void {
  visit(n);
  switch (n.t) {
    case "un":
      walk(n.a, visit);
      break;
    case "bin":
      walk(n.a, visit);
      walk(n.b, visit);
      break;
    case "call":
      for (const a of n.args) walk(a, visit);
      break;
  }
}

/**
 * Parse `expr` and check every name against `allowed` vars plus the built-in
 * constants/functions. Returns a human-readable error, or undefined when valid.
 */
export function validateExpr(expr: string, allowed: Iterable<string>): string | undefined {
  if (typeof expr !== "string" || expr.trim().length === 0) return "empty expression";
  let ast: Node;
  try {
    ast = new Parser(tokenize(expr)).parse();
  } catch (e) {
    return e instanceof Error ? e.message : String(e);
  }
  const names = new Set(allowed);
  let err: string | undefined;
  walk(ast, (n) => {
    if (err) return;
    if (n.t === "var" && !names.has(n.name) && !(n.name in CONSTS)) err = `unknown name '${n.name}'`;
    if (n.t === "call" && !(n.name in FUNCS)) err = `unknown function '${n.name}'`;
  });
  return err;
}

/** Compile to an evaluator. Unknown names/functions throw at evaluation time. */
export function compileExpr(expr: string): (vars: Record<string, number>) => number {
  const ast = new Parser(tokenize(expr)).parse();
  const evalNode = (n: Node, vars: Record<string, number>): number => {
    switch (n.t) {
      case "num":
        return n.v;
      case "var": {
        if (n.name in vars) return vars[n.name];
        if (n.name in CONSTS) return CONSTS[n.name];
        throw new Error(`unknown name '${n.name}'`);
      }
      case "un":
        return n.op === "-" ? -evalNode(n.a, vars) : evalNode(n.a, vars);
      case "bin": {
        const a = evalNode(n.a, vars);
        const b = evalNode(n.b, vars);
        switch (n.op) {
          case "+":
            return a + b;
          case "-":
            return a - b;
          case "*":
            return a * b;
          case "/":
            return a / b;
          case "^":
            return Math.pow(a, b);
        }
      }
      // eslint-disable-next-line no-fallthrough
      case "call": {
        const fn = FUNCS[n.name];
        if (!fn) throw new Error(`unknown function '${n.name}'`);
        return fn(...n.args.map((a) => evalNode(a, vars)));
      }
    }
    throw new Error("bad node");
  };
  return (vars) => evalNode(ast, vars);
}

/** Evaluate with a fresh compile each call (used by tests and one-off renders). */
export function evalExpr(expr: string, vars: Record<string, number>): number {
  return compileExpr(expr)(vars);
}
