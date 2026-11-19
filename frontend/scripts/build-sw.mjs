import { readdirSync, writeFileSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
const assets = readdirSync('dist/assets').map((f) => '/assets/' + f);
const files = ['/', '/index.html', '/icon.svg', '/manifest.webmanifest', ...assets];
const revision = createHash('sha256')
  .update(readFileSync('dist/index.html'))
  .digest('hex')
  .slice(0, 12);
writeFileSync(
  'dist/sw.js',
  `const CACHE='saha-${revision}';const FILES=${JSON.stringify(files)};
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)));self.skipWaiting();});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('saha-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==self.location.origin||u.pathname.startsWith('/api'))return;e.respondWith(fetch(e.request).catch(()=>caches.match(e.request).then(r=>r||(e.request.mode==='navigate'?caches.match('/index.html'):Response.error()))));});`,
);
