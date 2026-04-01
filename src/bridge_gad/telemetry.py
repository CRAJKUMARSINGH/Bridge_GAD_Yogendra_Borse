"""Telemetry module — opt-in only.

FIXES applied:
  KERO-002  — Telemetry is DISABLED by default; requires BRIDGE_GAD_TELEMETRY=1
  QODER-005 — save() is now debounced; disk write happens at most once per session
              rather than on every event() call
"""

import json
import os
import time
import datetime
import atexit
from pathlib import Path

TELEMETRY_FILE = Path.home() / "Bridge_GAD_Telemetry.json"

# FIX KERO-002: opt-in via environment variable; default is OFF
TELEMETRY_ENABLED: bool = os.environ.get("BRIDGE_GAD_TELEMETRY", "0") == "1"


class Telemetry:
    """Lightweight usage telemetry — only active when BRIDGE_GAD_TELEMETRY=1."""

    def __init__(self) -> None:
        self.start_time = time.time()
        self.data: dict = {"last_session": str(datetime.datetime.now())}
        self._dirty = False
        if TELEMETRY_ENABLED:
            self._load()
            # FIX QODER-005: flush once at process exit instead of on every event
            atexit.register(self._flush)

    def _load(self) -> None:
        if TELEMETRY_FILE.exists():
            try:
                with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
            except Exception:
                pass

    def event(self, name: str) -> None:
        """Record a named event. No-op when telemetry is disabled."""
        if not TELEMETRY_ENABLED:
            return
        self.data[name] = self.data.get(name, 0) + 1
        self._dirty = True
        # No immediate disk write — flushed at exit (FIX QODER-005)

    def _flush(self) -> None:
        """Write accumulated data to disk once (called at process exit)."""
        if not self._dirty:
            return
        elapsed = time.time() - self.start_time
        self.data["total_runtime_sec"] = self.data.get("total_runtime_sec", 0) + elapsed
        try:
            with open(TELEMETRY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def summarize(self) -> str:
        runtime_hr = self.data.get("total_runtime_sec", 0) / 3600
        return (
            f"Telemetry enabled: {TELEMETRY_ENABLED}\n"
            f"Sessions: {self.data.get('sessions', 0)}\n"
            f"Total runtime: {runtime_hr:.2f} hours\n"
            f"Feature uses: {self.data}"
        )


# Module-level singleton — inert when TELEMETRY_ENABLED is False
telemetry = Telemetry()
