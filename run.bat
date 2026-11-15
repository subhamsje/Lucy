@echo off
setlocal enabledelayedexpansion

title KHAGOL // SPACE AGENCY — The Mission Architect

echo =========================================================================
echo       KHAGOL // SPACE AGENCY : THE MISSION ARCHITECT
echo       Systems Engineering & Planetary Exploration Simulation Platform
echo =========================================================================
echo.

:: 1. Verify Python Installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    py --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python is not installed or not found in system PATH.
        echo Please install Python 3.10+ from https://www.python.org/
        pause
        exit /b 1
    ) else (
        set "PY_CMD=py -3"
    )
) else (
    set "PY_CMD=python"
)

echo [OK] Python runtime detected.

:: 2. Setup / Activate Virtual Environment
if not exist ".venv" (
    echo [INFO] Creating virtual environment in .venv ...
    %PY_CMD% -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] .venv activation script not found. Proceeding with system Python...
)

:: 3. Install Required Dependencies
echo [INFO] Verifying core aerospace dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet fastapi uvicorn pydantic httpx pytest

:: 4. Set Environment Variables
set PYTHONPATH=%CD%

echo.
echo =========================================================================
echo   SYSTEM ONLINE:
echo   - Public Portal:        http://localhost:8000/
echo   - Workstation App:      http://localhost:8000/app
echo   - Mars Exploration:     http://localhost:8000/mars
echo   - Titan Surface EVA:    http://localhost:8000/static/titan.html
echo   - API Documentation:    http://localhost:8000/docs
echo =========================================================================
echo.
echo [INFO] Opening default browser at http://localhost:8000/ ...
start "" "http://localhost:8000/"

echo [INFO] Launching FastAPI Uvicorn ASGI server with live reload...
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

pause
