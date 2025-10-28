@echo off
REM Advanced build script met alle dependencies embedded

echo ================================================
echo   DataSync - Advanced Portable Build
echo ================================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo.

REM Build GUI executable
echo Building DataSync.exe (GUI)...
pyinstaller --onefile ^
    --windowed ^
    --name DataSync ^
    --add-data "config.json;." ^
    --hidden-import tkinter ^
    --hidden-import pyodbc ^
    --hidden-import fdb ^
    --hidden-import requests ^
    gui.py

if errorlevel 1 (
    echo ERROR: Failed to build DataSync.exe
    pause
    exit /b 1
)
echo.

REM Build sync service executable
echo Building sync.exe (Service)...
pyinstaller --onefile ^
    --name sync ^
    --add-data "config.json;." ^
    --hidden-import pyodbc ^
    --hidden-import fdb ^
    --hidden-import requests ^
    sync.py

if errorlevel 1 (
    echo ERROR: Failed to build sync.exe
    pause
    exit /b 1
)
echo.

REM Create deployment package
echo Creating deployment package...
if exist DataSync-Portable rmdir /s /q DataSync-Portable
mkdir DataSync-Portable
mkdir DataSync-Portable\queries
mkdir DataSync-Portable\logs

REM Copy executables
copy dist\DataSync.exe DataSync-Portable\
copy dist\sync.exe DataSync-Portable\

REM Copy config and examples
copy config.json DataSync-Portable\
copy queries\*.sql DataSync-Portable\queries\
copy logs\.gitkeep DataSync-Portable\logs\

REM Copy documentation
copy README.md DataSync-Portable\
copy DEPLOYMENT.md DataSync-Portable\

echo.
echo ================================================
echo   Build Complete!
echo ================================================
echo.
echo Portable package created in: DataSync-Portable\
echo.
echo Contents:
echo   - DataSync.exe (GUI)
echo   - sync.exe (Service)
echo   - config.json (Template)
echo   - queries\ (Example SQL files)
echo   - logs\ (Log folder)
echo   - Documentation
echo.
echo Next steps:
echo   1. Test the executables in DataSync-Portable\
echo   2. Zip the folder for distribution
echo   3. Users can unzip and run without Python!
echo.
pause