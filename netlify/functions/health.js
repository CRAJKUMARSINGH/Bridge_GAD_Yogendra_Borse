exports.handler = async () => {
  const fastApiUrl = process.env.FASTAPI_URL;
  if (!fastApiUrl) {
    return {
      statusCode: 200,
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ frontend: "online", python: "demo", mode: "demo" }),
    };
  }

  try {
    const response = await fetch(`${fastApiUrl.replace(/\/$/, "")}/health`);
    return {
      statusCode: response.ok ? 200 : 503,
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ frontend: "online", python: response.ok ? "online" : "offline", mode: "live" }),
    };
  } catch {
    return {
      statusCode: 503,
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ frontend: "online", python: "offline", mode: "live" }),
    };
  }
};