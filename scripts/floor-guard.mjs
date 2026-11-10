#!/usr/bin/env node
// floor-guard.mjs — diff-scoped enforcement of the CONSTRAINTS.md floor.
// Usage: node floor-guard.mjs [--base <ref>]   (default base: origin/main)
//
// Adapted from .opencode/skills/constraint-driven-development/references/floor-guard.md
// for this repo's Python / Deno / Bash stack. The diff plumbing, the
// CONSTRAINTS.md checks, the exit codes, and the tight/loose direction are kept
// identical; only the pattern list and the ignore file are stack-specific.
//
// Deliberate adaptations, recorded in .opencode/UPSTREAM.md:
//  - CONSTRAINTS.md itself is exempt from the suppression/stub/skip patterns:
//    its Floor bullets name those patterns by design.
//  - A newly added CONSTRAINTS.md does not flag its own Exceptions rows.
//  - This file is exempt because its regexes contain the patterns.
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import path from 'node:path';

const base = (() => {
  const i = process.argv.indexOf('--base');
  return i > -1 ? process.argv[i + 1] : 'origin/main';
})();

// `git diff --no-index` exits 1 whenever the two sides differ, which is the normal case for a
// new file, so that output is kept. Any other failure is null, and null never reads as clean.
const git = (args, { diffExit = false } = {}) => {
  try {
    return execFileSync('git', ['-c', 'core.quotePath=false', ...args], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } catch (e) {
    return diffExit && e.status === 1 && typeof e.stdout === 'string' ? e.stdout : null;
  }
};
const bail = (msg) => {
  console.error('floor-guard: ' + msg);
  process.exit(2);
};

// Run from the top of the work tree. `git ls-files` lists only the current directory's subtree,
// relative to it, so a guard started in a subfolder would miss untracked files elsewhere and name
// the rest differently from `git diff`, which always covers the whole tree.
const top = git(['rev-parse', '--show-toplevel'])?.trim();
if (!top) bail('not inside a git work tree');
process.chdir(top);

// Merge base; bail to exit 2 rather than pretending a shallow/rootless clone is clean.
const mergeBase = git(['merge-base', base, 'HEAD'])?.trim();
if (!mergeBase) bail('no merge base against ' + base);

// Unified diff plus untracked files (git diff alone cannot see new files).
const tracked = git(['diff', '--no-prefix', '--unified=0', mergeBase, '--']);
if (tracked === null) bail('could not diff against ' + mergeBase);
const untrackedFiles = git(['ls-files', '--others', '--exclude-standard']);
if (untrackedFiles === null) bail('could not list untracked files');
const untracked = untrackedFiles
  .split('\n')
  .filter(Boolean)
  .map((f) => {
    const d = git(['diff', '--no-index', '--no-prefix', '--unified=0', '/dev/null', f], {
      diffExit: true,
    });
    if (d === null) bail('could not diff untracked file ' + f);
    return d;
  })
  .join('\n');
const diff = tracked + '\n' + untracked;

// Walk the diff. `---` and `+++` are file headers only between a file's `diff` line and its first
// `@@` hunk; inside a hunk every line is content, so an added `++i` (shown as `+++i`) or a removed
// `-- comment` is a change, not a header. Both headers name the file, so a deletion
// (`+++ /dev/null`) keeps its name.
const added = [];
const removed = [];
const deleted = [];
const pathOf = (s) => s.replace(/^[ab]\//, '');
const isTestPath = (f) => /\.(test|spec)\.|_test\.|test_/.test(f);
let file = '';
let oldFile = '';
let renameFrom = '';
let inHeader = false;
for (const line of diff.split('\n')) {
  if (line.startsWith('diff ')) {
    inHeader = true;
    renameFrom = '';
  } else if (line.startsWith('@@')) inHeader = false;
  else if (inHeader) {
    // A 100%-similarity rename has no ---/+++ pair; catch a test renamed to a
    // non-test here so deleting a test by renaming it still trips the gate.
    if (line.startsWith('rename from ')) {
      renameFrom = pathOf(line.slice('rename from '.length));
    } else if (line.startsWith('rename to ')) {
      const renameTo = pathOf(line.slice('rename to '.length));
      if (renameFrom && isTestPath(renameFrom) && !isTestPath(renameTo)) {
        deleted.push(renameFrom);
      }
      renameFrom = '';
    } else if (line.startsWith('--- ')) oldFile = pathOf(line.slice(4));
    else if (line.startsWith('+++ ')) {
      const newFile = pathOf(line.slice(4));
      file = newFile === '/dev/null' ? oldFile : newFile;
      if (newFile === '/dev/null') deleted.push(file);
    }
  } else if (line.startsWith('+')) added.push({ file, text: line.slice(1) });
  else if (line.startsWith('-')) removed.push({ file, text: line.slice(1) });
}

// `.constraintsignore`: one glob per line. Exempts vendored docs and recorded
// examples from the pattern checks, so a genuine exception is a tracked file
// rather than a loosened rule.
const globToRegExp = (glob) => {
  let out = '^';
  for (let i = 0; i < glob.length; i += 1) {
    const ch = glob[i];
    if (ch === '*') {
      if (glob[i + 1] === '*') {
        out += '.*';
        i += 1;
        if (glob[i + 1] === '/') i += 1;
      } else {
        out += '[^/]*';
      }
    } else if (ch === '?') {
      out += '[^/]';
    } else {
      out += ch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
  }
  return new RegExp(out + '$');
};
let ignoreGlobs = [];
try {
  ignoreGlobs = readFileSync(path.join(top, '.constraintsignore'), 'utf8')
    .split('\n')
    .map((s) => s.trim())
    .filter((s) => s && !s.startsWith('#'));
} catch {
  ignoreGlobs = [];
}
const ignoreRes = ignoreGlobs.map(globToRegExp);
const isIgnored = (f) =>
  f === 'scripts/floor-guard.mjs' || ignoreRes.some((re) => re.test(f));

const findings = [];
const flag = (rule, f, text) => findings.push({ rule, file: f, text: text.trim().slice(0, 120) });
const isTest = isTestPath;
// Exact root file only: a lookalike such as docs/CONSTRAINTS.md must not be
// treated as the bar (or exempted from the pattern checks).
const isConstraints = (f) => f === 'CONSTRAINTS.md';

// 1. Silenced checker — extended for Python, Deno, and Bash. The vendored pack
//    and this guard are exempt (see header).
const SUPPRESSIONS =
  /@ts-ignore|@ts-nocheck|eslint-disable|biome-ignore|deno-lint-ignore|# *noqa|# *type: *ignore|# *pyright: *ignore|# *pylint: *disable|# *shellcheck *disable|istanbul ignore|nosemgrep|gitleaks:allow|Stryker disable/;
// 4. Unfinished work.
const STUBS =
  /throw new (Error|NotImplemented).*[Nn]ot implemented|raise NotImplementedError|catch\s*\(\w*\)\s*\{\s*\}|catch\s*\{\s*\}|\bTODO\b|\bpass\s*# *stub/;
// 2. A test made easier (added skips).
const SKIPS =
  /\.(skip|todo)\b|\bxit\(|\bxdescribe\(|@pytest\.mark\.skip|@unittest\.skip|@unittest\.expectedFailure|pytest\.xfail|t\.Skip\(|Deno\.test\.ignore|\.only\(/;

// A file that is entirely new has no "before" state; its floor patterns were
// reviewed when the file was created. Skip unless it is inside the ignore list.
const isNewConstraints = added.some((l) => isConstraints(l.file)) && !removed.some((l) => isConstraints(l.file));

for (const { file: f, text } of added) {
  if (isIgnored(f) || isConstraints(f)) continue;
  if (SUPPRESSIONS.test(text)) flag('silenced-checker', f, text);
  if (STUBS.test(text)) flag('unfinished-work', f, text);
  if (SKIPS.test(text)) flag('test-made-easier', f, text);
}
for (const { file: f, text } of added) {
  if (!isConstraints(f) || isNewConstraints) continue;
  if (/^\| *(W|E)\d+ *\|/.test(text)) flag('new-exception', f, text);
}

// 2b. A test file deleted, or an assertion removed from a test file that still exists.
for (const f of deleted) if (isTest(f) && !isIgnored(f)) flag('test-deleted', f, 'file deleted');
for (const { file: f, text } of removed) {
  if (isIgnored(f)) continue;
  if (isTest(f) && !deleted.includes(f) && /\b(expect|assert|should)\b/.test(text)) {
    flag('assertion-removed', f, text);
  }
}

// 1b/2c. A rule in CONSTRAINTS.md weakened or removed. A rule is a floor bullet or a table row,
// identified by the bullet's text before its first colon or by the row's first cell. Each number
// carries a direction read from the words around it: a minimum (>=, at least, must not fall) is
// loosened by going down, a maximum (<=, at most, under, must not grow) by going up. A number whose
// direction cannot be read is reported whenever it changes, because the guard cannot tell
// tightening from loosening and staying quiet is the wrong default. Numbers are paired within
// their direction (the first minimum with the first minimum, and so on), so a number added
// elsewhere in the text does not shift the pairing; a threshold with no counterpart after the
// edit was removed, and an added one tightens.
const ruleKey = (t) => {
  const s = t.trim();
  if (s.startsWith('|')) return s.split('|').map((c) => c.trim()).filter(Boolean)[0] ?? '';
  if (/^[-*] /.test(s)) return s.slice(2).split(':')[0].trim();
  return null; // prose, headings, dates: not a rule
};
const isException = (t) => /^\| *(W|E)\d+ *\|/.test(t.trim());
const MIN_BEFORE = /(>=|>|≥|at least|minimum|\bmin\b|no less than|not fall|not drop)\s*$/;
const MAX_BEFORE = /(<=|<|≤|at most|maximum|\bmax\b|no more than|under|below|not grow|not exceed)\s*$/;
const MIN_AFTER = /^\s*\S*\s*(?:\|\s*)?(or more|or higher|must not fall|must not drop)/;
const MAX_AFTER = /^\s*\S*\s*(?:\|\s*)?(or less|or lower|must not grow|must not exceed)/;
const thresholds = (t) => {
  const out = [];
  const re = /\d+(?:\.\d+)?/g;
  let m;
  while ((m = re.exec(t))) {
    const before = t.slice(Math.max(0, m.index - 24), m.index).toLowerCase();
    const after = t.slice(m.index + m[0].length, m.index + m[0].length + 40).toLowerCase();
    const dir =
      MIN_BEFORE.test(before) || MIN_AFTER.test(after)
        ? 'min'
        : MAX_BEFORE.test(before) || MAX_AFTER.test(after)
          ? 'max'
          : null;
    out.push({ n: Number(m[0]), dir });
  }
  return out;
};
const removedRules = removed.filter((l) => isConstraints(l.file) && ruleKey(l.text) !== null);
const addedRules = added.filter((l) => isConstraints(l.file) && ruleKey(l.text) !== null);
for (const r of removedRules) {
  const a = addedRules.find((x) => ruleKey(x.text) === ruleKey(r.text));
  if (!a) {
    if (!isException(r.text)) flag('rule-removed', r.file, r.text); // dropping an exception tightens: silent
    continue;
  }
  const before = thresholds(r.text);
  const after = thresholds(a.text);
  let verdict = null;
  for (const dir of ['min', 'max', null]) {
    const was = before.filter((x) => x.dir === dir);
    const now = after.filter((x) => x.dir === dir);
    was.forEach((b, i) => {
      const n = now[i];
      if (verdict) return;
      if (!n) verdict = 'threshold-removed';
      else if (n.n === b.n) return;
      else if (dir === 'min' ? n.n < b.n : dir === 'max' ? n.n > b.n : true) {
        verdict = dir ? 'threshold-loosened' : 'threshold-changed';
      }
    });
  }
  if (verdict) flag(verdict, r.file, r.text + '  ->  ' + a.text);
}

if (findings.length === 0) {
  console.log('floor-guard: clean');
  process.exit(0);
}
// Never echo a live credential into CI logs; keep a short prefix for debugging.
const redact = (s) =>
  s
    .replace(/\b(?:gh[pousr]_|sk_live_|sk_test_|AKIA|AIza|xox[baprs]-)[A-Za-z0-9_-]{6,}/g, (m) => m.slice(0, 4) + '…')
    .replace(/((?:secret|token|password|api[_-]?key)\s*[=:]\s*)\S+/gi, '$1…');

console.error('floor-guard: ' + findings.length + ' floor violation(s):');
for (const f of findings) console.error(`  [${f.rule}] ${f.file}: ${redact(f.text)}`);
if (findings.some((f) => f.rule === 'rule-removed')) {
  console.error(
    "\nA rule-removed finding can also mean the rule's label changed: rename a rule in one commit and change its thresholds in another."
  );
}
if (findings.some((f) => f.rule === 'threshold-removed')) {
  console.error(
    '\nA threshold-removed finding can also mean a number gained or lost its direction words (">= 80%" becoming "80%", or the reverse): compare the two lines before assuming a threshold was deleted.'
  );
}
console.error('\nEach is a move that lowers the bar. Fix the code, or route it through a tracked exception.');
process.exit(1);
