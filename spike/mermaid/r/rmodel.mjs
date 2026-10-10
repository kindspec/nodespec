// SPDX-License-Identifier: MIT
// R, the renderer, as PRE-REGISTRATION.md §4.4 pins it: Mermaid 12.1.0 and
// jsdom 26.1.0 from the committed package-lock.json, under Node v24.20.0.
//
//   node rmodel.mjs            one diagram text on stdin; one JSON object out
//   node rmodel.mjs --batch    JSON lines in ({"id", "text"}); JSON lines out
//
// - The jsdom window and document are set on globalThis BEFORE Mermaid is
//   imported; without them DOMPurify defines no `sanitize` (§4.4).
// - mermaid.initialize is called with §4.4's configuration before every text,
//   so a directive or front matter in one text cannot carry into the next.
// - mermaid.parse(text) is called without suppressErrors (§4.4, probe5).
// - An error carrying jison's `hash`: the text does not parse.
// - Any other error: the fixed canary is parsed. If it parses, the text does
//   not parse and the error class and first message line are recorded. If it
//   fails, the toolchain is broken: {"abort": true} and exit 3.
// - The model is read with mermaid.mermaidAPI.getDiagramFromText(text) and
//   its flowchart database (§4.4, Appendix A).
//
// Test seams, each refused unless SPIKE_R_TEST=1 is also set, and each
// recorded in the output's "config" so a transcript shows it: NO_JSDOM=1
// skips the jsdom globals; DEFAULT_EDGES=1 leaves maxEdges at Mermaid's
// default. V0 uses them to show §4.4's failure modes.
const test = process.env.SPIKE_R_TEST === '1';
const noDom = test && process.env.NO_JSDOM === '1';
const defaultEdges = test && process.env.DEFAULT_EDGES === '1';
if (!test && (process.env.NO_JSDOM || process.env.DEFAULT_EDGES)) {
  console.log(JSON.stringify({ abort: true, cls: 'Usage', msg: 'NO_JSDOM and DEFAULT_EDGES need SPIKE_R_TEST=1' }));
  process.exit(3);
}
if (!noDom) {
  const { JSDOM } = await import('jsdom');
  const dom = new JSDOM('<!doctype html><html><body></body></html>');
  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
}
const mermaid = (await import('mermaid')).default;
const CONFIG = { startOnLoad: false, securityLevel: 'strict', flowchart: { htmlLabels: false } };
if (!defaultEdges) CONFIG.maxEdges = 100000;
const CANARY = 'flowchart TD\n  A[Alpha] --> B';
const VERSIONS = {
  node: process.version,
  mermaid: (await import('mermaid/package.json', { with: { type: 'json' } })).default.version,
};

function init() {
  mermaid.initialize(structuredClone(CONFIG));
}

function strs(a) {
  return Array.isArray(a) ? a.map(String) : [];
}

async function model(t) {
  init();
  await mermaid.parse(t);
  const d = await mermaid.mermaidAPI.getDiagramFromText(t);
  const db = d.db;
  if (typeof db.getVertices !== 'function') return { parse: true, diagramType: d.type, flowchart: false };
  return {
    parse: true,
    diagramType: d.type,
    flowchart: true,
    vertices: [...db.getVertices().entries()].map(([k, v]) => ({
      key: k, id: v.id, text: v.text ?? null, type: v.type ?? null,
      classes: strs(v.classes), styles: strs(v.styles),
      link: v.link ?? null, linkTarget: v.linkTarget ?? null,
      icon: v.icon ?? null, img: v.img ?? null,
    })),
    edges: db.getEdges().map((e) => ({
      id: e.id, isUserDefinedId: !!e.isUserDefinedId, start: e.start, end: e.end,
      type: e.type ?? null, stroke: e.stroke ?? null, length: e.length ?? null,
      text: e.text ?? '', style: e.style ? strs(e.style) : null,
    })),
    edgeDefaultStyle: db.getEdges().defaultStyle ? strs(db.getEdges().defaultStyle) : null,
    subgraphs: db.getSubGraphs().map((s) => ({ id: s.id, title: s.title, nodes: strs(s.nodes) })),
    classDefs: [...db.getClasses().entries()].map(([k, c]) => ({ id: k, styles: strs(c.styles) })),
  };
}

async function one(text) {
  try {
    return await model(text);
  } catch (e) {
    const hasHash = e !== null && typeof e === 'object' && 'hash' in e;
    const cls = e?.constructor?.name ?? typeof e;
    const msg = String(e?.message ?? e).split('\n')[0].slice(0, 200);
    if (hasHash) return { parse: false, hash: true, cls, msg };
    try {
      await model(CANARY);
    } catch (e2) {
      return { abort: true, cls, msg, canaryCls: e2?.constructor?.name ?? typeof e2 };
    }
    return { parse: false, hash: false, canary: 'ok', cls, msg };
  }
}

const config = { ...CONFIG, maxEdges: CONFIG.maxEdges ?? 'default', jsdom: !noDom, versions: VERSIONS };
let input = '';
for await (const c of process.stdin) input += c;
if (process.argv.includes('--batch')) {
  console.log(JSON.stringify({ config }));
  for (const line of input.split('\n')) {
    if (!line) continue;
    const { id, text } = JSON.parse(line);
    const r = await one(text);
    console.log(JSON.stringify({ id, ...r }));
    if (r.abort) process.exit(3);
  }
} else {
  const r = await one(input);
  console.log(JSON.stringify({ ...r, config }));
  if (r.abort) process.exit(3);
}
