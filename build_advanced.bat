@echo off
REM Advanced build script met alle dependencies embedded

echo ================================================
echo   DataSync - Advanced Portable Build
echo ================================================
echo.

REM Set Python path
set PYTHON="C:\Users\Joshua Faustin\AppData\Local\Programs\Python\Python313\python.exe"
set PYINSTALLER="C:\Users\Joshua Faustin\AppData\Local\Programs\Python\Python313\Scripts\pyinstaller.exe"

REM Check if PyInstaller is installed
%PYTHON% -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    %PYTHON% -m pip install pyinstaller
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
%PYINSTALLER% --onefile ^
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
%PYINSTALLER% --onefile ^
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
if exist "TaskForm Sync" rmdir /s /q "TaskForm Sync"
mkdir "TaskForm Sync"
mkdir "TaskForm Sync\queries"
mkdir "TaskForm Sync\logs"

REM Copy executables
copy dist\DataSync.exe "TaskForm Sync\"
copy dist\sync.exe "TaskForm Sync\"

REM Copy Firebird client DLL if it exists
if exist fbclient.dll (
    echo Copying Firebird client library...
    copy fbclient.dll "TaskForm Sync\"
) else (
    echo WARNING: fbclient.dll not found - Firebird support may not work!
)

REM Copy config template and examples
copy config.json "TaskForm Sync\config.template.json"
copy queries\*.sql "TaskForm Sync\queries\"
copy logs\.gitkeep "TaskForm Sync\logs\"

REM Copy documentation
copy README.md "TaskForm Sync\"
copy DEPLOYMENT.md "TaskForm Sync\"
copy INSTALLATIE.md "TaskForm Sync\"
copy USER_GUIDE.md "TaskForm Sync\"

REM Create ZIP file for distribution
echo.
echo Creating ZIP file for distribution...
if exist "TaskForm-Sync.zip" del /q "TaskForm-Sync.zip"
powershell -Command "Compress-Archive -Path 'TaskForm Sync' -DestinationPath 'TaskForm-Sync.zip' -Force"

if errorlevel 1 (
    echo WARNING: Failed to create ZIP file
) else (
    echo ZIP file created: TaskForm-Sync.zip
)

echo.
echo ================================================
echo   Build Complete!
echo ================================================
echo.
echo Portable package created in: TaskForm Sync\
echo ZIP file created: TaskForm-Sync.zip
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
echo   1. Test the executables in "TaskForm Sync\"
echo   2. Distribute TaskForm-Sync.zip to customers
echo   3. Users can unzip and run without Python!
echo.
pause