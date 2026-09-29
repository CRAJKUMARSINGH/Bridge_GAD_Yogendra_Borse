import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dist = path.join(root, "frontend", "dist");
const port = Number(process.env.PORT || 3000);
const pythonApi = (process.env.PYTHON_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".json": "application/json; charset=utf-8",
  ".ico": "image/x-icon",
};

function sendJson(response, status, payload) {
  const body = JSON.stringify(payload);
  response.writeHead(status, { "content-type": "application/json; charset=utf-8", "content-length": Buffer.byteLength(body) });
  response.end(body);
}

async function readRequestBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return Buffer.concat(chunks);
}

async function proxyToPython(request, response, requestPath, query) {
  const body = ["GET", "HEAD"].includes(request.method) ? undefined : await readRequestBody(request);
  const headers = {};
  if (request.headers["content-type"]) headers["content-type"] = request.headers["content-type"];
  if (request.headers.accept) headers.accept = request.headers.accept;
  const upstream = await fetch(`${pythonApi}${requestPath}${query}`, {
    method: request.method,
    headers,
    body,
  });
  const responseHeaders = {};
  for (const name of ["content-type", "content-disposition", "cache-control"]) {
    const value = upstream.headers.get(name);
    if (value) responseHeaders[name] = value;
  }
  response.writeHead(upstream.status, responseHeaders);
  response.end(Buffer.from(await upstream.arrayBuffer()));
}

function serveStatic(request, response, requestPath) {
  const requested = requestPath === "/" ? "/index.html" : requestPath;
  const candidate = path.resolve(dist, `.${requested}`);
  const safeCandidate = candidate.startsWith(`${dist}${path.sep}`) ? candidate : path.join(dist, "index.html");
  const filePath = fs.existsSync(safeCandidate) && fs.statSync(safeCandidate).isFile()
    ? safeCandidate
    : path.join(dist, "index.html");
  if (!fs.existsSync(filePath)) {
    sendJson(response, 503, { error: "Frontend is not built. Run npm run build first." });
    return;
  }
  response.writeHead(200, { "content-type": mimeTypes[path.extname(filePath)] || "application/octet-stream" });
  fs.createReadStream(filePath).pipe(response);
}

const server = http.createServer(async (request, response) => {
  const url = new URL(request.url || "/", `http://${request.headers.host || "localhost"}`);
  try {
    if (url.pathname === "/api/health") {
      try {
        const upstream = await fetch(`${pythonApi}/health`);
        sendJson(response, upstream.ok ? 200 : 503, { frontend: "online", python: upstream.ok ? "online" : "offline" });
      } catch {
        sendJson(response, 503, { frontend: "online", python: "offline" });
      }
      return;
    }
    if (url.pathname.startsWith("/api/")) {
      await proxyToPython(request, response, url.pathname.slice(4) || "/", url.search);
      return;
    }
    serveStatic(request, response, url.pathname);
  } catch (error) {
    sendJson(response, 502, { error: error instanceof Error ? error.message : "Gateway error" });
  }
});

server.listen(port, "0.0.0.0", () => {
  console.log(`Bridge GAD workspace listening on ${port}; Python API: ${pythonApi}`);
});