// Rebuilds the `context` of previews/assets/geo-<uf>.json (sc, rs, df): every Brazilian state and every country inside a
// window around the state, in one neutral layer, so the state map never shows white where there is land (D101).
// Brazilian states: IBGE state mesh (assets/ibge-uf-intermediaria.geojson). Countries: Natural Earth 1:50m
// (assets/countries-50m.json), grown by 3 km and cut at Brazil's IBGE border, so the two sources meet with no gap and no
// overlap. Municipalities, bounds and projection in the file are kept as they are; the projection is rebuilt from the
// file's own metadata (rotate and km per unit). Run after build-geo-state.cjs or build-geo-df.cjs.
// Checks: the main state's IBGE outline, projected again, matches the municipalities' bounds (median edge within 0.25
// units; proves the rebuilt projection); every name sits inside its own area. --control shifts the projection by 3 units: the alignment
// check must fail. Run: node docs/superpowers/tools/build-geo-context.cjs <sc|rs|df> [--control]
const fs = require('fs');
const path = require('path');
const d3 = require('./vendor/d3.min.js');
const topojson = require('./vendor/topojson-client.min.js');
const ClipperLib = require('./vendor/clipper.js');

const ASSETS = path.join(__dirname, '../previews/assets');
const args = process.argv.slice(2);
const UF = (args.find((a) => !a.startsWith('--')) || '').toLowerCase();
const CONTROL = args.includes('--control');
const MAIN = { sc: '42', rs: '43', df: '53' }[UF];
if (!MAIN) { console.error('usage: build-geo-context.cjs <sc|rs|df> [--control]'); process.exit(1); }
const FILE = path.join(ASSETS, `geo-${UF}.json`);
const geo = JSON.parse(fs.readFileSync(FILE, 'utf8'));

const UF_NAMES = { 11: 'Rondônia', 12: 'Acre', 13: 'Amazonas', 14: 'Roraima', 15: 'Pará', 16: 'Amapá', 17: 'Tocantins', 21: 'Maranhão', 22: 'Piauí',
  23: 'Ceará', 24: 'Rio Grande do Norte', 25: 'Paraíba', 26: 'Pernambuco', 27: 'Alagoas', 28: 'Sergipe', 29: 'Bahia', 31: 'Minas Gerais',
  32: 'Espírito Santo', 33: 'Rio de Janeiro', 35: 'São Paulo', 41: 'Paraná', 42: 'Santa Catarina', 43: 'Rio Grande do Sul',
  50: 'Mato Grosso do Sul', 51: 'Mato Grosso', 52: 'Goiás', 53: 'Distrito Federal' };
const COUNTRY_NAMES = { '032': 'Argentina', 858: 'Uruguai', 600: 'Paraguai', '068': 'Bolívia', 152: 'Chile', 604: 'Peru' };

const rotate = geo.meta.projection.match(/rotate \[([-\d.]+), ([-\d.]+)\]/).slice(1).map(Number);
const K = 6371.0088 / geo.meta.kmPerUnit;
const projection = d3.geoAzimuthalEqualArea().rotate(rotate).scale(1).translate([0, 0]);
const shift = CONTROL ? 3 : 0;
const P = (c) => { const [x, y] = projection(c); return [x * K + shift, -y * K]; };
const polygonsOf = (g) => (g.type === 'Polygon' ? [g.coordinates] : g.type === 'MultiPolygon' ? g.coordinates : []);
const openRing = (r) => { const x = r.slice(); const a = x[0], b = x[x.length - 1]; if (a[0] === b[0] && a[1] === b[1]) x.pop(); return x; };
const round = (v) => Math.round(v * 1000) / 1000;
const SCALE = 1000;
const toPath = (ring) => ring.map(([x, y]) => ({ X: Math.round(x * SCALE), Y: Math.round(y * SCALE) }));
const fromPath = (p) => p.map(({ X, Y }) => [round(X / SCALE), round(Y / SCALE)]);
const run = (type, subj, clip, fillS = ClipperLib.PolyFillType.pftNonZero) => {
  const c = new ClipperLib.Clipper(); c.AddPaths(subj, ClipperLib.PolyType.ptSubject, true);
  if (clip) c.AddPaths(clip, ClipperLib.PolyType.ptClip, true);
  const t = new ClipperLib.PolyTree(); c.Execute(type, t, fillS, ClipperLib.PolyFillType.pftNonZero); return t;
};
const exPolys = (tree) => ClipperLib.JS.PolyTreeToExPolygons(tree);
const asPaths = (ex) => ex.flatMap((e) => [e.outer, ...e.holes]);
// One polygon's rings as Clipper paths with outer and holes oriented the Clipper way (even-odd resolves the holes).
const polyPaths = (poly) => asPaths(exPolys(run(ClipperLib.ClipType.ctUnion, poly.map((r) => toPath(openRing(r).map(P))), null, ClipperLib.PolyFillType.pftEvenOdd)));
const bbox = (pts) => pts.reduce(([a, b, c, d], [x, y]) => [Math.min(a, x), Math.min(b, y), Math.max(c, x), Math.max(d, y)], [Infinity, Infinity, -Infinity, -Infinity]);

