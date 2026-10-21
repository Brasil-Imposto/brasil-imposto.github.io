import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';

// Round 2 composite: option A (Maquete). A narrow field of view keeps the camera close to orthographic,
// so the part of the continent nearer the camera is not enlarged (that is what made Argentina look too big).
const P = { tilt: 34, fov: 11, brazilDepth: 5, neighbourDepth: 1, border: 1.5, lift: 2.4, shadow: 0.18 };

// Shared with the classic-script state map (statemap.js), which cannot import modules when opened from file://.
export const T3 = { THREE, CSS2DRenderer, CSS2DObject };

const NO_DATA = '#C4CCD6';
const GREEN = ['#E6E3D6', '#BFDDB8', '#7CC287', '#35A05E', '#12803F', '#06592B'];
const RED = ['#E6E3D6', '#F5C4B6', '#EE8D76', '#DA4A3C', '#B41E25', '#7A0710'];
// Neighbours are deliberately darker than Brazil so they recede; borders almost black.
const NEIGHBOUR_BASE = '#E4E8EC';
const NEIGHBOUR_TINT = '#A9B2BB';
const NEIGHBOUR_SIDE = '#8C969F';
const OTHER_CAP = '#B9C1C8';
const COUNTRY_BORDER = '#1B2229';
const FLAG_OPACITY = 0.3;
const MIN_NAME_UNITS = 0.85;
const DF_SNAP_PX = 18;

const lerpStops = (stops, t) => {
  const x = Math.min(Math.max(t, 0), 1) * (stops.length - 1);
  const i = Math.min(Math.floor(x), stops.length - 2);
  return new THREE.Color(stops[i]).lerp(new THREE.Color(stops[i + 1]), x - i);
};

// Positive = sends more than it receives (green); negative = receives more (red).
// Each side is normalised by its own extreme, so the deepest red is the state that receives the most.
export function colorFor(value, maxPositive, maxNegative) {
  if (value == null || Number.isNaN(value)) return new THREE.Color(NO_DATA);
  if (value >= 0) return lerpStops(GREEN, Math.pow(Math.min(value / maxPositive, 1), 0.75));
  return lerpStops(RED, Math.pow(Math.min(-value / maxNegative, 1), 0.75));
}
export const legendGradient = () =>
  `linear-gradient(90deg, ${[...GREEN].reverse().join(', ')}, ${RED.slice(1).join(', ')})`;

const luminance = (c) => 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;

function shapesFrom(polys) {
  return polys.map((poly) => {
    const shape = new THREE.Shape(poly[0].map(([x, y]) => new THREE.Vector2(x, y)));
    for (const hole of poly.slice(1)) shape.holes.push(new THREE.Path(hole.map(([x, y]) => new THREE.Vector2(x, y))));
    return shape;
  });
}

function ringLine(ring, z, material) {
  const pts = [];
  for (const [x, y] of ring) pts.push(x, y, z);
  pts.push(ring[0][0], ring[0][1], z);
  const geom = new LineGeometry();
  geom.setPositions(pts);
  return new Line2(geom, material);
}

