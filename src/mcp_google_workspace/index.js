#!/usr/bin/env node
/**
 * Google Workspace MCP Server (`google-workspace-mcp`).
 * Uses `@modelcontextprotocol/sdk` + `googleapis` when `node_modules` are installed,
 * and falls back seamlessly to a built-in zero-dependency Node.js (`https` + `readline`)
 * MCP JSON-RPC 2.0 `stdio` transport + Google Workspace REST v1/v3/v4 client when
 * installed directly via `agy plugin install` without `npm install`.
 */
const fs = require("fs");
const https = require("https");
const os = require("os");
const path = require("path");
const readline = require("readline");

const TOKEN_PATH = path.join(__dirname, "tokens.json");
const ADC_PATH = path.join(os.homedir(), ".config/gcloud/application_default_credentials.json");

const TOOL_SPECS = [
  {
    name: "gmail_list_messages",
    _meta: { "antigravity/alwaysLoad": true },
    description: "List recent messages from the user's Gmail inbox.",
    inputSchema: {
      type: "object",
      properties: {
        maxResults: { type: "number", description: "Maximum number of messages to return (default 10)" },
        q: { type: "string", description: "Search query to filter messages (standard Gmail search syntax)" },
      },
    },
  },
  {
    name: "gmail_send_email",
    _meta: { "antigravity/alwaysLoad": true },
    description: "Send an email message to a recipient.",
    inputSchema: {
      type: "object",
      properties: {
        to: { type: "string", description: "Recipient's email address" },
        subject: { type: "string", description: "Email subject line" },
        body: { type: "string", description: "Email body content (HTML or plain text)" },
      },
      required: ["to", "subject", "body"],
    },
  },
  {
    name: "calendar_list_events",
    _meta: { "antigravity/alwaysLoad": true },
    description: "List upcoming events from the user's primary Google Calendar.",
    inputSchema: {
      type: "object",
      properties: {
        maxResults: { type: "number", description: "Maximum number of events to return (default 10)" },
      },
    },
  },
  {
    name: "calendar_create_event",
    _meta: { "antigravity/alwaysLoad": true },
    description: "Create a new event in the user's primary Google Calendar.",
    inputSchema: {
      type: "object",
      properties: {
        summary: { type: "string", description: "Title of the calendar event" },
        startTime: { type: "string", description: "Event start time in ISO-8601 format (e.g. 2026-07-03T10:00:00Z)" },
        endTime: { type: "string", description: "Event end time in ISO-8601 format (e.g. 2026-07-03T11:00:00Z)" },
        description: { type: "string", description: "Optional description or notes for the event" },
      },
      required: ["summary", "startTime", "endTime"],
    },
  },
  {
    name: "drive_list_files",
    _meta: { "antigravity/alwaysLoad": true },
    description: "List files stored in the user's Google Drive.",
    inputSchema: {
      type: "object",
      properties: {
        pageSize: { type: "number", description: "Maximum number of files to return (default 10)" },
      },
    },
  },
  {
    name: "sheets_create_spreadsheet",
    _meta: { "antigravity/alwaysLoad": true },
    description: "Create a new Google Spreadsheet.",
    inputSchema: {
      type: "object",
      properties: {
        title: { type: "string", description: "Title of the new spreadsheet" },
      },
      required: ["title"],
    },
  },
];

function makeEmail(to, subject, body) {
  const str = [
    `To: ${to}`,
    "Content-Type: text/html; charset=utf-8",
    "MIME-Version: 1.0",
    `Subject: ${subject}`,
    "",
    body,
  ].join("\r\n");
  return Buffer.from(str)
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

function httpsJsonRequest(urlStr, method = "GET", headers = {}, bodyStr = null) {
  return new Promise((resolve, reject) => {
    const u = new URL(urlStr);
    const reqHeaders = { ...headers };
    if (bodyStr !== null) {
      reqHeaders["Content-Length"] = Buffer.byteLength(bodyStr);
    }
    const req = https.request(
      {
        hostname: u.hostname,
        port: u.port || 443,
        path: u.pathname + u.search,
        method,
        headers: reqHeaders,
        timeout: 15000,
      },
      (res) => {
        const chunks = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () => {
          const raw = Buffer.concat(chunks).toString("utf8");
          if (res.statusCode >= 400) {
            reject(new Error(`HTTP ${res.statusCode}: ${raw.slice(0, 300)}`));
            return;
          }
          try {
            resolve(raw ? JSON.parse(raw) : {});
          } catch (e) {
            resolve({ raw });
          }
        });
      }
    );
    req.on("error", reject);
    req.on("timeout", () => {
      req.destroy(new Error("HTTPS request timed out"));
    });
    if (bodyStr !== null) req.write(bodyStr);
    req.end();
  });
}

