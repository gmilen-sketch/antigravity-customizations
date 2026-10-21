// Node.js Sidecar entrypoint for Antigravity External & Web AuxPane compatibility
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const port = parseInt(process.env.ANTIGRAVITY_SIDECAR_WEB_PORT || '0', 10);

const server = http.createServer((req, res) => {
  const urlPath = (req.url || '/').split('?')[0];
  if (urlPath === '/' || urlPath === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(fs.readFileSync(path.join(__dirname, 'index.html')));
  } else if (urlPath === '/styles.css') {
    res.writeHead(200, { 'Content-Type': 'text/css; charset=utf-8' });
    res.end(fs.readFileSync(path.join(__dirname, 'styles.css')));
  } else if (urlPath === '/preload.js') {
    res.writeHead(200, { 'Content-Type': 'application/javascript; charset=utf-8' });
    res.end('window.sidecar = window.sidecar || { conversationId: null, agent: { sendMessage: async () => {} }, ui: { toggleAuxPane: async () => {} } };\n');
  } else if (urlPath === '/api/status' || urlPath === '/healthz') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({
      status: 'ok',
      version: '1.3.0',
      skill_count: 20,
      subagent_count: 5,
      mcp_server_count: 7,
      plugin_packs: 4,
      kg_entities: 6,
      entrypoint: 'SIDECAR_UI_ENTRYPOINT_AUX_PANE'
    }));
  } else {
    res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ error: 'not_found' }));
  }
});

server.listen(port, '127.0.0.1');
