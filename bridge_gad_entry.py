"""Entry point script for Bridge GAD executable."""

import sys
import os

# Add the src directory to the path so we can import bridge_gad
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from bridge_gad.__main__ import app

if __name__ == "__main__":
    app()