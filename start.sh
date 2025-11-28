#!/bin/bash
# Bridge GAD FastAPI Server Launcher

set -e

echo "🌉 Starting Bridge GAD Generator..."
echo "📍 Port: 5000"
echo "📚 Docs: http://localhost:5000/docs"
echo "=" 60

# Add src to Python path and run server
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
cd "$(dirname "$0")"

# Run the FastAPI server
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

import uvicorn
from bridge_gad.api import app

uvicorn.run(
    app,
    host='0.0.0.0',
    port=5000,
    reload=False,
    log_level='info'
)
"
