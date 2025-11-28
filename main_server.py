#!/usr/bin/env python3
"""
Bridge GAD FastAPI Server - Main Entry Point
Runs on 0.0.0.0:5000 for web access
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add src to path so we can import bridge_gad
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
os.chdir(project_root)

try:
    from bridge_gad.api import app
    
    if __name__ == "__main__":
        print("\n" + "=" * 70)
        print("🌉 BRIDGE GAD GENERATOR API - STARTING")
        print("=" * 70)
        print("🚀 Server running at: http://localhost:5000")
        print("📚 API Docs at:       http://localhost:5000/docs")
        print("🏥 Health check at:   http://localhost:5000/health")
        print("=" * 70 + "\n")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=5000,
            reload=False,
            log_level="info"
        )
        
except ImportError as e:
    print(f"❌ ERROR: Failed to import Bridge GAD module: {e}")
    print(f"📁 Project root: {project_root}")
    print(f"📁 Source path: {project_root / 'src'}")
    print(f"🔍 sys.path: {sys.path}")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
