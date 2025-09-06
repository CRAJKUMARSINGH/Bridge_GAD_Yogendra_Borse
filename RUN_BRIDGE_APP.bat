@echo off
title Enhanced Bridge GAD Generator
echo ========================================
echo    Enhanced Bridge GAD Generator
echo ========================================
echo.
echo Starting the Enhanced Bridge Application...
echo.
echo This application includes ALL missing LISP functions:
echo - Enhanced Pier Geometry with detailed drawings
echo - Complex Abutment Geometry with dirt walls
echo - Professional Layout Grid System
echo - Advanced Text Styling and dimensioning
echo - Cross-Section terrain representation
echo.
echo Controls:
echo - Mouse wheel: Zoom in/out
echo - Mouse drag: Pan around
echo - I: Enter input mode for parameters
echo - D: Save as DXF file
echo - P: Save as PDF file
echo - R: Reset view
echo.
echo Press any key to start...
pause >nul

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing required packages...
pip install -r requirements.txt

echo.
echo Starting Enhanced Bridge GAD Generator...
python enhanced_bridge_app.py

echo.
echo Application closed.
echo Press any key to exit...
pause >nul
