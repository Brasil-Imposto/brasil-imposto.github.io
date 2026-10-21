// Builds previews/assets/map-geo.json: IBGE state mesh + Natural Earth neighbours,
// projected once (Equal Earth, central meridian 54°W) so the browser only extrudes.
// Neighbour names are fitted INSIDE each country here, so nothing can overflow its territory.
// Run: node docs/superpowers/tools/build-geo.cjs
const fs = require('fs');
const path = require('path');
const d3 = require('./vendor/d3.min.js');
const topojson = require('./vendor/topojson-client.min.js');
const ClipperLib = require('./vendor/clipper.js');

const ASSETS = path.join(__dirname, '../previews/assets');
const readJson = (f) => JSON.parse(fs.readFileSync(path.join(ASSETS, f), 'utf8'));

const ibgeMesh = readJson('ibge-uf-intermediaria.geojson');
const ibgeStates = readJson('ibge-estados.json');
const world = readJson('countries-50m.json');

const SOUTH_AMERICA = {
  // focus: the point of the flag (0..1 from its left/top) kept visible when the flag is cropped to the territory
  '032': { name: 'Argentina', flag: 'ar', focus: [0.5, 0.5] },
  '068': { name: 'Bolívia', flag: 'bo', focus: [0.5, 0.5] },
  '152': { name: 'Chile', flag: 'cl', focus: [0.17, 0.25] },
  '170': { name: 'Colômbia', flag: 'co', focus: [0.5, 0.4] },
  '218': { name: 'Equador', flag: 'ec', focus: [0.5, 0.45] },
  '250': { name: 'Guiana Francesa', flag: 'fr', focus: [0.5, 0.5], largestOnly: true },
  '328': { name: 'Guiana', flag: 'gy', focus: [0.4, 0.5] },
  '600': { name: 'Paraguai', flag: 'py', focus: [0.5, 0.5] },
  '604': { name: 'Peru', flag: 'pe', focus: [0.5, 0.5] },
  '740': { name: 'Suriname', flag: 'sr', focus: [0.5, 0.5] },
  '858': { name: 'Uruguai', flag: 'uy', focus: [0.18, 0.28] },
  '862': { name: 'Venezuela', flag: 've', focus: [0.5, 0.55] },
};
// Central America and the Caribbean get flag and name too. The Falklands stay neutral:
// the sovereignty dispute is not this site's subject.
const CENTRAL_AMERICA = {
  '591': { name: 'Panamá', flag: 'pa' }, '188': { name: 'Costa Rica', flag: 'cr' }, '558': { name: 'Nicarágua', flag: 'ni' },
  '340': { name: 'Honduras', flag: 'hn' }, '222': { name: 'El Salvador', flag: 'sv' }, '320': { name: 'Guatemala', flag: 'gt' },
  '084': { name: 'Belize', flag: 'bz' }, '484': { name: 'México', flag: 'mx' }, '192': { name: 'Cuba', flag: 'cu' },
  '388': { name: 'Jamaica', flag: 'jm' }, '332': { name: 'Haiti', flag: 'ht' }, '214': { name: 'República Dominicana', flag: 'do' },
  '630': { name: 'Porto Rico', flag: 'pr' }, '780': { name: 'Trinidad e Tobago', flag: 'tt' }, '044': { name: 'Bahamas', flag: 'bs' },
  '533': { name: 'Aruba', flag: 'aw' }, '531': { name: 'Curaçao', flag: 'cw' },
};
// Brazil comes from IBGE. Every other land mass in the frame stays as neutral, unlabelled ground, so Central
// America and the Caribbean connect the continent instead of leaving South America floating like an island.
const NOT_LAND_IN_FRAME = new Set(['076', '840', '124', '010', '239', '132']);
const FRAME = { lonMin: -100, lonMax: -20, latMin: -62, latMax: 28 };

const projection = d3.geoEqualEarth().rotate([54, 0]).scale(1).translate([0, 0]);

