@echo off
REM Build script for creating standalone executables

echo Building DataSync executables...
echo.

REM Build GUI executable
echo Building DataSync.exe...
pyinstaller --onefile --windowed --name DataSync gui.py --icon=NONE
echo.

REM Build sync service executable
echo Building sync.exe...
pyinstaller --onefile --name sync sync.py --icon=NONE
echo.

echo Build complete!
echo Executables are in the dist folder.
echo.
pause