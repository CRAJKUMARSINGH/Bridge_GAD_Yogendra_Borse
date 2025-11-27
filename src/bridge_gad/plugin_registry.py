import json
from pathlib import Path
from bridge_gad.plugins import load_plugins

REGISTRY_FILE = Path.home() / "Bridge_GAD_PluginRegistry.json"

def build_registry():
    """Collect metadata of all installed plugins."""
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

def get_registry():
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

import requests

PLUGIN_UPDATE_URL = "https://api.github.com/repos/CRAJKUMARSINGH/Bridge_GAD_Yogendra_Borse/releases/latest"

def check_for_plugin_updates():
    try:
        r = requests.get(PLUGIN_UPDATE_URL, timeout=5)
        if r.status_code == 200:
            latest = r.json().get("tag_name", "v1.0.0")
            return f"Latest plugin pack version: {latest}"
    except Exception:
        pass
    return "Unable to check for updates."