const ufMesh = JSON.parse(fs.readFileSync(path.join(ASSETS, 'ibge-uf-intermediaria.geojson'), 'utf8'));
const world = JSON.parse(fs.readFileSync(path.join(ASSETS, 'countries-50m.json'), 'utf8'));

// Alignment: the main state's IBGE outline against the municipalities' bounds.
const mainF = ufMesh.features.find((f) => String(f.properties.codarea) === MAIN);
const mainPts = polygonsOf(mainF.geometry).flatMap((p) => openRing(p[0]).map(P));
const mb = bbox(mainPts), gb = geo.bounds;
// IBGE generalizes its state mesh and its municipal mesh differently at extreme points, so the check is the median edge.
const diffs = mb.map((v, i) => Math.abs(v - gb[i])).sort((a, b) => a - b), align = (diffs[1] + diffs[2]) / 2;
if (align > 0.25) { console.error(`CHECK FAILED: the rebuilt projection is off by ${align.toFixed(3)} units`); process.exit(1); }
if (CONTROL) { console.error('control run passed the alignment check: the check is not working'); process.exit(2); }

const [bx0, by0, bx1, by1] = gb, W = bx1 - bx0, H = by1 - by0;
const win = [bx0 - 1.2 * W, by0 - 1.2 * H, bx1 + 1.2 * W, by1 + 1.2 * H];
const winPath = [[{ X: win[0] * SCALE, Y: win[1] * SCALE }, { X: win[2] * SCALE, Y: win[1] * SCALE }, { X: win[2] * SCALE, Y: win[3] * SCALE }, { X: win[0] * SCALE, Y: win[3] * SCALE }]];
const inner = [bx0 - 0.35 * W, by0 - 0.35 * H, bx1 + 0.35 * W, by1 + 0.35 * H];
const innerPath = [[{ X: inner[0] * SCALE, Y: inner[1] * SCALE }, { X: inner[2] * SCALE, Y: inner[1] * SCALE }, { X: inner[2] * SCALE, Y: inner[3] * SCALE }, { X: inner[0] * SCALE, Y: inner[3] * SCALE }]];
const near = (pts) => { const [a, b, c, d] = bbox(pts); return c >= win[0] && a <= win[2] && d >= win[1] && b <= win[3]; };

const context = [];
const brazil = [];
for (const f of ufMesh.features) {
  const code = String(f.properties.codarea);
  const paths = polygonsOf(f.geometry).flatMap(polyPaths);
  brazil.push(...paths);
  if (code === MAIN) continue;
  const ex = exPolys(run(ClipperLib.ClipType.ctIntersection, paths, winPath));
  if (ex.length) context.push({ name: UF_NAMES[code] || code, kind: 'state', ex, paths });
}
const brazilUnion = asPaths(exPolys(run(ClipperLib.ClipType.ctUnion, brazil, null)));
const GROW = (3 / geo.meta.kmPerUnit) * SCALE;
const lon = -rotate[0], lat = -rotate[1];
for (const f of topojson.feature(world, world.objects.countries).features) {
  if (f.id === '076') continue;
  const polys = polygonsOf(f.geometry).filter((p) => p[0].some(([x, y]) => Math.abs(x - lon) < 30 && Math.abs(y - lat) < 25));
  if (!polys.length || !polys.some((p) => near(openRing(p[0]).map(P)))) continue;
  const paths = polys.flatMap(polyPaths);
  const co = new ClipperLib.ClipperOffset(2, 0.25 * SCALE); co.AddPaths(paths, ClipperLib.JoinType.jtRound, ClipperLib.EndType.etClosedPolygon);
  const grown = new ClipperLib.Paths(); co.Execute(grown, GROW);
  const cut = asPaths(exPolys(run(ClipperLib.ClipType.ctDifference, grown, brazilUnion)));
  const ex = exPolys(run(ClipperLib.ClipType.ctIntersection, cut, winPath));
  if (ex.length) context.push({ name: COUNTRY_NAMES[f.id] || null, kind: 'country', ex, paths: cut });
}

