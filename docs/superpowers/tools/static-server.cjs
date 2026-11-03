// A static server for the probes: no queue limit, and --no-csp strips the CSP meta so P2's control can run the same page without it.
const http = require('http'), fs = require('fs'), path = require('path');
const [root, port = '8791', flag] = process.argv.slice(2);
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.txt': 'text/plain', '.geojson': 'application/json' };
http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (p.endsWith('/')) p += 'index.html';
  const f = path.join(root, path.normalize(p));
  if (!f.startsWith(path.resolve(root))) { res.writeHead(403); return res.end(); }
  fs.readFile(f, (e, b) => {
    if (e) { res.writeHead(404); return res.end(); }
    if (flag === '--no-csp' && f.endsWith('.html')) b = Buffer.from(String(b).replace(/<meta http-equiv="Content-Security-Policy"[^>]*>/, ''));
    if (flag !== '--pages') { res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' }); return res.end(b); }
    // --pages: GitHub Pages' caching (max-age=600, an ETag, gzip), and one line per file served, for the loader's cache measure
    const etag = `"${b.length.toString(16)}-${fs.statSync(f).mtimeMs.toString(16)}"`;
    if (req.headers['if-none-match'] === etag) { console.log(`304 ${p}`); res.writeHead(304, { etag, 'cache-control': 'max-age=600' }); return res.end(); }
    const gz = /gzip/.test(req.headers['accept-encoding'] || '') ? require('zlib').gzipSync(b) : b;
    console.log(`200 ${p} ${gz.length}`);
    res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream', 'cache-control': 'max-age=600', etag,
      'last-modified': fs.statSync(f).mtime.toUTCString(), ...(gz !== b ? { 'content-encoding': 'gzip' } : {}) });
    res.end(gz);
  });
}).listen(+port, '127.0.0.1', () => console.log(`serving ${root} on ${port}${flag ? ' ' + flag : ''}`));