async function resolveAccessToken() {
  if (fs.existsSync(TOKEN_PATH)) {
    const tokens = JSON.parse(fs.readFileSync(TOKEN_PATH, "utf8"));
    if (tokens.access_token && (!tokens.expiry_date || tokens.expiry_date > Date.now() + 60000)) {
      return tokens.access_token;
    }
    if (tokens.refresh_token) {
      const form = new URLSearchParams({
        client_id: process.env.GOOGLE_WORKSPACE_CLIENT_ID || tokens.client_id || "",
        client_secret: process.env.GOOGLE_WORKSPACE_CLIENT_SECRET || tokens.client_secret || "",
        refresh_token: tokens.refresh_token,
        grant_type: "refresh_token",
      }).toString();
      const refreshed = await httpsJsonRequest(
        "https://oauth2.googleapis.com/token",
        "POST",
        { "Content-Type": "application/x-www-form-urlencoded" },
        form
      );
      if (refreshed.access_token) return refreshed.access_token;
    }
  }
  if (fs.existsSync(ADC_PATH)) {
    const adc = JSON.parse(fs.readFileSync(ADC_PATH, "utf8"));
    if (adc.refresh_token && adc.client_id && adc.client_secret) {
      const form = new URLSearchParams({
        client_id: adc.client_id,
        client_secret: adc.client_secret,
        refresh_token: adc.refresh_token,
        grant_type: "refresh_token",
      }).toString();
      const refreshed = await httpsJsonRequest(
        "https://oauth2.googleapis.com/token",
        "POST",
        { "Content-Type": "application/x-www-form-urlencoded" },
        form
      );
      if (refreshed.access_token) return refreshed.access_token;
    }
  }
  throw new Error("No credentials available. Configure tokens.json or run gcloud auth application-default login.");
}

async function executeWorkspaceToolRest(name, args = {}) {
  try {
    const token = await resolveAccessToken();
    const authHeaders = {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    };
    switch (name) {
      case "gmail_list_messages": {
        const qs = new URLSearchParams({ maxResults: String(args.maxResults || 10) });
        if (args.q) qs.set("q", String(args.q));
        const listRes = await httpsJsonRequest(
          `https://gmail.googleapis.com/gmail/v1/users/me/messages?${qs.toString()}`,
          "GET",
          authHeaders
        );
        const msgs = listRes.messages || [];
        const details = await Promise.all(
          msgs.map(async (m) => {
            const d = await httpsJsonRequest(
              `https://gmail.googleapis.com/gmail/v1/users/me/messages/${encodeURIComponent(m.id)}?format=minimal`,
              "GET",
              authHeaders
            );
            return { id: m.id, snippet: d.snippet || "" };
          })
        );
        return { content: [{ type: "text", text: JSON.stringify(details, null, 2) }] };
      }
      case "gmail_send_email": {
        const raw = makeEmail(args.to, args.subject, args.body);
        const res = await httpsJsonRequest(
          "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
          "POST",
          authHeaders,
          JSON.stringify({ raw })
        );
        return { content: [{ type: "text", text: `Email sent successfully. Message ID: ${res.id}` }] };
      }
      case "calendar_list_events": {
        const qs = new URLSearchParams({
          timeMin: new Date().toISOString(),
          maxResults: String(args.maxResults || 10),
          singleEvents: "true",
          orderBy: "startTime",
        });
        const res = await httpsJsonRequest(
          `https://www.googleapis.com/calendar/v3/calendars/primary/events?${qs.toString()}`,
          "GET",
          authHeaders
        );
        const items = (res.items || []).map((e) => ({
          summary: e.summary,
          start: (e.start && (e.start.dateTime || e.start.date)) || "",
          end: (e.end && (e.end.dateTime || e.end.date)) || "",
          link: e.htmlLink || "",
        }));
        return { content: [{ type: "text", text: JSON.stringify(items, null, 2) }] };
      }
      case "calendar_create_event": {
        const res = await httpsJsonRequest(
          "https://www.googleapis.com/calendar/v3/calendars/primary/events",
          "POST",
          authHeaders,
          JSON.stringify({
            summary: args.summary,
            description: args.description || "",
            start: { dateTime: args.startTime, timeZone: "UTC" },
            end: { dateTime: args.endTime, timeZone: "UTC" },
          })
        );
        return { content: [{ type: "text", text: `Event created successfully. Event Link: ${res.htmlLink}` }] };
      }
      case "drive_list_files": {
        const qs = new URLSearchParams({
          pageSize: String(args.pageSize || 10),
          fields: "nextPageToken,files(id,name,mimeType)",
        });
        const res = await httpsJsonRequest(
          `https://www.googleapis.com/drive/v3/files?${qs.toString()}`,
          "GET",
          authHeaders
        );
        return { content: [{ type: "text", text: JSON.stringify(res.files || [], null, 2) }] };
      }
      case "sheets_create_spreadsheet": {
        const res = await httpsJsonRequest(
          "https://sheets.googleapis.com/v4/spreadsheets",
          "POST",
          authHeaders,
          JSON.stringify({ properties: { title: args.title } })
        );
        return { content: [{ type: "text", text: `Spreadsheet created successfully. URL: ${res.spreadsheetUrl}` }] };
      }
      default:
        return { isError: true, content: [{ type: "text", text: `Tool not found: ${name}` }] };
    }
  } catch (err) {
    return { isError: true, content: [{ type: "text", text: `API Error: ${err.message}` }] };
  }
}