// Names: the label already placed for a neighbour (just across the state's border, D83) is kept when it falls inside the
// new shape; any other neighbour gets the pole of inaccessibility of its part inside the inner window, when it has one.
const inside = ([x, y], ring) => { let c = false; for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) { const [x1, y1] = ring[i], [x2, y2] = ring[j]; if ((y1 > y) !== (y2 > y) && x < ((x2 - x1) * (y - y1)) / (y2 - y1) + x1) c = !c; } return c; };
const inPoly = (pt, poly) => inside(pt, poly[0]) && !poly.slice(1).some((h) => inside(pt, h));
function dist(x, y, poly) {
  let ins = false, min = Infinity;
  for (const ring of poly) for (let i = 0, n = ring.length, j = n - 1; i < n; j = i++) {
    const a = ring[i], b = ring[j];
    if ((a[1] > y) !== (b[1] > y) && x < ((b[0] - a[0]) * (y - a[1])) / (b[1] - a[1]) + a[0]) ins = !ins;
    let px = b[0], py = b[1], dx = a[0] - px, dy = a[1] - py;
    if (dx || dy) { const t = ((x - px) * dx + (y - py) * dy) / (dx * dx + dy * dy); if (t > 1) { px = a[0]; py = a[1]; } else if (t > 0) { px += dx * t; py += dy * t; } }
    min = Math.min(min, (x - px) ** 2 + (y - py) ** 2);
  }
  return (ins ? 1 : -1) * Math.sqrt(min);
}
function polylabel(poly, precision = 0.2) {
  const [a, b, c, d] = bbox(poly[0]); const w = c - a, h = d - b, size = Math.min(w, h);
  const cell = (x, y, s) => { const dd = dist(x, y, poly); return { x, y, s, d: dd, max: dd + s * Math.SQRT2 }; };
  let best = cell(a + w / 2, b + h / 2, 0); const q = [];
  for (let x = a; x < c; x += size) for (let y = b; y < d; y += size) q.push(cell(x + size / 2, y + size / 2, size / 2));
  while (q.length) { q.sort((m, n) => m.max - n.max); const k = q.pop(); if (k.d > best.d) best = k; if (k.max - best.d <= precision) continue;
    const s = k.s / 2; q.push(cell(k.x - s, k.y - s, s), cell(k.x + s, k.y - s, s), cell(k.x - s, k.y + s, s), cell(k.x + s, k.y + s, s)); }
  return [round(best.x), round(best.y), best.d];
}
const oldLabel = Object.fromEntries((geo.context || []).filter((c) => c.label).map((c) => [c.name, c.label]));
// Fill: each area grown by 0.3 units, so it runs under the state's own municipalities (drawn higher) and no white sliver
// is left where the two IBGE meshes differ. Lines: the area's own outline, ungrown, without the window's straight edges.
const grow = (paths) => { const co = new ClipperLib.ClipperOffset(2, 0.25 * SCALE); co.AddPaths(paths, ClipperLib.JoinType.jtRound, ClipperLib.EndType.etClosedPolygon); const g = new ClipperLib.Paths(); co.Execute(g, 0.3 * SCALE); return g; };
const onEdge = ([x1, y1], [x2, y2]) => [[0, x1, x2], [2, x1, x2], [1, y1, y2], [3, y1, y2]].some(([i, a, b]) => Math.abs(a - win[i]) < 0.01 && Math.abs(b - win[i]) < 0.01);
const linesOf = (polys) => { const out = []; for (const p of polys) for (const ring of p) { let run = []; for (let i = 0; i <= ring.length; i++) { const a = ring[i % ring.length], b = ring[(i + 1) % ring.length]; if (i < ring.length && !onEdge(a, b)) { if (!run.length) run.push(a); run.push(b); } else if (run.length) { out.push(run); run = []; } } if (run.length > 1) out.push(run); } return out; };
const out = [];
for (const c of context) {
  const polys = c.ex.map((e) => [fromPath(e.outer), ...e.holes.map(fromPath)]);
  const fill = exPolys(run(ClipperLib.ClipType.ctIntersection, grow(asPaths(c.ex)), winPath)).map((e) => [fromPath(e.outer), ...e.holes.map(fromPath)]);
  let label = null;
  if (c.name && oldLabel[c.name] && polys.some((p) => inPoly(oldLabel[c.name], p))) label = oldLabel[c.name];
  else if (c.name) {
    const vis = exPolys(run(ClipperLib.ClipType.ctIntersection, c.paths, innerPath)).map((e) => [fromPath(e.outer), ...e.holes.map(fromPath)]);
    const best = vis.map((p) => polylabel(p)).sort((m, n) => n[2] - m[2])[0];
    if (best && best[2] > 0.06 * Math.min(W, H)) label = [best[0], best[1]];
  }
  out.push({ name: c.name, kind: c.kind, polys: fill, lines: linesOf(polys), label, _own: polys });
}
const bad = out.filter((c) => c.label && !c._own.some((p) => inPoly(c.label, p)));
for (const c of out) delete c._own;
if (bad.length) { console.error(`CHECK FAILED: names outside their own area: ${bad.map((c) => c.name).join(', ')}`); process.exit(1); }
geo.context = out;
geo.meta.context = { sources: ['IBGE, malha dos estados, qualidade intermediária', 'Natural Earth 1:50m (países), ampliada 3 km e cortada na divisa do IBGE'],
  window: 'o estado mais 120% da largura e da altura de cada lado', built_by: 'docs/superpowers/tools/build-geo-context.cjs' };
fs.writeFileSync(FILE, JSON.stringify(geo));
console.log(`${UF}: alignment ${align.toFixed(3)} units; context ${out.length} areas (${out.filter((c) => c.label).map((c) => c.name).join(', ')} named); ${Math.round(fs.statSync(FILE).size / 1024)} KB`);
