// Builds previews/assets/geo-<uf>.json: the municipalities of a state (IBGE mesh), with the neighbouring states and
// countries as context, projected once (azimuthal equal-area centred on the state). One entry in STATES per state map.
// Inputs (IBGE): https://servicodados.ibge.gov.br/api/v3/malhas/estados/<code>?formato=application/vnd.geo+json&qualidade=intermediaria&intrarregiao=municipio
//                https://servicodados.ibge.gov.br/api/v1/localidades/estados/<code>/municipios
// Run: node docs/superpowers/tools/build-geo-state.cjs <UF> <mesh.json> <names.json>
const fs = require('fs');
const path = require('path');
const d3 = require('./vendor/d3.min.js');
const topojson = require('./vendor/topojson-client.min.js');

const ASSETS = path.join(__dirname, '../previews/assets');
const [UF, meshFile, namesFile] = process.argv.slice(2);
// rotate: projection centre; frame: [west, south, east, north] in degrees for the context; states: IBGE code -> name;
// countries: Natural Earth id -> name; near(mx0, my0, mx1, my1): label positions just across the state's border.
const STATES = {
  SC: { code: '42', count: 295, rotate: [50.5, 27.3], frame: [-55.5, -30.5, -46.5, -24.5],
    states: { 41: 'Paraná', 43: 'Rio Grande do Sul', 35: 'São Paulo' }, countries: { '032': 'Argentina' },
    near: (mx0, my0, mx1, my1) => ({ 'Paraná': [mx0 + (mx1 - mx0) * 0.45, my1 + 6], 'Rio Grande do Sul': [mx0 + (mx1 - mx0) * 0.4, my0 + 6], 'Argentina': [mx0 - 11, my0 + (my1 - my0) * 0.82] }),
    // D83: Argentina sat over the north-west of Rio Grande do Sul; now west of SC's western tip, inside Argentina.
    sources: ['IBGE, API de malhas v3, municípios de SC, qualidade intermediária', 'IBGE, API de localidades (nomes)', 'Natural Earth 1:50m (Argentina)'] },
  RS: { code: '43', count: 497, rotate: [53.3, 30.4], frame: [-59.5, -35.5, -47.5, -25.5],
    states: { 42: 'Santa Catarina', 41: 'Paraná' }, countries: { '032': 'Argentina', 858: 'Uruguai' },
    near: (mx0, my0, mx1, my1) => ({ 'Santa Catarina': [mx0 + (mx1 - mx0) * 0.62, my1 + 5], 'Argentina': [mx0 + (mx1 - mx0) * 0.12, my1 - (my1 - my0) * 0.08], 'Uruguai': [mx0 + (mx1 - mx0) * 0.15, my0 + (my1 - my0) * 0.09] }),
    sources: ['IBGE, API de malhas v3, municípios do RS, qualidade intermediária', 'IBGE, API de localidades (nomes)', 'Natural Earth 1:50m (Argentina e Uruguai)'] },
};
const S = STATES[UF];
if (!S) { console.error(`unknown state ${UF}; known: ${Object.keys(STATES).join(', ')}`); process.exit(1); }
const mesh = JSON.parse(fs.readFileSync(meshFile, 'utf8'));
const names = Object.fromEntries(JSON.parse(fs.readFileSync(namesFile, 'utf8')).map((m) => [String(m.id), m.nome]));
const ufMesh = JSON.parse(fs.readFileSync(path.join(ASSETS, 'ibge-uf-intermediaria.geojson'), 'utf8'));
const world = JSON.parse(fs.readFileSync(path.join(ASSETS, 'countries-50m.json'), 'utf8'));

const projection = d3.geoAzimuthalEqualArea().rotate(S.rotate).scale(1).translate([0, 0]);
const polygonsOf = (g) => (g.type === 'Polygon' ? [g.coordinates] : g.type === 'MultiPolygon' ? g.coordinates : []);
const openRing = (r) => { const x = r.slice(); const [a, b] = [x[0], x[x.length - 1]]; if (a[0] === b[0] && a[1] === b[1]) x.pop(); return x; };
const ringArea = (r) => { let s = 0; for (let i = 0, j = r.length - 1; i < r.length; j = i++) s += (r[j][0] - r[i][0]) * (r[j][1] + r[i][1]); return Math.abs(s / 2); };
const bbox = (r) => r.reduce(([a, b, c, d], [x, y]) => [Math.min(a, x), Math.min(b, y), Math.max(c, x), Math.max(d, y)], [Infinity, Infinity, -Infinity, -Infinity]);

