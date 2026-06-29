// Extension: harness-review-board
// Harness asset: interactive AI code-review board canvas.
//
// The agent runs the `harness-code-review` skill, then pushes findings into
// this canvas. The board groups findings by severity (blocking / warning /
// info), supports marking items resolved, and live-refreshes via SSE so the
// agent and user see the same state.

import { createServer } from "node:http";
import { joinSession, createCanvas } from "@github/copilot-sdk/extension";

// Per-instance state: { findings, clients, server, url }
const boards = new Map();
const SEVERITIES = ["blocking", "warning", "info"];

function ensure(instanceId) {
    let b = boards.get(instanceId);
    if (!b) {
        b = { findings: [], clients: new Set(), server: null, url: null };
        boards.set(instanceId, b);
    }
    return b;
}

function broadcast(b) {
    const payload = `data: ${JSON.stringify(b.findings)}\n\n`;
    for (const res of b.clients) res.write(payload);
}

function nextId(b) {
    return "f" + (b.findings.length + 1) + "-" + Math.random().toString(36).slice(2, 6);
}

function renderHtml(instanceId) {
    return `<!doctype html>
<html><head><meta charset="utf-8"/><title>Harness Review Board</title>
<style>
  :root{color-scheme:dark}
  body{font-family:system-ui,sans-serif;margin:0;background:#0d1117;color:#e6edf3}
  header{padding:14px 20px;border-bottom:1px solid #30363d;display:flex;align-items:center;gap:10px}
  header h1{font-size:16px;margin:0}.tag{font-size:11px;color:#7d8590}
  .cols{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;padding:18px}
  .col{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:10px;min-height:200px}
  .col h2{font-size:13px;margin:4px 6px 12px;display:flex;justify-content:space-between}
  .blocking h2{color:#ff7b72}.warning h2{color:#d29922}.info h2{color:#58a6ff}
  .card{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:10px;margin-bottom:8px}
  .card.done{opacity:.45;text-decoration:line-through}
  .card .f{font-size:11px;color:#7d8590}.card .t{font-weight:600;margin:4px 0;font-size:13px}
  .card .d{font-size:12px;color:#adbac7}.empty{color:#484f58;font-size:12px;padding:8px}
</style></head>
<body>
  <header><h1>🔧 Harness Review Board</h1><span class="tag">${instanceId}</span></header>
  <div class="cols" id="cols"></div>
  <script>
    const C=document.getElementById('cols');
    const SEV=${JSON.stringify(SEVERITIES)};
    function render(items){
      C.innerHTML=SEV.map(s=>{
        const f=items.filter(i=>i.severity===s);
        const cards=f.map(i=>'<div class="card '+(i.resolved?'done':'')+'"><div class="f">'+(i.file||'')+(i.line?':'+i.line:'')+'</div><div class="t">'+i.title+'</div><div class="d">'+(i.detail||'')+'</div></div>').join('')||'<div class="empty">없음</div>';
        return '<div class="col '+s+'"><h2>'+s.toUpperCase()+'<span>'+f.length+'</span></h2>'+cards+'</div>';
      }).join('');
    }
    const es=new EventSource('/events');
    es.onmessage=e=>render(JSON.parse(e.data));
    fetch('/state').then(r=>r.json()).then(render);
  </script>
</body></html>`;
}

async function startServer(instanceId) {
    const b = ensure(instanceId);
    const server = createServer((req, res) => {
        if (req.url === "/state") {
            res.setHeader("Content-Type", "application/json");
            return res.end(JSON.stringify(b.findings));
        }
        if (req.url === "/events") {
            res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive" });
            res.write(`data: ${JSON.stringify(b.findings)}\n\n`);
            b.clients.add(res);
            req.on("close", () => b.clients.delete(res));
            return;
        }
        res.setHeader("Content-Type", "text/html; charset=utf-8");
        res.end(renderHtml(instanceId));
    });
    await new Promise((r) => server.listen(0, "127.0.0.1", r));
    b.server = server;
    b.url = `http://127.0.0.1:${server.address().port}/`;
}

const session = await joinSession({
    canvases: [
        createCanvas({
            id: "harness-review-board",
            displayName: "Harness Review Board",
            description: "Interactive AI code-review board grouped by severity",
            inputSchema: {
                type: "object",
                properties: { findings: { type: "array", items: { type: "object" } } },
            },
            actions: [
                {
                    name: "set_findings",
                    description: "Replace all findings on the board",
                    inputSchema: {
                        type: "object",
                        properties: { findings: { type: "array", items: { type: "object" } } },
                        required: ["findings"],
                    },
                    handler: async (ctx) => {
                        const b = ensure(ctx.instanceId);
                        b.findings = (ctx.input?.findings || []).map((f) => ({ id: nextId(b), resolved: false, severity: "info", ...f }));
                        broadcast(b);
                        return { ok: true, count: b.findings.length };
                    },
                },
                {
                    name: "add_finding",
                    description: "Add one finding (title, severity, file, line, detail)",
                    inputSchema: {
                        type: "object",
                        properties: {
                            title: { type: "string" }, severity: { enum: SEVERITIES },
                            file: { type: "string" }, line: { type: "number" }, detail: { type: "string" },
                        },
                        required: ["title", "severity"],
                    },
                    handler: async (ctx) => {
                        const b = ensure(ctx.instanceId);
                        b.findings.push({ id: nextId(b), resolved: false, ...ctx.input });
                        broadcast(b);
                        return { ok: true, count: b.findings.length };
                    },
                },
                {
                    name: "resolve_finding",
                    description: "Mark a finding resolved by id",
                    inputSchema: { type: "object", properties: { id: { type: "string" } }, required: ["id"] },
                    handler: async (ctx) => {
                        const b = ensure(ctx.instanceId);
                        const f = b.findings.find((x) => x.id === ctx.input.id);
                        if (f) f.resolved = true;
                        broadcast(b);
                        return { ok: !!f };
                    },
                },
            ],
            open: async (ctx) => {
                const b = ensure(ctx.instanceId);
                if (!b.server) await startServer(ctx.instanceId);
                if (Array.isArray(ctx.input?.findings)) {
                    b.findings = ctx.input.findings.map((f) => ({ id: nextId(b), resolved: false, severity: "info", ...f }));
                    broadcast(b);
                }
                return { title: "Harness Review Board", url: b.url };
            },
            onClose: async (ctx) => {
                const b = boards.get(ctx.instanceId);
                if (b?.server) { boards.delete(ctx.instanceId); await new Promise((r) => b.server.close(() => r())); }
            },
        }),
    ],
});
