@echo off
setlocal enabledelayedexpansion

:: 1. Force Working Directory to Script Directory (Crucial for Windows double-click)
cd /d "%~dp0"

:: 2. Set Console CodePage to UTF-8 for clean typography
chcp 65001 >nul 2>&1

title KHAGOL // SPACE AGENCY — The Mission Architect

echo =========================================================================
echo       KHAGOL // SPACE AGENCY : THE MISSION ARCHITECT
echo       Systems Engineering & Planetary Exploration Simulation Platform
echo =========================================================================
echo.

:: 3. Detect Python Runtime
set "PY_CMD="
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=python"
) else (
    py -3 --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=py -3"
    ) else (
        py --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set "PY_CMD=py"
        )
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python 3.10+ was not found on your system PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo (Make sure to check the box "Add Python to PATH" during installation)
    echo.
    pause
    exit /b 1
)

echo [OK] Python runtime detected via: %PY_CMD%

:: 4. Virtual Environment (.venv) Setup
if not exist ".venv" (
    echo [INFO] Creating Python virtual environment in .venv ...
    %PY_CMD% -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Could not create virtual environment. Running with global Python...
        set "VENV_PY=%PY_CMD%"
    ) else (
        set "VENV_PY=.venv\Scripts\python.exe"
    )
) else (
    set "VENV_PY=.venv\Scripts\python.exe"
)

:: Activate venv if activate.bat exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    set "RUN_PY=python"
) else (
    set "RUN_PY=%PY_CMD%"
)

:: 5. Dependency Verification
echo [INFO] Verifying aerospace dependencies from requirements.txt ...
%RUN_PY% -m pip install --upgrade pip >nul 2>&1
if exist "requirements.txt" (
    %RUN_PY% -m pip install -r requirements.txt --quiet
) else (
    %RUN_PY% -m pip install fastapi uvicorn pydantic httpx websockets python-multipart pytest --quiet
)

:: 6. Set Environment Variables
set "PYTHONPATH=%~dp0"

echo.
echo =========================================================================
echo   SYSTEM ONLINE — HOSTING ON LOCALHOST 8000:
echo   - Public Portal:        http://localhost:8000/
echo   - Workstation App:      http://localhost:8000/app
echo   - Mars Exploration:     http://localhost:8000/mars
echo   - Titan Surface EVA:    http://localhost:8000/static/titan.html
echo   - API Documentation:    http://localhost:8000/docs
echo =========================================================================
echo.

:: 7. Launch Browser automatically
echo [INFO] Opening mission interface at http://localhost:8000/ ...
start "" "http://localhost:8000/"

:: 8. Launch Uvicorn ASGI Server on 0.0.0.0:8000 (accessible on localhost:8000)
echo [INFO] Starting FastAPI Uvicorn Server on http://localhost:8000 ...
%RUN_PY% -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server encountered an unexpected termination.
    pause
)