// The neighbour's cap is one texture: its flag as the background of the territory, faded, with the
// name fitted inside it (the fit is computed at build time and re-checked here with real glyph widths).
async function neighbourTexture(country, flagImg, renderer) {
  const [x0, y0, x1, y1] = country.flagBox;
  const w = x1 - x0, h = y1 - y0;
  const longSide = country.area > 400 ? 2048 : country.area > 40 ? 1024 : 512;
  const W = w >= h ? longSide : Math.round((longSide * w) / h);
  const H = w >= h ? Math.round((longSide * h) / w) : longSide;
  const s = W / w;
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = NEIGHBOUR_BASE;
  ctx.fillRect(0, 0, W, H);

  // Official flags keep their own proportions (Commons files: 3:2, 2:1, 5:3...), so the box follows the image.
  const fw = 640, fh = Math.round((640 * (flagImg.naturalHeight || 3)) / (flagImg.naturalWidth || 4));
  const k = Math.max(W / fw, H / fh);
  const [fx, fy] = country.flagFocus;
  const dx = Math.min(0, Math.max(W - fw * k, W / 2 - fx * fw * k));
  const dy = Math.min(0, Math.max(H - fh * k, H / 2 - fy * fh * k));
  ctx.globalAlpha = FLAG_OPACITY;
  ctx.filter = 'saturate(0.7)';
  ctx.drawImage(flagImg, dx, dy, fw * k, fh * k);
  ctx.filter = 'none';
  ctx.globalAlpha = 1;

  const label = country.nameLabel;
  if (label && label.font >= MIN_NAME_UNITS) {
    const cx = (label.x - x0) * s, cy = (y1 - label.y) * s;
    let px = label.font * s;
    ctx.save();
    ctx.translate(cx, cy);
    if (label.vertical) ctx.rotate(-Math.PI / 2);
    const setFont = () => {
      ctx.font = `800 ${px}px Manrope`;
      ctx.letterSpacing = `${(px * (label.tracking ?? 0.12)).toFixed(1)}px`;
    };
    setFont();
    // Measured width must stay within the box the build step proved fits inside the territory.
    const boxW = Math.max(...label.lines.map((l) => l.length)) * (label.charW ?? 0.84) * label.font * s;
    const widest = Math.max(...label.lines.map((l) => ctx.measureText(l).width));
    if (widest > boxW) { px *= boxW / widest; setFont(); }
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.lineJoin = 'round';
    ctx.lineWidth = Math.max(2, px * 0.12);
    ctx.strokeStyle = 'rgba(255,255,255,0.7)';
    ctx.fillStyle = 'rgba(12,18,24,0.66)';
    const lh = px * 1.18;
    label.lines.forEach((line, i) => {
      const y = (i - (label.lines.length - 1) / 2) * lh;
      ctx.strokeText(line, 0, y);
      ctx.fillText(line, 0, y);
    });
    ctx.restore();
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
  tex.repeat.set(1 / w, 1 / h);
  tex.offset.set(-x0 / w, -y0 / h);
  return tex;
}

export async function createHero(root, { geo, assetBase = 'assets/', onSelect = () => {} }) {
  const mapEl = root.querySelector('.hero-map');
  const tooltip = root.querySelector('.hero-tooltip');

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  mapEl.appendChild(renderer.domElement);

  const labels = new CSS2DRenderer();
  labels.domElement.className = 'hero-labels';
  mapEl.appendChild(labels.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(P.fov, 1, 10, 20000);
  camera.up.set(0, 0, 1);

  const [bx0, by0, bx1, by1] = geo.bounds.brazilMainland;
  const center = new THREE.Vector3((bx0 + bx1) / 2, (by0 + by1) / 2, P.brazilDepth / 2);

  const hemi = new THREE.HemisphereLight('#ffffff', '#d5dbe2', 1.9);
  hemi.position.set(0, 0, 1);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight('#ffffff', 1.5);
  sun.position.set(center.x - 90, center.y + 70, 160);
  sun.target.position.set(center.x, center.y, 0);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -170, right: 170, top: 170, bottom: -170, near: 1, far: 800 });
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.02;
  scene.add(sun, sun.target);

  const ground = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.ShadowMaterial({ opacity: P.shadow }));
  ground.receiveShadow = true;
  scene.add(ground);

  const lineMaterials = [];
  const lineMat = (color, width) => {
    const m = new LineMaterial({ color, linewidth: width, worldUnits: false });
    lineMaterials.push(m);
    return m;
  };

  await document.fonts.load('800 64px Manrope');
  const flagImages = {};
  await Promise.all(geo.countries.filter((c) => c.flag).map(async (c) => {
    const img = new Image();
    // Inlined data URI when present: an image read from file:// would taint the canvas and block the texture.
    img.src = (window.BI && window.BI.flagData[c.flag]) || `${assetBase}flags/${c.flag}.svg`;
    await img.decode();
    flagImages[c.flag] = img;
  }));

  const neighbourBorder = lineMat(COUNTRY_BORDER, 1.3);
  const fitPoints = [];
  const neighbourMeshes = [];
  for (const c of geo.countries) {
    const depth = c.named ? P.neighbourDepth : P.neighbourDepth * 0.6;
    const geom = new THREE.ExtrudeGeometry(shapesFrom(c.polys), { depth, bevelEnabled: false, curveSegments: 1 });
    const cap = c.named
      ? new THREE.MeshLambertMaterial({ color: NEIGHBOUR_TINT, map: await neighbourTexture(c, flagImages[c.flag], renderer) })
      : new THREE.MeshLambertMaterial({ color: OTHER_CAP });
    const mesh = new THREE.Mesh(geom, [cap, new THREE.MeshLambertMaterial({ color: NEIGHBOUR_SIDE })]);
    mesh.receiveShadow = true;
    mesh.userData.country = c.named ? c.name : null;
    scene.add(mesh);
    if (c.named) {
      neighbourMeshes.push(mesh);
      for (const poly of c.polys) scene.add(ringLine(poly[0], depth + 0.02, neighbourBorder));
    }
  }

  let hovered = null;
  const states = new Map();
  function hoverState(uf) {
    if (uf === hovered) return;
    if (hovered) states.get(hovered).liftTo = 0;
    hovered = uf;
    if (uf) states.get(uf).liftTo = P.lift;
    dirty = true;
  }

  const border = lineMat('#ffffff', P.border);
  for (const s of geo.brazil) {
    const group = new THREE.Group();
    const geom = new THREE.ExtrudeGeometry(shapesFrom(s.polys), { depth: P.brazilDepth, bevelEnabled: false, curveSegments: 1 });
    const cap = new THREE.MeshLambertMaterial({ color: NO_DATA });
    const side = new THREE.MeshLambertMaterial({ color: new THREE.Color(NO_DATA).multiplyScalar(0.72) });
    const mesh = new THREE.Mesh(geom, [cap, side]);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData.uf = s.uf;
    group.add(mesh);
    for (const poly of s.polys) for (const ring of poly) group.add(ringLine(ring, P.brazilDepth + 0.03, border));
    const el = document.createElement('div');
    el.className = 'uf-label';
    el.textContent = s.uf;
    const obj = new CSS2DObject(el);
    obj.position.set(s.label[0], s.label[1], P.brazilDepth + 0.1);
    group.add(obj);
    scene.add(group);
    for (const poly of s.polys) if (poly[0].length > 40) poly[0].forEach((p, i) => { if (i % 8 === 0) fitPoints.push(new THREE.Vector3(p[0], p[1], P.brazilDepth)); });
    states.set(s.uf, { ...s, group, mesh, cap, side, el, obj, liftTo: 0 });
  }

  // Fit: the camera looks at the centre of Brazil, so Brazil sits in the exact centre of the hero,
  // and backs off only until Brazil fits; the rest of the continent runs off the edges.
  const tilt = THREE.MathUtils.degToRad(P.tilt);
  const base = { distance: 1000 };
  const ndc = new THREE.Vector3();
  const place = (distance, azimuth, tiltRad) => {
    const dir = new THREE.Vector3(Math.sin(azimuth) * Math.sin(tiltRad), -Math.cos(azimuth) * Math.sin(tiltRad), Math.cos(tiltRad));
    camera.position.copy(center).addScaledVector(dir, distance);
    camera.lookAt(center);
    camera.updateMatrixWorld();
  };
  const fit = (margin) => {
    let lo = 50, hi = 20000;
    for (let i = 0; i < 34; i++) {
      const d = (lo + hi) / 2;
      place(d, 0, tilt);
      let inside = true;
      for (const p of fitPoints) {
        ndc.copy(p).project(camera);
        if (Math.abs(ndc.x) > margin.x || Math.abs(ndc.y) > margin.y) { inside = false; break; }
      }
      if (inside) hi = d; else lo = d;
    }
    base.distance = hi;
    place(hi, 0, tilt);
  };

  let width = 0, height = 0, dirty = true;
  const resize = () => {
    // Page units, not screen units: under CSS zoom (the desktop page renders at 90%) the label layer and the canvas are
    // laid out in page px, so they must be sized in page px or the labels drift.
    width = Math.max(1, Math.round(mapEl.offsetWidth));
    height = Math.max(1, Math.round(mapEl.offsetHeight));
    renderer.setSize(width, height, false);
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';
    labels.setSize(width, height);
    for (const m of lineMaterials) m.resolution.set(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    fit(width < 700 ? { x: 0.94, y: 0.9 } : { x: 0.9, y: 0.8 });
    const pxPerUnit = height / (2 * base.distance * Math.tan(THREE.MathUtils.degToRad(P.fov) / 2));
    for (const s of states.values()) {
      const size = Math.min(Math.max(Math.sqrt(s.area) * pxPerUnit * 0.3, 9), 17);
      s.el.style.fontSize = `${size.toFixed(1)}px`;
    }
    dirty = true;
  };
  new ResizeObserver(resize).observe(mapEl);
  resize();

  // Interaction. DF is a few pixels wide, so it keeps its real shape but gets a snap radius: any pointer
  // within DF_SNAP_PX of its centre lifts and selects DF before the ray reaches Goiás.
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  const meshes = [...states.values()].map((s) => s.mesh);
  const df = states.get('DF');
  const dfScreen = new THREE.Vector3();
  let describe = () => '', parallax = { x: 0, y: 0 }, parallaxNow = { x: 0, y: 0 };

  const pick = (e) => {
    const r = mapEl.getBoundingClientRect();
    const mx = e.clientX - r.left, my = e.clientY - r.top;
    pointer.set((mx / r.width) * 2 - 1, -(my / r.height) * 2 + 1);
    dfScreen.set(df.label[0], df.label[1], P.brazilDepth).add(df.group.position).project(camera);
    const dfx = ((dfScreen.x + 1) / 2) * r.width, dfy = ((1 - dfScreen.y) / 2) * r.height;
    if (Math.hypot(mx - dfx, my - dfy) < DF_SNAP_PX) return { uf: 'DF', mx, my, r };
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(meshes, false)[0];
    if (hit) return { uf: hit.object.userData.uf, mx, my, r };
    const n = raycaster.intersectObjects(neighbourMeshes, false)[0];
    return { country: n ? n.object.userData.country : null, mx, my, r };
  };
  // Screen box of a state, so the balloon can sit beside it instead of over it.
  const boxOf = (uf, r) => {
    const s = states.get(uf); let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity; const q = new THREE.Vector3();
    for (const p of s.polys) for (let i = 0; i < p[0].length; i += Math.max(1, Math.floor(p[0].length / 60))) {
      q.set(p[0][i][0], p[0][i][1], P.brazilDepth + s.group.position.z).project(camera);
      const sx = ((q.x + 1) / 2) * r.width, sy = ((1 - q.y) / 2) * r.height;
      x0 = Math.min(x0, sx); y0 = Math.min(y0, sy); x1 = Math.max(x1, sx); y1 = Math.max(y1, sy);
    }
    return { x0, y0, x1, y1 };
  };
  const placeTooltip = (html, mx0, my0, r0, uf) => {
    tooltip.innerHTML = html;
    tooltip.hidden = false;
    // Pointer and box are in screen px; the balloon is placed in page px (k = 0.9 under the desktop zoom, else 1).
    const k = r0.width / (mapEl.offsetWidth || r0.width), mx = mx0 / k, my = my0 / k, r = { width: r0.width / k, height: r0.height / k };
    const w = tooltip.offsetWidth, h = tooltip.offsetHeight, g = 12, m = 8;
    const a0 = uf ? boxOf(uf, r0) : { x0: mx0 - 4, y0: my0 - 4, x1: mx0 + 4, y1: my0 + 4 };
    const a = { x0: a0.x0 / k, y0: a0.y0 / k, x1: a0.x1 / k, y1: a0.y1 / k };
    const cy = Math.max(m, Math.min(my - h / 2, r.height - h - m)), cx = Math.max(m, Math.min(mx - w / 2, r.width - w - m));
    const options = [[a.x1 + g, cy], [a.x0 - g - w, cy], [cx, a.y0 - g - h], [cx, a.y1 + g], [mx + g, my + g]];
    const fits = ([tx, ty]) => tx >= m && ty >= m && tx + w <= r.width - m && ty + h <= r.height - m;
    const overlap = ([tx, ty]) => Math.max(0, Math.min(tx + w, a.x1) - Math.max(tx, a.x0)) * Math.max(0, Math.min(ty + h, a.y1) - Math.max(ty, a.y0));
    let best = options.find((o) => fits(o) && overlap(o) === 0);
    if (!best) best = options.map(([tx, ty]) => [Math.max(m, Math.min(tx, r.width - w - m)), Math.max(m, Math.min(ty, r.height - h - m))]).sort((p, q) => overlap(p) - overlap(q))[0];
    tooltip.style.transform = `translate(${Math.round(best[0])}px, ${Math.round(best[1])}px)`;
  };
  const onMove = (e) => {
    if (root.classList.contains('modal-open')) return;
    const { uf, country, mx, my, r } = pick(e);
    parallax = { x: pointer.x, y: pointer.y };
    hoverState(uf || null);
    if (uf) placeTooltip(describe(uf), mx, my, r, uf);
    else if (country) placeTooltip(`<strong>${country}</strong><span class="muted">País vizinho</span>`, mx, my, r);
    else tooltip.hidden = true;
    mapEl.style.cursor = uf ? 'pointer' : 'default';
  };
  mapEl.addEventListener('pointermove', onMove);
  mapEl.addEventListener('pointerleave', () => { hoverState(null); tooltip.hidden = true; parallax = { x: 0, y: 0 }; });
  mapEl.addEventListener('click', (e) => {
    if (root.classList.contains('modal-open')) return;
    const { uf } = pick(e);
    if (uf) { tooltip.hidden = true; onSelect(uf); }
  });

  const tick = () => {
    let moving = false;
    for (const s of states.values()) {
      const z = s.group.position.z;
      const next = z + (s.liftTo - z) * 0.2;
      const settled = Math.abs(next - s.liftTo) <= 0.005;
      if (!settled) moving = true;
      s.group.position.z = settled ? s.liftTo : next;
    }
    const px = parallaxNow.x + (parallax.x - parallaxNow.x) * 0.08;
    const py = parallaxNow.y + (parallax.y - parallaxNow.y) * 0.08;
    if (Math.abs(px - parallaxNow.x) > 1e-4 || Math.abs(py - parallaxNow.y) > 1e-4) moving = true;
    parallaxNow = { x: px, y: py };
    if (moving || dirty) {
      place(base.distance, THREE.MathUtils.degToRad(1.2) * px, tilt + THREE.MathUtils.degToRad(1) * py);
      renderer.render(scene, camera);
      labels.render(scene, camera);
      dirty = false;
    }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
  renderer.render(scene, camera);
  labels.render(scene, camera);

  return {
    setData({ values, describe: fn, scale = {} }) {
      const vals = Object.values(values).filter((v) => v != null);
      const maxPos = scale.maxPositive ?? Math.max(...vals.filter((v) => v > 0), 1);
      const maxNeg = scale.maxNegative ?? Math.max(...vals.filter((v) => v < 0).map((v) => -v), 1);
      for (const s of states.values()) {
        const c = colorFor(values[s.uf], maxPos, maxNeg);
        s.cap.color.copy(c);
        s.side.color.copy(c).multiplyScalar(0.72);
        s.el.classList.toggle('on-dark', luminance(c) < 0.38);
      }
      describe = fn;
      dirty = true;
    },
    colorOf(uf) { return '#' + states.get(uf).cap.color.getHexString(THREE.SRGBColorSpace); },
    clearHover() { hoverState(null); tooltip.hidden = true; },
  };
}
