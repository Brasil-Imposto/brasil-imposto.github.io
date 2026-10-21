// Builds previews/assets/geo-df.json: the 37 Regiões Administrativas (RAs) of the Distrito Federal (GDF official
// layer, IDE-DF), with Goiás and Minas Gerais (their municipalities near the DF, IBGE mesh, dissolved by state) as context, projected once
// (azimuthal equal-area centred on the DF). Same shape as geo-sc.json, so statemap.js draws it unchanged: the RAs go in
// `municipalities` (the DF has no municipalities), each with its official code ("RA-IX") and number.
//
// Inputs (cached in data/df/cache/regions/, fetched 2026-10-02):
//   ra-geoportal.geojson  https://www.geoservicos.ide.df.gov.br/arcgis/rest/services/Publico/LIMITES/MapServer/1/query
//                         ?where=1%3D1&outFields=objectid,ra_cira,ra_nome,ra_codigo,ra_areakm2&returnGeometry=true&outSR=4326&f=geojson
//   mesh-52.json, mesh-31.json  https://servicodados.ibge.gov.br/api/v3/malhas/estados/{52,31}
//                         ?formato=application/vnd.geo%2Bjson&qualidade=intermediaria&intrarregiao=municipio
//   mun-52.json, mun-31.json    https://servicodados.ibge.gov.br/api/v1/localidades/estados/{52,31}/municipios
// Run: node docs/superpowers/tools/build-geo-df.cjs [cache-dir] [--control]
//   --control simplifies every ring on its own (no shared borders); the border check must then fail.
const fs = require('fs');
const path = require('path');
const d3 = require('./vendor/d3.min.js');
const ClipperLib = require('./vendor/clipper.js');

const ASSETS = path.join(__dirname, '../previews/assets');
const args = process.argv.slice(2);
const CONTROL = args.includes('--control');
const CACHE = args.find((a) => !a.startsWith('--')) || path.join(__dirname, '../../../data/df/cache/regions');
const read = (f) => JSON.parse(fs.readFileSync(path.join(CACHE, f), 'utf8'));

