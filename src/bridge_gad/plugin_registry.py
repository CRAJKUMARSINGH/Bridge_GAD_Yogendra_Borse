"""Plugin registry — discovers and caches installed plugin metadata.

FIXES applied:
  KIMI-005 — changed absolute import to relative import
  WARP-004 — requests import and HTTP call moved inside function (lazy);
             no longer blocks startup on import
"""

import json
from pathlib import Path

# FIX KIMI-005: use relative import so the package works when installed
from .plugins import load_plugins

REGISTRY_FILE = Path.home() / "Bridge_GAD_PluginRegistry.json"
_PLUGIN_UPDATE_URL = (
    "https://api.github.com/repos/CRAJKUMARSINGH/Bridge_GAD_Yogendra_Borse/releases/latest"
)


def build_registry() -> dict:
    """Collect metadata of all installed plugins and persist to disk."""
    plugins = load_plugins()
    registry = {
        p.name: {
            "version": getattr(p, "version", "1.0.0"),
            "author": getattr(p, "author", "Unknown"),
            "description": getattr(p, "description", ""),
        }
        for p in plugins
    }
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    return registry


def get_registry() -> dict:
    """Return the cached plugin registry, or an empty dict if not built yet."""
    if REGISTRY_FILE.exists():
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def check_for_plugin_updates() -> str:
    """Check GitHub for the latest plugin pack release.

    FIX WARP-004: `import requests` is deferred to inside this function so
    that importing the module never triggers a network call.  Call this
    function explicitly only when the user requests an update check.
    """
    try:
        import requests  # lazy import — no startup penalty
        r = requests.get(_PLUGIN_UPDATE_URL, timeout=5)
        if r.status_code == 200:
            data = r.json()
            # Basic schema validation before trusting the response
            latest = str(data.get("tag_name", "")).strip()
            if latest and latest.startswith("v"):
                return f"Latest plugin pack version: {latest}"
    except Exception:
        pass
    return "Unable to check for updates."
