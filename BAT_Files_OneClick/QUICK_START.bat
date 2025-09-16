@echo off
title BridgeGAD Quick Start
color 0A

echo ===============================================
echo   🚀 BRIDGE GAD - QUICK START
echo ===============================================

cd /d "%~dp0.."
call venv\Scripts\activate.bat

echo 🎯 Choose Quick Action:
echo [1] Generate Sample Bridge
echo [2] Start Web Server
echo [3] View All Commands
set /p choice="Choice (1-3): "

if "%choice%"=="1" (
    python -m bridge_gad generate sample_input.xlsx --output Test_Results_Output\quick_bridge.dxf
    echo ✅ Bridge generated: Test_Results_Output\quick_bridge.dxf
)
if "%choice%"=="2" (
    echo 🌐 Starting web server at http://localhost:8000
    python -m bridge_gad serve
)
if "%choice%"=="3" (
    python -m bridge_gad --help
)

pause