async function handleJsonRpc(msg) {
  if (!msg || typeof msg !== "object") return null;
  const hasId = Object.prototype.hasOwnProperty.call(msg, "id");
  const method = String(msg.method || "");
  const params = msg.params && typeof msg.params === "object" ? msg.params : {};
  if (!hasId || method.startsWith("notifications/")) return null;

  if (method === "initialize") {
    return {
      jsonrpc: "2.0",
      id: msg.id,
      result: {
        protocolVersion: params.protocolVersion || "2024-11-05",
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: "google-workspace-mcp", version: "1.5.0" },
      },
    };
  }
  if (method === "ping") {
    return { jsonrpc: "2.0", id: msg.id, result: {} };
  }
  if (method === "tools/list") {
    return { jsonrpc: "2.0", id: msg.id, result: { tools: TOOL_SPECS } };
  }
  if (method === "tools/call") {
    const result = await executeWorkspaceToolRest(String(params.name || ""), params.arguments || {});
    return { jsonrpc: "2.0", id: msg.id, result };
  }
  if (method === "resources/list") {
    return { jsonrpc: "2.0", id: msg.id, result: { resources: [] } };
  }
  if (method === "prompts/list") {
    return { jsonrpc: "2.0", id: msg.id, result: { prompts: [] } };
  }
  return {
    jsonrpc: "2.0",
    id: msg.id,
    error: { code: -32601, message: `Method not found: ${method}` },
  };
}

function startStdlibStdioServer() {
  const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
  rl.on("line", async (line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.toLowerCase().startsWith("content-length:")) return;
    try {
      const msg = JSON.parse(trimmed);
      const resp = await handleJsonRpc(msg);
      if (resp) {
        process.stdout.write(JSON.stringify(resp) + "\n");
      }
    } catch (err) {
      process.stdout.write(
        JSON.stringify({ jsonrpc: "2.0", id: null, error: { code: -32700, message: `Parse error: ${err.message}` } }) + "\n"
      );
    }
  });
}

(async function bootstrap() {
  try {
    const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
    const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
    const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");
    const server = new Server(
      { name: "google-workspace-mcp", version: "1.5.0" },
      { capabilities: { tools: {} } }
    );
    server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOL_SPECS }));
    server.setRequestHandler(CallToolRequestSchema, async (req) =>
      executeWorkspaceToolRest(req.params.name, req.params.arguments || {})
    );
    const transport = new StdioServerTransport();
    await server.connect(transport);
  } catch (_) {
    startStdlibStdioServer();
  }
})();
