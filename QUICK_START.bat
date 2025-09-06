@echo off
title Quick Start - Bridge GAD Generator
echo ========================================
echo    Quick Start - Bridge GAD Generator
echo ========================================
echo.
echo Quick starting the Enhanced Bridge App...
echo.
echo Features:
echo ✓ All missing LISP functions implemented
echo ✓ Professional drawing layouts
echo ✓ Enhanced pier and abutment geometry
echo ✓ Cross-section terrain plotting
echo ✓ Advanced text styling
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo Activating environment and starting app...
call venv\Scripts\activate.bat
python enhanced_bridge_app.py

echo.
echo App closed. Press any key to exit...
pause >nul
