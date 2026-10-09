// R wrapper, draft v4 §4.4. Reads one diagram text on stdin; prints one JSON object.
// Synthetic use only. jsdom globals are set BEFORE mermaid is imported.
// Rules: never suppressErrors. An error with jison's `hash` => does not parse.
// Any other error => re-parse the fixed canary `A[Alpha] --> B`: if the canary parses,
// the text does not parse (error class recorded); if the canary fails, abort (exit 3).
const noDom = process.env.NO_JSDOM === '1';
if (!noDom) {
  const { JSDOM } = await import('jsdom');
  const dom = new JSDOM('<!doctype html><html><body></body></html>');
  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
}
const mermaid = (await import('mermaid')).default;
const maxEdges = Number(process.env.MAX_EDGES || 100000);
mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', maxEdges, flowchart: { htmlLabels: false } });
const CANARY = 'flowchart TD\n  A[Alpha] --> B';
let text = '';
for await (const c of process.stdin) text += c;

async function model(t) {
  await mermaid.parse(t);
  const d = await mermaid.mermaidAPI.getDiagramFromText(t);
  const db = d.db;
  if (typeof db.getVertices !== 'function') return { parse: true, diagramType: d.type, flowchart: false };
  return {
    parse: true,
    diagramType: d.type,
    flowchart: true,
    vertices: [...db.getVertices().entries()].map(([k, v]) => ({ id: k, text: v.text, type: v.type ?? null, classes: v.classes, styles: v.styles, link: v.link ?? null, linkTarget: v.linkTarget ?? null })),
    edges: db.getEdges().map(e => ({ id: e.id, user: !!e.isUserDefinedId, start: e.start, end: e.end, type: e.type, stroke: e.stroke, text: e.text, style: e.style ?? null })),
    subgraphs: db.getSubGraphs().map(s => ({ id: s.id, title: s.title, nodes: s.nodes })),
  };
}

try {
  console.log(JSON.stringify(await model(text)));
} catch (e) {
  const hasHash = e && typeof e === 'object' && 'hash' in e;
  const cls = e?.constructor?.name ?? typeof e;
  const msg = String(e?.message ?? e).split('\n')[0].slice(0, 160);
  if (hasHash) {
    console.log(JSON.stringify({ parse: false, hash: true, cls, msg }));
  } else {
    let canaryOk = false;
    try { await model(CANARY); canaryOk = true; } catch { canaryOk = false; }
    if (canaryOk) console.log(JSON.stringify({ parse: false, hash: false, canary: 'ok', cls, msg }));
    else { console.log(JSON.stringify({ abort: true, cls, msg })); process.exit(3); }
  }
}