const openRing = (ring) => {
  const r = ring.slice();
  const [a, b] = [r[0], r[r.length - 1]];
  if (a[0] === b[0] && a[1] === b[1]) r.pop();
  return r;
};
const polygonsOf = (geometry) =>
  geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.type === 'MultiPolygon' ? geometry.coordinates : [];
const geoBBox = (ring) => {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const [x, y] of ring) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
  return [x0, y0, x1, y1];
};
const inFrame = (ring) => {
  const [x0, y0, x1, y1] = geoBBox(ring);
  return x1 >= FRAME.lonMin && x0 <= FRAME.lonMax && y1 >= FRAME.latMin && y0 <= FRAME.latMax;
};
const ringArea = (ring) => {
  let s = 0;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) s += (ring[j][0] - ring[i][0]) * (ring[j][1] + ring[i][1]);
  return Math.abs(s / 2);
};

// Scale so Brazil is 100 units wide.
let bx0 = Infinity, bx1 = -Infinity;
for (const f of ibgeMesh.features) for (const poly of polygonsOf(f.geometry)) for (const [lon, lat] of poly[0]) {
  const [x] = projection([lon, lat]); bx0 = Math.min(bx0, x); bx1 = Math.max(bx1, x);
}
const K = 100 / (bx1 - bx0);
const round = (v) => Math.round(v * 1000) / 1000;
const project = (ring) => openRing(ring).map(([lon, lat]) => {
  const [x, y] = projection([lon, lat]);
  return [round(x * K), round(-y * K)];
});

// Pole of inaccessibility (Mapbox polylabel algorithm) so each label sits inside its shape.
function pointToPolygonDist(x, y, polygon) {
  let inside = false, minDistSq = Infinity;
  for (const ring of polygon) {
    for (let i = 0, len = ring.length, j = len - 1; i < len; j = i++) {
      const a = ring[i], b = ring[j];
      if ((a[1] > y) !== (b[1] > y) && x < ((b[0] - a[0]) * (y - a[1])) / (b[1] - a[1]) + a[0]) inside = !inside;
      let px = b[0], py = b[1], dx = a[0] - px, dy = a[1] - py;
      if (dx !== 0 || dy !== 0) {
        const t = ((x - px) * dx + (y - py) * dy) / (dx * dx + dy * dy);
        if (t > 1) { px = a[0]; py = a[1]; } else if (t > 0) { px += dx * t; py += dy * t; }
      }
      dx = x - px; dy = y - py;
      minDistSq = Math.min(minDistSq, dx * dx + dy * dy);
    }
  }
  return (inside ? 1 : -1) * Math.sqrt(minDistSq);
}
function polylabel(polygon, precision = 0.05) {
  const [minX, minY, maxX, maxY] = geoBBox(polygon[0]);
  const width = maxX - minX, height = maxY - minY;
  const cellSize = Math.min(width, height);
  const cell = (x, y, h) => { const d = pointToPolygonDist(x, y, polygon); return { x, y, h, d, max: d + h * Math.SQRT2 }; };
  let best = cell(minX + width / 2, minY + height / 2, 0);
  const queue = [];
  for (let x = minX; x < maxX; x += cellSize) for (let y = minY; y < maxY; y += cellSize) queue.push(cell(x + cellSize / 2, y + cellSize / 2, cellSize / 2));
  while (queue.length) {
    queue.sort((a, b) => a.max - b.max);
    const c = queue.pop();
    if (c.d > best.d) best = c;
    if (c.max - best.d <= precision) continue;
    const h = c.h / 2;
    queue.push(cell(c.x - h, c.y - h, h), cell(c.x + h, c.y - h, h), cell(c.x - h, c.y + h, h), cell(c.x + h, c.y + h, h));
  }
  return [round(best.x), round(best.y)];
}

