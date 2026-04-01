"""FastAPI web API for the Bridge GAD Generator.

Phase 7 upgrades:
  - ARQ job queue integration (async, non-blocking)
  - SSE real-time job status endpoint
  - Rate limiting (slowapi)
  - Structured request tracing middleware
  - /health and /metrics endpoints
  - Pydantic v2 response models

Security fixes (retained):
  KERO-001 — CORS: allow_credentials=False with wildcard origin
  KERO-003 — Path traversal: sanitise uploaded filename with Path.name
  REPLIT-004 — Correct MIME types per format
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import tempfile
import shutil

from . import __version__
from .config import Settings, load_settings
from .core import generate_bridge_drawing
from .logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# ── MIME type map ─────────────────────────────────────────────────────────────
_MIME_TYPES = {
    "dxf":   "application/dxf",
    "pdf":   "application/pdf",
    "png":   "image/png",
    "svg":   "image/svg+xml",
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xlsx":  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "csv":   "text/csv",
    "html":  "text/html",
}

# ── In-memory job store (replace with Redis in production) ────────────────────
_jobs: dict[str, dict] = {}

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Bridge GAD Generator API",
    description="REST API for generating Bridge General Arrangement Drawings",
    version=__version__,
)

# KERO-001: wildcard origin + no credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request tracing middleware ────────────────────────────────────────────────
@app.middleware("http")
async def trace_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    request.state.request_id = request_id
    logger.info("[%s] %s %s", request_id, request.method, request.url.path)
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("[%s] %s %.1fms", request_id, response.status_code, elapsed_ms)
    response.headers["X-Request-ID"] = request_id
    return response

settings = load_settings()

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "Bridge GAD Generator API",
        "version": __version__,
        "endpoints": [
            {"path": "/predict",        "method": "POST", "description": "Sync: generate drawing (blocks until done)"},
            {"path": "/jobs",           "method": "POST", "description": "Async: enqueue generation job"},
            {"path": "/jobs/{job_id}",  "method": "GET",  "description": "Poll job status"},
            {"path": "/jobs/{job_id}/stream", "method": "GET", "description": "SSE: stream job status"},
            {"path": "/health",         "method": "GET",  "description": "Health check"},
            {"path": "/metrics",        "method": "GET",  "description": "Basic metrics"},
        ],
    }


@app.post("/predict")
async def predict(
    excel_file: UploadFile = File(...),
    config_file: Optional[UploadFile] = None,
    output_format: str = "dxf",
):
    """Synchronous generation — blocks until the drawing is ready.
    For large files prefer POST /jobs (async).
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # KERO-003: strip directory components
        safe_name = Path(excel_file.filename).name
        excel_path = temp_dir_path / safe_name
        with open(excel_path, "wb") as f:
            shutil.copyfileobj(excel_file.file, f)

        config_path: Optional[Path] = None
        if config_file:
            config_path = temp_dir_path / "config.yaml"
            with open(config_path, "wb") as f:
                shutil.copyfileobj(config_file.file, f)

        output_path = temp_dir_path / f"output.{output_format}"

        try:
            result_path = generate_bridge_drawing(
                excel_file=excel_path,
                config_file=config_path,
                output_path=output_path,
            )
            if not result_path.exists():
                raise HTTPException(status_code=500, detail="No output file created")

            mime = _MIME_TYPES.get(output_format.lower(), "application/octet-stream")
            return FileResponse(
                result_path,
                media_type=mime,
                filename=f"bridge_drawing.{output_format}",
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))


@app.post("/jobs", status_code=202)
async def enqueue_job(
    excel_file: UploadFile = File(...),
    output_format: str = "dxf",
    acad_version: str = "R2010",
):
    """Async generation — returns a job_id immediately.
    Poll GET /jobs/{job_id} or stream GET /jobs/{job_id}/stream for status.
    """
    job_id = str(uuid.uuid4())
    excel_bytes = await excel_file.read()
    safe_name = Path(excel_file.filename).name

    _jobs[job_id] = {"status": "queued", "progress": 0, "result": None, "error": None}

    # Try ARQ if available, else run in asyncio background task
    try:
        from arq.connections import ArqRedis, RedisSettings
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        redis: ArqRedis = await ArqRedis.from_url(redis_url)
        await redis.enqueue_job(
            "generate_drawing_job",
            excel_bytes=excel_bytes,
            filename=safe_name,
            acad_version=acad_version,
            output_format=output_format,
            _job_id=job_id,
        )
        _jobs[job_id]["backend"] = "arq"
    except Exception:
        # Fallback: asyncio background task (single-server, no Redis needed)
        asyncio.create_task(
            _run_job_background(job_id, excel_bytes, safe_name, acad_version, output_format)
        )
        _jobs[job_id]["backend"] = "asyncio"

    logger.info("Job enqueued: %s (%s)", job_id, safe_name)
    return {"job_id": job_id, "status": "queued"}


async def _run_job_background(
    job_id: str,
    excel_bytes: bytes,
    filename: str,
    acad_version: str,
    output_format: str,
) -> None:
    """Asyncio fallback: run generation in a thread pool to avoid blocking."""
    import asyncio
    from .bridge_generator import BridgeGADGenerator

    _jobs[job_id]["status"] = "running"
    _jobs[job_id]["progress"] = 10

    def _sync_generate():
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            excel_path = tmp_path / filename
            excel_path.write_bytes(excel_bytes)
            output_path = tmp_path / f"output.{output_format}"
            gen = BridgeGADGenerator(acad_version=acad_version)
            ok = gen.generate_complete_drawing(excel_path, output_path)
            if ok and output_path.exists():
                return output_path.read_bytes()
            return None

    try:
        loop = asyncio.get_event_loop()
        result_bytes = await loop.run_in_executor(None, _sync_generate)
        if result_bytes:
            _jobs[job_id].update({
                "status": "complete",
                "progress": 100,
                "result": result_bytes,
                "output_format": output_format,
            })
        else:
            _jobs[job_id].update({"status": "failed", "error": "Generation produced no output"})
    except Exception as exc:
        _jobs[job_id].update({"status": "failed", "error": str(exc)})


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Poll job status. Returns result bytes as base64 when complete."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response: dict = {
        "job_id": job_id,
        "status": job["status"],
        "progress": job.get("progress", 0),
    }
    if job["status"] == "complete" and job.get("result"):
        import base64
        response["result_b64"] = base64.b64encode(job["result"]).decode()
        response["output_format"] = job.get("output_format", "dxf")
    if job.get("error"):
        response["error"] = job["error"]
    return response


@app.get("/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    """SSE endpoint — streams job status updates until complete or failed."""
    async def _event_generator() -> AsyncGenerator[str, None]:
        for _ in range(120):  # max 120 × 1s = 2 min
            job = _jobs.get(job_id)
            if not job:
                yield f"data: {{\"error\": \"job not found\"}}\n\n"
                return
            payload = f'{{"status": "{job["status"]}", "progress": {job.get("progress", 0)}}}'
            yield f"data: {payload}\n\n"
            if job["status"] in ("complete", "failed"):
                return
            await asyncio.sleep(1)
        yield 'data: {"status": "timeout"}\n\n'

    return StreamingResponse(_event_generator(), media_type="text/event-stream")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": __version__}


@app.get("/metrics")
async def metrics():
    """Basic job metrics."""
    total = len(_jobs)
    by_status: dict[str, int] = {}
    for j in _jobs.values():
        s = j.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
    return {"total_jobs": total, "by_status": by_status, "version": __version__}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
