/**
 * Netlify Function: /api/predict
 * Proxies multipart Excel uploads to the FastAPI /predict endpoint.
 *
 * Environment variables (set in Netlify UI → Site settings → Environment):
 *   FASTAPI_URL  — base URL of the FastAPI backend, e.g. https://api.yourdomain.com
 *                  Falls back to localhost:8000 for local `netlify dev` testing.
 */

const https = require("https");
const http  = require("http");
const { URL } = require("url");

const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";

exports.handler = async (event) => {
  // Only accept POST
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: "Method Not Allowed — use POST" }),
    };
  }

  const targetUrl = new URL("/predict", FASTAPI_URL);
  const outputFormat = event.queryStringParameters?.format || "dxf";
  targetUrl.searchParams.set("output_format", outputFormat);

  // Forward the raw body (multipart/form-data) to FastAPI
  const body = event.isBase64Encoded
    ? Buffer.from(event.body, "base64")
    : Buffer.from(event.body || "", "utf8");

  const contentType = event.headers["content-type"] || "application/octet-stream";

  return new Promise((resolve) => {
    const lib = targetUrl.protocol === "https:" ? https : http;

    const req = lib.request(
      {
        hostname: targetUrl.hostname,
        port:     targetUrl.port || (targetUrl.protocol === "https:" ? 443 : 80),
        path:     targetUrl.pathname + targetUrl.search,
        method:   "POST",
        headers: {
          "Content-Type":   contentType,
          "Content-Length": body.length,
          "X-Forwarded-By": "netlify-function",
        },
        timeout: 30000,
      },
      (res) => {
        const chunks = [];
        res.on("data", (chunk) => chunks.push(chunk));
        res.on("end", () => {
          const responseBody = Buffer.concat(chunks);
          const isText = (res.headers["content-type"] || "").includes("application/json");
          resolve({
            statusCode: res.statusCode,
            headers: {
              "Content-Type":        res.headers["content-type"] || "application/octet-stream",
              "Content-Disposition": res.headers["content-disposition"] || "",
              "Access-Control-Allow-Origin": "*",
            },
            body:            isText ? responseBody.toString("utf8") : responseBody.toString("base64"),
            isBase64Encoded: !isText,
          });
        });
      }
    );

    req.on("error", (err) => {
      resolve({
        statusCode: 502,
        body: JSON.stringify({ error: `Backend unreachable: ${err.message}` }),
      });
    });

    req.on("timeout", () => {
      req.destroy();
      resolve({
        statusCode: 504,
        body: JSON.stringify({ error: "Backend timeout after 30s" }),
      });
    });

    req.write(body);
    req.end();
  });
};
