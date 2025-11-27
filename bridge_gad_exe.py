#!/usr/bin/env python3
"""
Executable script for Bridge GAD Generator.
This script can be used to create a standalone executable.
"""

import sys
import os

# Add the src directory to the path so we can import bridge_gad modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bridge_gad.cli import main

if __name__ == "__main__":
    main()