// Largest text box that fits entirely inside a polygon, horizontal or vertical, one or two lines.
// Glyph metrics approximate Manrope 800 uppercase with .12em tracking.
const CHAR_W = 0.84, BOX_H = 1.0, TWO_LINE_H = 2.2;
function insidePoly(x, y, polygon) {
  let inside = false;
  for (const ring of polygon) {
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const a = ring[i], b = ring[j];
      if ((a[1] > y) !== (b[1] > y) && x < ((b[0] - a[0]) * (y - a[1])) / (b[1] - a[1]) + a[0]) inside = !inside;
    }
  }
  return inside;
}
function boxFits(cx, cy, w, h, vertical, polygon) {
  const N = 8;
  for (let i = 0; i <= N; i++) {
    const t = i / N;
    for (const [lx, ly] of [[-w / 2 + t * w, -h / 2], [-w / 2 + t * w, h / 2], [-w / 2, -h / 2 + t * h], [w / 2, -h / 2 + t * h]]) {
      const x = vertical ? cx - ly : cx + lx, y = vertical ? cy + lx : cy + ly;
      if (!insidePoly(x, y, polygon)) return false;
    }
  }
  for (const ring of polygon) for (const [vx, vy] of ring) {
    const dx = vx - cx, dy = vy - cy;
    const lx = vertical ? dy : dx, ly = vertical ? -dx : dy;
    if (Math.abs(lx) < w / 2 && Math.abs(ly) < h / 2) return false;
  }
  return true;
}
function fitLabel(name, polygon, charW = CHAR_W) {
  const upper = name.toUpperCase();
  const layouts = [{ lines: [upper] }];
  const cut = upper.indexOf(' ');
  if (cut > 0) layouts.push({ lines: [upper.slice(0, cut), upper.slice(cut + 1)] });
  const [x0, y0, x1, y1] = geoBBox(polygon[0]);
  const step = Math.max(x1 - x0, y1 - y0) / 40;
  const candidates = [];
  for (let x = x0 + step / 2; x < x1; x += step) for (let y = y0 + step / 2; y < y1; y += step) {
    const d = pointToPolygonDist(x, y, polygon);
    if (d > 0) candidates.push({ x, y, d });
  }
  candidates.sort((a, b) => b.d - a.d);
  const pl = polylabel(polygon);
  const pool = [{ x: pl[0], y: pl[1] }, ...candidates.slice(0, 80)];
  let best = { score: 0 };
  for (const c of pool) for (const vertical of [false, true]) for (const layout of layouts) {
    const longest = Math.max(...layout.lines.map((l) => l.length));
    const hFactor = layout.lines.length === 1 ? BOX_H : TWO_LINE_H;
    let lo = 0, hi = Math.max(x1 - x0, y1 - y0);
    for (let i = 0; i < 16; i++) {
      const f = (lo + hi) / 2;
      if (boxFits(c.x, c.y, longest * charW * f, hFactor * f, vertical, polygon)) lo = f; else hi = f;
    }
    // Horizontal and single-line read better: they win unless the alternative is clearly larger.
    const score = lo * (vertical ? 0.62 : 1) * (layout.lines.length === 1 ? 1 : 0.85);
    if (score > best.score) best = { score, x: round(c.x), y: round(c.y), vertical, font: round(lo * 0.86), lines: layout.lines, charW, tracking: charW < CHAR_W ? 0.03 : 0.12 };
  }
  const { score, ...label } = best;
  return label;
}

// Inset copy of each state for the "separate pieces" option (visible gaps between states).
const CLIP_SCALE = 1000;
function inset(polygon, delta) {
  const co = new ClipperLib.ClipperOffset(2, 0.25 * CLIP_SCALE);
  co.AddPaths(polygon.map((ring) => ring.map(([x, y]) => ({ X: Math.round(x * CLIP_SCALE), Y: Math.round(y * CLIP_SCALE) }))),
    ClipperLib.JoinType.jtRound, ClipperLib.EndType.etClosedPolygon);
  const tree = new ClipperLib.PolyTree();
  co.Execute(tree, -delta * CLIP_SCALE);
  return ClipperLib.JS.PolyTreeToExPolygons(tree).map((ex) =>
    [ex.outer, ...ex.holes].map((ring) => ring.map((p) => [round(p.X / CLIP_SCALE), round(p.Y / CLIP_SCALE)])));
}

