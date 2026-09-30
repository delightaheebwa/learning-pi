// Unit tests for the viz-mode pure modules (spec validation, expression
// evaluation, canonical form, ASCII rendering).
//
//   deno run --allow-all test/viz_test.mjs
//
// These run without pi: viz-mode/spec.ts, expr.ts, and render-ascii.ts import
// no pi packages.
import {
  canonicalJson,
  extractVizFences,
  parseVizFences,
  sampleSpec,
  validateSpec,
} from '../.pi/extensions/viz-mode/spec.ts';
import { evalExpr, validateExpr } from '../.pi/extensions/viz-mode/expr.ts';
import { renderAscii } from '../.pi/extensions/viz-mode/render-ascii.ts';
import { renderSvg } from '../.pi/extensions/viz-mode/render-svg.ts';
import { firstVizSpec, replaceVizFences } from '../.pi/extensions/viz-mode/wire.ts';

const assert = (n, c) => console.log((c ? 'PASS ' : 'FAIL ') + n);

// --- expression evaluator ---------------------------------------------------
assert('evalExpr respects precedence and parentheses', evalExpr('2 + 3 * 4', {}) === 14 && evalExpr('(2 + 3) * 4', {}) === 20);
assert('evalExpr supports vars and functions', Math.abs(evalExpr('a * sin(x)', { a: 2, x: Math.PI / 2 }) - 2) < 1e-9);
assert('evalExpr rejects unknown names', validateExpr('a + b', ['a']) !== undefined);
assert('evalExpr accepts allowed params', validateExpr('m * x + c', ['m', 'x', 'c']) === undefined);

// --- canonical form and fence extraction ------------------------------------
assert('canonicalJson sorts keys', canonicalJson({ b: 1, a: 2 }) === canonicalJson({ a: 2, b: 1 }));
const fenced = 'Here:\n```viz\n{"viz":"1","kind":"bar","bars":[{"label":"a","value":1}]}\n```\ndone';
assert('extractVizFences finds the block', extractVizFences(fenced).length === 1);
assert('parseVizFences validates a good block', parseVizFences(fenced)[0].result.ok === true);

// --- schema validation ------------------------------------------------------
const lineSpec = {
  viz: '1',
  kind: 'line',
  title: 'Loss vs iteration',
  xLabel: 'iteration',
  yLabel: 'loss',
  series: [{ name: 'lr=0.1', points: [[0, 5], [1, 3.2], [2, 2.1]] }],
};
assert('valid line spec accepted', validateSpec(lineSpec).ok === true);
assert('non-finite numbers rejected', validateSpec({ ...lineSpec, series: [{ points: [[0, Number.NaN]] }] }).ok === false);
assert('unknown kind rejected', validateSpec({ viz: '1', kind: 'pie' }).ok === false);
assert('bar requires bars', validateSpec({ viz: '1', kind: 'bar' }).ok === false);
assert('diagram edges must reference nodes', validateSpec({ viz: '1', kind: 'diagram', nodes: [{ id: 'a' }], edges: [{ from: 'a', to: 'z' }] }).ok === false);
assert('formula must mention declared params', validateSpec({ viz: '1', kind: 'line', formula: { expr: 'k * x', xMin: 0, xMax: 1 } }).ok === false);
assert(
  'formula with declared params accepted',
  validateSpec({ viz: '1', kind: 'line', params: [{ name: 'k', min: 0, max: 2, step: 0.1, value: 1 }], formula: { expr: 'k * sin(x)', xMin: 0, xMax: 6.28, samples: 50 } }).ok === true
);
assert('frames recurse into the validator', validateSpec({ viz: '1', kind: 'bar', frames: [{ spec: { viz: '1', kind: 'pie' } }] }).ok === false);
assert(
  'frames-only spec needs no top-level data',
  validateSpec({ viz: '1', kind: 'line', frames: [{ caption: 'a', spec: { viz: '1', kind: 'bar', bars: [{ label: 'x', value: 1 }] } }] }).ok === true
);
assert('table spec accepted', validateSpec({ viz: '1', kind: 'table', columns: ['a', 'b'], rows: [['1', 2]] }).ok === true);