let x0 = Infinity, x1 = -Infinity;
for (const f of mesh.features) for (const p of polygonsOf(f.geometry)) for (const c of p[0]) { const [x] = projection(c); x0 = Math.min(x0, x); x1 = Math.max(x1, x); }
const K = 100 / (x1 - x0);
const round = (v) => Math.round(v * 1000) / 1000;
const project = (ring) => openRing(ring).map((c) => { const [x, y] = projection(c); return [round(x * K), round(-y * K)]; });

// Pole of inaccessibility (Mapbox polylabel), so a label or pin sits inside its municipality.
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

const municipalities = mesh.features.map((f) => {
  const code = String(f.properties.codarea);
  const polys = polygonsOf(f.geometry).map((p) => p.map(project));
  const largest = polys.reduce((m, n) => (ringArea(n[0]) > ringArea(m[0]) ? n : m));
  return { code, name: names[code] || code, area: round(polys.reduce((s, p) => s + ringArea(p[0]), 0)), label: polylabel(largest), polys };
}).sort((a, b) => a.code.localeCompare(b.code));

// Context: the neighbouring states from the IBGE state mesh and Argentina from Natural Earth, clipped to a frame.
const FRAME = S.frame;
const inFrame = (ring) => { const [a, b, c, d] = bbox(ring); return c >= FRAME[0] && a <= FRAME[2] && d >= FRAME[1] && b <= FRAME[3]; };
const context = [];
for (const f of ufMesh.features) {
  const code = String(f.properties.codarea);
  if (code === S.code) continue;
  const polys = polygonsOf(f.geometry).filter((p) => inFrame(p[0])).map((p) => p.map(project));
  if (polys.length) context.push({ name: S.states[code] || code, kind: 'state', polys });
}
for (const [id, name] of Object.entries(S.countries)) {
  const c = topojson.feature(world, world.objects.countries).features.find((f) => f.id === id);
  context.push({ name, kind: 'country', polys: polygonsOf(c.geometry).filter((p) => inFrame(p[0])).map((p) => p.map(project)) });
}
for (const c of context) {
  const largest = c.polys.reduce((m, n) => (ringArea(n[0]) > ringArea(m[0]) ? n : m));
  c.label = polylabel(largest, 0.2);
}
// The neighbours' own centres fall outside the frame, so their names sit just across SC's border.
{
  const xs = [], ys = [];
  for (const m of municipalities) for (const p of m.polys) for (const [x, y] of p[0]) { xs.push(x); ys.push(y); }
  const [mx0, my0, mx1, my1] = [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
  const NEAR = S.near(mx0, my0, mx1, my1);
  for (const c of context) if (NEAR[c.name]) c.label = NEAR[c.name].map(round);
}
// Every placed name must fall inside its own state or country (a name over the neighbour, or over the state, misleads).
const inside = ([x, y], ring) => { let c = false; for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) { const [x1, y1] = ring[i], [x2, y2] = ring[j]; if ((y1 > y) !== (y2 > y) && x < ((x2 - x1) * (y - y1)) / (y2 - y1) + x1) c = !c; } return c; };
const outside = context.filter((c) => !c.polys.some((p) => inside(c.label, p[0])));
if (outside.length) { console.error(`labels outside their own area: ${outside.map((c) => `${c.name} ${c.label.join(' ')}`).join(', ')}`); process.exit(1); }

const allX = [], allY = [];
for (const m of municipalities) for (const p of m.polys) for (const [x, y] of p[0]) { allX.push(x); allY.push(y); }
const out = {
  meta: { projection: `azimuthal equal-area, rotate [${S.rotate.join(', ')}]; ${UF} = 100 units wide`, kmPerUnit: round(6371.0088 / K),
          sources: S.sources },
  bounds: [round(Math.min(...allX)), round(Math.min(...allY)), round(Math.max(...allX)), round(Math.max(...allY))],
  municipalities, context,
};
if (municipalities.length !== S.count) { console.error(`expected ${S.count} municipalities in ${UF}, got ${municipalities.length}`); process.exit(1); }
const unnamed = municipalities.filter((m) => m.name === m.code);
if (unnamed.length) { console.error(`${unnamed.length} municipalities without an IBGE name`); process.exit(1); }
const OUT = path.join(ASSETS, `geo-${UF.toLowerCase()}.json`);
fs.writeFileSync(OUT, JSON.stringify(out));
console.log('municipalities', municipalities.length, 'context', context.map((c) => c.name).join(', '), 'bounds', out.bounds.join(' '),
  'KB', Math.round(fs.statSync(OUT).size / 1024));
