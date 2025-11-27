@echo off
echo ===========================
echo Building Bridge_GAD .EXE
echo ===========================

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Create standalone executable using CLI entrypoint
python -m PyInstaller --onefile ^
    --name Bridge_GAD ^
    --hidden-import=yaml ^
    --hidden-import=ezdxf ^
    --hidden-import=reportlab ^
    --hidden-import=pygame ^
    --hidden-import=numpy ^
    --hidden-import=pandas ^
    --hidden-import=matplotlib ^
    --hidden-import=openpyxl ^
    --hidden-import=scipy ^
    --hidden-import=requests ^
    --hidden-import=xlrd ^
    --hidden-import=PIL ^
    --add-data "src\bridge_gad\*.py;bridge_gad" ^
    src\bridge_gad\cli.py

REM Build GUI version with version info
python -m PyInstaller --onefile --noconsole ^
    --name Bridge_GAD_GUI ^
    --icon=bridge.ico ^
    --version-file file_version_info.txt ^
    --hidden-import=yaml ^
    --hidden-import=ezdxf ^
    --hidden-import=reportlab ^
    --hidden-import=pygame ^
    --hidden-import=numpy ^
    --hidden-import=pandas ^
    --hidden-import=matplotlib ^
    --hidden-import=openpyxl ^
    --hidden-import=scipy ^
    --hidden-import=requests ^
    --hidden-import=xlrd ^
    --hidden-import=PIL ^
    --hidden-import=tkPDFViewer ^
    --add-data "docs\Bridge_GAD_User_Manual.md;docs" ^
    --add-data "docs\Bridge_GAD_User_Manual.pdf;docs" ^
    src\bridge_gad\gui.py

echo.
echo ✅ Build complete! Executable located in: dist\Bridge_GAD.exe
pause