// --- formula sampling -------------------------------------------------------
const formulaSpec = validateSpec({
  viz: '1',
  kind: 'line',
  params: [{ name: 'k', min: 0, max: 2, step: 0.5, value: 1 }],
  formula: { expr: 'k * x', xMin: 0, xMax: 10, samples: 11 },
}).spec;
const sampled = sampleSpec(formulaSpec);
assert('formula samples to points', sampled.length === 1 && sampled[0].points.length === 11);
assert('formula uses parameter value', Math.abs(sampled[0].points[5].y - 5) < 1e-9);
const overridden = sampleSpec(formulaSpec, { k: 2 });
assert('formula honors a parameter override', Math.abs(overridden[0].points[5].y - 10) < 1e-9);

// --- ASCII rendering --------------------------------------------------------
const barLines = renderAscii({ viz: '1', kind: 'bar', title: 'Counts', bars: [{ label: 'a', value: 2 }, { label: 'b', value: 5 }] });
assert('bar render includes title and bars', barLines[0].includes('Counts') && barLines.some((l) => l.includes('█')));
const tableLines = renderAscii({ viz: '1', kind: 'table', columns: ['x', 'y'], rows: [['a', 'b']] });
assert('table render aligns columns', tableLines.length >= 3 && tableLines[0].includes('x') && tableLines[0].includes('y'));
const lineLines = renderAscii(lineSpec);
assert('line render contains axes and braille dots', lineLines.some((l) => l.includes('│')) && lineLines.some((l) => /[\u2800-\u28ff]/.test(l)));
assert('line render labels the x axis', lineLines.some((l) => l.includes('iteration')));
const asciiOverride = renderAscii({ viz: '1', kind: 'bar', bars: [{ label: 'a', value: 1 }], ascii: 'CUSTOM' });
assert('hand-tuned ascii override is used verbatim', asciiOverride.length === 1 && asciiOverride[0] === 'CUSTOM');
const frameLines = renderAscii({ viz: '1', kind: 'bar', frames: [{ caption: 'one', spec: { viz: '1', kind: 'bar', bars: [{ label: 'a', value: 1 }] } }, { caption: 'two', spec: { viz: '1', kind: 'bar', bars: [{ label: 'a', value: 2 }] } }] });
assert('frames render with captions and an index', frameLines.some((l) => l.includes('[1/2] one')) && frameLines.some((l) => l.includes('[2/2] two')));

// --- SVG generation ---------------------------------------------------------
const svg = renderSvg({ viz: '1', kind: 'line', title: 'Loss', series: [{ points: [[0, 5], [1, 3]] }] });
assert('svg is well-formed and escapes labels', svg.startsWith('<svg') && svg.trimEnd().endsWith('</svg>'));
assert('svg includes a polyline path', svg.includes('<path d="M'));
const barSvg = renderSvg({ viz: '1', kind: 'bar', bars: [{ label: '<x>', value: 2 }] });
assert('svg escapes special characters', barSvg.includes('&lt;x&gt;') && !barSvg.includes('<x>'));

// --- wire: display-time fence replacement -----------------------------------
const wireSrc = 'Intro.\n```viz\n{"viz":"1","kind":"bar","title":"T","bars":[{"label":"a","value":3}]}\n```\nOutro.';
const replaced = replaceVizFences(wireSrc, 40);
assert('replaceVizFences renders a valid fence to text', !replaced.includes('```viz') && replaced.includes('```text') && replaced.includes('T'));
assert('replaceVizFences keeps surrounding prose', replaced.startsWith('Intro.') && replaced.trimEnd().endsWith('Outro.'));
const badWire = 'x\n```viz\nnot json\n```\ny';
assert('replaceVizFences leaves an invalid fence untouched', replaceVizFences(badWire).includes('```viz'));
assert('firstVizSpec returns a valid spec', firstVizSpec(wireSrc)?.kind === 'bar');
assert('firstVizSpec returns undefined for an invalid fence', firstVizSpec(badWire) === undefined);