const raLayer = read('ra-geoportal.geojson');
// Official names as written in the creating laws (the layer stores them in capitals and without some accents).
// RA I: Lei nº 1.648/1997 ("passa a denominar-se Região Administrativa Plano Piloto"); RA XXXVI: Lei nº 7.918/2026;
// RA XXXVII: Lei nº 7.917/2026; the others as in the IPEDF table of creating laws (PDAD-A 2024, Tabela 2).
const NAMES = {
  1: 'Plano Piloto', 2: 'Gama', 3: 'Taguatinga', 4: 'Brazlândia', 5: 'Sobradinho', 6: 'Planaltina', 7: 'Paranoá',
  8: 'Núcleo Bandeirante', 9: 'Ceilândia', 10: 'Guará', 11: 'Cruzeiro', 12: 'Samambaia', 13: 'Santa Maria',
  14: 'São Sebastião', 15: 'Recanto das Emas', 16: 'Lago Sul', 17: 'Riacho Fundo', 18: 'Lago Norte', 19: 'Candangolândia',
  20: 'Águas Claras', 21: 'Riacho Fundo II', 22: 'Sudoeste/Octogonal', 23: 'Varjão', 24: 'Park Way', 25: 'SCIA/Estrutural',
  26: 'Sobradinho II', 27: 'Jardim Botânico', 28: 'Itapoã', 29: 'SIA', 30: 'Vicente Pires', 31: 'Fercal',
  32: 'Sol Nascente/Pôr do Sol', 33: 'Arniqueira', 34: 'Arapoanga', 35: 'Água Quente', 36: '26 de Setembro', 37: 'Ponte Alta',
};
const roman = (n) => [[10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']].reduce((s, [v, r]) => { while (n >= v) { s += r; n -= v; } return s; }, '');

const projection = d3.geoAzimuthalEqualArea().rotate([47.8, 15.78]).scale(1).translate([0, 0]);
const polygonsOf = (g) => (g.type === 'Polygon' ? [g.coordinates] : g.type === 'MultiPolygon' ? g.coordinates : []);
const openRing = (r) => { const x = r.slice(); const [a, b] = [x[0], x[x.length - 1]]; if (a[0] === b[0] && a[1] === b[1]) x.pop(); return x; };
const ringArea = (r) => { let s = 0; for (let i = 0, j = r.length - 1; i < r.length; j = i++) s += (r[j][0] - r[i][0]) * (r[j][1] + r[i][1]); return Math.abs(s / 2); };
const polyArea = (p) => ringArea(p[0]) - p.slice(1).reduce((s, h) => s + ringArea(h), 0);
const bbox = (r) => r.reduce(([a, b, c, d], [x, y]) => [Math.min(a, x), Math.min(b, y), Math.max(c, x), Math.max(d, y)], [Infinity, Infinity, -Infinity, -Infinity]);

let x0 = Infinity, x1 = -Infinity;
for (const f of raLayer.features) for (const p of polygonsOf(f.geometry)) for (const c of p[0]) { const [x] = projection(c); x0 = Math.min(x0, x); x1 = Math.max(x1, x); }
const K = 100 / (x1 - x0);
const KM_PER_UNIT = 6371.0088 / K;
const round = (v) => Math.round(v * 1000) / 1000;
const proj = (c) => { const [x, y] = projection(c); return [x * K, -y * K]; };

// ---- Topology-preserving simplification. Neighbouring RAs share their border vertices in the GDF layer, so each ring
// is cut at the vertices where the set of rings that use it changes, and every piece (an arc between two such points) is
// simplified once in a canonical direction: both neighbours then get the very same simplified border, with no gaps.
const TOLERANCE = 0.025; // map units (about 24 m)
const key = (c) => `${c[0].toFixed(7)},${c[1].toFixed(7)}`;
const rings = []; // { ra, poly, idx, pts: [[lon,lat]] }
raLayer.features.forEach((f, ra) => polygonsOf(f.geometry).forEach((p, pi) => p.forEach((r, ri) => rings.push({ ra, poly: pi, idx: ri, pts: openRing(r) }))));
const users = new Map();
rings.forEach((r, i) => r.pts.forEach((c) => { const k = key(c); if (!users.has(k)) users.set(k, new Set()); users.get(k).add(i); }));
const sig = (c) => [...users.get(key(c))].sort((a, b) => a - b).join('|');

function douglasPeucker(pts, tol) {
  if (pts.length <= 2) return pts.slice();
  const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length - 1] = 1;
  const stack = [[0, pts.length - 1]];
  while (stack.length) {
    const [a, b] = stack.pop(); const [ax, ay] = pts[a], [bx, by] = pts[b];
    const dx = bx - ax, dy = by - ay, len2 = dx * dx + dy * dy;
    let best = -1, bestD = 0;
    for (let i = a + 1; i < b; i++) {
      const [px, py] = pts[i];
      let t = len2 ? ((px - ax) * dx + (py - ay) * dy) / len2 : 0; t = Math.max(0, Math.min(1, t));
      const ex = ax + t * dx - px, ey = ay + t * dy - py, d = ex * ex + ey * ey;
      if (d > bestD) { bestD = d; best = i; }
    }
    if (best > 0 && bestD > tol * tol) { keep[best] = 1; stack.push([a, best], [best, b]); }
  }
  return pts.filter((_, i) => keep[i]);
}
function simplifyRing(r) {
  const P = r.pts.map(proj); const n = P.length;
  let fixed = [];
  if (!CONTROL) for (let i = 0; i < n; i++) {
    const s = sig(r.pts[i]);
    if (s.includes('|') && (s !== sig(r.pts[(i + n - 1) % n]) || s !== sig(r.pts[(i + 1) % n]) || s.split('|').length > 2)) fixed.push(i);
  }
  if (fixed.length < 2) { // a ring with no junctions: anchor it at its first point and the point farthest from it
    let far = 0, fd = -1; P.forEach(([x, y], i) => { const d = (x - P[0][0]) ** 2 + (y - P[0][1]) ** 2; if (d > fd) { fd = d; far = i; } });
    fixed = [...new Set([...fixed, 0, far])].sort((a, b) => a - b);
  }
  const out = [];
  for (let j = 0; j < fixed.length; j++) {
    const a = fixed[j], b = fixed[(j + 1) % fixed.length];
    const idx = []; for (let i = a; ; i = (i + 1) % n) { idx.push(i); if (i === b) break; }
    let chain = idx.map((i) => P[i]);
    const flip = key(r.pts[a]) > key(r.pts[b]) || (key(r.pts[a]) === key(r.pts[b]) && key(r.pts[idx[1]]) > key(r.pts[idx[idx.length - 2]]));
    if (flip) chain.reverse();
    chain = douglasPeucker(chain, TOLERANCE);
    if (flip) chain.reverse();
    out.push(...chain.slice(0, -1));
  }
  return out.map(([x, y]) => [round(x), round(y)]);
}

// Pole of inaccessibility (Mapbox polylabel), so a label or pin sits inside its region.
function dist(x, y, poly) {
  let inside = false, min = Infinity;
  for (const ring of poly) for (let i = 0, n = ring.length, j = n - 1; i < n; j = i++) {
    const a = ring[i], b = ring[j];
    if ((a[1] > y) !== (b[1] > y) && x < ((b[0] - a[0]) * (y - a[1])) / (b[1] - a[1]) + a[0]) inside = !inside;
    let px = b[0], py = b[1], dx = a[0] - px, dy = a[1] - py;
    if (dx || dy) { const t = ((x - px) * dx + (y - py) * dy) / (dx * dx + dy * dy); if (t > 1) { px = a[0]; py = a[1]; } else if (t > 0) { px += dx * t; py += dy * t; } }
    min = Math.min(min, (x - px) ** 2 + (y - py) ** 2);
  }
  return (inside ? 1 : -1) * Math.sqrt(min);
}
function polylabel(poly, precision = 0.02) {
  const [a, b, c, d] = bbox(poly[0]); const w = c - a, h = d - b, size = Math.min(w, h);
  const cell = (x, y, s) => { const dd = dist(x, y, poly); return { x, y, s, d: dd, max: dd + s * Math.SQRT2 }; };
  let best = cell(a + w / 2, b + h / 2, 0); const q = [];
  for (let x = a; x < c; x += size) for (let y = b; y < d; y += size) q.push(cell(x + size / 2, y + size / 2, size / 2));
  while (q.length) {
    q.sort((m, n) => m.max - n.max); const k = q.pop();
    if (k.d > best.d) best = k;
    if (k.max - best.d <= precision) continue;
    const s = k.s / 2; q.push(cell(k.x - s, k.y - s, s), cell(k.x + s, k.y - s, s), cell(k.x - s, k.y + s, s), cell(k.x + s, k.y + s, s));
  }
  return [round(best.x), round(best.y)];
}

const simplified = rings.map(simplifyRing);
const municipalities = raLayer.features.map((f, ra) => {
  const number = f.properties.ra_cira;
  const polys = [];
  rings.forEach((r, i) => { if (r.ra !== ra) return; (polys[r.poly] = polys[r.poly] || [])[r.idx] = simplified[i]; });
  const largest = polys.reduce((m, n) => (polyArea(n) > polyArea(m) ? n : m));
  return { code: `RA-${roman(number)}`, number, name: NAMES[number], area: round(polys.reduce((s, p) => s + polyArea(p), 0)), label: polylabel(largest), polys };
}).sort((a, b) => a.number - b.number);

// ---- Context: the GO and MG municipalities that border the DF or reach a window around it (IBGE mesh), whole, as SC
// keeps its whole neighbours, so no hole opens beside the DF. `borders` says which ones touch it. Their names sit near
// the DF: the label is the pole of the part inside the window.
const allX = [], allY = [];
for (const m of municipalities) for (const p of m.polys) for (const [x, y] of p[0]) { allX.push(x); allY.push(y); }
const bounds = [round(Math.min(...allX)), round(Math.min(...allY)), round(Math.max(...allX)), round(Math.max(...allY))];
const NEAR = 1.5; // map units: a municipality counts as a neighbour when it comes this close to an RA (about 1.4 km)
const WINDOW = 12; // map units around the DF where context labels may sit
const SCALE = 1000;
const toPath = (ring) => ring.map(([x, y]) => ({ X: Math.round(x * SCALE), Y: Math.round(y * SCALE) }));
const raPaths = []; for (const m of municipalities) for (const p of m.polys) raPaths.push(toPath(p[0]));
const union = (() => { const c = new ClipperLib.Clipper(); c.AddPaths(raPaths, ClipperLib.PolyType.ptSubject, true); const s = new ClipperLib.Paths(); c.Execute(ClipperLib.ClipType.ctUnion, s, ClipperLib.PolyFillType.pftNonZero, ClipperLib.PolyFillType.pftNonZero); return s; })();
const grown = (() => { const o = new ClipperLib.ClipperOffset(); o.AddPaths(union, ClipperLib.JoinType.jtRound, ClipperLib.EndType.etClosedPolygon); const s = new ClipperLib.Paths(); o.Execute(s, NEAR * SCALE); return s; })();
const clip = (subj, clipPaths) => { const c = new ClipperLib.Clipper(); c.AddPaths(subj, ClipperLib.PolyType.ptSubject, true); c.AddPaths(clipPaths, ClipperLib.PolyType.ptClip, true); const s = new ClipperLib.Paths(); c.Execute(ClipperLib.ClipType.ctIntersection, s, ClipperLib.PolyFillType.pftNonZero, ClipperLib.PolyFillType.pftNonZero); return s; };
const [bx0, by0, bx1, by1] = bounds;
const windowPath = [[{ X: (bx0 - WINDOW) * SCALE, Y: (by0 - WINDOW) * SCALE }, { X: (bx1 + WINDOW) * SCALE, Y: (by0 - WINDOW) * SCALE }, { X: (bx1 + WINDOW) * SCALE, Y: (by1 + WINDOW) * SCALE }, { X: (bx0 - WINDOW) * SCALE, Y: (by1 + WINDOW) * SCALE }]];
// The neighbours show their state's name, as SC's do. The municipalities that reach the window are
// dissolved into one shape per state (Goiás, Minas Gerais); `neighbours` keeps the municipality list for the checks.
const context = [], neighbours = [], failures0 = [];
const inside = ([x, y], ring) => { let c = false; for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) { const [x1, y1] = ring[i], [x2, y2] = ring[j]; if ((y1 > y) !== (y2 > y) && x < ((x2 - x1) * (y - y1)) / (y2 - y1) + x1) c = !c; } return c; };
const fromPath = (p) => p.map(({ X, Y }) => [round(X / SCALE), round(Y / SCALE)]);
for (const [uf, sigla, state] of [['52', 'GO', 'Goiás'], ['31', 'MG', 'Minas Gerais']]) {
  const mesh = read(`mesh-${uf}.json`);
  const names = Object.fromEntries(read(`mun-${uf}.json`).map((m) => [String(m.id), m.nome]));
  const rings = [], near = [];
  for (const f of mesh.features) {
    const polys = polygonsOf(f.geometry).map((p) => p.map((r) => openRing(r).map(proj).map(([x, y]) => [round(x), round(y)])));
    const borders = polys.some((p) => clip([toPath(p[0])], grown).length > 0);
    const inWindow = []; for (const p of polys) for (const piece of clip([toPath(p[0])], windowPath)) inWindow.push(piece.map(({ X, Y }) => [X / SCALE, Y / SCALE]));
    if (!inWindow.length) continue;
    neighbours.push({ name: names[String(f.properties.codarea)] || String(f.properties.codarea), uf: sigla, borders });
    for (const p of polys) for (const r of p) rings.push(toPath(r));
    near.push(...inWindow);
  }
  if (!rings.length) continue;
  const c = new ClipperLib.Clipper(); c.AddPaths(rings, ClipperLib.PolyType.ptSubject, true);
  const tree = new ClipperLib.PolyTree(); c.Execute(ClipperLib.ClipType.ctUnion, tree, ClipperLib.PolyFillType.pftNonZero, ClipperLib.PolyFillType.pftNonZero);
  const polys = ClipperLib.JS.PolyTreeToExPolygons(tree).map((e) => [fromPath(e.outer), ...e.holes.map(fromPath)]);
  // The label sits just across the DF's border, like SC's neighbours: Goiás above the DF's straight northern edge (the
  // top margin is the only one the camera leaves at every width; Goiás surrounds the DF on three sides), Minas Gerais
  // beside the DF's south-east corner, the only place it touches (Cabeceira Grande), at the height of the southern edge.
  const label = sigla === 'GO' ? [round((bounds[0] + bounds[2]) / 2), round(bounds[3] + 4.5)] : [round(bounds[2] + 7.3), round(bounds[1] + 1.2)];
  if (!polys.some((p) => inside(label, p[0]))) failures0.push(`${state} label ${label.join(' ')} is not inside ${state}`);
  context.push({ code: uf, name: state, uf: sigla, kind: 'state', polys, label });
}
neighbours.sort((a, b) => a.name.localeCompare(b.name, 'pt'));