const byCode = Object.fromEntries(ibgeStates.map((s) => [String(s.id), s]));
const brazil = ibgeMesh.features.map((f) => {
  const meta = byCode[f.properties.codarea];
  const polys = polygonsOf(f.geometry).map((poly) => poly.map(project));
  const largest = polys.reduce((a, b) => (ringArea(b[0]) > ringArea(a[0]) ? b : a));
  return {
    code: meta.id, uf: meta.sigla, name: meta.nome, region: meta.regiao.sigla,
    area: round(polys.reduce((s, p) => s + ringArea(p[0]), 0)),
    label: polylabel(largest),
    polys,
    inset: polys.flatMap((p) => inset(p, 0.32)),
  };
}).sort((a, b) => a.code - b.code);

const countries = topojson.feature(world, world.objects.countries).features
  .filter((f) => !NOT_LAND_IN_FRAME.has(f.id))
  .map((f) => {
    const sa = SOUTH_AMERICA[f.id] || (CENTRAL_AMERICA[f.id] && { focus: [0.5, 0.5], ...CENTRAL_AMERICA[f.id] });
    let polys = polygonsOf(f.geometry).filter((poly) => inFrame(poly[0])).map((poly) => poly.map(project));
    if (!polys.length) return null;
    const largest = polys.reduce((a, b) => (ringArea(b[0]) > ringArea(a[0]) ? b : a));
    if (sa && sa.largestOnly) polys = [largest];
    return {
      id: f.id, name: sa ? sa.name : f.properties.name, flag: sa ? sa.flag : null,
      named: Boolean(sa), southAmerica: Boolean(SOUTH_AMERICA[f.id]),
      area: round(polys.reduce((s, p) => s + ringArea(p[0]), 0)),
      // Narrow isthmus countries get tighter lettering so their names still fit inside the border.
      nameLabel: sa ? fitLabel(sa.name, largest, SOUTH_AMERICA[f.id] ? CHAR_W : 0.72) : null,
      flagFocus: sa ? sa.focus : null,
      flagBox: sa ? geoBBox(largest[0]).map(round) : null,
      polys,
    };
  })
  .filter(Boolean);

const bboxOf = (items) => {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const it of items) for (const p of it.polys) { const [a, b, c, d] = geoBBox(p[0]); x0 = Math.min(x0, a); y0 = Math.min(y0, b); x1 = Math.max(x1, c); y1 = Math.max(y1, d); }
  return [round(x0), round(y0), round(x1), round(y1)];
};

const out = {
  meta: {
    projection: 'Equal Earth, rotate [54, 0]; Brazil = 100 units wide',
    kmPerUnit: round(6371.0088 / K),
    sources: [
      'IBGE, API de malhas v3, qualidade intermediária, intrarregião UF',
      'IBGE, API de localidades v1 (siglas e nomes)',
      'Natural Earth 1:50m via world-atlas@2 (países vizinhos)',
    ],
  },
  bounds: {
    brazil: bboxOf(brazil),
    // Oceanic islands (Trindade, Fernando de Noronha) stretch the box far east; the visual centre uses the mainland.
    brazilMainland: bboxOf(brazil.map((s) => ({ polys: s.polys.filter((p) => ringArea(p[0]) > 5) }))),
    southAmerica: bboxOf([...brazil, ...countries.filter((c) => c.southAmerica)]),
  },
  brazil,
  countries,
};
fs.writeFileSync(path.join(ASSETS, 'map-geo.json'), JSON.stringify(out));
console.log('states', brazil.length, 'countries', countries.length, 'sa', countries.filter((c) => c.southAmerica).length);
console.log('bounds', JSON.stringify(out.bounds), 'km/unit', out.meta.kmPerUnit);
console.log('labels', brazil.map((s) => s.uf + ':' + s.label.join(',')).join(' '));
console.log('insets empty', brazil.filter((s) => !s.inset.length).map((s) => s.uf));
console.log('size KB', Math.round(fs.statSync(path.join(ASSETS, 'map-geo.json')).size / 1024));
