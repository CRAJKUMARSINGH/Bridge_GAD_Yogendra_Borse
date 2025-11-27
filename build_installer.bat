@echo off
echo ==============================
echo Bridge_GAD Installer Builder
echo ==============================

REM Check if Inno Setup Compiler is available
where ISCC >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Inno Setup Compiler (ISCC) not found.
    echo Please install Inno Setup from https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "dist\Bridge_GAD.exe" (
    echo ❌ CLI executable not found: dist\Bridge_GAD.exe
    echo Please build the executables first using build_exe.bat
    pause
    exit /b 1
)

if not exist "dist\Bridge_GAD_GUI.exe" (
    echo ❌ GUI executable not found: dist\Bridge_GAD_GUI.exe
    echo Please build the executables first using build_exe.bat
    pause
    exit /b 1
)

if not exist "docs\Bridge_GAD_User_Manual.pdf" (
    echo ❌ User manual not found: docs\Bridge_GAD_User_Manual.pdf
    echo Please generate the manual first using build_manual.bat
    pause
    exit /b 1
)

if not exist "bridge.ico" (
    echo ⚠️  Application icon not found: bridge.ico
    echo Continuing without icon...
)

if not exist "LICENSE" (
    echo ⚠️  License file not found: LICENSE
    echo Continuing without license...
)

if not exist "VERSION.txt" (
    echo ❌ Version file not found: VERSION.txt
    echo Please create VERSION.txt with the version number
    pause
    exit /b 1
)

REM Build the installer
echo Building installer...
ISCC "Bridge_GAD_Installer.iss"

if %errorlevel% equ 0 (
    echo.
    echo ✅ Installer built successfully!
    echo Output: dist\Bridge_GAD_Setup.exe
) else (
    echo.
    echo ❌ Installer build failed!
    exit /b 1
)

pause