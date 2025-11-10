@echo off
REM Clean build script to reduce false positives

echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo.

echo Building sync.exe with optimized settings...
pyinstaller ^
    --onefile ^
    --name sync ^
    --clean ^
    --noconfirm ^
    --log-level WARN ^
    --noupx ^
    --optimize 2 ^
    --exclude-module pytest ^
    --exclude-module unittest ^
    --exclude-module pdb ^
    --exclude-module doctest ^
    --exclude-module sqlite3 ^
    --exclude-module tkinter ^
    --add-data "config.json;." ^
    --add-data "queries;queries" ^
    sync.py

echo.
echo Build complete! Check dist/sync.exe
echo.

REM Move to final location
if exist "TaskForm Sync" (
    copy "dist\sync.exe" "TaskForm Sync\sync.exe"
    echo Copied to TaskForm Sync folder
)

echo.
echo Tips to reduce false positives:
echo 1. Add dist folder to antivirus exclusions
echo 2. Upload to VirusTotal to verify it's clean
echo 3. Consider code signing for production use
echo.
pause