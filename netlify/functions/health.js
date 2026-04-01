/**
 * Netlify Function: /api/health
 * Returns Netlify function health + probes the FastAPI backend health endpoint.
 */

const https = require("https");
const http  = require("http");
const { URL } = require("url");

const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";

exports.handler = async () => {
  const result = {
    netlify_function: "ok",
    timestamp: new Date().toISOString(),
    fastapi_backend: "unknown",
    fastapi_url: FASTAPI_URL,
  };

  try {
    const backendStatus = await probeBackend();
    result.fastapi_backend = backendStatus;
  } catch (err) {
    result.fastapi_backend = `unreachable: ${err.message}`;
  }

  const allOk = result.fastapi_backend === "ok";
  return {
    statusCode: allOk ? 200 : 503,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    body: JSON.stringify(result, null, 2),
  };
};

function probeBackend() {
  return new Promise((resolve, reject) => {
    const url = new URL("/health", FASTAPI_URL);
    const lib = url.protocol === "https:" ? https : http;
    const req = lib.get(
      { hostname: url.hostname, port: url.port, path: url.pathname, timeout: 5000 },
      (res) => {
        const chunks = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () => {
          if (res.statusCode === 200) resolve("ok");
          else resolve(`http_${res.statusCode}`);
        });
      }
    );
    req.on("error", reject);
    req.on("timeout", () => { req.destroy(); reject(new Error("timeout")); });
  });
}
