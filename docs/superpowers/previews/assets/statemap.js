// State hero map (round 9): the municipalities of a state, coloured by the same rule as the country map.
// Classic script so the previews open from the file path. The 3D version needs window.T3 (three.js and the
// CSS2D renderer, set by the page's module script); the flat version is plain SVG.
(function () {
  // Same colour stops as hero3d.js: green sends more than it receives, red receives more.
  const GREEN = ['#E6E3D6', '#BFDDB8', '#7CC287', '#35A05E', '#12803F', '#06592B'];
  const RED = ['#E6E3D6', '#F5C4B6', '#EE8D76', '#DA4A3C', '#B41E25', '#7A0710'];
  const NO_DATA = '#C4CCD6';
  const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const mix = (a, b, t) => '#' + hex(a).map((x, i) => Math.round(x + (hex(b)[i] - x) * t).toString(16).padStart(2, '0')).join('');
  const stop = (stops, t) => {
    const x = Math.min(Math.max(t, 0), 1) * (stops.length - 1);
    const i = Math.min(Math.floor(x), stops.length - 2);
    return mix(stops[i], stops[i + 1], x - i);
  };
  // Municipal values have extreme outliers (port cities, head offices), so each side is scaled by its 90th percentile.
  function scaleOf(values) {
    const pos = values.filter((v) => v > 0).sort((a, b) => a - b), neg = values.filter((v) => v < 0).map((v) => -v).sort((a, b) => a - b);
    const p90 = (a) => (a.length ? a[Math.floor(a.length * 0.9)] || a[a.length - 1] : 1);
    return { maxPos: p90(pos), maxNeg: p90(neg) };
  }
  // A neutral blue ramp for measures that are not a balance with the Union (the DF regions: population), so they are
  // never read as green "sends" or red "receives".
  const BLUE = ['#EEF2F7', '#C9D8EA', '#93B3D6', '#5B88BE', '#2F5F9C', '#173E6E'];
  function colorFor(v, s) {
    if (v == null || Number.isNaN(v)) return NO_DATA;
    if (s.neutral) return stop(BLUE, Math.pow(v / s.max, 0.7));
    return v >= 0 ? stop(GREEN, Math.pow(v / s.maxPos, 0.75)) : stop(RED, Math.pow(-v / s.maxNeg, 0.75));
  }
  const neutralGradient = () => `linear-gradient(90deg, ${BLUE.join(', ')})`;
  const legendGradient = () => `linear-gradient(90deg, ${[...GREEN].reverse().join(', ')}, ${RED.slice(1).join(', ')})`;
  const lum = (h) => hex(h).map((c) => c / 255).map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)).reduce((a, c, i) => a + c * [0.2126, 0.7152, 0.0722][i], 0);

  // Places the balloon beside the hovered area, never over it: tries right, left, above and below the area's
  // box (in stage pixels) and keeps the first that fits; if none fits, the one that covers the area least.
  function tooltipAt(tip, html, el, x0, y0, avoid) {
    tip.innerHTML = html; tip.hidden = false;
    // x, y and avoid are in screen px; the balloon is placed in page px (k = 0.9 under the desktop zoom, else 1).
    const r0 = el.getBoundingClientRect(), k = r0.width / (el.offsetWidth || r0.width), x = x0 / k, y = y0 / k;
    const r = { width: r0.width / k, height: r0.height / k }; const w = tip.offsetWidth, h = tip.offsetHeight, g = 12, m = 8;
    const a = avoid ? { x0: avoid.x0 / k, y0: avoid.y0 / k, x1: avoid.x1 / k, y1: avoid.y1 / k } : { x0: x - 4, y0: y - 4, x1: x + 4, y1: y + 4 };
    const cy = Math.max(m, Math.min(y - h / 2, r.height - h - m)), cx = Math.max(m, Math.min(x - w / 2, r.width - w - m));
    const options = [[a.x1 + g, cy], [a.x0 - g - w, cy], [cx, a.y0 - g - h], [cx, a.y1 + g], [x + g, y + g], [x - g - w, y - g - h]];
    const fits = ([tx, ty]) => tx >= m && ty >= m && tx + w <= r.width - m && ty + h <= r.height - m;
    const overlap = ([tx, ty]) => Math.max(0, Math.min(tx + w, a.x1) - Math.max(tx, a.x0)) * Math.max(0, Math.min(ty + h, a.y1) - Math.max(ty, a.y0));
    let best = options.find((o) => fits(o) && overlap(o) === 0);
    if (!best) best = options.map(([tx, ty]) => [Math.max(m, Math.min(tx, r.width - w - m)), Math.max(m, Math.min(ty, r.height - h - m))]).sort((p, q) => overlap(p) - overlap(q))[0];
    tip.style.transform = `translate(${Math.round(best[0])}px, ${Math.round(best[1])}px)`;
  }
  function frame(el) {
    el.classList.add('sm');
    el.innerHTML = '<div class="sm-stage"></div><div class="sm-tip" hidden></div>';
    return { stage: el.querySelector('.sm-stage'), tip: el.querySelector('.sm-tip') };
  }

  // ---------- 3D maquete (same look as the country map) ----------
  function create3d(el, opts) {
    const { THREE, CSS2DRenderer, CSS2DObject } = window.T3;
    const { geo } = opts;
    const { stage, tip } = frame(el);
    const DEPTH = 3, LIFT = 1.6;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    stage.appendChild(renderer.domElement);
    const labels = new CSS2DRenderer(); labels.domElement.className = 'sm-labels'; stage.appendChild(labels.domElement);
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(12, 1, 10, 20000); camera.up.set(0, 0, 1);
    const [bx0, by0, bx1, by1] = geo.bounds;
    const center = new THREE.Vector3((bx0 + bx1) / 2, (by0 + by1) / 2, DEPTH / 2);
    const hemi = new THREE.HemisphereLight('#ffffff', '#d5dbe2', 1.9); hemi.position.set(0, 0, 1); scene.add(hemi);
    const sun = new THREE.DirectionalLight('#ffffff', 1.4);
    sun.position.set(center.x - 60, center.y + 50, 120); sun.target.position.set(center.x, center.y, 0);
    sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
    Object.assign(sun.shadow.camera, { left: -90, right: 90, top: 90, bottom: -90, near: 1, far: 600 });
    sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
    scene.add(sun, sun.target);
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.ShadowMaterial({ opacity: 0.16 }));
    ground.receiveShadow = true; scene.add(ground);
    const shapes = (polys) => polys.map((p) => { const s = new THREE.Shape(p[0].map(([x, y]) => new THREE.Vector2(x, y))); for (const h of p.slice(1)) s.holes.push(new THREE.Path(h.map(([x, y]) => new THREE.Vector2(x, y)))); return s; });
    const edges = (polys, z, color, opacity) => {
      const pts = [];
      for (const p of polys) for (const ring of p) for (let i = 0; i < ring.length; i++) { const a = ring[i], b = ring[(i + 1) % ring.length]; pts.push(a[0], a[1], z, b[0], b[1], z); }
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
      return new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color, transparent: opacity < 1, opacity }));
    };
    // D101: the neighbours are one flat, neutral layer that covers all the land in view (build-geo-context.cjs), with thin
    // light borders; the old dark slabs and near-black outlines read as broken edges.
    const lines = (runs, z, color, opacity) => {
      const pts = [];
      for (const r of runs) for (let i = 0; i + 1 < r.length; i++) pts.push(r[i][0], r[i][1], z, r[i + 1][0], r[i + 1][1], z);
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
      return new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color, transparent: opacity < 1, opacity }));
    };
    const ctxCap = new THREE.MeshLambertMaterial({ color: '#CDD3D9' }), ctxSide = new THREE.MeshLambertMaterial({ color: '#C3CAD1' });
    for (const c of geo.context) {
      const mesh = new THREE.Mesh(new THREE.ExtrudeGeometry(shapes(c.polys), { depth: 0.25, bevelEnabled: false, curveSegments: 1 }), [ctxCap, ctxSide]);
      mesh.receiveShadow = true; scene.add(mesh);
      if (c.lines) scene.add(lines(c.lines, 0.27, '#ffffff', 0.95)); else scene.add(edges(c.polys, 0.27, '#ffffff', 0.95));
      if (!c.label || !c.name) continue;
      const l = document.createElement('div'); l.className = 'sm-ctx'; l.textContent = c.name;
      const o = new CSS2DObject(l); o.position.set(c.label[0], c.label[1], 0.35); scene.add(o);
    }
    const byCode = new Map(); const meshes = [];
    for (const m of geo.municipalities) {
      const group = new THREE.Group();
      const cap = new THREE.MeshLambertMaterial({ color: NO_DATA }), side = new THREE.MeshLambertMaterial({ color: NO_DATA });
      const mesh = new THREE.Mesh(new THREE.ExtrudeGeometry(shapes(m.polys), { depth: DEPTH, bevelEnabled: false, curveSegments: 1 }), [cap, side]);
      mesh.castShadow = true; mesh.receiveShadow = true; mesh.userData.code = m.code;
      const line = edges(m.polys, DEPTH + 0.02, '#ffffff', 0.85);
      group.add(mesh, line); scene.add(group); meshes.push(mesh);
      byCode.set(m.code, { ...m, group, cap, side, line, liftTo: 0 });
    }
    const addLabel = (code, cls, html) => {
      const m = byCode.get(code); if (!m) return;
      const d = document.createElement('div'); d.className = cls; d.innerHTML = html;
      const o = new CSS2DObject(d); o.position.set(m.label[0], m.label[1], DEPTH + 0.2); m.group.add(o);
    };
    // labelHtml lets a map mark one place differently (the DF: ★ Brasília on the Plano Piloto).
    for (const code of opts.labels || []) addLabel(code, 'sm-name', (opts.labelHtml && opts.labelHtml(code)) || (byCode.get(code) ? byCode.get(code).name : ''));
    // D60: a case is a small dot on its municipality (the old balloon on a stem covered the municipalities behind it).
    for (const p of opts.pins || []) addLabel(p.code, 'sm-pin', '<span class="dot"></span>');
    // A neighbour's name the frame would cut is hidden rather than shown in half (D83): on a phone the side margins are thin.
    const clipCtx = () => { const s = stage.getBoundingClientRect(); for (const l of labels.domElement.querySelectorAll('.sm-ctx')) { l.style.visibility = ''; const b = l.getBoundingClientRect(); l.style.visibility = b.left < s.left + 2 || b.right > s.right - 2 || b.top < s.top + 2 || b.bottom > s.bottom - 2 ? 'hidden' : ''; } };
    const tilt = THREE.MathUtils.degToRad(30);
    let distance = 800;
    const place = (d) => { camera.position.copy(center).add(new THREE.Vector3(0, -Math.sin(tilt) * d, Math.cos(tilt) * d)); camera.lookAt(center); camera.updateMatrixWorld(); };
    const fitPts = []; for (const m of geo.municipalities) for (const p of m.polys) p[0].forEach((q, i) => { if (i % 6 === 0) fitPts.push(new THREE.Vector3(q[0], q[1], DEPTH)); });
    const v = new THREE.Vector3();
    const fit = () => {
      let lo = 50, hi = 20000;
      for (let i = 0; i < 32; i++) { const d = (lo + hi) / 2; place(d); let ok = true; for (const p of fitPts) { v.copy(p).project(camera); if (Math.abs(v.x) > 0.94 || Math.abs(v.y) > 0.9) { ok = false; break; } } if (ok) hi = d; else lo = d; }
      distance = hi; place(hi);
    };
    let dirty = true, alive = true, hovered = null, selected = null, describe = () => '';
    const resize = () => {
      const w = Math.max(1, Math.round(stage.offsetWidth)), h = Math.max(1, Math.round(stage.offsetHeight));  // page px, as in hero3d.js
      renderer.setSize(w, h, false); renderer.domElement.style.width = '100%'; renderer.domElement.style.height = '100%';
      labels.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); fit(); dirty = true;
    };
    const ro = new ResizeObserver(resize); ro.observe(stage); resize();
    const setLift = () => { for (const m of byCode.values()) m.liftTo = m.code === selected ? LIFT * 1.3 : m.code === hovered ? LIFT : 0; dirty = true; };
    const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
    const pick = (e) => {
      const r = stage.getBoundingClientRect(); const x = e.clientX - r.left, y = e.clientY - r.top;
      ptr.set((x / r.width) * 2 - 1, -(y / r.height) * 2 + 1); ray.setFromCamera(ptr, camera);
      const hit = ray.intersectObjects(meshes, false)[0]; return { code: hit ? hit.object.userData.code : null, x, y, r };
    };
    const screenBox = (code, r) => {
      const m = byCode.get(code); let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      for (const p of m.polys) for (let i = 0; i < p[0].length; i += Math.max(1, Math.floor(p[0].length / 60))) {
        v.set(p[0][i][0], p[0][i][1], DEPTH + m.group.position.z).project(camera);
        const sx = ((v.x + 1) / 2) * r.width, sy = ((1 - v.y) / 2) * r.height;
        x0 = Math.min(x0, sx); y0 = Math.min(y0, sy); x1 = Math.max(x1, sx); y1 = Math.max(y1, sy);
      }
      return { x0, y0, x1, y1 };
    };
    stage.addEventListener('pointermove', (e) => {
      const { code, x, y, r } = pick(e);
      if (code !== hovered) { hovered = code; setLift(); }
      if (code) tooltipAt(tip, describe(code), stage, x, y, screenBox(code, r)); else tip.hidden = true;
      stage.style.cursor = code ? 'pointer' : 'default';
    });
    stage.addEventListener('pointerleave', () => { hovered = null; tip.hidden = true; setLift(); });
    stage.addEventListener('click', (e) => { const { code } = pick(e); if (code && opts.onSelect) { tip.hidden = true; opts.onSelect(code); } });
    const tick = () => {
      if (!alive) return;
      let moving = false;
      for (const m of byCode.values()) { const z = m.group.position.z, n = z + (m.liftTo - z) * 0.22; if (Math.abs(n - m.liftTo) > 0.005) { moving = true; m.group.position.z = n; } else m.group.position.z = m.liftTo; }
      if (moving || dirty) { renderer.render(scene, camera); labels.render(scene, camera); clipCtx(); dirty = false; }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    return {
      // scale: optional { maxPos, maxNeg } from outside (the DF uses the country map's scale of 26 states).
      setData(values, fn, neutral, scale) {
        const vs = Object.values(values).filter((x) => x != null);
        const s = scale || (neutral ? { neutral: true, max: Math.max(...vs, 1) } : scaleOf(vs));
        for (const m of byCode.values()) {
          const c = colorFor(values[m.code], s);
          m.cap.color.set(c); m.side.color.set(c).multiplyScalar(0.72);
        }
        describe = fn; dirty = true;
      },
      setSelected(code) { selected = code; for (const m of byCode.values()) m.line.material.color.set(m.code === code ? '#14202B' : '#ffffff'); setLift(); },
      dispose() { alive = false; ro.disconnect(); renderer.dispose(); renderer.forceContextLoss(); el.innerHTML = ''; },
    };
  }

  // ---------- flat SVG ----------
  function createFlat(el, opts) {
    const { geo } = opts;
    const { stage, tip } = frame(el);
    const [x0, y0, x1, y1] = geo.bounds; const pad = 3;
    const path = (polys) => polys.map((p) => p.map((r) => 'M' + r.map(([x, y]) => `${x.toFixed(2)},${(-y).toFixed(2)}`).join('L') + 'Z').join('')).join('');
    const vb = `${x0 - pad} ${-y1 - pad} ${x1 - x0 + 2 * pad} ${y1 - y0 + 2 * pad}`;
    const byCode = new Map(geo.municipalities.map((m) => [m.code, m]));
    stage.innerHTML = `<svg class="sm-svg" viewBox="${vb}" preserveAspectRatio="xMidYMid meet">
      ${geo.context.map((c) => `<path class="ctx" d="${path(c.polys)}"/>`).join('')}
      ${geo.context.filter((c) => c.label && c.name).map((c) => `<text class="ctx-l" x="${c.label[0]}" y="${-c.label[1]}">${c.name}</text>`).join('')}
      <g class="muns">${geo.municipalities.map((m) => `<path data-code="${m.code}" d="${path(m.polys)}"/>`).join('')}</g>
      ${(opts.labels || []).filter((c) => byCode.has(c)).map((c) => `<text class="nm" x="${byCode.get(c).label[0]}" y="${-byCode.get(c).label[1] - 1.2}">${(opts.labelText && opts.labelText(c)) || byCode.get(c).name}</text>`).join('')}
      ${(opts.pins || []).filter((p) => byCode.has(p.code)).map((p) => `<g class="pin" transform="translate(${byCode.get(p.code).label[0]} ${-byCode.get(p.code).label[1]})"><circle class="dot" cy="-1.6" r=".55"/></g>`).join('')}
    </svg>`;
    const svg = stage.querySelector('svg');
    let describe = () => '';
    svg.addEventListener('pointermove', (e) => {
      const p = e.target.closest('path[data-code]'); const r = stage.getBoundingClientRect();
      svg.querySelectorAll('path.hover').forEach((q) => q !== p && q.classList.remove('hover'));
      if (p) {
        p.classList.add('hover'); const b = p.getBoundingClientRect();
        tooltipAt(tip, describe(p.dataset.code), stage, e.clientX - r.left, e.clientY - r.top, { x0: b.left - r.left, y0: b.top - r.top, x1: b.right - r.left, y1: b.bottom - r.top });
      } else tip.hidden = true;
    });
    svg.addEventListener('pointerleave', () => { tip.hidden = true; svg.querySelectorAll('path.hover').forEach((q) => q.classList.remove('hover')); });
    svg.addEventListener('click', (e) => { const p = e.target.closest('path[data-code]'); if (p && opts.onSelect) { tip.hidden = true; opts.onSelect(p.dataset.code); } });
    return {
      // scale: optional { maxPos, maxNeg } from outside (the DF uses the country map's scale of 26 states).
      setData(values, fn, neutral, scale) {
        const vs = Object.values(values).filter((x) => x != null);
        const s = scale || (neutral ? { neutral: true, max: Math.max(...vs, 1) } : scaleOf(vs));
        svg.querySelectorAll('path[data-code]').forEach((p) => { p.style.fill = colorFor(values[p.dataset.code], s); });
        describe = fn;
      },
      setSelected(code) { svg.querySelectorAll('path[data-code]').forEach((p) => p.classList.toggle('sel', p.dataset.code === code)); const s = svg.querySelector(`path[data-code="${code}"]`); if (s) s.parentNode.appendChild(s); },
      dispose() { el.innerHTML = ''; },
    };
  }

  window.BIS = { create3d, createFlat, colorFor, scaleOf, legendGradient, neutralGradient, lum };
})();
