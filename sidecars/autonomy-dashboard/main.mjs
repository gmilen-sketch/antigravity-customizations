// Node.js Sidecar entrypoint for Antigravity External & Web AuxPane compatibility
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..');

function countKbDossiers(dir) {
  if (!fs.existsSync(dir)) return 0;
  let count = 0;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      count += countKbDossiers(full);
    } else if (entry.isFile() && entry.name.endsWith('.md') && entry.name !== 'index.md' && entry.name !== 'log.md') {
      count += 1;
    }
  }
  return count;
}

function computeStatusPayload() {
  const verFile = path.join(repoRoot, 'VERSION');
  const version = fs.existsSync(verFile) ? fs.readFileSync(verFile, 'utf8').trim() : '1.5.0';
  const skillsDir = path.join(repoRoot, 'skills');
  const skillCount = fs.existsSync(skillsDir)
    ? fs.readdirSync(skillsDir, { withFileTypes: true }).filter((d) => d.isDirectory() && fs.existsSync(path.join(skillsDir, d.name, 'SKILL.md'))).length
    : 20;
  const pluginsDir = path.join(repoRoot, 'plugins');
  const pluginPacks = fs.existsSync(pluginsDir)
    ? fs.readdirSync(pluginsDir, { withFileTypes: true }).filter((d) => d.isDirectory() && fs.existsSync(path.join(pluginsDir, d.name, 'plugin.json'))).length
    : 4;
  const kgEntities = countKbDossiers(path.join(repoRoot, 'kb'));
  return {
    status: 'ok',
    version,
    skill_count: skillCount,
    subagent_count: 5,
    mcp_server_count: 10,
    plugin_packs: pluginPacks,
    kg_entities: kgEntities,
    entrypoint: 'SIDECAR_UI_ENTRYPOINT_AUX_PANE'
  };
}

if (process.argv.includes('--self-test')) {
  process.stdout.write(JSON.stringify(computeStatusPayload(), null, 2) + '\n');
  process.exit(0);
}

const port = parseInt(process.env.ANTIGRAVITY_SIDECAR_WEB_PORT || process.env.PORT || '0', 10);

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
    res.end(JSON.stringify(computeStatusPayload()));
  } else {
    res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ error: 'not_found' }));
  }
});

server.listen(port, '127.0.0.1', () => {
  const addr = server.address();
  const boundPort = typeof addr === 'object' && addr ? addr.port : port;
  process.stderr.write(`[autonomy-dashboard] Listening on http://127.0.0.1:${boundPort}\n`);
});
