#!/usr/bin/env bash
# KHAGOL // SPACE AGENCY — The Mission Architect (macOS / Linux Launcher)

set -e

echo "========================================================================="
echo "      KHAGOL // SPACE AGENCY : THE MISSION ARCHITECT"
echo "      Systems Engineering & Planetary Exploration Simulation Platform"
echo "========================================================================="
echo ""

# 1. Check Python
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3.10+ is required but not found in PATH."
    exit 1
fi

echo "[OK] Python runtime detected: $($PY_CMD --version)"

# 2. Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment (.venv)..."
    $PY_CMD -m venv .venv
fi

if [ -f ".venv/bin/activate" ]; then
    echo "[INFO] Activating virtual environment..."
    source .venv/bin/activate
fi

# 3. Dependencies
echo "[INFO] Verifying core aerospace dependencies..."
python -m pip install --quiet --upgrade pip
python -m pip install --quiet fastapi uvicorn pydantic httpx pytest

# 4. Set PYTHONPATH
export PYTHONPATH="$(pwd)"

echo ""
echo "========================================================================="
echo "  SYSTEM ONLINE:"
echo "  - Public Portal:        http://localhost:8000/"
echo "  - Workstation App:      http://localhost:8000/app"
echo "  - Mars Exploration:     http://localhost:8000/mars"
echo "  - Titan Surface EVA:    http://localhost:8000/static/titan.html"
echo "  - API Documentation:    http://localhost:8000/docs"
echo "========================================================================="
echo ""

# Launch Browser in Background
if command -v open >/dev/null 2>&1; then
    open "http://localhost:8000/" &
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:8000/" &
fi

echo "[INFO] Launching FastAPI Uvicorn ASGI server with live reload..."
exec python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