// ---- Checks (the script writes nothing unless they pass).
const failures = [...failures0];
if (municipalities.length !== 37) failures.push(`expected 37 RAs, got ${municipalities.length}`);
const km2 = (units2) => units2 * KM_PER_UNIT * KM_PER_UNIT;
const totalKm2 = km2(municipalities.reduce((s, m) => s + m.area, 0));
// IBGE territorial area of the DF (Área Territorial 2024): 5.760,784 km².
if (Math.abs(totalKm2 / 5760.784 - 1) > 0.01) failures.push(`RA area sum ${totalKm2.toFixed(1)} km² is more than 1% from the DF's 5,760.8 km²`);
// The two RAs of July 2026 against the area in their laws' memoriais descritivos.
for (const [n, ha] of [[36, 1389.3555], [37, 5491.6281]]) {
  const m = municipalities.find((x) => x.number === n); const a = km2(m.area) * 100;
  if (Math.abs(a / ha - 1) > 0.01) failures.push(`${m.name}: ${a.toFixed(1)} ha vs ${ha} ha in the law`);
}
// Shared borders: an edge used by only one ring must lie on the DF's outer limit. Their total length must stay close
// to the outer perimeter; with independently simplified rings it jumps (gaps and overlaps along every border).
const edgeCount = new Map(); let perimeter = 0;
for (const m of municipalities) for (const p of m.polys) for (const r of p) for (let i = 0; i < r.length; i++) {
  const a = r[i].join(','), b = r[(i + 1) % r.length].join(','); const k = a < b ? a + ';' + b : b + ';' + a;
  edgeCount.set(k, (edgeCount.get(k) || 0) + 1);
}
for (const [k, c] of edgeCount) if (c === 1) { const [a, b] = k.split(';').map((s) => s.split(',').map(Number)); perimeter += Math.hypot(a[0] - b[0], a[1] - b[1]); }
const outer = union.reduce((s, r) => s + r.reduce((t, p, i) => { const q = r[(i + 1) % r.length]; return t + Math.hypot(p.X - q.X, p.Y - q.Y) / SCALE; }, 0), 0);
if (perimeter > outer * 1.15) failures.push(`unshared edges add up to ${perimeter.toFixed(1)} units against an outer limit of ${outer.toFixed(1)}: borders do not match`);
if (neighbours.filter((c) => c.borders).length < 10) failures.push(`only ${neighbours.filter((c) => c.borders).length} municipalities border the DF`);
if (context.length !== 2) failures.push(`expected Goiás and Minas Gerais as context, got ${context.map((c) => c.name).join(', ')}`);
console.log('RAs', municipalities.length, '| area km²', totalKm2.toFixed(1), '| unshared edges', perimeter.toFixed(1), 'vs outer limit', outer.toFixed(1),
  '| context', context.map((c) => `${c.name} (${c.polys.length} pieces, label ${c.label.join(' ')})`).join(', '),
  '| neighbours', neighbours.map((c) => `${c.name} (${c.uf})${c.borders ? '*' : ''}`).join(', '));
if (failures.length) { console.error('CHECKS FAILED:\n- ' + failures.join('\n- ')); process.exit(1); }
if (CONTROL) { console.error('control run passed the checks: the border check is not working'); process.exit(2); }

const out = {
  meta: {
    projection: 'azimuthal equal-area, rotate [47.8, 15.78]; DF = 100 units wide', kmPerUnit: round(KM_PER_UNIT),
    unit: 'região administrativa', note: 'The DF has no municipalities: `municipalities` holds its 37 Regiões Administrativas (code = official RA code).',
    sources: ['GDF, IDE-DF (SEDUH), geoserviço LIMITES, camada Regiões Administrativas (37 RAs, com as Leis nº 7.917 e 7.918 de 2026)',
      'IBGE, API de malhas v3, municípios de GO e MG, qualidade intermediária', 'IBGE, API de localidades (nomes)'],
    simplification: `Douglas-Peucker on shared arcs, tolerance ${TOLERANCE} units (${Math.round(TOLERANCE * KM_PER_UNIT * 1000)} m)`,
  },
  bounds, municipalities, context,
};
fs.writeFileSync(path.join(ASSETS, 'geo-df.json'), JSON.stringify(out));
console.log('bounds', bounds.join(' '), 'kmPerUnit', round(KM_PER_UNIT), 'KB', Math.round(fs.statSync(path.join(ASSETS, 'geo-df.json')).size / 1024));
